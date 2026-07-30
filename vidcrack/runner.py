"""
VidCrack 마스터 러너
5단계를 순서대로 자동 실행: 대본 → 이미지 → 영상 → 음성+자막 → 편집
다중 채널 운영 지원
"""

import os
import sys
import time
import json
from datetime import datetime
from .utils import load_config, save_config, get_output_dir, log_step, ensure_dir
from .step1_script import run_step1, generate_script
from .step2_images import run_step2, generate_images
from .step3_video import run_step3, convert_images_to_videos
from .step4_tts import run_step4, generate_tts_and_subtitles
from .step5_edit import run_step5, create_final_video


def run_full_pipeline(topic: str, config: dict = None, output_dir: str = None) -> str:
    """
    전체 5단계 파이프라인 실행
    
    Args:
        topic: 영상 주제
        config: 설정
        output_dir: 출력 디렉토리
    
    Returns:
        최종 영상 파일 경로
    """
    if config is None:
        config = load_config()
    
    if output_dir is None:
        output_dir = get_output_dir(topic)
    
    start_time = time.time()
    
    print("\n" + "=" * 60)
    print("🎬 VidCrack - YouTube Shorts 자동화")
    print("=" * 60)
    print(f"  주제: {topic}")
    print(f"  출력: {output_dir}")
    print(f"  시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60 + "\n")
    
    try:
        # Step 1: 대본 생성
        script_path = run_step1(topic, config, output_dir)
        
        # Step 2: 이미지 생성
        scenes = run_step2(script_path, config, output_dir)
        
        # Step 3: 영상 변환
        scenes = run_step3(script_path, config, output_dir)
        
        # Step 4: 음성 + 자막
        scenes = run_step4(script_path, config, output_dir)
        
        # Step 5: 최종 편집
        final_path = run_step5(script_path, config, output_dir)
        
        elapsed = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("🎉 완성!")
        print("=" * 60)
        print(f"  📹 최종 영상: {final_path}")
        print(f"  ⏱️ 소요 시간: {elapsed:.1f}초 ({elapsed/60:.1f}분)")
        print(f"  📁 출력 폴더: {output_dir}")
        print("=" * 60 + "\n")
        
        return final_path
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ 오류 발생 ({elapsed:.1f}초 후): {e}")
        import traceback
        traceback.print_exc()
        raise


def run_single_step(step: int, topic: str = None, script_path: str = None,
                     config: dict = None, output_dir: str = None):
    """개별 단계만 실행"""
    if config is None:
        config = load_config()
    
    if step == 1:
        if not topic:
            raise ValueError("Step 1에는 주제가 필요합니다.")
        return run_step1(topic, config, output_dir)
    elif step == 2:
        return run_step2(script_path, config, output_dir)
    elif step == 3:
        return run_step3(script_path, config, output_dir)
    elif step == 4:
        return run_step4(script_path, config, output_dir)
    elif step == 5:
        return run_step5(script_path, config, output_dir)
    else:
        raise ValueError(f"잘못된 단계: {step} (1-5)")


def run_multi_channel(config: dict = None, videos_per_channel: int = 1):
    """
    다중 채널 운영
    설정된 채널별로 돌아가며 영상 제작
    """
    if config is None:
        config = load_config()
    
    channels = config.get('channels', [])
    enabled_channels = [ch for ch in channels if ch.get('enabled', True)]
    
    if not enabled_channels:
        print("⚠️ 활성화된 채널이 없습니다. config.yaml을 확인해주세요.")
        return
    
    print(f"\n📺 다중 채널 모드")
    print(f"  활성 채널: {len(enabled_channels)}개")
    print(f"  채널당 영상: {videos_per_channel}개")
    print(f"  총 제작 수: {len(enabled_channels) * videos_per_channel}개\n")
    
    results = []
    
    for round_num in range(videos_per_channel):
        for channel in enabled_channels:
            channel_name = channel.get('name', 'Unknown')
            topic = channel.get('topic', '')
            
            if not topic:
                print(f"  ⚠️ {channel_name}: 주제가 없습니다.")
                continue
            
            # 채널별 주제 조합 (라운드마다 다른 주제)
            full_topic = f"{topic} {channel_name} 편 {round_num + 1}"
            
            print(f"\n{'─' * 40}")
            print(f"📺 {channel_name} | {full_topic}")
            print(f"{'─' * 40}")
            
            try:
                final_path = run_full_pipeline(full_topic, config)
                results.append({
                    'channel': channel_name,
                    'topic': full_topic,
                    'video': final_path,
                    'status': 'success'
                })
            except Exception as e:
                results.append({
                    'channel': channel_name,
                    'topic': full_topic,
                    'error': str(e),
                    'status': 'failed'
                })
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 다중 채널 결과 요약")
    print("=" * 60)
    for r in results:
        status = "✅" if r['status'] == 'success' else "❌"
        print(f"  {status} {r['channel']}: {r['topic']}")
        if r['status'] == 'success':
            print(f"     📹 {r['video']}")
        else:
            print(f"     ❌ {r['error']}")
    print("=" * 60)
    
    return results
