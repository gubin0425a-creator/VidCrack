"""
Step 1: 대본 생성
주제를 입력받아 AI가 장면별 대본, 이미지 프롬프트, 자막을 생성
"""

import os
import json
from .utils import load_config, save_script_json, parse_script, log_step


SCRIPT_PROMPT = """당신은 유튜브 쇼츠 전문 대본 작가입니다.

주제: {topic}
장면 수: {scene_count}개

다음 형식으로 정확하게 작성해주세요. 각 장면마다:

[장면 N]
내레이션: (음성으로 읽힐 대사. 자연스럽고 흥미롭게. 각 장면 5-8초 분량)
이미지: (이미지 생성용 프롬프트. 영어로 작성. {style_prompt})
자막: (화면에 표시될 짧은 텍스트)

규칙:
1. 첫 장면은 시청자의 시선을 끄는 후킹으로 시작
2. 마지막 장면은 댓글 유도로 마무리
3. 내레이션은 구어체로 자연스럽게
4. 이미지 프롬프트는 항상 "{style_prompt}" 스타일로 시작
5. 자막은 내레이션의 핵심만 짧게
6. 전체 내레이션 길이가 40-60초가 되도록
"""


def generate_script_gemini(topic: str, config: dict) -> str:
    """Gemini API로 대본 생성 (google-genai SDK)"""
    from google import genai

    api_key = config.get('ai', {}).get('gemini_api_key', '')
    if not api_key:
        raise ValueError("Gemini API 키가 설정되지 않았습니다. config.yaml에서 gemini_api_key를 설정해주세요.")

    client = genai.Client(api_key=api_key)

    scene_count = config.get('output', {}).get('scene_count', 7)
    style_prompt = config.get('output', {}).get('style_prompt', 'cinematic, high quality, detailed, 4k')

    prompt = SCRIPT_PROMPT.format(
        topic=topic,
        scene_count=scene_count,
        style_prompt=style_prompt
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text


def generate_script_openai(topic: str, config: dict) -> str:
    """OpenAI API로 대본 생성"""
    import openai

    api_key = config.get('ai', {}).get('openai_api_key', '')
    if not api_key:
        raise ValueError("OpenAI API 키가 설정되지 않았습니다.")

    client = openai.OpenAI(api_key=api_key)

    scene_count = config.get('output', {}).get('scene_count', 7)
    style_prompt = config.get('output', {}).get('style_prompt', 'cinematic, high quality, detailed, 4k')

    prompt = SCRIPT_PROMPT.format(
        topic=topic,
        scene_count=scene_count,
        style_prompt=style_prompt
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )

    return response.choices[0].message.content


def generate_script(topic: str, config: dict = None) -> list:
    """
    주제로 대본 생성

    Args:
        topic: 영상 주제
        config: 설정 딕셔너리

    Returns:
        장면 리스트 [{narration, image_prompt, subtitle}, ...]
    """
    if config is None:
        config = load_config()

    log_step(1, f"대본 생성: '{topic}'")

    model = config.get('ai', {}).get('script_model', 'gemini')

    print(f"  AI 모델: {model}")
    print(f"  주제: {topic}")

    if model == 'gemini':
        raw_script = generate_script_gemini(topic, config)
    elif model == 'openai':
        raw_script = generate_script_openai(topic, config)
    else:
        raise ValueError(f"지원하지 않는 모델: {model}")

    # 대본 파싱
    scenes = parse_script(raw_script)

    # 이미지 프롬프트에 스타일 추가
    style_prompt = config.get('output', {}).get('style_prompt', 'cinematic, high quality, detailed, 4k')
    for scene in scenes:
        if 'image_prompt' in scene:
            # 이미 스타일이 포함되어 있지 않으면 추가
            if style_prompt.split(',')[0].lower() not in scene['image_prompt'].lower():
                scene['image_prompt'] = f"{style_prompt}, {scene['image_prompt']}"

    print(f"  ✅ 장면 {len(scenes)}개 생성 완료")
    for i, scene in enumerate(scenes, 1):
        narration = scene.get('narration', '')[:50]
        print(f"    장면 {i}: {narration}...")

    return scenes


def run_step1(topic: str, config: dict = None, output_dir: str = None) -> str:
    """
    Step 1 실행: 대본 생성 및 저장

    Returns:
        저장된 JSON 파일 경로
    """
    from .utils import get_output_dir

    if config is None:
        config = load_config()
    if output_dir is None:
        output_dir = get_output_dir(topic)

    scenes = generate_script(topic, config)

    # 원본 대본도 저장
    raw_path = os.path.join(output_dir, "raw_script.txt")
    with open(raw_path, "w", encoding="utf-8") as f:
        for i, scene in enumerate(scenes, 1):
            f.write(f"[장면 {i}]\n")
            f.write(f"내레이션: {scene.get('narration', '')}\n")
            f.write(f"이미지: {scene.get('image_prompt', '')}\n")
            f.write(f"자막: {scene.get('subtitle', scene.get('narration', '')[:20])}\n\n")

    # JSON으로 저장
    script_path = save_script_json(scenes, output_dir)

    print(f"\n  📁 대본 저장: {script_path}")
    return script_path
