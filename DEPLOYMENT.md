# 빠른 배포 가이드

## 변경 사항 요약

✅ **Flask 서버를 Netlify Functions로 변환**
- Python Flask 서버 → Python Netlify Serverless Function
- `/api/generate` 엔드포인트 → `/.netlify/functions/generate`

✅ **해상도 선택 기능 추가**
- 1K (1024×1024)
- 1.5K (1536×1536)
- 2K (2048×2048)
- 2.5K (2560×2560)

✅ **프로젝트 구조 변경**
```
pixelsquid-netlify/
├── netlify.toml              # Netlify 설정
├── public/
│   └── index.html            # 프론트엔드
└── netlify/
    └── functions/
        ├── requirements.txt  # Python 패키지
        └── generate.py       # 백엔드 함수
```

## 3단계 배포 방법

### 1️⃣ GitHub 업로드

```bash
cd pixelsquid-netlify

# Git 초기화
git init
git add .
git commit -m "Initial commit: PixelSquid with Netlify support"

# GitHub에 푸시
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git branch -M main
git push -u origin main
```

### 2️⃣ Netlify 연결

1. https://app.netlify.com/ 접속
2. "Add new site" → "Import an existing project"
3. "Deploy with GitHub" 선택
4. 저장소 선택
5. 설정 확인:
   - **Build command**: (비워두기)
   - **Publish directory**: `public`
   - **Functions directory**: `netlify/functions`
6. "Deploy site" 클릭!

### 3️⃣ 완료!

배포가 완료되면 Netlify가 URL을 제공합니다 (예: `https://your-site-name.netlify.app`)

## 로컬 테스트 (선택사항)

```bash
# Netlify CLI 설치
npm install -g netlify-cli

# 로컬에서 실행
cd pixelsquid-netlify
netlify dev
```

로컬 서버: http://localhost:8888

## API 키 발급

- **Gemini API**: https://aistudio.google.com/app/apikey
- **Replicate API**: https://replicate.com/account/api-tokens

웹사이트에서 API 키를 입력하면 브라우저에 자동 저장됩니다.

## 주요 기능

✨ **해상도 선택**: 버튼으로 쉽게 1K~2.5K 선택
✨ **카메라 각도**: 3D 큐브 드래그로 각도 조절
✨ **배경 제거**: Replicate API로 자동 투명 배경
✨ **참조 이미지**: 스타일 참조용 이미지 업로드

## 문제 해결

### "Function invocation failed" 오류
- Netlify Functions가 Python 3.11을 지원하는지 확인
- `requirements.txt` 파일이 올바른 위치에 있는지 확인

### 이미지 생성 실패
- Gemini API 키 확인
- API 할당량 확인
- 브라우저 콘솔에서 에러 메시지 확인

### 배경 제거 실패
- Replicate API 키 입력 확인
- 배경 제거 없이도 원본 이미지 다운로드 가능

## 비용 안내

- **Netlify**: 무료 플랜 제공 (월 100GB 대역폭, 300분 빌드 시간)
- **Gemini API**: 무료 할당량 후 유료
- **Replicate API**: 사용량 기반 과금

## 추가 정보

자세한 내용은 `README.md` 파일을 참고하세요.
