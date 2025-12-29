import json
import base64
import io
import os
import tempfile
from urllib.parse import parse_qs
import google.generativeai as genai
import replicate
from PIL import Image

def handler(event, context):
    """
    Netlify serverless function for generating images with Gemini and removing backgrounds with Replicate
    """
    
    # Handle CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Content-Type': 'application/json'
    }
    
    # Handle preflight request
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        api_key = body.get('apiKey')
        prompt = body.get('prompt')
        reference_image = body.get('referenceImage')
        replicate_api_key = body.get('replicateApiKey')
        resolution = body.get('resolution', '1024x1024')  # New: resolution parameter
        
        if not api_key:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': {'message': 'API 키가 필요합니다'}})
            }
        
        if not prompt:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': {'message': '프롬프트가 필요합니다'}})
            }
        
        print(f"🚀 이미지 생성 시작...")
        print(f"Prompt: {prompt[:100]}...")
        print(f"Resolution: {resolution}")
        
        # Parse resolution
        width, height = map(int, resolution.split('x'))
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Set up generation config with resolution
        generation_config = {
            "temperature": 0.4,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_modalities": ["image"],
        }
        
        # Add prompt with resolution specification
        enhanced_prompt = f"{prompt}\n\nGenerate this as a high-quality {resolution} image with professional lighting and detail."
        
        if reference_image:
            # If reference image provided
            print("📸 참조 이미지 사용")
            image_data = base64.b64decode(reference_image.split(',')[1])
            reference_pil = Image.open(io.BytesIO(image_data))
            
            response = model.generate_content(
                [enhanced_prompt, reference_pil],
                generation_config=generation_config
            )
        else:
            # Text-only generation
            print("📝 텍스트만으로 생성")
            response = model.generate_content(
                enhanced_prompt,
                generation_config=generation_config
            )
        
        # Get the generated image
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data'):
                        generated_image_data = part.inline_data.data
                        print("✅ Gemini 이미지 생성 완료!")
                        
                        # Decode and potentially resize the image to exact resolution
                        img_bytes = base64.b64decode(generated_image_data)
                        img = Image.open(io.BytesIO(img_bytes))
                        
                        # Resize if needed to exact resolution
                        if img.size != (width, height):
                            print(f"🔄 이미지 크기 조정: {img.size} -> {width}x{height}")
                            img = img.resize((width, height), Image.LANCZOS)
                            
                            # Convert back to base64
                            buffer = io.BytesIO()
                            img.save(buffer, format='PNG')
                            generated_image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        
                        # Save to temporary file for Replicate
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                            tmp_file.write(base64.b64decode(generated_image_data))
                            tmp_filename = tmp_file.name
                        
                        # Remove background with Replicate if API key provided
                        has_transparency = False
                        warning = None
                        
                        if replicate_api_key:
                            try:
                                print("🔄 Replicate로 배경 제거 시작...")
                                os.environ['REPLICATE_API_TOKEN'] = replicate_api_key
                                
                                # Open the file and run Replicate
                                with open(tmp_filename, 'rb') as image_file:
                                    output = replicate.run(
                                        "lucataco/remove-bg:95fcc2a26d3899cd6c2691c900465aaeff466285a65c14638cc5f36f34befaf1",
                                        input={
                                            "image": image_file
                                        }
                                    )
                                
                                print(f"📡 Replicate 출력: {output}")
                                
                                # Download the result
                                import urllib.request
                                with urllib.request.urlopen(output) as response_data:
                                    result_image_data = base64.b64encode(response_data.read()).decode('utf-8')
                                
                                # Clean up temp file
                                os.unlink(tmp_filename)
                                
                                print("✅ 배경 제거 완료!")
                                has_transparency = True
                                
                                return {
                                    'statusCode': 200,
                                    'headers': headers,
                                    'body': json.dumps({
                                        'image': result_image_data,
                                        'hasTransparency': has_transparency,
                                        'warning': None,
                                        'resolution': resolution
                                    })
                                }
                                
                            except Exception as bg_error:
                                print(f"❌ Replicate 배경 제거 실패: {bg_error}")
                                warning = f"배경 제거 실패: {str(bg_error)}. 원본 이미지를 반환합니다."
                                # Clean up temp file
                                try:
                                    os.unlink(tmp_filename)
                                except:
                                    pass
                        else:
                            print("⚠️ Replicate API 키가 없어 배경 제거를 건너뜁니다")
                            warning = "Replicate API 키가 없어 배경 제거를 건너뛰었습니다."
                            # Clean up temp file
                            try:
                                os.unlink(tmp_filename)
                            except:
                                pass
                        
                        # Return original image if background removal failed or was skipped
                        return {
                            'statusCode': 200,
                            'headers': headers,
                            'body': json.dumps({
                                'image': generated_image_data,
                                'hasTransparency': has_transparency,
                                'warning': warning,
                                'resolution': resolution
                            })
                        }
        
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': {'message': '이미지를 생성할 수 없습니다'}})
        }
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': {'message': str(e)}})
        }
