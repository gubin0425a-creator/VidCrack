# -*- coding: utf-8 -*-
import os
import uuid
import json
import time
from datetime import datetime
from flask import Flask, request, jsonify, render_template, make_response, redirect

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
QUEUE_FILE = os.path.join(BASE_DIR, 'queue.json')
DEVICES_FILE = os.path.join(BASE_DIR, 'devices.json')

def load_json(path, default=None):
    if default is None:
        default = []
    if not os.path.exists(path):
        return default
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return default

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_hooks_data():
    return load_json(os.path.join(DATA_DIR, 'hooks_data.json'), {})

def get_prompts_data():
    return load_json(os.path.join(DATA_DIR, 'prompts_data.json'), {})

def get_monetization_data():
    return load_json(os.path.join(DATA_DIR, 'monetization_data.json'), {})

@app.before_request
def check_auth():
    if request.path in ['/login', '/api/auth']:
        return
    if request.path.startswith('/static'):
        return
    device_id = request.cookies.get('device_id')
    devices = load_json(DEVICES_FILE, [])
    device = next((d for d in devices if d['id'] == device_id), None)
    if not device:
        return redirect('/login')
    device['last_used'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_json(DEVICES_FILE, devices)

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/api/auth', methods=['POST'])
def auth_device():
    pwd = request.form.get('password', '').strip()
    if pwd != '635835':
        return jsonify({'success': False, 'msg': '마스터 암호가 일치하지 않습니다. (635835)'})
    devices = load_json(DEVICES_FILE, [])
    if len(devices) >= 9:
        return jsonify({'success': False, 'msg': '최대 등록 디바이스 한도(9대)를 초과했습니다. 관리자에게 문의하세요.'})
    new_id = str(uuid.uuid4())
    user_agent = request.headers.get('User-Agent', 'Unknown Device')
    device_name = request.form.get('device_name', f'Member Device #{len(devices)+1}')
    devices.append({
        'id': new_id,
        'device_name': device_name,
        'product_name': user_agent[:45],
        'registered_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'last_used': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    save_json(DEVICES_FILE, devices)
    resp = make_response(jsonify({'success': True}))
    resp.set_cookie('device_id', new_id, max_age=60*60*24*365)
    return resp

@app.route('/api/logout', methods=['POST'])
def logout():
    device_id = request.cookies.get('device_id')
    devices = load_json(DEVICES_FILE, [])
    devices = [d for d in devices if d['id'] != device_id]
    save_json(DEVICES_FILE, devices)
    resp = make_response(jsonify({'success': True}))
    resp.delete_cookie('device_id')
    return resp

@app.route('/api/devices')
def list_devices():
    devices = load_json(DEVICES_FILE, [])
    current_id = request.cookies.get('device_id')
    return jsonify({
        'devices': devices,
        'current_id': current_id,
        'count': len(devices),
        'max_limit': 9
    })

@app.route('/')
def index():
    devices = load_json(DEVICES_FILE, [])
    current_id = request.cookies.get('device_id')
    current_device = next((d for d in devices if d['id'] == current_id), None)
    return render_template('index.html', device=current_device, device_count=len(devices))

@app.route('/api/hooks')
def api_hooks():
    return jsonify(get_hooks_data())

@app.route('/api/prompts')
def api_prompts():
    return jsonify(get_prompts_data())

@app.route('/api/monetization')
def api_monetization():
    return jsonify(get_monetization_data())

@app.route('/api/queue')
def api_queue():
    queue = load_json(QUEUE_FILE, [])
    return jsonify({'queue': queue, 'total': len(queue)})

@app.route('/api/queue/delete', methods=['POST'])
def api_queue_delete():
    item_id = request.json.get('id') if request.json else request.form.get('id')
    queue = load_json(QUEUE_FILE, [])
    queue = [q for q in queue if q.get('id') != item_id]
    save_json(QUEUE_FILE, queue)
    return jsonify({'success': True, 'queue': queue})

@app.route('/api/queue/clear', methods=['POST'])
def api_queue_clear():
    save_json(QUEUE_FILE, [])
    return jsonify({'success': True})

@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.form if request.form else (request.json or {})
    product_input = data.get('coupang_url', '').strip()
    industry_key = data.get('industry', 'beauty_fashion')
    mechanism_id = data.get('mechanism', 'loss_aversion')
    custom_target = data.get('custom_target', '').strip()
    voice_tone = data.get('voice_tone', 'info')
    
    hooks_info = get_hooks_data()
    prompts_info = get_prompts_data()
    
    ind_dict = hooks_info.get('industry_dictionary', {})
    ind_data = ind_dict.get(industry_key, {})
    ind_name = ind_data.get('name', '뷰티·패션')
    
    # Clean product name
    product_name = product_input
    if 'http' in product_input:
        if 'kbeauty_serum' in product_input or '라운드랩' in product_input:
            product_name = '라운드랩 자작나무 수분크림'
        elif 'kbeauty_pad' in product_input or '달바' in product_input:
            product_name = '달바 비건 미스트 세럼'
        elif 'kbeauty_sun' in product_input or '구달' in product_input:
            product_name = '구달 맑은 어성초 선크림'
        elif 'kbeauty_lip' in product_input or '롬앤' in product_input:
            product_name = '롬앤 쥬시 래스팅 틴트'
        else:
            bestsellers = ind_data.get('bestsellers', ['쿠팡 베스트셀러 대란템'])
            product_name = bestsellers[0]
    elif not product_name:
        bestsellers = ind_data.get('bestsellers', ['쿠팡 베스트셀러 대란템'])
        product_name = bestsellers[0]

    # Hook 0~3s
    hook_candidates = {
        'loss_aversion': f'🔥 품절 임박! {product_name} 지금 안 사면 무조건 손해봅니다',
        'curiosity_gap': f'🤫 누적 10만 개 팔린 {product_name}의 숨겨진 비밀',
        'social_proof': f'📈 조회수 300만 돌파! 요즘 다들 난리 난 {product_name} 실사용기',
        'pattern_interrupt': f'⚠️ 절대 사지 마세요! {product_name} 쓰기 전에 모르면 후회하는 사실',
        'identity_calling': f'👀 {custom_target if custom_target else ind_name + " 필수 타깃"}라면 이 영상 무조건 끝까지 보세요'
    }
    hook_text = hook_candidates.get(mechanism_id, hook_candidates['loss_aversion'])

    # Problem 3~8s
    problem_texts = {
        'food': '매번 비싼 외식이나 맛없는 배달음식 때문에 고민 많으셨죠? 집에서 5분 만에 완성되는 꿀맛을 찾고 계셨을 텐데요.',
        'beauty_fashion': '피부과에 100만 원 쏟아붓기 전에 잠깐만요. 매일 바르는 화장품 순서와 성분만 바꿔도 피부가 확 달라집니다.',
        'health_fitness': '아무리 굶고 열심히 운동해도 안 빠지는 살 때문에 스트레스 받으셨나요? 원인은 따로 있습니다.',
        'finance_realestate': '매달 월급 들어오자마자 스쳐 지나가고, 세금과 물가 때문에 통장 잔고가 늘지 않아 막막하셨죠?',
        'selfdev_career': '열심히 사는데 성과는 안 나오고 번아웃만 오는 이유, 당신의 노력 문제가 아니라 시스템 문제입니다.',
        'travel': '남들 다 가는 뻔하고 바가지 쓰는 관광지 대신, 진짜 현지인만 아는 인생 명소를 찾고 싶으셨죠?',
        'parenting_pet': '말 못 하는 우리 아이, 반려견이 불편해하고 긁는데 원인을 몰라 마음 아프셨던 적 있으시죠?',
        'it_tech_gadget': '비싸게 주고 산 기기, 기본 기능의 10%만 쓰고 계신가요? 99%가 모르는 핵심 치트키가 있습니다.',
        'business_marketing': '좋은 제품만 만들면 팔릴 줄 알았는데, 매출은 제자리이고 광고비만 날리고 계셨나요?',
        'interior_lifestyle': '좁고 답답한 원룸, 큰돈 들이지 않고 호텔처럼 세련되게 바꿀 수 없을까 고민하셨죠?'
    }
    problem_text = problem_texts.get(industry_key, problem_texts['beauty_fashion'])

    # Solution 8~25s
    solution_texts = {
        'food': f'이 {product_name} 하나면 셰프급 비법 소스와 신선한 원재료로 3분 만에 호텔 레스토랑 퀄리티가 완성됩니다. 가성비까지 완벽해요!',
        'beauty_fashion': f'이 {product_name}은 흡수율을 극대화한 독자 배합으로 바르자마자 맑고 투명한 글래스 스킨을 만들어줍니다. 번들거림 없이 촉촉함만 남아요.',
        'health_fitness': f'하루 딱 7분, 이 {product_name} 루틴을 적용하면 기초대사량이 급상승하면서 체지방이 빠르게 연소됩니다. 실제 데이터로 검증된 방법이에요.',
        'finance_realestate': f'이 {product_name} 절세 전략과 자동 저축 시스템을 구축하면 연간 200만 원 이상을 자동으로 아끼고 복리 수익을 만들 수 있습니다.',
        'selfdev_career': f'상위 1% 전문가들이 매일 실천하는 {product_name} 3단계 프레임워크를 적용하세요. 업무 시간은 절반으로 줄고 성과는 3배가 됩니다.',
        'travel': f'이 {product_name} 코스를 따라가면 비용은 50만 원 아끼면서, 줄 서지 않고 숨은 에메랄드빛 절경과 인생샷을 독점할 수 있습니다.',
        'parenting_pet': f'수의사와 전문가가 권장하는 {product_name} 안심 케어법으로 스트레스 없이 건강하고 행복한 일상을 선물하세요.',
        'it_tech_gadget': f'이 {product_name}의 숨은 단축 설정 하나로 작업 속도가 3배 빨라집니다. 실사용자 만족도 99%를 기록한 이유가 바로 여기에 있어요.',
        'business_marketing': f'자본금 100만 원으로 월 매출을 폭발시킨 {product_name} 마케팅 자동화 퍼널입니다. 고객이 스스로 결제하게 만드는 구조를 복사해가세요.',
        'interior_lifestyle': f'이 {product_name} 꿀조합으로 조명과 수납을 재배치하면, 7평 원룸도 1.5배 넓어 보이고 인스타 감성 무드로 완벽 변신합니다.'
    }
    solution_text = solution_texts.get(industry_key, solution_texts['beauty_fashion'])

    cta_text = '📌 나중에 꼭 써먹을 꿀팁이니 지금 [저장]해두고 하나씩 따라해보세요! 친구에게 공유하면 더 좋습니다.'

    full_script = f'[0~3초 후킹]\n{hook_text}\n\n[3~8초 공감/문제]\n{problem_text}\n\n[8~25초 솔루션/가치]\n{solution_text}\n\n[마지막 3초 CTA]\n{cta_text}'

    captions = {
        'layer1_header': f'{hook_text[:28]}...',
        'layer2_sub': f'{ind_name} 실전 압축 꿀팁 대방출',
        'layer3_cta': '👉 저장해두고 매일 꺼내보세요!'
    }

    visual_notes = {
        'visual_hook': ind_data.get('visual_tip', 'Before/After 스플릿 스크린 / 제품 클로즈업'),
        'first_frame': '1.5초 내 시각적 자극: 고대비 텍스트 팝업 + 역동적 줌인',
        'shot_breakdown': [
            '0~3s: 극적인 제품/결과물 초근접 클로즈업 (텍스트 팝업)',
            '3~8s: 일상 속 문제 상황 캔디드 샷 (POV 또는 분할 화면)',
            '8~20s: 제품 언박싱 & 실제 사용 모습 (슬로모션 + 텍스처 강조)',
            '20~25s: 비포/애프터 비교 및 만족스러운 최종 결과',
            '25~30s: 프로필 유도 커버 & 저장 CTA 모션 그래픽'
        ]
    }

    audio_notes = {
        'voice_tone': hooks_info.get('audio_guide', {}).get(voice_tone, {}).get('tone', '또렷하고 빠른 톤 (+20% 에너지)'),
        'bgm_mood': f'{ind_name} 맞춤 릴스 트렌딩 오디오 (상승 화살표 BGM 적용)',
        'sfx': '0초 화면전환 팝 사운드 → 8초 솔루션 전환 챠임벨 → 마지막 CTA 클릭음'
    }

    if industry_key == 'food':
        mj_prompt = 'ultra-realistic 8K food photography, gourmet dish freshly served with sizzling steam and glistening sauce texture, elegant ceramic tableware in high-end restaurant lighting, shallow depth of field, Canon EOS R5 50mm f/1.4 lens, commercial advertising quality --ar 9:16 --style raw --v 7'
    elif industry_key in ['beauty_fashion', 'beauty']:
        mj_prompt = f'ultra realistic beauty skincare macro shot, {product_name} bottle with glass dropper, glowing hydrated porcelain skin texture with visible pores, soft clinical studio lighting, neutral minimal background, high-end cosmetic campaign photography --ar 9:16 --style raw --v 7'
    elif industry_key == 'health_fitness':
        mj_prompt = 'cinematic fitness lifestyle photography, athletic aesthetic model training in modern luxury gym, dynamic motion capture with soft rim lighting, sweat droplets texture, hyper-detailed 8K --ar 9:16 --style raw --v 7'
    elif industry_key == 'it_tech_gadget':
        mj_prompt = f'minimalist tech product hero shot of {product_name}, sleek modern design on dark brushed aluminum surface, subtle cyber blue and neon pink accent reflections, studio lighting, Phase One IQ4 120mm macro --ar 9:16 --style raw --v 7'
    elif industry_key == 'interior_lifestyle':
        mj_prompt = 'modern aesthetic minimal studio apartment interior, warm ambient sunset lighting streaming through sheer curtains, scandinavian furniture and indoor plants, architectural digest quality --ar 9:16 --style raw --v 7'
    else:
        mj_prompt = f'commercial advertising photography of {product_name}, luxury aesthetic, pristine studio lighting, 8k resolution, photorealistic textures, Vogue magazine quality --ar 9:16 --style raw --v 7'

    first_word = ind_name.replace('·', ' ').replace('/', ' ').split()[0]
    hashtags = [
        f'#{first_word}',
        f'#{product_name.split()[0]}추천',
        '#릴스꿀팁',
        '#인스타트렌드',
        '#살림꿀팁' if industry_key in ['food', 'interior_lifestyle'] else '#꿀템추천'
    ]

    item_id = str(uuid.uuid4())[:8]
    result_package = {
        'id': item_id,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'product_name': product_name,
        'industry_key': industry_key,
        'industry_name': ind_name,
        'mechanism_name': mechanism_id,
        'hook_text': hook_text,
        'problem_text': problem_text,
        'solution_text': solution_text,
        'cta_text': cta_text,
        'full_script': full_script,
        'captions': captions,
        'visual_notes': visual_notes,
        'audio_notes': audio_notes,
        'midjourney_prompt': mj_prompt,
        'hashtags': hashtags,
        'upload_time': '오후 19:00 ~ 21:00 (퇴근 후 최고 참여율 골든타임)',
        'link': product_input
    }

    queue = load_json(QUEUE_FILE, [])
    queue.insert(0, result_package)
    save_json(QUEUE_FILE, queue)

    return jsonify({'success': True, 'package': result_package})

@app.route('/api/simulate', methods=['POST'])
def api_simulate():
    data = request.json or {}
    followers = int(data.get('followers', 10000))
    clients = int(data.get('clients', 1))
    orders = int(data.get('orders', 5))
    
    if followers < 3000:
        r1_per = 0
        r1_monthly = 0
    elif followers < 5000:
        r1_per = 50000
        r1_monthly = r1_per * 3
    elif followers < 10000:
        r1_per = 140000
        r1_monthly = r1_per * 3
    elif followers < 30000:
        r1_per = 300000
        r1_monthly = r1_per * 4
    else:
        r1_per = 550000
        r1_monthly = r1_per * 5
    
    r2_monthly = clients * 600000
    r3_monthly = orders * 60000
    total_monthly = r1_monthly + r2_monthly + r3_monthly
    
    return jsonify({
        'followers': followers,
        'r1_creator': {'per_ad': r1_per, 'monthly': r1_monthly},
        'r2_agency': {'clients': clients, 'monthly': r2_monthly},
        'r3_freelance': {'orders': orders, 'monthly': r3_monthly},
        'total_monthly': total_monthly,
        'formatted_total': f'{total_monthly:,}원'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
