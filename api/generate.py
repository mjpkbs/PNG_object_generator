from http.server import BaseHTTPRequestHandler
import json
import base64
import os
import replicate

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
            
            replicate_api_key = body.get('replicateApiKey')
            prompt = body.get('prompt')
            resolution = body.get('resolution', '1024x1024')
            
            if not replicate_api_key:
                self.send_error(400, 'Replicate API 키가 필요합니다')
                return
            
            if not prompt:
                self.send_error(400, '프롬프트가 필요합니다')
                return
            
            print(f"🚀 이미지 생성 시작...")
            print(f"Prompt: {prompt[:100]}...")
            print(f"Resolution: {resolution}")
            
            # Parse resolution
            width, height = map(int, resolution.split('x'))
            
            # Set up Replicate
            os.environ['REPLICATE_API_TOKEN'] = replicate_api_key
            
            # Use Flux for high-quality image generation
            print("🎨 Flux로 이미지 생성 중...")
            output = replicate.run(
                "black-forest-labs/flux-schnell",
                input={
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "num_outputs": 1,
                    "output_format": "png",
                    "output_quality": 100
                }
            )
            
            print(f"📡 Flux 출력: {output}")
            
            # Download the generated image
            # output is a list of FileOutput objects - convert to URL string
            import urllib.request
            file_output = output[0] if isinstance(output, list) else output
            image_url = str(file_output)  # Convert FileOutput to URL string
            
            print(f"🔗 이미지 URL: {image_url}")
            
            with urllib.request.urlopen(image_url) as response_data:
                image_bytes = response_data.read()
            
            # Convert to base64
            generated_image_data = base64.b64encode(image_bytes).decode('utf-8')
            
            print("✅ 이미지 생성 완료!")
            
            # Now remove background with Replicate
            has_transparency = False
            warning = None
            
            try:
                print("🔄 배경 제거 시작...")
                
                import tempfile
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    tmp_file.write(image_bytes)
                    tmp_filename = tmp_file.name
                
                # Remove background
                with open(tmp_filename, 'rb') as image_file:
                    bg_output = replicate.run(
                        "lucataco/remove-bg:95fcc2a26d3899cd6c2691c900465aaeff466285a65c14638cc5f36f34befaf1",
                        input={"image": image_file}
                    )
                
                print(f"📡 배경 제거 출력: {bg_output}")
                
                # Download result
                with urllib.request.urlopen(bg_output) as response_data:
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
                print(f"❌ 배경 제거 실패: {bg_error}")
                warning = f"배경 제거 실패: {str(bg_error)}. 원본 이미지를 반환합니다."
            
            # Return original image if background removal failed
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
            
        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            self.send_error(500, str(e))
