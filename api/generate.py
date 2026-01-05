from http.server import BaseHTTPRequestHandler
import json
import base64
import os
import replicate
from PIL import Image
import io

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        try:
            print("="*50)
            print("🔵 Request received")
            
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))
            
            print(f"📦 Request body keys: {list(body.keys())}")
            
            replicate_api_key = body.get('replicateApiKey')
            prompt = body.get('prompt')
            resolution = body.get('resolution', '1024x1024')
            model_choice = body.get('model', 'flux-schnell')  # Default to FLUX Schnell
            
            print(f"🤖 Model: {model_choice}")
            print(f"📐 Resolution: {resolution}")
            
            if not replicate_api_key:
                print("❌ No API key provided")
                self.send_error(400, 'Replicate API 키가 필요합니다')
                return
            
            if not prompt:
                print("❌ No prompt provided")
                self.send_error(400, '프롬프트가 필요합니다')
                return
            
            print(f"🚀 이미지 생성 시작...")
            print(f"Model: {model_choice}")
            print(f"Prompt: {prompt[:100]}...")
            print(f"해상도: {resolution}")
            
            # Parse resolution
            width, height = map(int, resolution.split('x'))
            
            # Set up Replicate
            os.environ['REPLICATE_API_TOKEN'] = replicate_api_key
            
            # Generate image based on selected model
            try:
                if model_choice == 'flux-schnell':
                    print(f"🎨 FLUX Schnell로 이미지 생성 중 (1024x1024)...")
                    output = replicate.run(
                        "black-forest-labs/flux-schnell",
                        input={
                            "prompt": prompt,
                            "output_format": "png",
                            "output_quality": 100,
                            "aspect_ratio": "1:1"
                        }
                    )
                    
                    # Extract URL from FileOutput (handle list or single object)
                    if isinstance(output, list):
                        output = output[0] if len(output) > 0 else output
                    
                    if hasattr(output, 'url'):
                        image_url = output.url
                    elif isinstance(output, str):
                        image_url = output
                    else:
                        image_url = str(output)
                    
                    print(f"🔗 생성된 이미지 URL: {image_url}")
                    
                    # If resolution > 1K, upscale before background removal
                    if width > 1024 or height > 1024:
                        print(f"📈 Real-ESRGAN으로 {width}x{height}로 업스케일 중...")
                        # Calculate scale factor
                        scale_factor = max(width / 1024, height / 1024)
                        if scale_factor <= 2:
                            scale = 2
                        elif scale_factor <= 4:
                            scale = 4
                        else:
                            scale = 4  # Max scale
                        
                        # Upscale with Real-ESRGAN (nightmareai)
                        upscale_output = replicate.run(
                            "nightmareai/real-esrgan",  # Use latest version
                            input={
                                "image": image_url,
                                "scale": scale,
                                "face_enhance": False
                            }
                        )
                        # Update output to upscaled result
                        if isinstance(upscale_output, list):
                            upscale_output = upscale_output[0] if len(upscale_output) > 0 else upscale_output
                        if hasattr(upscale_output, 'url'):
                            output = upscale_output.url
                        elif isinstance(upscale_output, str):
                            output = upscale_output
                        else:
                            output = str(upscale_output)
                        print(f"✅ 업스케일 완료! URL: {output}")
                    else:
                        # Use original URL
                        output = image_url
                    
                elif model_choice == 'nano-banana':
                    print(f"🎨 Google Nano Banana로 이미지 생성 중 (1024x1024)...")
                    output = replicate.run(
                        "google/nano-banana",
                        input={
                            "prompt": prompt,
                            "aspect_ratio": "1:1",
                            "output_format": "png"
                        }
                    )
                    
                    # Extract URL from output (handle list or single object)
                    if isinstance(output, list):
                        output = output[0] if len(output) > 0 else output
                    
                    if hasattr(output, 'url'):
                        image_url = output.url
                    elif isinstance(output, str):
                        image_url = output
                    else:
                        image_url = str(output)
                    
                    print(f"🔗 생성된 이미지 URL: {image_url}")
                    
                    # If resolution > 1K, upscale before background removal
                    if width > 1024 or height > 1024:
                        print(f"📈 Real-ESRGAN으로 {width}x{height}로 업스케일 중...")
                        # Calculate scale factor
                        scale_factor = max(width / 1024, height / 1024)
                        if scale_factor <= 2:
                            scale = 2
                        elif scale_factor <= 4:
                            scale = 4
                        else:
                            scale = 4  # Max scale
                        
                        # Upscale with Real-ESRGAN (nightmareai)
                        upscale_output = replicate.run(
                            "nightmareai/real-esrgan",  # Use latest version
                            input={
                                "image": image_url,
                                "scale": scale,
                                "face_enhance": False
                            }
                        )
                        # Update output to upscaled result
                        if isinstance(upscale_output, list):
                            upscale_output = upscale_output[0] if len(upscale_output) > 0 else upscale_output
                        if hasattr(upscale_output, 'url'):
                            output = upscale_output.url
                        elif isinstance(upscale_output, str):
                            output = upscale_output
                        else:
                            output = str(upscale_output)
                        print(f"✅ 업스케일 완료! URL: {output}")
                    else:
                        # Use original URL
                        output = image_url
                    
                elif model_choice == 'flux-pro-ultra':
                    print(f"🎨 FLUX 1.1 Pro Ultra로 {width}x{height} 이미지 생성 중...")
                    # FLUX Pro Ultra supports up to 4MP (2048x2048+)
                    output = replicate.run(
                        "black-forest-labs/flux-1.1-pro-ultra",
                        input={
                            "prompt": prompt,
                            "aspect_ratio": "1:1",
                            "output_format": "png",
                            "output_quality": "ultra",  # ultra for highest quality
                            "safety_tolerance": 2
                        }
                    )
                else:
                    print(f"❌ Unknown model: {model_choice}")
                    # Send JSON error instead of HTTP error
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'error': f'Unsupported model: {model_choice}'
                    }).encode('utf-8'))
                    return
            except Exception as model_error:
                print(f"❌ Model execution failed: {str(model_error)}")
                import traceback
                traceback.print_exc()
                # Send JSON error instead of HTTP error to avoid encoding issues with Korean
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_msg = str(model_error)
                self.wfile.write(json.dumps({
                    'error': f'Model execution failed: {error_msg}'
                }).encode('utf-8'))
                return
            
            print(f"📡 모델 출력: {output}")
            
            # Extract URL from output (handles FileOutput, string, or other types)
            if hasattr(output, 'url'):
                image_url = output.url
            elif isinstance(output, str):
                image_url = output
            else:
                image_url = str(output)
            
            print(f"🔗 이미지 URL: {image_url}")
            
            # Download the generated image
            import urllib.request
            with urllib.request.urlopen(image_url) as response_data:
                image_bytes = response_data.read()
            
            # Verify generated image size
            img = Image.open(io.BytesIO(image_bytes))
            actual_size = img.size
            print(f"✅ 생성된 이미지 크기: {actual_size[0]}x{actual_size[1]}")
            
            # Convert to base64
            generated_image_data = base64.b64encode(image_bytes).decode('utf-8')
            
            print("✅ 이미지 생성 완료!")
            
            # Remove background using 851-labs model
            has_transparency = False
            warning = None
            
            try:
                print("🔄 배경 제거 시작...")
                
                import tempfile
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    tmp_file.write(image_bytes)
                    tmp_filename = tmp_file.name
                
                # Remove background using BiRefNet (best quality!)
                with open(tmp_filename, 'rb') as image_file:
                    bg_output = replicate.run(
                        "men1scus/birefnet:f74986db0355b58403ed20963af156525e2891ea3c2d499bfbfb2a28cd87c5d7",
                        input={"image": image_file}
                    )
                
                print(f"📡 배경 제거 출력: {bg_output}")
                
                # Convert FileOutput to URL string
                bg_url = str(bg_output)
                print(f"🔗 배경 제거 URL: {bg_url}")
                
                # Download result
                with urllib.request.urlopen(bg_url) as response_data:
                    bg_removed_bytes = response_data.read()
                
                # Resize back to original resolution if needed
                bg_image = Image.open(io.BytesIO(bg_removed_bytes))
                bg_size = bg_image.size
                print(f"📏 배경 제거 후 크기: {bg_size}, 목표 크기: {actual_size}")
                
                if bg_size != actual_size:
                    print(f"🔄 이미지 크기 복원 중: {bg_size} -> {actual_size}")
                    # Use LANCZOS for high-quality upscaling
                    bg_image = bg_image.resize(actual_size, Image.LANCZOS)
                
                # Convert back to base64
                buffer = io.BytesIO()
                bg_image.save(buffer, format='PNG')
                result_image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                os.unlink(tmp_filename)
                
                print("✅ 배경 제거 완료!")
                has_transparency = True
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'image': result_image_data,
                    'originalImage': generated_image_data,  # Original image before BG removal
                    'hasTransparency': has_transparency,
                    'warning': None,
                    'resolution': f"{actual_size[0]}x{actual_size[1]}"
                }).encode())
                return
                
            except Exception as bg_error:
                print(f"❌ 배경 제거 실패: {bg_error}")
                warning = f"배경 제거 실패: {str(bg_error)}. 원본 이미지를 반환합니다."
                try:
                    os.unlink(tmp_filename)
                except:
                    pass
            
            # Return original image if background removal failed
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'image': generated_image_data,
                'hasTransparency': has_transparency,
                'warning': warning,
                'resolution': f"{actual_size[0]}x{actual_size[1]}"
            }).encode())
            
        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            self.send_error(500, str(e))
