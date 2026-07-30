# 🎬 VidCrack - YouTube Shorts 자동화 시스템

> 주제 하나로 쇼츠 영상 전자동 생성: 대본 → 이미지 → 영상 → 음성+자막 → 편집

## 🚀 빠른 시작 (USB 실행)

### Windows
1. USB에 이 폴더 전체를 복사
2. `run.bat` 더블클릭
3. 주제 입력 → 영상 자동 생성!

### Mac/Linux
1. USB에 이 폴더 전체를 복사
2. 터미널에서 실행:
```bash
cd /path/to/VidCrack
chmod +x run.sh
./run.sh
```

### 사전 요구사항
- **Python 3.9+** (https://www.python.org/downloads/)
- **FFmpeg** (영상 편집용)
  - Windows: https://www.gyan.dev/ffmpeg/builds/ 에서 다운로드 → `ffmpeg/` 폴더에 배치
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
- **Gemini API 키** (https://aistudio.google.com/apikey - 무료 크레딧 40만원어치)

## 📋 사용법

### 기본 사용 (주제로 전체 자동화)
```bash
python -m vidcrack "흑백요리사 깨두부 효능"
python -m vidcrack "다이소에서 과소비하는 방법"
python -m vidcrack "게임 잘하는 사람이 공부도 잘하는 이유"
```

### 개별 단계 실행
```bash
# Step 1: 대본 생성만
python -m vidcrack "주제" --step 1

# Step 2: 이미지 생성만 (대본 JSON 필요)
python -m vidcrack --step 2 --script output/.../script.json

# Step 3: 영상 변환만
python -m vidcrack --step 3 --script output/.../script.json

# Step 4: 음성+자막만
python -m vidcrack --step 4 --script output/.../script.json

# Step 5: 최종 편집만
python -m vidcrack --step 5 --script output/.../script.json
```

### 다중 채널 모드
```bash
# 채널당 1개 영상
python -m vidcrack --multi-channel

# 채널당 3개 영상
python -m vidcrack --multi-channel --count 3
```

### 설정
```bash
# 설정 확인
python -m vidcrack --show-config

# API 키 설정
python -m vidcrack --set-key ai.gemini_api_key --set-value YOUR_API_KEY

# 출력 디렉토리 지정
python -m vidcrack "주제" --output /path/to/output
```

## 🔄 5단계 자동화 파이프라인

| Step | 내용 | 도구 | 비용 |
|------|------|------|------|
| 1 | 대본 생성 | Gemini API / ChatGPT | 무료~ |
| 2 | 이미지 생성 | Pollinations / Gemini API | 무료 |
| 3 | 영상 변환 | FFmpeg Ken Burns / Grok Imagine | 무료 |
| 4 | 음성+자막 | Google TTS + FFmpeg | 무료 |
| 5 | 최종 편집 | FFmpeg | 무료 |

### Step 1: 대본 생성
- 주제를 입력하면 AI가 장면별 대본, 이미지 프롬프트, 자막 생성
- 첫 장면은 후킹, 마지막은 댓글 유도
- 이미지 프롬프트에 스타일 통일 (영상 전체 그림체 일관성)

### Step 2: 이미지 생성
- 대본의 이미지 프롬프트로 장면별 이미지 자동 생성
- Pollinations (완전 무료) 또는 Gemini API (무료 크레딧 40만원)
- 스타일 프롬프트로 영상 전체 그림체 통일

### Step 3: 영상 변환
- 정지 이미지를 움직이는 영상으로 변환
- FFmpeg Ken Burns 효과 (줌 인/아웃, 팬) - 무료
- Grok Imagine 브라우저 자동화 (선택사항) - 무료
- "Maintain the visual style" 프롬프트로 스타일 유지

### Step 4: 음성 + 자막
- Google TTS로 내레이션 음성 생성 (무료)
- 음성 길이 밀리초 단위 측정 → 자막 타이밍 자동 계산
- SRT/ASS 자막 파일 생성
- 한국어 폰트 지원

### Step 5: 최종 편집
- FFmpeg로 영상+음성+자막 합성
- 1080x1920 세로 쇼츠 포맷
- 장면 이어붙이기 + 자막 오버레이
- faststart 플래그로 유튜브 업로드 최적화

## ⚙️ 설정 (config.yaml)

```yaml
# AI 모델
ai:
  script_model: "gemini"        # 대본 생성 모델
  image_model: "pollinations"   # 이미지 생성 모델 (무료)
  gemini_api_key: ""            # API 키

# 영상 변환
video_conversion:
  method: "ffmpeg_effect"       # ffmpeg_effect 또는 grok_imagine

# 음성
tts:
  engine: "google"              # google (무료) 또는 elevenlabs
  language: "ko"                # 한국어

# 자막
subtitle:
  enabled: true
  font_size: 28
  font_color: "white"
  border_color: "black"

# 영상
output:
  width: 1080
  height: 1920
  fps: 30
  scene_count: 7
  style_prompt: "cinematic, high quality, detailed, 4k"

# 다중 채널
channels:
  - name: "채널A"
    topic: "요리"
    enabled: true
  - name: "채널B"
    topic: "건강"
    enabled: true
```

## 💰 비용 비교

| 항목 | 수작업 | VidCrack 자동화 |
|------|--------|-----------------|
| 시간 | 4시간/영상 | 2-5분/영상 |
| 비용 | 1,000~1,500원 | 0~500원 |
| 자막 | 수동 싱크 | 자동 계산 |
| 반복 | 매일 수작업 | 명령어 한 줄 |

## 📁 프로젝트 구조

```
VidCrack/
├── run.bat                  # Windows 실행 스크립트
├── run.sh                   # Linux/Mac 실행 스크립트
├── config.yaml              # 설정 파일
├── requirements.txt         # Python 패키지
├── vidcrack/
│   ├── __init__.py
│   ├── __main__.py          # CLI 진입점
│   ├── main.py              # 메인
│   ├── runner.py             # 마스터 러너
│   ├── step1_script.py       # 대본 생성
│   ├── step2_images.py       # 이미지 생성
│   ├── step3_video.py        # 영상 변환
│   ├── step4_tts.py          # 음성+자막
│   ├── step5_edit.py         # 최종 편집
│   ├── utils.py              # 유틸리티
│   └── fonts/                # 폰트
├── output/                  # 출력 폴더
└── ffmpeg/                  # FFmpeg 바이너리 (선택)
```

## 🛠️ 문제 해결

### FFmpeg 오류
- FFmpeg가 설치되어 있는지 확인: `ffmpeg -version`
- Windows: `ffmpeg/` 폴더에 `ffmpeg.exe` 배치
- PATH에 FFmpeg 경로 추가

### API 키 오류
- Gemini API 키 설정: `python -m vidcrack --set-key ai.gemini_api_key --set-value YOUR_KEY`
- API 키 발급: https://aistudio.google.com/apikey

### 이미지 생성 실패
- Pollinations는 무료지만 간혹 실패 → 자동 재시도 (3회)
- Gemini API로 전환: `python -m vidcrack --set-key ai.image_model --set-value gemini`

### 한글 폰트 깨짐
- `vidcrack/fonts/` 폴더에 `.ttf` 또는 `.otf` 폰트 파일 배치
- 추천: 나눔고딕, Noto Sans CJK

## 📄 라이선스

Public Domain (Unlicense) - 자유롭게 사용, 수정, 배포 가능

---

**VidCrack** - 수작업 4시간 → 명령어 한 줄 ⚡
