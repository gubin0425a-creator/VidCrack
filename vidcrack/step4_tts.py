"""
Step 4: 음성(TTS) + 자막 생성
Google TTS로 내레이션 음성 생성, 자막 타이밍 자동 계산
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from .utils import (
    load_config, load_script_json, get_ffmpeg_path, get_ffprobe_path,
    get_audio_duration, get_font_path, ensure_dir, log_step, log_progress
)


def generate_tts_google(text: str, output_path: str, language: str = "ko") -> str:
    """Google TTS로 음성 생성 (무료)"""
    from gtts import gTTS
    
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(output_path)
    return output_path


def generate_tts_elevenlabs(text: str, output_path: str, config: dict) -> str:
    """ElevenLabs TTS로 고품질 음성 생성 (유료)"""
    import requests
    
    api_key = config.get('tts', {}).get('elevenlabs_api_key', '')
    if not api_key:
        raise ValueError("ElevenLabs API 키가 설정되지 않았습니다.")
    
    # 한국어 지원 음성 ID
    voice_id = "yoZ06aMxZJJ28mfd3POQ"  # 기본 음성
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    response = requests.post(url, json=data, headers=headers, timeout=60)
    
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return output_path
    
    raise Exception(f"ElevenLabs TTS 실패: {response.status_code}")


def calculate_subtitle_timing(narration: str, audio_duration: float) -> list:
    """
    내레이션 텍스트를 자막 단위로 분할하고 타이밍 계산
    짧은 구문 단위로 나누어 읽기 편한 자막 생성
    """
    # 문장 분할 (마침표, 물음표, 느낌표, 쉼표 기준)
    import re
    sentences = re.split(r'(?<=[.!?。！？])\s+|(?<=,)\s+|(?<=다)\s+|(?<=요)\s+|(?<=죠)\s+|(?<=네)\s+', narration)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        # 분할이 안되면 15자 단위로 분할
        sentences = [narration[i:i+15] for i in range(0, len(narration), 15)]
    
    # 자막 길이에 따라 병합 (너무 짧은 것 합치기)
    merged = []
    current = ""
    for s in sentences:
        if len(current) + len(s) < 20:
            current += " " + s if current else s
        else:
            if current:
                merged.append(current)
            current = s
    if current:
        merged.append(current)
    
    sentences = merged if merged else sentences
    
    # 글자 수 비례 타이밍 분배
    total_chars = sum(len(s) for s in sentences)
    subtitles = []
    current_time = 0.0
    
    for sentence in sentences:
        char_ratio = len(sentence) / total_chars
        duration = audio_duration * char_ratio
        
        # 최소 1초 보장
        duration = max(duration, 1.0)
        
        subtitles.append({
            'text': sentence,
            'start': round(current_time, 3),
            'end': round(current_time + duration, 3),
            'duration': round(duration, 3)
        })
        
        current_time += duration
    
    return subtitles


def create_subtitle_srt(subtitles: list, output_path: str) -> str:
    """SRT 자막 파일 생성"""
    with open(output_path, "w", encoding="utf-8") as f:
        for i, sub in enumerate(subtitles, 1):
            start_h = int(sub['start'] // 3600)
            start_m = int((sub['start'] % 3600) // 60)
            start_s = int(sub['start'] % 60)
            start_ms = int((sub['start'] % 1) * 1000)
            
            end_h = int(sub['end'] // 3600)
            end_m = int((sub['end'] % 3600) // 60)
            end_s = int(sub['end'] % 60)
            end_ms = int((sub['end'] % 1) * 1000)
            
            f.write(f"{i}\n")
            f.write(f"{start_h:02d}:{start_m:02d}:{start_s:02d},{start_ms:03d} --> "
                    f"{end_h:02d}:{end_m:02d}:{end_s:02d},{end_ms:03d}\n")
            f.write(f"{sub['text']}\n\n")
    
    return output_path


def create_subtitle_ass(subtitles: list, output_path: str, width: int = 1080, height: int = 1920,
                         font_size: int = 28, font_color: str = "white", border_color: str = "black",
                         font_path: str = None) -> str:
    """ASS 자막 파일 생성 (스타일링 가능)"""
    
    # 색상 변환
    color_map = {
        'white': '&H00FFFFFF',
        'black': '&H00000000',
        'yellow': '&H0000FFFF',
        'red': '&H000000FF',
        'green': '&H0000FF00',
        'blue': '&H00FF0000',
    }
    
    fc = color_map.get(font_color.lower(), '&H00FFFFFF')
    bc = color_map.get(border_color.lower(), '&H00000000')
    
    font_name = "Arial"
    if font_path:
        font_name = os.path.splitext(os.path.basename(font_path))[0]
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("[Script Info]\n")
        f.write("Title: VidCrack Subtitles\n")
        f.write("ScriptType: v4.00+\n")
        f.write(f"PlayResX: {width}\n")
        f.write(f"PlayResY: {height}\n")
        f.write("WrapStyle: 0\n")
        f.write("ScaledBorderAndShadow: yes\n\n")
        
        f.write("[V4+ Styles]\n")
        f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
                "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
                "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
        
        # 메인 자막 스타일
        f.write(f"Style: Default,{font_name},{font_size},{fc},&H000000FF,{bc},&H80000000,"
                f"0,0,0,0,100,100,0,0,1,3,1,2,10,10,30,1\n")
        
        # 강조 스타일
        f.write(f"Style: Highlight,{font_name},{font_size + 4},&H0000FFFF,&H000000FF,{bc},&H80000000,"
                f"-1,0,0,0,100,100,0,0,1,3,1,2,10,10,30,1\n\n")
        
        f.write("[Events]\n")
        f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        
        for sub in subtitles:
            start = _format_ass_time(sub['start'])
            end = _format_ass_time(sub['end'])
            text = sub['text'].replace('\n', '\\N')
            f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n")
    
    return output_path


def _format_ass_time(seconds: float) -> str:
    """ASS 시간 포맷"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{ms:02d}"


def generate_tts_and_subtitles(scenes: list, config: dict = None, output_dir: str = None) -> list:
    """
    모든 장면의 TTS 음성과 자막 생성
    
    Args:
        scenes: 대본 장면 리스트
        config: 설정
        output_dir: 출력 디렉토리
    
    Returns:
        음성/자막 경로가 추가된 장면 리스트
    """
    if config is None:
        config = load_config()
    
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    
    audio_dir = ensure_dir(os.path.join(output_dir, "audio"))
    subtitle_dir = ensure_dir(os.path.join(output_dir, "subtitles"))
    
    tts_engine = config.get('tts', {}).get('engine', 'google')
    language = config.get('tts', {}).get('language', 'ko')
    subtitle_enabled = config.get('subtitle', {}).get('enabled', True)
    font_size = config.get('subtitle', {}).get('font_size', 28)
    font_color = config.get('subtitle', {}).get('font_color', 'white')
    border_color = config.get('subtitle', {}).get('border_color', 'black')
    width = config.get('output', {}).get('width', 1080)
    height = config.get('output', {}).get('height', 1920)
    
    log_step(4, f"음성 + 자막 생성 ({tts_engine})")
    print(f"  장면 수: {len(scenes)}")
    print(f"  TTS 엔진: {tts_engine}")
    print(f"  자막: {'활성' if subtitle_enabled else '비활성'}")
    
    all_subtitles = []
    
    for i, scene in enumerate(scenes):
        narration = scene.get('narration', '')
        if not narration:
            print(f"  ⚠️ 장면 {i+1}: 내레이션 없음")
            continue
        
        log_progress(i + 1, len(scenes), f"장면 {i+1}/{len(scenes)}")
        
        # TTS 음성 생성
        audio_path = os.path.join(audio_dir, f"scene_{i+1:02d}.mp3")
        
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000:
            print(f"\n  ⏭️ 장면 {i+1} 음성: 이미 존재함")
        else:
            try:
                if tts_engine == 'google':
                    generate_tts_google(narration, audio_path, language)
                elif tts_engine == 'elevenlabs':
                    generate_tts_elevenlabs(narration, audio_path, config)
                else:
                    generate_tts_google(narration, audio_path, language)
                
                print(f"\n  ✅ 장면 {i+1} 음성: {audio_path}")
            except Exception as e:
                print(f"\n  ❌ 장면 {i+1} TTS 실패: {e}")
                continue
        
        scene['audio_path'] = audio_path
        
        # 오디오 길이 측정
        try:
            audio_duration = get_audio_duration(audio_path)
        except:
            audio_duration = len(narration) * 0.15  # 추정치
        
        scene['audio_duration'] = audio_duration
        
        # 자막 타이밍 계산
        if subtitle_enabled:
            subtitle_text = scene.get('subtitle', narration)
            subtitles = calculate_subtitle_timing(subtitle_text, audio_duration)
            
            # 장면 시작 시간 오프셋 추가 (나중에 전체 편집 시 계산)
            for sub in subtitles:
                sub['scene'] = i
            all_subtitles.extend(subtitles)
            
            scene['subtitles'] = subtitles
            
            # 개별 장면 SRT/ASS 파일
            create_subtitle_srt(subtitles, os.path.join(subtitle_dir, f"scene_{i+1:02d}.srt"))
            font_path = get_font_path(config.get('subtitle', {}).get('font', 'default'))
            create_subtitle_ass(
                subtitles, os.path.join(subtitle_dir, f"scene_{i+1:02d}.ass"),
                width=width, height=height, font_size=font_size,
                font_color=font_color, border_color=border_color,
                font_path=font_path
            )
    
    # 전체 자막 파일 생성
    if all_subtitles:
        create_subtitle_srt(all_subtitles, os.path.join(output_dir, "full_subtitles.srt"))
        font_path = get_font_path(config.get('subtitle', {}).get('font', 'default'))
        create_subtitle_ass(
            all_subtitles, os.path.join(output_dir, "full_subtitles.ass"),
            width=width, height=height, font_size=font_size,
            font_color=font_color, border_color=border_color,
            font_path=font_path
        )
    
    return scenes


def run_step4(script_path: str, config: dict = None, output_dir: str = None) -> list:
    """
    Step 4 실행: 음성 + 자막 생성
    """
    if config is None:
        config = load_config()
    
    if output_dir is None:
        output_dir = os.path.dirname(script_path)
    
    scenes = load_script_json(script_path)
    scenes = generate_tts_and_subtitles(scenes, config, output_dir)
    
    from .utils import save_script_json
    save_script_json(scenes, output_dir)
    
    print(f"\n  📁 음성 저장: {os.path.join(output_dir, 'audio')}")
    print(f"  📁 자막 저장: {os.path.join(output_dir, 'subtitles')}")
    return scenes
