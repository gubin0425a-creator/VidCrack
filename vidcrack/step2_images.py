"""
Step 2: 이미지 생성
대본의 이미지 프롬프트로 장면별 이미지 생성
Pollinations (무료) 또는 Gemini API 사용
"""

import os
import time
import requests
from pathlib import Path
from .utils import load_config, load_script_json, generate_filename, ensure_dir, log_step, log_progress


def generate_image_pollinations(prompt: str, output_path: str, width: int = 1024, height: int = 1024) -> str:
    """
    Pollinations API로 이미지 생성 (무료)
    https://pollinations.ai
    """
    seed = int(time.time() * 1000) % 100000
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width={width}&height={height}&nologo=true&seed={seed}"

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=120)
            if response.status_code == 200 and len(response.content) > 1000:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return output_path
            else:
                print(f"\n  ⚠️ 재시도 {attempt+1}/{max_retries}: 응답 코드 {response.status_code}")
                time.sleep(3)
        except requests.exceptions.RequestException as e:
            print(f"\n  ⚠️ 재시도 {attempt+1}/{max_retries}: {e}")
            time.sleep(3)

    raise Exception(f"Pollinations 이미지 생성 실패: {prompt[:50]}")


def generate_image_gemini(prompt: str, output_path: str, config: dict) -> str:
    """Gemini API로 이미지 생성 (Imagen 3)"""
    from google import genai
    from PIL import Image
    import io

    api_key = config.get('ai', {}).get('gemini_api_key', '')
    if not api_key:
        raise ValueError("Gemini API 키가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)

    # Imagen 3 모델 사용
    response = client.models.generate_images(
        model="imagen-3.0-generate-002",
        prompt=prompt,
        config=dict(
            number_of_images=1,
        )
    )

    if response.generated_images:
        img = response.generated_images[0]
        # 이미지 데이터를 PIL Image로 변환 후 저장
        image = Image.open(io.BytesIO(img.image.image_bytes))
        image.save(output_path)
        return output_path

    raise Exception(f"Gemini 이미지 생성 실패: {prompt[:50]}")


def generate_images(scenes: list, config: dict = None, output_dir: str = None) -> list:
    """
    모든 장면의 이미지 생성

    Args:
        scenes: 대본 장면 리스트
        config: 설정
        output_dir: 출력 디렉토리

    Returns:
        이미지 경로가 추가된 장면 리스트
    """
    if config is None:
        config = load_config()

    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")

    images_dir = ensure_dir(os.path.join(output_dir, "images"))

    model = config.get('ai', {}).get('image_model', 'pollinations')
    width = config.get('output', {}).get('width', 1080)
    height = config.get('output', {}).get('height', 1920)

    log_step(2, f"이미지 생성 ({model})")
    print(f"  장면 수: {len(scenes)}")
    print(f"  해상도: {width}x{height}")

    for i, scene in enumerate(scenes):
        prompt = scene.get('image_prompt', scene.get('narration', ''))
        output_path = os.path.join(images_dir, f"scene_{i+1:02d}.png")

        # 이미 존재하면 스킵
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print(f"  ⏭️ 장면 {i+1}: 이미 존재함")
            scene['image_path'] = output_path
            continue

        log_progress(i + 1, len(scenes), f"장면 {i+1}/{len(scenes)}")

        try:
            if model == 'pollinations':
                generate_image_pollinations(prompt, output_path, width=min(width, 1024), height=min(height, 1024))
            elif model == 'gemini':
                generate_image_gemini(prompt, output_path, config)
            else:
                raise ValueError(f"지원하지 않는 이미지 모델: {model}")

            scene['image_path'] = output_path
            print(f"\n  ✅ 장면 {i+1}: {output_path}")

        except Exception as e:
            print(f"\n  ❌ 장면 {i+1} 이미지 생성 실패: {e}")
            # 폴백: 플레이스홀더 이미지 생성
            scene['image_path'] = create_placeholder(output_path, prompt, width, height)

        # Rate limiting
        time.sleep(2)

    return scenes


def create_placeholder(output_path: str, prompt: str, width: int = 1080, height: int = 1920) -> str:
    """이미지 생성 실패 시 플레이스홀더 생성"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        img = Image.new('RGB', (width, height), color=(30, 30, 50))
        draw = ImageDraw.Draw(img)

        # 그라데이션 배경
        for y in range(height):
            r = int(30 + (y / height) * 30)
            g = int(30 + (y / height) * 20)
            b = int(50 + (y / height) * 40)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        # 텍스트 (프롬프트 일부)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()

        text = prompt[:60] + "..." if len(prompt) > 60 else prompt
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        draw.text(
            ((width - text_w) // 2, (height - text_h) // 2),
            text, fill=(200, 200, 200), font=font
        )

        img.save(output_path)
        return output_path
    except Exception as e:
        print(f"  플레이스홀더 생성 실패: {e}")
        return output_path


def run_step2(script_path: str, config: dict = None, output_dir: str = None) -> list:
    """
    Step 2 실행: 이미지 생성

    Args:
        script_path: 대본 JSON 경로
        config: 설정
        output_dir: 출력 디렉토리

    Returns:
        이미지 경로가 추가된 장면 리스트
    """
    if config is None:
        config = load_config()

    if output_dir is None:
        output_dir = os.path.dirname(script_path)

    scenes = load_script_json(script_path)
    scenes = generate_images(scenes, config, output_dir)

    # 업데이트된 대본 저장
    from .utils import save_script_json
    save_script_json(scenes, output_dir)

    print(f"\n  📁 이미지 저장: {os.path.join(output_dir, 'images')}")
    return scenes
