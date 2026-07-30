"""
VidCrack - YouTube Shorts 자동화 시스템
메인 진입점
"""

import os
import sys
import argparse

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vidcrack.runner import run_full_pipeline, run_single_step, run_multi_channel
from vidcrack.utils import load_config, save_config


def main():
    parser = argparse.ArgumentParser(
        description="🎬 VidCrack - YouTube Shorts 자동화 시스템",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 주제로 전체 자동화 실행
  python -m vidcrack "흑백요리사 깨두부 효능"
  
  # 개별 단계 실행
  python -m vidcrack "주제" --step 1
  python -m vidcrack --step 2 --script output/.../script.json
  
  # 다중 채널 모드
  python -m vidcrack --multi-channel --count 3
  
  # 설정 확인
  python -m vidcrack --show-config
        """
    )
    
    parser.add_argument(
        "topic",
        nargs="?",
        help="영상 주제 (예: '흑백요리사 깨두부 효능')"
    )
    
    parser.add_argument(
        "--step", "-s",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="특정 단계만 실행 (1-5)"
    )
    
    parser.add_argument(
        "--script",
        help="대본 JSON 파일 경로 (Step 2-5에서 사용)"
    )
    
    parser.add_argument(
        "--config", "-c",
        help="설정 파일 경로 (기본: config.yaml)"
    )
    
    parser.add_argument(
        "--multi-channel",
        action="store_true",
        help="다중 채널 모드로 실행"
    )
    
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=1,
        help="채널당 제작 영상 수 (기본: 1)"
    )
    
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="현재 설정 확인"
    )
    
    parser.add_argument(
        "--set-key",
        help="설정 키 변경 (예: ai.gemini_api_key)"
    )
    
    parser.add_argument(
        "--set-value",
        default=None,
        help="설정 값"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="출력 디렉토리"
    )
    
    args = parser.parse_args()
    
    # 설정 로드
    config_path = args.config
    config = load_config(config_path)
    
    # 설정 확인
    if args.show_config:
        import yaml
        print(yaml.dump(config, allow_unicode=True, default_flow_style=False, sort_keys=False))
        return
    
    # 설정 변경
    if args.set_key and args.set_value is not None:
        keys = args.set_key.split('.')
        obj = config
        for key in keys[:-1]:
            if key not in obj:
                obj[key] = {}
            obj = obj[key]
        obj[keys[-1]] = args.set_value
        save_config(config, config_path)
        print(f"✅ 설정 변경: {args.set_key} = {args.set_value}")
        return
    
    # API 키 확인
    api_key = config.get('ai', {}).get('gemini_api_key', '')
    if not api_key and not args.multi_channel:
        print("⚠️ Gemini API 키가 설정되지 않았습니다.")
        print("   다음 명령으로 설정해주세요:")
        print("   python -m vidcrack --set-key ai.gemini_api_key --set-value YOUR_API_KEY")
        print()
        print("   API 키 발급: https://aistudio.google.com/apikey")
        print("   (무료 크레딧 약 40만원어치 제공)")
        print()
        
        # 계속 진행할지 물어봄
        try:
            response = input("그래도 계속하시겠습니까? (y/n): ")
            if response.lower() != 'y':
                return
        except:
            return
    
    # 다중 채널 모드
    if args.multi_channel:
        run_multi_channel(config, videos_per_channel=args.count)
        return
    
    # 주제 확인
    if not args.topic and not args.script:
        parser.print_help()
        print("\n❌ 주제를 입력해주세요!")
        print("   예: python -m vidcrack \"흑백요리사 깨두부 효능\"")
        return
    
    # 실행
    if args.step:
        # 개별 단계 실행
        result = run_single_step(
            step=args.step,
            topic=args.topic,
            script_path=args.script,
            config=config,
            output_dir=args.output
        )
        if isinstance(result, str):
            print(f"\n✅ 결과: {result}")
        elif isinstance(result, list):
            print(f"\n✅ {len(result)}개 장면 처리 완료")
    else:
        # 전체 파이프라인 실행
        run_full_pipeline(
            topic=args.topic,
            config=config,
            output_dir=args.output
        )


if __name__ == "__main__":
    main()
