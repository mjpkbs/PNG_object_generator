# PixelSquid 3D 오브젝트 생성기 - Netlify 배포판

Gemini API로 3D 오브젝트를 생성하고 Replicate API로 배경을 제거하는 웹 애플리케이션입니다.

## 주요 기능

- **Gemini 2.0 Flash**: AI 기반 3D 오브젝트 이미지 생성
- **Replicate**: 자동 배경 제거
- **해상도 선택**: 1K, 1.5K, 2K, 2.5K 옵션 제공
- **카메라 각도 제어**: 3D 큐브 인터페이스로 각도 조절
- **참조 이미지 지원**: 스타일 참조용 이미지 업로드 가능

## 해상도 옵션

- **1K**: 1024×1024px (기본)
- **1.5K**: 1536×1536px
- **2K**: 2048×2048px
- **2.5K**: 2560×2560px

## Netlify 배포 방법

### 1. GitHub에 코드 업로드

```bash
# Git 저장소 초기화
git init
git add .
git commit -m "Initial commit"

# GitHub 저장소에 푸시
git remote add origin https://github.com/your-username/your-repo-name.git
git branch -M main
git push -u origin main
```

### 2. Netlify에 연결

1. [Netlify](https://www.netlify.com/)에 로그인
2. "Add new site" → "Import an existing project" 클릭
3. GitHub 연결 후 저장소 선택
4. 빌드 설정은 자동으로 감지됩니다:
   - Build command: (비워두기)
   - Publish directory: `public`
   - Functions directory: `netlify/functions`

5. "Deploy site" 클릭

### 3. 환경 변수 설정 (선택사항)

Netlify 대시보드에서 환경 변수를 설정할 수도 있지만, 이 앱은 클라이언트 측에서 API 키를 입력하도록 설계되어 있습니다.

## 로컬 테스트

Netlify CLI를 사용하여 로컬에서 테스트할 수 있습니다:

```bash
# Netlify CLI 설치
npm install -g netlify-cli

# 로컬 개발 서버 실행
netlify dev
```

로컬 서버는 `http://localhost:8888`에서 실행됩니다.

## API 키 발급

### Gemini API Key
1. [Google AI Studio](https://aistudio.google.com/app/apikey) 방문
2. "Create API Key" 클릭
3. 생성된 키를 복사

### Replicate API Key
1. [Replicate Account](https://replicate.com/account/api-tokens) 방문
2. API 토큰 생성
3. 생성된 토큰을 복사

## 사용 방법

1. 웹사이트 접속
2. Gemini API 키와 Replicate API 키 입력 (브라우저에 저장됨)
3. 3D 큐브를 드래그하여 원하는 카메라 각도 설정
4. 해상도 선택 (1K ~ 2.5K)
5. 오브젝트 이름 입력 (한글 또는 영어)
6. (선택사항) 참조 이미지 업로드
7. "이미지 생성" 버튼 클릭
8. 생성된 이미지 다운로드

## 프로젝트 구조

```
pixelsquid-netlify/
├── netlify.toml              # Netlify 설정 파일
├── public/
│   └── index.html            # 메인 HTML 파일
└── netlify/
    └── functions/
        ├── requirements.txt  # Python 의존성
        └── generate.py       # 이미지 생성 서버리스 함수
```

## 기술 스택

- **Frontend**: React (CDN), Three.js, Tailwind CSS
- **Backend**: Netlify Functions (Python)
- **AI APIs**: Google Gemini 2.0 Flash, Replicate

## 주의사항

- 고해상도 이미지는 생성 시간이 더 오래 걸릴 수 있습니다 (15-60초)
- API 키는 브라우저의 localStorage에 저장됩니다
- Gemini와 Replicate 사용량에 따라 비용이 발생할 수 있습니다

## 문제 해결

### 이미지 생성 실패
- API 키가 올바른지 확인
- API 할당량을 초과하지 않았는지 확인
- 네트워크 연결 상태 확인

### 배경 제거 실패
- Replicate API 키가 입력되어 있는지 확인
- 배경 제거 없이 원본 이미지도 다운로드 가능

## 라이선스

MIT License
