"""
Step 5: 최종 편집
영상 + 음성 + 자막을 FFmpeg로 합쳐서 최종 쇼츠 영상 완성
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from .utils import (
    load_config, load_script_json, get_ffmpeg_path, get_ffprobe_path,
    get_audio_duration, get_font_path, ensure_dir, log_step
)


def combine_video_audio_subtitle(video_path: str, audio_path: str, subtitle_path: str,
                                  output_path: str, config: dict = None) -> str:
    """영상 + 음성 + 자막 합성"""
    ffmpeg = get_ffmpeg_path()
    
    if config is None:
        config = load_config()
    
    width = config.get('output', {}).get('width', 1080)
    height = config.get('output', {}).get('height', 1920)
    
    # 자막 필터
    subtitle_filter = ""
    if subtitle_path and os.path.exists(subtitle_path):
        # ASS 자막이 있으면 사용
        if subtitle_path.endswith('.ass'):
            # FFmpeg에서 ASS 자막 경로에 특수문자/콜론 이스케이프
            escaped_sub = subtitle_path.replace('\\', '/').replace(':', '\\:').replace("'", "\\'")
            subtitle_filter = f"subtitles='{escaped_sub}'"
        else:
            escaped_sub = subtitle_path.replace('\\', '/').replace(':', '\\:').replace("'", "\\'")
            subtitle_filter = f"subtitles='{escaped_sub}'"
    
    # 오디오가 영상보다 길면 오디오 길이에 맞춤
    try:
        audio_duration = get_audio_duration(audio_path)
    except:
        audio_duration = None
    
    cmd = [
        ffmpeg, "-y",
        "-i", video_path,
        "-i", audio_path,
    ]
    
    # 비디오 필터
    vf_parts = [f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}"]
    if subtitle_filter:
        vf_parts.append(subtitle_filter)
    
    vf = ",".join(vf_parts)
    
    cmd.extend([
        "-vf", vf,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-preset", "medium",
        "-crf", "23",
    ])
    
    if audio_duration:
        cmd.extend(["-t", str(audio_duration + 0.5)])
    
    cmd.append(output_path)
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        # 자막 없이 재시도
        print(f"  ⚠️ 자막 합성 실패, 자막 없이 재시도: {result.stderr[:100]}")
        cmd_retry = [
            ffmpeg, "-y",
            "-i", video_path,
            "-i", audio_path,
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            "-preset", "medium",
            "-crf", "23",
            output_path
        ]
        result2 = subprocess.run(cmd_retry, capture_output=True, text=True, timeout=300)
        if result2.returncode != 0:
            raise Exception(f"FFmpeg 합성 실패: {result2.stderr[:200]}")
    
    return output_path


def create_final_video(scenes: list, config: dict = None, output_dir: str = None) -> str:
    """
    모든 장면을 합쳐 최종 쇼츠 영상 완성
    
    Args:
        scenes: 대본 장면 리스트
        config: 설정
        output_dir: 출력 디렉토리
    
    Returns:
        최종 영상 파일 경로
    """
    if config is None:
        config = load_config()
    
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    
    ffmpeg = get_ffmpeg_path()
    width = config.get('output', {}).get('width', 1080)
    height = config.get('output', {}).get('height', 1920)
    fps = config.get('output', {}).get('fps', 30)
    
    log_step(5, "최종 편집")
    
    # 1단계: 각 장면 영상+음성 합성
    print("  📌 각 장면 영상+음성 합성 중...")
    scene_videos = []
    temp_dir = ensure_dir(os.path.join(output_dir, "temp"))
    
    for i, scene in enumerate(scenes):
        video_path = scene.get('video_path', '')
        audio_path = scene.get('audio_path', '')
        
        if not video_path or not os.path.exists(video_path):
            print(f"  ⚠️ 장면 {i+1}: 영상 없음, 스킵")
            continue
        
        combined_path = os.path.join(temp_dir, f"combined_{i+1:02d}.mp4")
        
        if audio_path and os.path.exists(audio_path):
            # 자막 파일
            subtitle_path = os.path.join(output_dir, "subtitles", f"scene_{i+1:02d}.ass")
            if not os.path.exists(subtitle_path):
                subtitle_path = os.path.join(output_dir, "subtitles", f"scene_{i+1:02d}.srt")
            if not os.path.exists(subtitle_path):
                subtitle_path = None
            
            try:
                combine_video_audio_subtitle(video_path, audio_path, subtitle_path, combined_path, config)
                scene_videos.append(combined_path)
                print(f"  ✅ 장면 {i+1} 합성 완료")
            except Exception as e:
                print(f"  ❌ 장면 {i+1} 합성 실패: {e}")
                # 영상만 사용
                scene_videos.append(video_path)
        else:
            # 음성 없으면 영상만
            scene_videos.append(video_path)
    
    if not scene_videos:
        raise Exception("합성할 영상이 없습니다.")
    
    # 2단계: 장면 이어붙이기
    print("\n  📌 장면 이어붙이기 중...")
    
    # concat 파일 생성
    concat_file = os.path.join(temp_dir, "concat.txt")
    with open(concat_file, "w", encoding="utf-8") as f:
        for video in scene_videos:
            # 경로에 특수문자 방지
            abs_path = os.path.abspath(video).replace("\\", "/")
            f.write(f"file '{abs_path}'\n")
    
    final_no_bgm = os.path.join(output_dir, "final_no_bgm.mp4")
    
    cmd_concat = [
        ffmpeg, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "23",
        "-movflags", "+faststart",
        final_no_bgm
    ]
    
    result = subprocess.run(cmd_concat, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        # 대안: 직접 이어붙이기
        print(f"  ⚠️ concat 실패, 직접 결합 시도: {result.stderr[:100]}")
        _direct_concat(scene_videos, final_no_bgm, width, height, fps)
    
    # 3단계: 전체 자막 오버레이 (선택사항)
    final_with_sub = final_no_bgm
    full_sub_path = os.path.join(output_dir, "full_subtitles.ass")
    if os.path.exists(full_sub_path):
        final_with_sub = os.path.join(output_dir, "final_with_subtitles.mp4")
        try:
            escaped_sub = full_sub_path.replace('\\', '/').replace(':', '\\:').replace("'", "\\'")
            cmd_sub = [
                ffmpeg, "-y",
                "-i", final_no_bgm,
                "-vf", f"subtitles='{escaped_sub}'",
                "-c:v", "libx264",
                "-c:a", "copy",
                "-pix_fmt", "yuv420p",
                "-preset", "medium",
                "-crf", "23",
                final_with_sub
            ]
            subprocess.run(cmd_sub, capture_output=True, text=True, timeout=300)
        except Exception as e:
            print(f"  ⚠️ 전체 자막 오버레이 실패: {e}")
            final_with_sub = final_no_bgm
    
    # 4단계: 최종 파일명
    final_path = os.path.join(output_dir, "final_shorts.mp4")
    if os.path.exists(final_with_sub) and final_with_sub != final_path:
        os.replace(final_with_sub, final_path)
    elif os.path.exists(final_no_bgm) and not os.path.exists(final_path):
        os.replace(final_no_bgm, final_path)
    
    # 임시 파일 정리
    try:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    except:
        pass
    
    # 결과 확인
    if os.path.exists(final_path):
        file_size = os.path.getsize(final_path) / (1024 * 1024)
        print(f"\n  🎬 최종 영상: {final_path}")
        print(f"  📦 파일 크기: {file_size:.1f} MB")
        
        # 영상 정보 출력
        try:
            ffprobe = get_ffprobe_path()
            cmd_info = [ffprobe, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", final_path]
            result = subprocess.run(cmd_info, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                info = json.loads(result.stdout)
                duration = float(info.get('format', {}).get('duration', 0))
                print(f"  ⏱️ 재생 시간: {duration:.1f}초")
        except:
            pass
    else:
        raise Exception("최종 영상 생성 실패")
    
    return final_path


def _direct_concat(video_paths: list, output_path: str, width: int, height: int, fps: int) -> str:
    """직접 영상 결합 (concat 필터 사용)"""
    ffmpeg = get_ffmpeg_path()
    
    # 각 영상을 동일 포맷으로 변환 후 결합
    inputs = []
    filter_parts = []
    
    for i, path in enumerate(video_paths):
        inputs.extend(["-i", path])
        filter_parts.append(f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setsar=1,fps={fps}[v{i}]")
    
    # 오디오가 있는 첫 번째 스트림 사용
    filter_parts.append(f"[0:a]anull[a0]")
    
    # concat 필터
    video_streams = "".join(f"[v{i}]" for i in range(len(video_paths)))
    audio_streams = "".join(f"[{i}:a]" for i in range(len(video_paths)))
    
    filter_parts.append(f"{video_streams}concat=n={len(video_paths)}:v=1:a=0[outv]")
    
    # 오디오가 있으면 concat
    has_audio = True
    try:
        filter_parts.append(f"{audio_streams}concat=n={len(video_paths)}:v=0:a=1[outa]")
    except:
        has_audio = False
    
    filter_complex = ";".join(filter_parts)
    
    cmd = [
        ffmpeg, "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[outv]",
    ]
    
    if has_audio:
        cmd.extend(["-map", "[outa]"])
    
    cmd.extend([
        "-c:v", "libx264",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "23",
        "-movflags", "+faststart",
        output_path
    ])
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise Exception(f"직접 결합 실패: {result.stderr[:200]}")
    
    return output_path


def run_step5(script_path: str, config: dict = None, output_dir: str = None) -> str:
    """
    Step 5 실행: 최종 편집
    
    Returns:
        최종 영상 파일 경로
    """
    if config is None:
        config = load_config()
    
    if output_dir is None:
        output_dir = os.path.dirname(script_path)
    
    scenes = load_script_json(script_path)
    final_path = create_final_video(scenes, config, output_dir)
    
    return final_path
