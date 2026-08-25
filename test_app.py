# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import app

client = app.test_client()

# 1. Test Login
res_login = client.get('/login')
assert res_login.status_code == 200, f"Login failed: {res_login.status_code}"
print("[1/6] Login page: OK")

# 2. Test Auth
res_auth = client.post('/api/auth', data={'password': '635835', 'device_name': 'Test Device'})
assert res_auth.json['success'] == True
print("[2/6] Auth API: OK")

# 3. Test Hooks
res_hooks = client.get('/api/hooks')
assert len(res_hooks.json['templates']) == 108
print(f"[3/6] Hooks API: OK (108 templates, {len(res_hooks.json['industry_dictionary'])} industries)")

# 4. Test Prompts
res_prompts = client.get('/api/prompts')
assert len(res_prompts.json['master_prompts']) == 20
print(f"[4/6] Prompts API: OK (20 master prompts)")

# 5. Test Monetization
res_monet = client.get('/api/monetization')
assert len(res_monet.json['routes']) == 3
print("[5/6] Monetization API: OK (3 routes)")

# 6. Test Generation
res_gen = client.post('/api/generate', data={
    'coupang_url': 'https://link.coupang.com/a/kbeauty_serum_01',
    'industry': 'beauty_fashion',
    'mechanism': 'loss_aversion',
    'voice_tone': 'info'
})
assert res_gen.json['success'] == True
pkg = res_gen.json['package']
assert '0~3초 후킹' in pkg['full_script']
print(f"[6/6] Generation API: OK (Product: {pkg['product_name']})")

print("\n🎉 ALL BACKEND APIS AND SERVICES VERIFIED 100% OPERATIONAL!")
