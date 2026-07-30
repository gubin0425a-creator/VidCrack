"""
Step 3: 영상 변환
정지 이미지를 움직이는 영상으로 변환
- FFmpeg Ken Burns 효과 (로컬, 무료)
- Grok Imagine 브라우저 자동화 (선택사항)
"""

import os
import json
import random
import subprocess
from pathlib import Path
from .utils import (
    load_config, load_script_json, get_ffmpeg_path, get_audio_duration,
    ensure_dir, log_step, log_progress
)


def create_video_ffmpeg_kenburns(image_path: str, output_path: str, duration: float = 5.0,
                                  width: int = 1080, height: int = 1920, fps: int = 30) -> str:
    """
    FFmpeg Ken Burns 효과로 이미지를 영상으로 변환
    랜덤 줌/팬 효과 적용
    """
    ffmpeg = get_ffmpeg_path()
    
    # 랜덤 효과 선택
    effects = [
        _zoom_in, _zoom_out, _pan_left, _pan_right, _zoom_center
    ]
    effect = random.choice(effects)
    
    filter_complex = effect(duration, width, height)
    
    cmd = [
        ffmpeg,
        "-y",
        "-loop", "1",
        "-i", image_path,
        "-t", str(duration),
        "-vf", filter_complex,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-r", str(fps),
        "-preset", "medium",
        "-crf", "23",
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        # 폴백: 단순 줌 인
        filter_simple = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},zoompan=z='min(zoom+0.0015,1.5)':d={int(duration*fps)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height}:fps={fps}"
        cmd_fallback = [
            ffmpeg, "-y", "-loop", "1", "-i", image_path,
            "-t", str(duration), "-vf", filter_simple,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-r", str(fps), "-preset", "medium", "-crf", "23",
            output_path
        ]
        result2 = subprocess.run(cmd_fallback, capture_output=True, text=True, timeout=120)
        if result2.returncode != 0:
            raise Exception(f"FFmpeg 영상 변환 실패: {result2.stderr[:200]}")
    
    return output_path


def _zoom_in(duration: float, width: int, height: int) -> str:
    """줌 인 효과"""
    fps = 30
    total_frames = int(duration * fps)
    return (
        f"scale={width*2}:{height*2}:force_original_aspect_ratio=increase,"
        f"crop={width*2}:{height*2},"
        f"zoompan=z='min(zoom+0.0015,1.5)':d={total_frames}:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"s={width}x{height}:fps={fps}"
    )


def _zoom_out(duration: float, width: int, height: int) -> str:
    """줌 아웃 효과"""
    fps = 30
    total_frames = int(duration * fps)
    return (
        f"scale={width*2}:{height*2}:force_original_aspect_ratio=increase,"
        f"crop={width*2}:{height*2},"
        f"zoompan=z='if(eq(on,1),1.5,max(zoom-0.001,1))':d={total_frames}:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"s={width}x{height}:fps={fps}"
    )


def _pan_left(duration: float, width: int, height: int) -> str:
    """왼쪽 팬 효과"""
    fps = 30
    total_frames = int(duration * fps)
    return (
        f"scale={width*2}:{height*2}:force_original_aspect_ratio=increase,"
        f"crop={width*2}:{height*2},"
        f"zoompan=z='1.2':d={total_frames}:"
        f"x='iw/2-(iw/zoom/2)-on*2':y='ih/2-(ih/zoom/2)':"
        f"s={width}x{height}:fps={fps}"
    )


def _pan_right(duration: float, width: int, height: int) -> str:
    """오른쪽 팬 효과"""
    fps = 30
    total_frames = int(duration * fps)
    return (
        f"scale={width*2}:{height*2}:force_original_aspect_ratio=increase,"
        f"crop={width*2}:{height*2},"
        f"zoompan=z='1.2':d={total_frames}:"
        f"x='iw/2-(iw/zoom/2)+on*2':y='ih/2-(ih/zoom/2)':"
        f"s={width}x{height}:fps={fps}"
    )


def _zoom_center(duration: float, width: int, height: int) -> str:
    """중앙 줌 효과"""
    fps = 30
    total_frames = int(duration * fps)
    return (
        f"scale={width*2}:{height*2}:force_original_aspect_ratio=increase,"
        f"crop={width*2}:{height*2},"
        f"zoompan=z='1.0+0.0008*on':d={total_frames}:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"s={width}x{height}:fps={fps}"
    )


def create_video_grok(image_path: str, output_path: str, config: dict) -> str:
    """
    Grok Imagine 브라우저 자동화로 이미지를 영상으로 변환
    (Playwright 필요)
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  ⚠️ Playwright가 설치되지 않음. FFmpeg 효과로 대체합니다.")
        return create_video_ffmpeg_kenburns(image_path, output_path)
    
    headless = config.get('video_conversion', {}).get('grok_headless', True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # Grok Imagine 접속
            page.goto("https://grok.com/imagine", timeout=60000)
            page.wait_for_load_state("networkidle", timeout=30000)
            
            # 이미지 업로드
            file_input = page.query_selector('input[type="file"]')
            if file_input:
                file_input.set_input_files(image_path)
            else:
                # 드래그 앤 드롭 영역 찾기
                upload_area = page.query_selector('[data-testid="upload"]') or page.query_selector('.upload-area')
                if upload_area:
                    upload_area.set_input_files(image_path)
            
            # 프롬프트 입력
            prompt_input = page.query_selector('textarea') or page.query_selector('input[type="text"]')
            if prompt_input:
                prompt_input.fill("Maintain the visual style, add subtle motion, cinematic movement")
            
            # 생성 버튼 클릭
            generate_btn = page.query_selector('button:has-text("Generate")') or page.query_selector('button[type="submit"]')
            if generate_btn:
                generate_btn.click()
            
            # 영상 생성 대기
            page.wait_for_timeout(60000)
            
            # 결과 영상 다운로드
            video_element = page.query_selector('video source') or page.query_selector('video')
            if video_element:
                video_src = video_element.get_attribute('src')
                if video_src:
                    import requests
                    response = requests.get(video_src)
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    browser.close()
                    return output_path
            
            browser.close()
            
        except Exception as e:
            browser.close()
            print(f"  ⚠️ Grok Imagine 실패: {e}")
    
    # 폴백
    return create_video_ffmpeg_kenburns(image_path, output_path)


def convert_images_to_videos(scenes: list, config: dict = None, output_dir: str = None) -> list:
    """
    모든 장면의 이미지를 영상으로 변환
    
    Args:
        scenes: 대본 장면 리스트
        config: 설정
        output_dir: 출력 디렉토리
    
    Returns:
        영상 경로가 추가된 장면 리스트
    """
    if config is None:
        config = load_config()
    
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    
    videos_dir = ensure_dir(os.path.join(output_dir, "videos"))
    
    method = config.get('video_conversion', {}).get('method', 'ffmpeg_effect')
    clip_duration = config.get('output', {}).get('clip_duration', 5)
    width = config.get('output', {}).get('width', 1080)
    height = config.get('output', {}).get('height', 1920)
    fps = config.get('output', {}).get('fps', 30)
    
    log_step(3, f"영상 변환 ({method})")
    print(f"  장면 수: {len(scenes)}")
    print(f"  클립 길이: {clip_duration}초")
    
    for i, scene in enumerate(scenes):
        image_path = scene.get('image_path', '')
        output_path = os.path.join(videos_dir, f"scene_{i+1:02d}.mp4")
        
        if not image_path or not os.path.exists(image_path):
            print(f"  ⚠️ 장면 {i+1}: 이미지 없음, 스킵")
            continue
        
        # 이미 존재하면 스킵
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print(f"  ⏭️ 장면 {i+1}: 이미 존재함")
            scene['video_path'] = output_path
            continue
        
        log_progress(i + 1, len(scenes), f"장면 {i+1}/{len(scenes)}")
        
        try:
            if method == 'grok_imagine':
                create_video_grok(image_path, output_path, config)
            else:
                create_video_ffmpeg_kenburns(
                    image_path, output_path,
                    duration=clip_duration,
                    width=width, height=height, fps=fps
                )
            
            scene['video_path'] = output_path
            print(f"\n  ✅ 장면 {i+1}: {output_path}")
            
        except Exception as e:
            print(f"\n  ❌ 장면 {i+1} 영상 변환 실패: {e}")
            # 단순 변환 시도
            try:
                _simple_image_to_video(image_path, output_path, duration=clip_duration, width=width, height=height)
                scene['video_path'] = output_path
            except Exception as e2:
                print(f"  ❌ 단순 변환도 실패: {e2}")
    
    return scenes


def _simple_image_to_video(image_path: str, output_path: str, duration: float = 5.0,
                            width: int = 1080, height: int = 1920) -> str:
    """단순 이미지→영상 변환 (효과 없음)"""
    ffmpeg = get_ffmpeg_path()
    fps = 30
    
    cmd = [
        ffmpeg, "-y",
        "-loop", "1", "-i", image_path,
        "-t", str(duration),
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-r", str(fps), "-preset", "fast", "-crf", "23",
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise Exception(f"FFmpeg 실패: {result.stderr[:200]}")
    
    return output_path


def run_step3(script_path: str, config: dict = None, output_dir: str = None) -> list:
    """
    Step 3 실행: 영상 변환
    """
    if config is None:
        config = load_config()
    
    if output_dir is None:
        output_dir = os.path.dirname(script_path)
    
    scenes = load_script_json(script_path)
    scenes = convert_images_to_videos(scenes, config, output_dir)
    
    from .utils import save_script_json
    save_script_json(scenes, output_dir)
    
    print(f"\n  📁 영상 저장: {os.path.join(output_dir, 'videos')}")
    return scenes
