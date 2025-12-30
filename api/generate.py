from http.server import BaseHTTPRequestHandler
import json
import base64
import io
import os
import tempfile
import google.generativeai as genai
import replicate
from PIL import Image

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))
            
            api_key = body.get('apiKey')
            prompt = body.get('prompt')
            reference_image = body.get('referenceImage')
            replicate_api_key = body.get('replicateApiKey')
            resolution = body.get('resolution', '1024x1024')
            
            if not api_key:
                self.send_error(400, 'API 키가 필요합니다')
                return
            
            if not prompt:
                self.send_error(400, '프롬프트가 필요합니다')
                return
            
            print(f"🚀 이미지 생성 시작...")
            print(f"Prompt: {prompt[:100]}...")
            print(f"Resolution: {resolution}")
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            # Set up generation config (without response_modalities)
            generation_config = {
                "temperature": 0.4,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
            
            # Add prompt with resolution specification
            enhanced_prompt = f"{prompt}\n\nGenerate this as a high-quality {resolution} image with professional lighting and detail."
            
            if reference_image:
                print("📸 참조 이미지 사용")
                image_data = base64.b64decode(reference_image.split(',')[1])
                reference_pil = Image.open(io.BytesIO(image_data))
                
                response = model.generate_content(
                    [enhanced_prompt, reference_pil],
                    generation_config=generation_config
                )
            else:
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
                            # inline_data.data is already base64 string
                            generated_image_data = base64.b64encode(part.inline_data.data).decode('utf-8')
                            print("✅ Gemini 이미지 생성 완료!")
                            
                            # Remove background with Replicate if API key provided
                            has_transparency = False
                            warning = None
                            
                            if replicate_api_key:
                                try:
                                    print("🔄 Replicate로 배경 제거 시작...")
                                    
                                    # Save to temp file for Replicate
                                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                                        tmp_file.write(base64.b64decode(generated_image_data))
                                        tmp_filename = tmp_file.name
                                    
                                    os.environ['REPLICATE_API_TOKEN'] = replicate_api_key
                                    
                                    with open(tmp_filename, 'rb') as image_file:
                                        output = replicate.run(
                                            "lucataco/remove-bg:95fcc2a26d3899cd6c2691c900465aaeff466285a65c14638cc5f36f34befaf1",
                                            input={"image": image_file}
                                        )
                                    
                                    print(f"📡 Replicate 출력: {output}")
                                    
                                    import urllib.request
                                    with urllib.request.urlopen(output) as response_data:
                                        result_image_data = base64.b64encode(response_data.read()).decode('utf-8')
                                    
                                    os.unlink(tmp_filename)
                                    
                                    print("✅ 배경 제거 완료!")
                                    has_transparency = True
                                    
                                    self.send_response(200)
                                    self.send_header('Content-Type', 'application/json')
                                    self.send_header('Access-Control-Allow-Origin', '*')
                                    self.end_headers()
                                    self.wfile.write(json.dumps({
                                        'image': result_image_data,
                                        'hasTransparency': has_transparency,
                                        'warning': None,
                                        'resolution': resolution
                                    }).encode())
                                    return
                                    
                                except Exception as bg_error:
                                    print(f"❌ Replicate 배경 제거 실패: {bg_error}")
                                    warning = f"배경 제거 실패: {str(bg_error)}. 원본 이미지를 반환합니다."
                                    try:
                                        os.unlink(tmp_filename)
                                    except:
                                        pass
                            else:
                                print("⚠️ Replicate API 키가 없어 배경 제거를 건너뜁니다")
                                warning = "Replicate API 키가 없어 배경 제거를 건너뛰었습니다."
                            
                            # Return original image (already base64 string from Gemini)
                            self.send_response(200)
                            self.send_header('Content-Type', 'application/json')
                            self.send_header('Access-Control-Allow-Origin', '*')
                            self.end_headers()
                            self.wfile.write(json.dumps({
                                'image': generated_image_data,
                                'hasTransparency': has_transparency,
                                'warning': warning,
                                'resolution': resolution
                            }).encode())
                            return
            
            self.send_error(500, '이미지를 생성할 수 없습니다')
            
        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            self.send_error(500, str(e))
