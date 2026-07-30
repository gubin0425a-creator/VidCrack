"""유틸리티 함수 모듈"""

import os
import re
import json
import yaml
import time
import hashlib
from pathlib import Path
from datetime import datetime


def load_config(config_path: str = None) -> dict:
    """config.yaml 로드"""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
    
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_config(config: dict, config_path: str = None):
    """config.yaml 저장"""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
    
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def ensure_dir(path: str) -> str:
    """디렉토리 보장"""
    os.makedirs(path, exist_ok=True)
    return path


def get_output_dir(topic: str, base_dir: str = None) -> str:
    """주제별 출력 디렉토리 생성"""
    if base_dir is None:
        base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    
    # 파일명 안전하게 변환
    safe_topic = re.sub(r'[^\w\s-]', '', topic).strip().replace(' ', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_name = f"{safe_topic}_{timestamp}"
    output_dir = os.path.join(base_dir, dir_name)
    return ensure_dir(output_dir)


def parse_script(text: str) -> list:
    """
    AI가 생성한 대본을 장면 단위로 파싱
    형식: [장면 N] 또는 장면 N: 으로 구분
    """
    scenes = []
    
    # [장면 1] 또는 장면 1: 또는 Scene 1: 패턴으로 분리
    parts = re.split(r'\[?\s*장면\s*(\d+)\s*\]?|Scene\s*(\d+)\s*:', text, flags=re.IGNORECASE)
    
    if len(parts) > 1:
        # 패턴 매칭된 경우
        for i, part in enumerate(parts):
            if isinstance(part, str) and part.strip() and not part.strip().isdigit():
                scene = parse_scene_block(part.strip())
                if scene:
                    scenes.append(scene)
    else:
        # 패턴이 없으면 줄바꿈으로 분리 시도
        lines = text.strip().split('\n')
        current_scene = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # 내레이션/이미지 프롬프트 구분
            if line.startswith('내레이션:') or line.startswith('나레이션:') or line.startswith('대사:'):
                current_scene['narration'] = line.split(':', 1)[1].strip()
            elif line.startswith('이미지:') or line.startswith('화면:') or line.startswith('프롬프트:'):
                current_scene['image_prompt'] = line.split(':', 1)[1].strip()
            elif 'narration' in current_scene or 'image_prompt' in current_scene:
                # 이미 장면 데이터가 있으면 추가
                if 'narration' not in current_scene:
                    current_scene['narration'] = line
                elif 'image_prompt' not in current_scene:
                    current_scene['image_prompt'] = line
                else:
                    scenes.append(current_scene)
                    current_scene = {}
                    current_scene['narration'] = line
            else:
                current_scene['narration'] = line
        
        if current_scene and ('narration' in current_scene or 'image_prompt' in current_scene):
            scenes.append(current_scene)
    
    # 장면이 없으면 전체 텍스트를 하나의 장면으로
    if not scenes:
        scenes = [{'narration': text.strip(), 'image_prompt': text.strip()}]
    
    return scenes


def parse_scene_block(text: str) -> dict:
    """장면 블록 파싱"""
    scene = {}
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 내레이션
        if line.startswith('내레이션:') or line.startswith('나레이션:') or line.startswith('대사:') or line.startswith('음성:'):
            scene['narration'] = line.split(':', 1)[1].strip()
        # 이미지 프롬프트
        elif line.startswith('이미지:') or line.startswith('화면:') or line.startswith('프롬프트:') or line.startswith('화면설명:'):
            scene['image_prompt'] = line.split(':', 1)[1].strip()
        # 자막
        elif line.startswith('자막:') or line.startswith('텍스트:'):
            scene['subtitle'] = line.split(':', 1)[1].strip()
        # 나머지는 내레이션으로
        elif 'narration' not in scene:
            scene['narration'] = line
        elif 'image_prompt' not in scene:
            scene['image_prompt'] = line
    
    return scene if scene else None


def save_script_json(scenes: list, output_dir: str) -> str:
    """대본을 JSON으로 저장"""
    filepath = os.path.join(output_dir, "script.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(scenes, f, ensure_ascii=False, indent=2)
    return filepath


def load_script_json(filepath: str) -> list:
    """JSON 대본 로드"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_filename(prompt: str, ext: str = ".png") -> str:
    """프롬프트 기반 파일명 생성"""
    hash_val = hashlib.md5(prompt.encode()).hexdigest()[:8]
    return f"img_{hash_val}{ext}"


def get_ffmpeg_path() -> str:
    """FFmpeg 경로 찾기"""
    # 1. 프로젝트 내 ffmpeg 디렉토리
    project_dir = os.path.dirname(os.path.dirname(__file__))
    local_ffmpeg = os.path.join(project_dir, "ffmpeg", "ffmpeg")
    if os.name == 'nt':
        local_ffmpeg += ".exe"
    if os.path.exists(local_ffmpeg):
        return local_ffmpeg
    
    # 2. 시스템 PATH
    import shutil
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    
    return "ffmpeg"  # 기본값


def get_ffprobe_path() -> str:
    """FFprobe 경로 찾기"""
    project_dir = os.path.dirname(os.path.dirname(__file__))
    local_ffprobe = os.path.join(project_dir, "ffmpeg", "ffprobe")
    if os.name == 'nt':
        local_ffprobe += ".exe"
    if os.path.exists(local_ffprobe):
        return local_ffprobe
    
    import shutil
    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        return ffprobe
    
    return "ffprobe"


def get_audio_duration(audio_path: str) -> float:
    """오디오 파일 길이(초) 구하기"""
    import subprocess
    ffprobe = get_ffprobe_path()
    
    cmd = [
        ffprobe,
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        audio_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    except Exception as e:
        print(f"[경고] 오디오 길이 측정 실패: {e}")
        return 5.0  # 기본값


def get_font_path(font_name: str = "default") -> str:
    """폰트 경로 찾기"""
    fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")
    
    # 내장 폰트 확인
    if os.path.exists(fonts_dir):
        for f in os.listdir(fonts_dir):
            if f.endswith(('.ttf', '.otf')):
                return os.path.join(fonts_dir, f)
    
    # 시스템 폰트 경로
    system_fonts = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "C:\\Windows\\Fonts\\malgun.ttf",
        "C:\\Windows\\Fonts\\malgunbd.ttf",
        "/System/Library/Fonts/PingFang.ttc",
    ]
    
    for font_path in system_fonts:
        if os.path.exists(font_path):
            return font_path
    
    # 폰트를 찾지 못하면 FFmpeg 기본 폰트 사용
    return None


def log_step(step: int, message: str):
    """단계별 로그 출력"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n{'='*60}")
    print(f"[{timestamp}] Step {step}/5 | {message}")
    print(f"{'='*60}\n")


def log_progress(current: int, total: int, message: str):
    """진행 상황 로그"""
    percent = (current / total) * 100
    bar_len = 30
    filled = int(bar_len * current / total)
    bar = '█' * filled + '░' * (bar_len - filled)
    print(f"\r  [{bar}] {percent:.0f}% ({current}/{total}) {message}", end='', flush=True)
    if current == total:
        print()
