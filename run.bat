@echo off
chcp 65001 >nul 2>&1
title VidCrack - YouTube Shorts 자동화

echo.
echo ============================================================
echo   VidCrack - YouTube Shorts 자동화 시스템
echo   USB 포터블 실행
echo ============================================================
echo.

:: USB 드라이브 경로 감지
set "USB_DIR=%~dp0"
cd /d "%USB_DIR%"

:: Python 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo.
    echo Python 3.9+ 설치가 필요합니다:
    echo   https://www.python.org/downloads/
    echo.
    echo 설치 시 "Add Python to PATH" 체크하세요!
    echo.
    pause
    exit /b 1
)

echo [1/4] Python 확인 완료
echo.

:: 가상환경 확인/생성
if not exist "venv" (
    echo [2/4] 가상환경 생성 중...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [오류] 가상환경 생성 실패
        pause
        exit /b 1
    )
) else (
    echo [2/4] 가상환경 확인 완료
)
echo.

:: 가상환경 활성화
call venv\Scripts\activate.bat

:: 패키지 설치
echo [3/4] 패키지 설치 중...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo [오류] 패키지 설치 실패
    echo 인터넷 연결을 확인해주세요.
    pause
    exit /b 1
)
echo.

:: FFmpeg 확인
echo [4/4] FFmpeg 확인 중...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [경고] FFmpeg가 설치되어 있지 않습니다!
    echo.
    echo FFmpeg 설치 방법:
    echo   1. https://www.gyan.dev/ffmpeg/builds/ 에서 다운로드
    echo   2. ffmpeg-release-essentials.zip 다운로드
    echo   3. 압축 해제 후 ffmpeg\bin 폴더를 이 USB의 ffmpeg 폴더에 복사
    echo.
    echo   또는 이 USB에 ffmpeg 폴더를 만들고 ffmpeg.exe를 넣어주세요.
    echo.
    pause
)

echo.
echo ============================================================
echo   설치 완료! 
echo ============================================================
echo.
echo 사용법:
echo   venv\Scripts\activate.bat
echo   python -m vidcrack "주제"
echo.
echo 예시:
echo   python -m vidcrack "흑백요리사 깨두부 효능"
echo   python -m vidcrack "다이소 과소비 팁"
echo   python -m vidcrack --multi-channel
echo.
echo 설정:
echo   python -m vidcrack --show-config
echo   python -m vidcrack --set-key ai.gemini_api_key --set-value YOUR_KEY
echo.
echo ============================================================
echo.

:: 메인 메뉴
:menu
echo.
echo 선택하세요:
echo   1. 영상 만들기 (주제 입력)
echo   2. 다중 채널 모드
echo   3. 설정 확인
echo   4. API 키 설정
echo   5. 종료
echo.
set /p choice="번호 입력: "

if "%choice%"=="1" goto make_video
if "%choice%"=="2" goto multi_channel
if "%choice%"=="3" goto show_config
if "%choice%"=="4" goto set_api
if "%choice%"=="5" exit /b 0
goto menu

:make_video
set /p topic="주제 입력: "
python -m vidcrack "%topic%"
pause
goto menu

:multi_channel
python -m vidcrack --multi-channel
pause
goto menu

:show_config
python -m vidcrack --show-config
pause
goto menu

:set_api
set /p apikey="Gemini API 키 입력: "
python -m vidcrack --set-key ai.gemini_api_key --set-value "%apikey%"
pause
goto menu
