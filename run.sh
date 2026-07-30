#!/bin/bash
# VidCrack - YouTube Shorts 자동화 시스템
# USB 포터블 실행 스크립트 (Linux/Mac)

set -e

echo ""
echo "============================================================"
echo "  VidCrack - YouTube Shorts 자동화 시스템"
echo "  USB 포터블 실행"
echo "============================================================"
echo ""

# USB 디렉토리로 이동
cd "$(dirname "$0")"

# Python 확인
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "[오류] Python이 설치되어 있지 않습니다."
        echo ""
        echo "Python 3.9+ 설치가 필요합니다:"
        echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
        echo "  Mac: brew install python3"
        echo ""
        exit 1
    fi
    PYTHON=python
else
    PYTHON=python3
fi

echo "[1/4] Python 확인 완료"
echo ""

# 가상환경 확인/생성
if [ ! -d "venv" ]; then
    echo "[2/4] 가상환경 생성 중..."
    $PYTHON -m venv venv
else
    echo "[2/4] 가상환경 확인 완료"
fi
echo ""

# 가상환경 활성화
source venv/bin/activate

# 패키지 설치
echo "[3/4] 패키지 설치 중..."
pip install -r requirements.txt -q
echo ""

# FFmpeg 확인
echo "[4/4] FFmpeg 확인 중..."
if ! command -v ffmpeg &> /dev/null; then
    echo ""
    echo "[경고] FFmpeg가 설치되어 있지 않습니다!"
    echo ""
    echo "FFmpeg 설치 방법:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  Mac: brew install ffmpeg"
    echo ""
fi

echo ""
echo "============================================================"
echo "  설치 완료!"
echo "============================================================"
echo ""
echo "사용법:"
echo "  source venv/bin/activate"
echo "  python -m vidcrack \"주제\""
echo ""
echo "예시:"
echo "  python -m vidcrack \"흑백요리사 깨두부 효능\""
echo "  python -m vidcrack \"다이소 과소비 팁\""
echo "  python -m vidcrack --multi-channel"
echo ""
echo "============================================================"
echo ""

# 인자가 있으면 바로 실행
if [ $# -gt 0 ]; then
    python -m vidcrack "$@"
else
    # 대화형 모드
    while true; do
        echo ""
        echo "선택하세요:"
        echo "  1. 영상 만들기 (주제 입력)"
        echo "  2. 다중 채널 모드"
        echo "  3. 설정 확인"
        echo "  4. API 키 설정"
        echo "  5. 종료"
        echo ""
        read -p "번호 입력: " choice
        
        case $choice in
            1)
                read -p "주제 입력: " topic
                python -m vidcrack "$topic"
                ;;
            2)
                python -m vidcrack --multi-channel
                ;;
            3)
                python -m vidcrack --show-config
                ;;
            4)
                read -p "Gemini API 키 입력: " apikey
                python -m vidcrack --set-key ai.gemini_api_key --set-value "$apikey"
                ;;
            5)
                exit 0
                ;;
        esac
    done
fi
