# -*- coding: utf-8 -*-
import os

def compile_static():
    # Read original index template
    template_path = 'vidcrack_all_in_one/templates/index.html'
    if not os.path.exists(template_path):
        # Fallback if run from repo root
        template_path = 'templates/index.html'
    
    if not os.path.exists(template_path):
        print(f"Error: {template_path} not found.")
        return
        
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Define the login panel HTML
    login_html = """
    <!-- LOGIN VIEW -->
    <div id="loginView" class="bg-[#0a0a0c] flex items-center justify-center min-h-screen text-white p-4 relative overflow-hidden w-full h-screen">
        <div class="absolute -top-40 -left-40 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl pointer-events-none"></div>
        <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-pink-600/20 rounded-full blur-3xl pointer-events-none"></div>
        
        <div class="bg-[#141518]/90 backdrop-blur-xl p-8 md:p-10 rounded-3xl shadow-2xl border border-[#26282d] w-full max-w-md text-center relative z-10">
            <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 to-pink-500 mb-6 shadow-lg shadow-blue-500/20">
                <i class="fa-solid fa-wand-magic-sparkles text-2xl text-white"></i>
            </div>
            
            <h1 class="text-3xl font-extrabold mb-2 bg-gradient-to-r from-blue-400 via-indigo-300 to-pink-400 bg-clip-text text-transparent">VidCrack AI Pro</h1>
            <p class="text-xs text-gray-400 mb-8 font-medium tracking-wide">올인원 AI 숏폼 영상·이미지·수익화 마스터 스튜디오</p>
            
            <form id="loginForm" onsubmit="authStatic(event)" class="space-y-4">
                <div class="text-left">
                    <label class="block text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wider">디바이스 별칭</label>
                    <input type="text" id="devName" placeholder="예: 작업용 PC, 맥북 프로" class="w-full bg-[#0e0f10] text-white px-4 py-3 border border-[#2a2b2e] rounded-xl text-sm focus:border-blue-500 outline-none transition">
                </div>
                
                <div class="text-left">
                    <label class="block text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wider">마스터 패스코드</label>
                    <input type="password" id="pwd" placeholder="••••••" maxlength="6" class="w-full bg-[#0e0f10] text-white px-4 py-4 border border-[#2a2b2e] rounded-xl text-center text-2xl tracking-[0.6em] focus:border-pink-500 outline-none transition font-mono">
                </div>
                
                <button type="submit" id="btnLogin" class="w-full bg-gradient-to-r from-blue-600 to-pink-600 text-white font-bold py-4 rounded-xl shadow-lg shadow-pink-500/25 hover:opacity-95 transition flex items-center justify-center gap-2 mt-4">
                    <i class="fa-solid fa-arrow-right-to-bracket"></i> Connect Workspace
                </button>
                
                <p id="msg" class="text-pink-400 text-xs font-bold min-h-[20px]"></p>
            </form>
            
            <div class="mt-6 pt-6 border-t border-[#222] flex justify-between text-xs text-gray-500">
                <span><i class="fa-solid fa-shield-halved mr-1"></i> Device Limit: 9</span>
                <span>v2.5 Pro All-in-One</span>
            </div>
        </div>
    </div>
"""

    # Wrap main content in a container
    html = html.replace(
        '<!-- Toast Notification -->',
        login_html + '\\n    <!-- Toast Notification -->\\n    <div id="mainView" class="hidden flex h-screen w-full overflow-hidden">'
    )

    # Add closing div for mainView right before main javascript tag
    html = html.replace(
        '<!-- MAIN APP JAVASCRIPT -->',
        '</div>\\n    <!-- MAIN APP JAVASCRIPT -->'
    )

    # Replace jinja template tags with HTML spans
    html = html.replace(
        "{{ device.device_name if device else '인증된 디바이스' }}",
        "<span id=\\\"deviceNameLabel\\\">인증된 디바이스</span>"
    )
    html = html.replace(
        "{{ device_count }}",
        "<span id=\\\"deviceCountLabel\\\">1</span>"
    )

    # Remove flex layout from body tag to allow login screen vs mainView splitting
    html = html.replace(
        '<body class="bg-[#0a0a0c] text-gray-200 font-sans flex h-screen overflow-hidden">',
        '<body class="bg-[#0a0a0c] text-gray-200 font-sans h-screen overflow-hidden">'
    )

    # Replace the script block with a completely client-side JS implementation
    js_code = """
    <!-- MAIN APP JAVASCRIPT -->
    <script>
        let currentTab = 'tab-factory';
        let currentIndustry = 'beauty_fashion';
        let currentPackage = null;
        let hooksData = null;
        let promptsData = null;
        let monetizationData = null;

        // AUTHENTICATION STATE & LOGIC
        function checkAuth() {
            const isAuth = localStorage.getItem('vidcrack_auth') === 'true';
            const devName = localStorage.getItem('vidcrack_device') || 'Member Device';
            
            if (isAuth) {
                document.getElementById('loginView').classList.add('hidden');
                document.getElementById('mainView').classList.remove('hidden');
                document.getElementById('deviceNameLabel').innerText = devName;
                document.getElementById('deviceCountLabel').innerText = "1";
                initData();
            } else {
                document.getElementById('loginView').classList.remove('hidden');
                document.getElementById('mainView').classList.add('hidden');
            }
        }

        function authStatic(e) {
            e.preventDefault();
            const btn = document.getElementById('btnLogin');
            const msg = document.getElementById('msg');
            const pwd = document.getElementById('pwd').value.trim();
            const dev = document.getElementById('devName').value.trim() || '작업용 PC';

            if (!pwd) {
                msg.innerText = "마스터 암호를 입력해주세요.";
                return;
            }

            btn.disabled = true;
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Authenticating...';

            setTimeout(() => {
                if (pwd === '635835') {
                    msg.className = "text-blue-400 text-xs font-bold";
                    msg.innerText = "인증 완료! 스튜디오로 이동합니다...";
                    localStorage.setItem('vidcrack_auth', 'true');
                    localStorage.setItem('vidcrack_device', dev);
                    setTimeout(() => {
                        btn.disabled = false;
                        btn.innerHTML = '<i class="fa-solid fa-arrow-right-to-bracket"></i> Connect Workspace';
                        checkAuth();
                    }, 400);
                } else {
                    msg.className = "text-pink-400 text-xs font-bold";
                    msg.innerText = "비밀번호가 올바르지 않습니다.";
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fa-solid fa-arrow-right-to-bracket"></i> Connect Workspace';
                }
            }, 500);
        }

        function logout() {
            if(!confirm("연결을 해제하고 로그인 페이지로 이동하시겠습니까?")) return;
            localStorage.removeItem('vidcrack_auth');
            localStorage.removeItem('vidcrack_device');
            checkAuth();
        }

        // TABS CONTROLLER
        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            
            const target = document.getElementById(tabId);
            if(target) target.classList.remove('hidden');
            
            const btn = document.getElementById(tabId.replace('tab-', 'nav-'));
            if(btn) btn.classList.add('active');
            
            currentTab = tabId;
            if(tabId === 'tab-queue') loadQueue();
        }

        function showToast(msg, icon='fa-circle-check') {
            const toast = document.getElementById('toast');
            document.getElementById('toastMsg').innerText = msg;
            document.getElementById('toastIcon').className = `fa-solid ${icon} text-blue-400`;
            toast.classList.remove('opacity-0', 'pointer-events-none', 'translate-y-[-10px]');
            setTimeout(() => {
                toast.classList.add('opacity-0', 'pointer-events-none', 'translate-y-[-10px]');
            }, 2200);
        }

        function copyText(txt) {
            if(!txt) return;
            navigator.clipboard.writeText(txt).then(() => {
                showToast("클립보드에 복사되었습니다!");
            });
        }

        // FETCH STATIC DATA
        async function initData() {
            try {
                const [hRes, pRes, mRes] = await Promise.all([
                    fetch('data/hooks_data.json'),
                    fetch('data/prompts_data.json'),
                    fetch('data/monetization_data.json')
                ]);
                hooksData = await hRes.json();
                promptsData = await pRes.json();
                monetizationData = await mRes.json();

                renderIndustryChips();
                renderBestsellerChips();
                renderMechanismCards();
                renderHookCategories();
                renderHooks();
                renderIndustryDictionary();
                renderMasterPrompts();
                renderMonetization();
                renderChecklists();
                updateMediaKitPreview();
                calcSimulation();
                loadQueue();
            } catch(e) {
                console.error("Init data error:", e);
                showToast("데이터 로딩 중 오류가 발생했습니다.", 'fa-circle-exclamation');
            }
        }

        function renderIndustryChips() {
            if(!hooksData || !hooksData.industry_dictionary) return;
            const dict = hooksData.industry_dictionary;
            const container = document.getElementById('industryChips');
            
            container.innerHTML = Object.entries(dict).map(([key, item]) => {
                const isAct = key === currentIndustry;
                return `
                    <button type="button" onclick="selectIndustry('${key}')" class="p-3 rounded-2xl border text-left transition flex items-center gap-2.5 ${isAct ? 'bg-blue-600/20 border-blue-500 text-white font-bold shadow-lg shadow-blue-500/10' : 'bg-[#141518] border-[#22242a] text-gray-400 hover:border-[#333] hover:text-white'}">
                        <i class="fa-solid ${item.icon} text-base ${isAct ? 'text-pink-400' : 'text-gray-500'}"></i>
                        <span class="text-xs truncate">${item.name}</span>
                    </button>
                `;
            }).join('');
        }

        function selectIndustry(key) {
            currentIndustry = key;
            renderIndustryChips();
            renderBestsellerChips();
        }

        function renderBestsellerChips() {
            if(!hooksData || !hooksData.industry_dictionary) return;
            const item = hooksData.industry_dictionary[currentIndustry];
            if(!item) return;
            const container = document.getElementById('bestsellerChips');
            
            container.innerHTML = item.bestsellers.map(b => `
                <button type="button" onclick="fillKeyword('${b}')" class="bg-[#141518] hover:bg-pink-500/20 hover:border-pink-500 border border-[#26282d] text-xs text-gray-300 px-3 py-1.5 rounded-xl transition flex items-center gap-1.5">
                    <span class="text-pink-400">✨</span> ${b}
                </button>
            `).join('');
        }

        function fillKeyword(keyword) {
            const input = document.getElementById('coupangUrl');
            input.value = keyword;
            input.classList.add('bg-blue-900/30');
            setTimeout(() => input.classList.remove('bg-blue-900/30'), 300);
            showToast(`'${keyword}' 자동 입력 완료`);
        }

        function renderMechanismCards() {
            if(!hooksData || !hooksData.mechanisms) return;
            const container = document.getElementById('mechanismCards');
            container.innerHTML = hooksData.mechanisms.map(m => `
                <div class="bg-[#141518] border border-[#22242a] p-4 rounded-2xl space-y-2 hover:border-purple-500/50 transition">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-black text-pink-400">${m.no}</span>
                        <span class="text-[10px] bg-[#222] text-gray-400 px-2 py-0.5 rounded">심리 트리거</span>
                    </div>
                    <h4 class="text-xs font-bold text-white leading-tight">${m.name}</h4>
                    <p class="text-[11px] text-gray-400 leading-snug">${m.desc}</p>
                </div>
            `).join('');
        }

        let currentHookCat = 'ALL';
        function renderHookCategories() {
            if(!hooksData || !hooksData.categories) return;
            const container = document.getElementById('hookCatFilters');
            const cats = [{code: 'ALL', name: '전체 (108)'}, ...hooksData.categories];
            
            container.innerHTML = cats.map(c => `
                <button type="button" onclick="filterHookCat('${c.code}')" class="text-xs px-3 py-1.5 rounded-xl border transition ${currentHookCat === c.code ? 'bg-pink-600/20 border-pink-500 text-white font-bold' : 'bg-[#141518] border-[#26282d] text-gray-400 hover:text-white'}">
                    ${c.name}
                </button>
            `).join('');
        }

        function filterHookCat(code) {
            currentHookCat = code;
            renderHookCategories();
            renderHooks();
        }

        function renderHooks() {
            if(!hooksData || !hooksData.templates) return;
            const container = document.getElementById('hooksList');
            const query = (document.getElementById('hookSearch')?.value || '').toLowerCase();
            
            const varItem = document.getElementById('var_item')?.value || '';
            const varPlace = document.getElementById('var_place')?.value || '';
            const varJob = document.getElementById('var_job')?.value || '';
            const varMoney = document.getElementById('var_money')?.value || '';
            const varTime = document.getElementById('var_time')?.value || '';
            const varN = document.getElementById('var_n')?.value || '';

            let list = hooksData.templates;
            if(currentHookCat !== 'ALL') {
                list = list.filter(t => t.cat === currentHookCat || (currentHookCat === 'H' && (t.cat === 'H_OPEN' || t.cat === 'H_CLOSE')));
            }
            if(query) {
                list = list.filter(t => t.template.toLowerCase().includes(query) || t.example.toLowerCase().includes(query));
            }

            container.innerHTML = list.map(t => {
                let replaced = t.template;
                if(varItem) replaced = replaced.replaceAll('[주제]', varItem).replaceAll('[아이템]', varItem).replaceAll('[물건]', varItem).replaceAll('[제품]', varItem);
                if(varPlace) replaced = replaced.replaceAll('[장소]', varPlace).replaceAll('[플랫폼]', varPlace);
                if(varJob) replaced = replaced.replaceAll('[직업]', varJob).replaceAll('[전문가]', varJob).replaceAll('[셰프]', varJob);
                if(varMoney) replaced = replaced.replaceAll('[금액]', varMoney).replaceAll('[가격대]', varMoney).replaceAll('[소득]', varMoney);
                if(varTime) replaced = replaced.replaceAll('[시간]', varTime).replaceAll('[기간]', varTime).replaceAll('[기한]', varTime);
                if(varN) replaced = replaced.replaceAll('N가지', `${varN}가지`).replaceAll('N탄', `${varN}탄`).replaceAll('N일차', `${varN}일차`).replaceAll('Top N', `Top ${varN}`).replaceAll('N', varN);

                const hasReplaced = replaced !== t.template;

                return `
                    <div class="bg-[#141518] border border-[#22242a] p-5 rounded-2xl hover:border-blue-500/50 transition flex flex-col justify-between space-y-3">
                        <div class="space-y-2">
                            <div class="flex items-center justify-between">
                                <span class="bg-[#222] text-[11px] text-pink-400 font-bold px-2 py-0.5 rounded border border-[#333]">#${t.id} ${t.cat_name}</span>
                                <button onclick="copyText('${replaced.replace(/'/g, "\\\\'")}')" class="text-xs text-gray-400 hover:text-white p-1" title="복사"><i class="fa-regular fa-copy"></i></button>
                            </div>
                            <h4 class="text-sm font-bold text-white leading-snug ${hasReplaced ? 'text-blue-300' : ''}">${replaced}</h4>
                            <p class="text-xs text-gray-500">예시: ${t.example}</p>
                        </div>
                        <div class="pt-2 border-t border-[#1e2025] flex justify-end">
                            <button onclick="applyHookToFactory('${replaced.replace(/'/g, "\\\\'")}')" class="text-[11px] text-blue-400 hover:text-blue-300 font-semibold flex items-center gap-1">
                                <i class="fa-solid fa-bolt"></i> 숏폼 공장에 적용
                            </button>
                        </div>
                    </div>
                `;
            }).join('');
        }

        function resetVariables() {
            ['var_item', 'var_place', 'var_job', 'var_money', 'var_time', 'var_n'].forEach(id => {
                const el = document.getElementById(id);
                if(el) el.value = '';
            });
            renderHooks();
            showToast("변수가 초기화되었습니다.");
        }

        function applyHookToFactory(hookText) {
            switchTab('tab-factory');
            const input = document.getElementById('coupangUrl');
            input.value = hookText;
            input.focus();
            showToast("선택한 훅 문구가 공장 입력창에 설정되었습니다!");
        }

        function renderIndustryDictionary() {
            if(!hooksData || !hooksData.industry_dictionary) return;
            const container = document.getElementById('industryDictionaryList');
            
            container.innerHTML = Object.entries(hooksData.industry_dictionary).map(([key, item]) => `
                <div class="bg-[#141518] border border-[#22242a] p-6 rounded-3xl space-y-4">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2.5">
                            <i class="fa-solid ${item.icon} text-pink-400 text-lg"></i>
                            <h4 class="text-base font-bold text-white">${item.name}</h4>
                        </div>
                        <button onclick="selectIndustry('${key}'); switchTab('tab-factory');" class="text-xs bg-blue-500/20 text-blue-400 border border-blue-500/30 px-3 py-1 rounded-lg">공장에서 사용</button>
                    </div>
                    <div class="bg-[#0a0a0c] p-3 rounded-xl border border-[#222] text-xs text-amber-300">
                        <i class="fa-solid fa-video mr-1"></i> <b class="text-white">비주얼 팁:</b> ${item.visual_tip}
                    </div>
                    <div class="space-y-2 text-xs">
                        ${item.hooks.map(h => `
                            <div class="flex items-start justify-between bg-[#101114] p-2.5 rounded-xl border border-[#1e2025]">
                                <div>
                                    <span class="text-pink-400 font-bold mr-1.5">[${h.type}]</span>
                                    <span class="text-gray-200">${h.template}</span>
                                    <span class="text-gray-500 block mt-0.5">예: ${h.example}</span>
                                </div>
                                <button onclick="copyText('${h.example.replace(/'/g, "\\\\'")}')" class="text-gray-500 hover:text-white p-1"><i class="fa-regular fa-copy"></i></button>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `).join('');
        }

        function renderMasterPrompts() {
            if(!promptsData || !promptsData.master_prompts) return;
            const container = document.getElementById('masterPromptsGrid');
            
            container.innerHTML = promptsData.master_prompts.map(p => `
                <div class="bg-[#141518] border border-[#22242a] p-6 rounded-3xl space-y-4 hover:border-purple-500/50 transition">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <span class="bg-purple-500/20 text-purple-400 text-xs font-black px-2.5 py-1 rounded-lg">#${String(p.id).padStart(2, '0')}</span>
                            <h4 class="text-base font-bold text-white">${p.title}</h4>
                        </div>
                        <span class="bg-[#222] text-[11px] text-gray-400 px-2 py-0.5 rounded font-mono">AR ${p.ar}</span>
                    </div>

                    <div class="flex flex-wrap gap-1.5">
                        ${p.tags.map(t => `<span class="bg-[#1e2025] text-gray-400 text-[10px] px-2 py-0.5 rounded">#${t}</span>`).join('')}
                    </div>

                    <div class="bg-[#0a0a0c] p-4 rounded-xl border border-[#222] font-mono text-xs text-gray-200 leading-relaxed relative group">
                        <p class="select-all">${p.prompt}</p>
                        <button onclick="copyText('${p.prompt.replace(/'/g, "\\\\'")}')" class="absolute top-2 right-2 bg-blue-600/40 hover:bg-blue-600 text-white text-[11px] px-2.5 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition">
                            <i class="fa-regular fa-copy mr-1"></i> 복사
                        </button>
                    </div>

                    <details class="bg-[#101114] p-3 rounded-xl border border-[#1e2025] text-xs text-gray-400 cursor-pointer">
                        <summary class="font-bold text-gray-300 hover:text-white">8요소 분석 및 활용 팁 보기</summary>
                        <div class="mt-3 space-y-1.5 pt-2 border-t border-[#222]">
                            <div><b class="text-pink-400">주제:</b> ${p.analysis.subject}</div>
                            <div><b class="text-blue-400">묘사:</b> ${p.analysis.description}</div>
                            <div><b class="text-purple-400">구도:</b> ${p.analysis.composition}</div>
                            <div><b class="text-amber-400">조명:</b> ${p.analysis.lighting}</div>
                            <div><b class="text-emerald-400">카메라/스타일:</b> ${p.analysis.camera} / ${p.analysis.style}</div>
                            <div class="pt-2 text-gray-300 font-semibold">
                                <span class="text-pink-400 font-bold">💡 팁:</span> ${p.tips.join(' • ')}
                            </div>
                        </div>
                    </details>
                </div>
            `).join('');
        }

        function updateBuiltPrompt() {
            const subj = document.getElementById('b_subj')?.value || 'a luxury product';
            const desc = document.getElementById('b_desc')?.value || 'ultra-realistic details';
            const comp = document.getElementById('b_comp')?.value || 'centered composition';
            const light = document.getElementById('b_light')?.value || 'clinical studio lighting';
            const mood = document.getElementById('b_mood')?.value || 'luxury aesthetic';
            const cam = document.getElementById('b_cam')?.value || 'Phase One IQ4 + 120mm macro';
            const style = document.getElementById('b_style')?.value || 'commercial advertising quality, 8k';
            const params = document.getElementById('b_params')?.value || '--ar 9:16 --style raw --v 7';

            const result = `${subj}, ${desc}, ${comp}, ${light}, ${mood}, ${cam}, ${style} ${params}`;
            document.getElementById('builtPromptResult').innerText = result;
        }

        function setCamPreset(gear) {
            document.getElementById('b_cam').value = gear;
            updateBuiltPrompt();
            showToast(`카메라 프리셋: ${gear}`);
        }

        function setFilmPreset(film) {
            const el = document.getElementById('b_mood');
            el.value = el.value ? `${el.value}, ${film} color grading` : `${film} color grading`;
            updateBuiltPrompt();
            showToast(`필름 스톡: ${film}`);
        }

        function resetBuilder() {
            document.getElementById('b_subj').value = '';
            document.getElementById('b_desc').value = '';
            document.getElementById('b_comp').value = '';
            document.getElementById('b_light').value = '';
            document.getElementById('b_mood').value = '';
            document.getElementById('b_cam').value = '';
            document.getElementById('b_style').value = '';
            document.getElementById('b_params').value = '--ar 9:16 --style raw --v 7';
            updateBuiltPrompt();
            showToast("빌더가 초기화되었습니다.");
        }

        function renderMonetization() {
            if(!monetizationData || !monetizationData.routes) return;
            const container = document.getElementById('monetizeRoutesCards');
            
            container.innerHTML = monetizationData.routes.map(r => `
                <div class="bg-[#141518] border border-[#22242a] p-6 rounded-3xl flex flex-col justify-between space-y-4 hover:border-amber-500/50 transition">
                    <div class="space-y-3">
                        <div class="flex items-center justify-between">
                            <span class="bg-amber-500/20 text-amber-400 text-xs font-black px-2.5 py-1 rounded-lg">루트 ${r.no}</span>
                            <span class="text-xs bg-emerald-500/20 text-emerald-400 font-bold px-2.5 py-1 rounded-lg">${r.badge}</span>
                        </div>
                        <h4 class="text-base font-bold text-white leading-tight">${r.name}</h4>
                        <p class="text-xs text-gray-400 leading-relaxed">${r.desc}</p>
                        <div class="bg-[#0a0a0c] p-3 rounded-xl border border-[#222] text-xs text-gray-300">
                            <b class="text-amber-400">⏱ 소요 시간:</b> ${r.time_needed}
                        </div>
                    </div>
                    <div class="pt-2 text-xs text-gray-500 border-t border-[#1e2025]">
                        <i class="fa-solid fa-lightbulb text-pink-400 mr-1"></i> ${r.key_point}
                    </div>
                </div>
            `).join('');

            const planList = document.getElementById('plan30DaysList');
            if(planList) {
                planList.innerHTML = monetizationData.plan_30days.map(p => `
                    <div class="bg-[#0a0a0c] p-3.5 rounded-2xl border border-[#222] flex items-center justify-between text-xs">
                        <div>
                            <span class="text-blue-400 font-bold block mb-0.5">${p.period}</span>
                            <span class="text-gray-300">${p.action}</span>
                        </div>
                        <div class="text-right">
                            <span class="text-pink-400 font-bold block">${p.goal}</span>
                            <span class="text-[10px] text-gray-500">${p.status}</span>
                        </div>
                    </div>
                `).join('');
            }

            const nicheList = document.getElementById('topNichesList');
            if(nicheList) {
                nicheList.innerHTML = monetizationData.top_niches.map(n => `
                    <div class="bg-[#0a0a0c] p-3 rounded-xl border border-[#222] flex items-center justify-between text-xs">
                        <div class="flex items-center gap-2">
                            <span class="w-5 h-5 rounded-full bg-[#1e2025] text-amber-400 flex items-center justify-center font-bold text-[10px]">${n.rank}</span>
                            <span class="text-white font-bold">${n.niche}</span>
                        </div>
                        <span class="text-gray-400 text-[11px]">${n.reason}</span>
                    </div>
                `).join('');
            }
        }

        function calcSimulation() {
            const followers = parseInt(document.getElementById('sl_followers')?.value || 10000);
            const clients = parseInt(document.getElementById('sl_clients')?.value || 1);
            const orders = parseInt(document.getElementById('sl_orders')?.value || 5);

            document.getElementById('val_followers').innerText = `${followers.toLocaleString()}명`;
            document.getElementById('val_clients').innerText = `${clients}곳`;
            document.getElementById('val_orders').innerText = `${orders}건`;

            let r1_monthly = 0;
            if(followers < 3000) r1_monthly = 0;
            else if(followers < 5000) r1_monthly = 150000;
            else if(followers < 10000) r1_monthly = 420000;
            else if(followers < 30000) r1_monthly = 1200000;
            else r1_monthly = 2750000;

            const r2_monthly = clients * 600000;
            const r3_monthly = orders * 60000;
            const total = r1_monthly + r2_monthly + r3_monthly;

            document.getElementById('rev_r1').innerText = `월 ${(r1_monthly/10000).toFixed(0)}만원`;
            document.getElementById('rev_r2').innerText = `월 ${(r2_monthly/10000).toFixed(0)}만원`;
            document.getElementById('rev_r3').innerText = `월 ${(r3_monthly/10000).toFixed(0)}만원`;
            document.getElementById('simTotal').innerText = `₩ ${total.toLocaleString()}`;
        }

        function updateMediaKitPreview() {
            const name = document.getElementById('mk_name')?.value || '뷰티 채널';
            const niche = document.getElementById('mk_niche')?.value || '뷰티';
            const fol = document.getElementById('mk_followers')?.value || '10,000';
            const price = document.getElementById('mk_price')?.value || '250,000';

            const txt = `========================================================\n[공식 미디어킷 & 협업 제안서] ${name}\n========================================================\n1. 채널 개요\n  - 채널명: ${name}\n  - 카테고리/니치: ${niche}\n  - 타깃 오디언스: 2030 구매력 높은 핵심 타깃 (여성 78% / 남성 22%)\n\n2. 핵심 성과 지표 (KPI)\n  - 팔로워 수: ${fol}명\n  - 릴스 평균 조회수: 45,000 ~ 120,000회\n  - 평균 참여율(ER): 8.4% (동급 계정 대비 2.3배)\n\n3. 협업 서비스 & 단가표\n  - 릴스 1편 단독 PPL/리뷰: ₩ ${price} (부가세 별도)\n  - 릴스 1편 + 프로필 링크트리 7일 게시: ₩ ${(parseInt(price.replace(/,/g,''))*1.2).toLocaleString()}\n  - 스토리 리포스트 (24시간): ₩ 50,000\n\n4. 협업 프로세스\n  - DM/이메일 문의 → 제품 수령 및 기획안 공유 → 영상 검수 → 업로드\n  - 광고 표시: '유료광고포함' 공식 태그 준수\n========================================================`;

            const el = document.getElementById('mediaKitPreview');
            if(el) el.innerText = txt;
        }

        function copyMediaKit() {
            updateMediaKitPreview();
            copyText(document.getElementById('mediaKitPreview').innerText);
        }

        ['mk_name', 'mk_niche', 'mk_followers', 'mk_price'].forEach(id => {
            document.getElementById(id)?.addEventListener('input', updateMediaKitPreview);
        });

        function renderChecklists() {
            if(!monetizationData || !monetizationData.preflight_checks) return;
            const mustEl = document.getElementById('mustChecksList');
            const niceEl = document.getElementById('niceChecksList');

            if(mustEl) {
                mustEl.innerHTML = monetizationData.preflight_checks.must.map(m => `
                    <label class="flex items-start gap-3 text-xs text-gray-300 cursor-pointer bg-[#0a0a0c] p-3 rounded-xl border border-[#222] hover:border-[#333] transition">
                        <input type="checkbox" onchange="updateCheckScores()" class="must-cb mt-0.5 accent-pink-500 rounded cursor-pointer">
                        <span>${m.label}</span>
                    </label>
                `).join('');
            }

            if(niceEl) {
                niceEl.innerHTML = monetizationData.preflight_checks.nice_to_have.map(n => `
                    <label class="flex items-start gap-3 text-xs text-gray-300 cursor-pointer bg-[#0a0a0c] p-3 rounded-xl border border-[#222] hover:border-[#333] transition">
                        <input type="checkbox" onchange="updateCheckScores()" class="nice-cb mt-0.5 accent-blue-500 rounded cursor-pointer">
                        <span>${n.label}</span>
                    </label>
                `).join('');
            }
        }

        function updateCheckScores() {
            const mustTotal = document.querySelectorAll('.must-cb').length;
            const mustDone = document.querySelectorAll('.must-cb:checked').length;
            document.getElementById('mustScore').innerText = `${mustDone}/${mustTotal} 완료`;

            const niceTotal = document.querySelectorAll('.nice-cb').length;
            const niceDone = document.querySelectorAll('.nice-cb:checked').length;
            document.getElementById('niceScore').innerText = `${niceDone}/${niceTotal} 완료`;
        }

        function setHookScore(status) {
            const resEl = document.getElementById('hookTestResult');
            resEl.classList.remove('hidden');
            if(status === 'pass') {
                resEl.className = "p-4 rounded-xl border border-emerald-500/50 bg-emerald-950/20 text-emerald-300 text-xs font-semibold";
                resEl.innerHTML = "🎉 <b class='text-white'>[합격 - 100점]</b> 호기심 유발 완벽! 3초 이내 스크롤 멈춤 및 완주율 가중치를 극대화할 수 있습니다.";
            } else if(status === 'warn') {
                resEl.className = "p-4 rounded-xl border border-amber-500/50 bg-amber-950/20 text-amber-300 text-xs font-semibold";
                resEl.innerHTML = "⚠️ <b class='text-white'>[보완 필요 - 60점]</b> 훅이 다소 뻔합니다. '아, 궁금하다'가 나오도록 [금액 손실]이나 [의외의 질문]으로 첫 줄을 수정하세요.";
            } else {
                resEl.className = "p-4 rounded-xl border border-pink-500/50 bg-pink-950/20 text-pink-300 text-xs font-semibold";
                resEl.innerHTML = "❌ <b class='text-white'>[재작성 권장 - 20점]</b> 시청자 이탈 위험이 매우 높습니다. 1.5초 내에 시각적 줌인과 충격적인 텍스트로 다시 설계하세요.";
            }
        }

        // CLIENT-SIDE GENERATION ENGINE (Equivalent to Python app.py logic)
        function generatePackageLocal(coupangUrl, industryKey, mechanismId, customTarget, voiceTone) {
            const indData = (hooksData && hooksData.industry_dictionary && hooksData.industry_dictionary[industryKey]) || {};
            const indName = indData.name || '뷰티·패션';
            
            let productName = coupangUrl.trim();
            if (coupangUrl.includes('http') || !productName) {
                if (coupangUrl.includes('kbeauty_serum') || coupangUrl.includes('라운드랩')) {
                    productName = '라운드랩 자작나무 수분크림';
                } else if (coupangUrl.includes('kbeauty_pad') || coupangUrl.includes('달바')) {
                    productName = '달바 비건 미스트 세럼';
                } else if (coupangUrl.includes('kbeauty_sun') || coupangUrl.includes('구달')) {
                    productName = '구달 맑은 어성초 선크림';
                } else if (coupangUrl.includes('kbeauty_lip') || coupangUrl.includes('롬앤')) {
                    productName = '롬앤 쥬시 래스팅 틴트';
                } else {
                    const bestsellers = indData.bestsellers || ['쿠팡 베스트셀러 대란템'];
                    productName = bestsellers[Math.floor(Math.random() * bestsellers.length)];
                }
            }

            const hookCandidates = {
                'loss_aversion': `🔥 품절 임박! ${productName} 지금 안 사면 무조건 손해봅니다`,
                'curiosity_gap': `🤫 누적 10만 개 팔린 ${productName}의 숨겨진 비밀`,
                'social_proof': `📈 조회수 300만 돌파! 요즘 다들 난리 난 ${productName} 실사용기`,
                'pattern_interrupt': `⚠️ 절대 사지 마세요! ${productName} 쓰기 전에 모르면 후회하는 사실`,
                'identity_calling': `👀 ${customTarget ? customTarget : indName + ' 필수 타깃'}라면 이 영상 무조건 끝까지 보세요`
            };
            const hookText = hookCandidates[mechanismId] || hookCandidates['loss_aversion'];

            const problemTexts = {
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
            };
            const problemText = problemTexts[industryKey] || problemTexts['beauty_fashion'];

            const solutionTexts = {
                'food': `이 ${productName} 하나면 셰프급 비법 소스와 신선한 원재료로 3분 만에 호텔 레스토랑 퀄리티가 완성됩니다. 가성비까지 완벽해요!`,
                'beauty_fashion': `이 ${productName}은 흡수율을 극대화한 독자 배합으로 바르자마자 맑고 투명한 글래스 스킨을 만들어줍니다. 번들거림 없이 촉촉함만 남아요.`,
                'health_fitness': `하루 딱 7분, 이 ${productName} 루틴을 적용하면 기초대사량이 급상승하면서 체지방이 빠르게 연소됩니다. 실제 데이터로 검증된 방법이에요.`,
                'finance_realestate': `이 ${productName} 절세 전략과 자동 저축 시스템을 구축하면 연간 200만 원 이상을 자동으로 아끼고 복리 수익을 만들 수 있습니다.`,
                'selfdev_career': `상위 1% 전문가들이 매일 실천하는 ${productName} 3단계 프레임워크를 적용하세요. 업무 시간은 절반으로 줄고 성과는 3배가 됩니다.`,
                'travel': `이 ${productName} 코스를 따라가면 비용은 50만 원 아끼면서, 줄 서지 않고 숨은 에메랄드빛 절경과 인생샷을 독점할 수 있습니다.`,
                'parenting_pet': `수의사와 전문가가 권장하는 ${productName} 안심 케어법으로 스트레스 없이 건강하고 행복한 일상을 선물하세요.`,
                'it_tech_gadget': `이 ${productName}의 숨은 단축 설정 하나로 작업 속도가 3배 빨라집니다. 실사용자 만족도 99%를 기록한 이유가 바로 여기에 있어요.`,
                'business_marketing': `자본금 100만 원으로 월 매출을 폭발시킨 ${productName} 마케팅 자동화 퍼널입니다. 고객이 스스로 결제하게 만드는 구조를 복사해가세요.`,
                'interior_lifestyle': `이 ${productName} 꿀조합으로 조명과 수납을 재배치하면, 7평 원룸도 1.5배 넓어 보이고 인스타 감성 무드로 완벽 변신합니다.`
            };
            const solutionText = solutionTexts[industryKey] || solutionTexts['beauty_fashion'];

            const ctaText = '📌 나중에 꼭 써먹을 꿀팁이니 지금 [저장]해두고 하나씩 따라해보세요! 친구에게 공유하면 더 좋습니다.';
            const fullScript = `[0~3초 후킹]\\n${hookText}\\n\\n[3~8초 공감/문제]\\n${problemText}\\n\\n[8~25초 솔루션/가치]\\n${solutionText}\\n\\n[마지막 3초 CTA]\\n${ctaText}`;

            const captions = {
                'layer1_header': `${hookText.substring(0, 28)}...`,
                'layer2_sub': `${indName} 실전 압축 꿀팁 대방출`,
                'layer3_cta': '👉 저장해두고 매일 꺼내보세요!'
            };

            const visualNotes = {
                'visual_hook': indData.visual_tip || 'Before/After 스플릿 스크린 / 제품 클로즈업',
                'first_frame': '1.5초 내 시각적 자극: 고대비 텍스트 팝업 + 역동적 줌인',
                'shot_breakdown': [
                    '0~3s: 극적인 제품/결과물 초근접 클로즈업 (텍스트 팝업)',
                    '3~8s: 일상 속 문제 상황 캔디드 샷 (POV 또는 분할 화면)',
                    '8~20s: 제품 언박싱 & 실제 사용 모습 (슬로모션 + 텍스처 강조)',
                    '20~25s: 비포/애프터 비교 및 만족스러운 최종 결과',
                    '25~30s: 프로필 유도 커버 & 저장 CTA 모션 그래픽'
                ]
            };

            const audioNotes = {
                'voice_tone': (hooksData && hooksData.audio_guide && hooksData.audio_guide[voiceTone] && hooksData.audio_guide[voiceTone].tone) || '또렷하고 빠른 톤 (+20% 에너지)',
                'bgm_mood': `${indName} 맞춤 릴스 트렌딩 오디오 (상승 화살표 BGM 적용)`,
                'sfx': '0초 화면전환 팝 사운드 → 8초 솔루션 전환 챠임벨 → 마지막 CTA 클릭음'
            };

            let mjPrompt = '';
            if (industryKey === 'food') {
                mjPrompt = 'ultra-realistic 8K food photography, gourmet dish freshly served with sizzling steam and glistening sauce texture, elegant ceramic tableware in high-end restaurant lighting, shallow depth of field, Canon EOS R5 50mm f/1.4 lens, commercial advertising quality --ar 9:16 --style raw --v 7';
            } else if (industryKey === 'beauty_fashion' || industryKey === 'beauty') {
                mjPrompt = `ultra realistic beauty skincare macro shot, ${productName} bottle with glass dropper, glowing hydrated porcelain skin texture with visible pores, soft clinical studio lighting, neutral minimal background, high-end cosmetic campaign photography --ar 9:16 --style raw --v 7`;
            } else if (industryKey === 'health_fitness') {
                mjPrompt = 'cinematic fitness lifestyle photography, athletic aesthetic model training in modern luxury gym, dynamic motion capture with soft rim lighting, sweat droplets texture, hyper-detailed 8K --ar 9:16 --style raw --v 7';
            } else if (industryKey === 'it_tech_gadget') {
                mjPrompt = `minimalist tech product hero shot of ${productName}, sleek modern design on dark brushed aluminum surface, subtle cyber blue and neon pink accent reflections, studio lighting, Phase One IQ4 120mm macro --ar 9:16 --style raw --v 7`;
            } else if (industryKey === 'interior_lifestyle') {
                mjPrompt = 'modern aesthetic minimal studio apartment interior, warm ambient sunset lighting streaming through sheer curtains, scandinavian furniture and indoor plants, architectural digest quality --ar 9:16 --style raw --v 7';
            } else {
                mjPrompt = `commercial advertising photography of ${productName}, luxury aesthetic, pristine studio lighting, 8k resolution, photorealistic textures, Vogue magazine quality --ar 9:16 --style raw --v 7`;
            }

            const firstWord = indName.replace('·', ' ').replace('/', ' ').split(' ')[0];
            const hashtags = [
                `#${firstWord}`,
                `#${productName.split(' ')[0]}추천`,
                '#릴스꿀팁',
                '#인스타트렌드',
                (industryKey === 'food' || industryKey === 'interior_lifestyle') ? '#살림꿀팁' : '#꿀템추천'
            ];

            const itemId = Math.random().toString(36).substring(2, 10);
            
            return {
                'id': itemId,
                'created_at': new Date().toISOString().replace('T', ' ').substring(0, 19),
                'product_name': productName,
                'industry_key': industryKey,
                'industry_name': indName,
                'mechanism_name': mechanismId,
                'hook_text': hookText,
                'problem_text': problemText,
                'solution_text': solutionText,
                'cta_text': ctaText,
                'full_script': fullScript,
                'captions': captions,
                'visual_notes': visualNotes,
                'audio_notes': audioNotes,
                'midjourney_prompt': mjPrompt,
                'hashtags': hashtags,
                'upload_time': '오후 19:00 ~ 21:00 (퇴근 후 최고 참여율 골든타임)',
                'link': coupangUrl
            };
        }

        const loadingTexts = [
            "쿠팡 상품 상세페이지 및 후기 분석 중...",
            "5대 심리 트리거 & 훅 문구 조립 중...",
            "4단계 바이럴 스크립트 (Hook-Problem-Solution-CTA) 완성 중...",
            "미드저니 8요소 프롬프트 및 최적 해시태그 패키징 중..."
        ];

        document.getElementById('genForm')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('btnGen');
            const loadBox = document.getElementById('loadingBox');
            const outSec = document.getElementById('outputSection');
            const txtEl = document.getElementById('loadingStepText');

            btn.disabled = true;
            btn.style.opacity = '0.5';
            loadBox.classList.remove('hidden');
            outSec.classList.add('hidden');

            let idx = 0;
            const interval = setInterval(() => {
                idx = (idx + 1) % loadingTexts.length;
                if(txtEl) txtEl.innerText = loadingTexts[idx];
            }, 1200);

            // Simulation of server latency
            setTimeout(() => {
                clearInterval(interval);
                btn.disabled = false;
                btn.style.opacity = '1';
                loadBox.classList.add('hidden');

                const coupangUrl = document.getElementById('coupangUrl').value.trim();
                const mechanism = document.getElementById('mechanismSelect').value;
                const voiceTone = document.getElementById('voiceToneSelect').value;
                const customTarget = document.getElementById('customTarget').value.trim();

                const pkg = generatePackageLocal(coupangUrl, currentIndustry, mechanism, customTarget, voiceTone);
                currentPackage = pkg;
                
                // Save to localStorage queue
                let queue = JSON.parse(localStorage.getItem('vidcrack_queue') || '[]');
                queue.unshift(pkg);
                localStorage.setItem('vidcrack_queue', JSON.stringify(queue));

                displayPackage(pkg);
                loadQueue();
                showToast("바이럴 릴스 패키지 생성이 완료되었습니다!");
            }, 3000);
        });

        function displayPackage(pkg) {
            document.getElementById('outHook').innerText = pkg.hook_text;
            document.getElementById('outProblem').innerText = pkg.problem_text;
            document.getElementById('outSolution').innerText = pkg.solution_text;
            document.getElementById('outCta').innerText = pkg.cta_text;

            document.getElementById('outCap1').innerText = pkg.captions.layer1_header;
            document.getElementById('outCap2').innerText = pkg.captions.layer2_sub;
            document.getElementById('outCap3').innerText = pkg.captions.layer3_cta;

            document.getElementById('outAudioTone').innerText = pkg.audio_notes.voice_tone;
            document.getElementById('outAudioBgm').innerText = pkg.audio_notes.bgm_mood;
            document.getElementById('outUploadTime').innerText = pkg.upload_time;

            document.getElementById('outMjPrompt').innerText = pkg.midjourney_prompt;

            const tagsContainer = document.getElementById('outHashtags');
            tagsContainer.innerHTML = pkg.hashtags.map(t => `<span class="bg-blue-500/10 text-blue-400 border border-blue-500/20 text-[10px] px-2 py-0.5 rounded font-mono">${t}</span>`).join('');

            const shotlistContainer = document.getElementById('outShotlist');
            shotlistContainer.innerHTML = pkg.visual_notes.shot_breakdown.map(s => `
                <div class="bg-[#0a0a0c] p-2 rounded-lg border border-[#222] flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-pink-500"></span>
                    <span>${s}</span>
                </div>
            `).join('');

            document.getElementById('outputSection').classList.remove('hidden');
            document.getElementById('outputSection').scrollIntoView({behavior: 'smooth'});
        }

        function copyFullPackage() {
            if(!currentPackage) return;
            const fullText = `[릴스 제목 / 상품]: ${currentPackage.product_name}\\n[업종]: ${currentPackage.industry_name}\\n[생성일시]: ${currentPackage.created_at}\\n\\n==================================================\\n1. 4단계 바이럴 릴스 대본\\n==================================================\\n${currentPackage.full_script}\\n\\n==================================================\\n2. 텍스트 오버레이 3층 자막\\n==================================================\\n- 1층 메인: ${currentPackage.captions.layer1_header}\\n- 2층 서브: ${currentPackage.captions.layer2_sub}\\n- 3층 행동: ${currentPackage.captions.layer3_cta}\\n\\n==================================================\\n3. 미드저니 v7 프롬프트\\n==================================================\\n${currentPackage.midjourney_prompt}\\n\\n==================================================\\n4. 해시태그 & 최적 업로드 시간\\n==================================================\\n- 해시태그: ${currentPackage.hashtags.join(' ')}\\n- 업로드 골든타임: ${currentPackage.upload_time}\\n`;
            copyText(fullText);
        }

        function downloadJsonPackage() {
            if(!currentPackage) return;
            const blob = new Blob([JSON.stringify(currentPackage, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `vidcrack_shorts_${currentPackage.id}.json`;
            a.click();
            URL.revokeObjectURL(url);
            showToast("JSON 파일이 다운로드되었습니다.");
        }

        // QUEUE MANAGER (Local Storage version)
        function loadQueue() {
            try {
                const queue = JSON.parse(localStorage.getItem('vidcrack_queue') || '[]');
                
                const badge = document.getElementById('queueBadge');
                if(badge) badge.innerText = queue.length;

                const container = document.getElementById('queueListContainer');
                if(!container) return;

                if(queue.length === 0) {
                    container.innerHTML = `
                        <div class="col-span-full text-center py-16 bg-[#141518] rounded-3xl border border-[#222]">
                            <i class="fa-solid fa-box-open text-4xl text-gray-600 mb-3"></i>
                            <h4 class="text-base font-bold text-gray-400">보관된 릴스가 없습니다</h4>
                            <p class="text-xs text-gray-600 mt-1">숏폼 원스톱 공장에서 새 릴스를 생성해보세요.</p>
                        </div>
                    `;
                    return;
                }

                container.innerHTML = queue.map(q => {
                    const safeQ = JSON.stringify(q).replace(/'/g, "&#39;").replace(/"/g, "&quot;");
                    return `
                        <div class="bg-[#141518] border border-[#22242a] p-6 rounded-3xl hover:border-blue-500/50 transition flex flex-col justify-between space-y-4 group">
                            <div class="space-y-3">
                                <div class="flex items-center justify-between">
                                    <span class="bg-[#1e2025] text-pink-400 text-[11px] font-bold px-2.5 py-1 rounded-lg border border-[#26282d]">${q.industry_name}</span>
                                    <span class="text-[11px] text-gray-500 font-mono">${q.created_at.split(' ')[0]}</span>
                                </div>
                                <h4 class="text-base font-bold text-white leading-tight group-hover:text-blue-400 transition">${q.hook_text}</h4>
                                <p class="text-xs text-gray-400 line-clamp-3 leading-relaxed">${q.problem_text} ${q.solution_text}</p>
                            </div>
                            <div class="pt-3 border-t border-[#1e2025] flex items-center justify-between">
                                <button onclick='openDetailModalStatic(${safeQ})' class="text-xs text-blue-400 hover:text-blue-300 font-semibold flex items-center gap-1">
                                    <i class="fa-solid fa-eye"></i> 전체 보기
                                </button>
                                <button onclick="deleteQueueItem('${q.id}')" class="text-xs text-gray-500 hover:text-red-400 transition p-1" title="삭제">
                                    <i class="fa-solid fa-trash-can"></i>
                                </button>
                            </div>
                        </div>
                    `;
                }).join('');
            } catch(e) {
                console.error("Queue load error:", e);
            }
        }

        function deleteQueueItem(id) {
            if(!confirm("이 릴스를 보관함에서 삭제하시겠습니까?")) return;
            let queue = JSON.parse(localStorage.getItem('vidcrack_queue') || '[]');
            queue = queue.filter(q => q.id !== id);
            localStorage.setItem('vidcrack_queue', JSON.stringify(queue));
            loadQueue();
            showToast("삭제되었습니다.");
        }

        function clearQueue() {
            if(!confirm("보관함의 모든 릴스를 삭제하시겠습니까?")) return;
            localStorage.setItem('vidcrack_queue', '[]');
            loadQueue();
            showToast("보관함이 비워졌습니다.");
        }

        function openDetailModalStatic(pkg) {
            document.getElementById('modalCategory').innerText = pkg.industry_name;
            document.getElementById('modalTitle').innerText = pkg.product_name;

            document.getElementById('modalBody').innerHTML = `
                <div class="space-y-4">
                    <div>
                        <h5 class="font-bold text-pink-400 mb-1">🔥 후킹 문구 (0~3초)</h5>
                        <p class="text-white bg-[#0a0a0c] p-3 rounded-xl border border-[#222]">${pkg.hook_text}</p>
                    </div>
                    <div>
                        <h5 class="font-bold text-blue-400 mb-1">📖 4단계 전체 대본</h5>
                        <div class="text-gray-200 bg-[#0a0a0c] p-4 rounded-xl border border-[#222] font-mono leading-relaxed whitespace-pre-wrap">${pkg.full_script}</div>
                    </div>
                    <div>
                        <h5 class="font-bold text-purple-400 mb-1">🎨 미드저니 v7 프롬프트</h5>
                        <div class="text-gray-200 bg-[#0a0a0c] p-3 rounded-xl border border-[#222] font-mono leading-relaxed select-all">${pkg.midjourney_prompt}</div>
                    </div>
                    <div>
                        <h5 class="font-bold text-emerald-400 mb-1">🏷 해시태그</h5>
                        <p class="text-emerald-300 font-mono">${pkg.hashtags.join(' ')}</p>
                    </div>
                </div>
            `;
            document.getElementById('detailModal').classList.remove('hidden');
        }

        function closeModal() {
            document.getElementById('detailModal').classList.add('hidden');
        }

        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            sidebar.classList.toggle('collapsed');
        }

        function saveApiKey(val) {
            localStorage.setItem('gemini_api_key', val);
        }

        function initApiKeyInput() {
            const stored = localStorage.getItem('gemini_api_key') || '';
            const el = document.getElementById('geminiApiKey');
            if (el) el.value = stored;
        }

        // AI Shorts Video Generator Logic (Veo 3.0 Integration)
        async function generateShortsVideo() {
            if (!currentPackage) {
                alert("생성된 패키지가 없습니다. 먼저 대본을 생성하세요.");
                return;
            }

            const apiKey = localStorage.getItem('gemini_api_key') || '';
            if (!apiKey) {
                alert("좌측 하단에 Gemini API Key를 입력하셔야 Veo 3.0 동영상 생성을 시작할 수 있습니다.");
                document.getElementById('geminiApiKey')?.focus();
                return;
            }

            const btn = document.getElementById('btnMakeVideo');
            const loadBox = document.getElementById('renderLoadingBox');
            const outputSec = document.getElementById('outputSection');
            const stepText = document.getElementById('renderStepText');
            const bar = document.getElementById('renderProgressBar');

            btn.disabled = true;
            btn.style.opacity = '0.5';
            loadBox.classList.remove('hidden');
            outputSec.scrollIntoView({behavior: 'smooth'});

            stepText.innerText = "Veo 3.0 비디오 생성 요청 전송 중...";
            bar.style.width = "10%";

            // Check if running on GitHub Pages
            const isStaticPages = window.location.hostname.includes('github.io');
            if (isStaticPages) {
                const stages = [
                    {pct: 25, text: "미드저니 AI 프롬프트 기반 Veo 3.0 비디오 프레임 구성 중... (GitHub Pages 데모)"},
                    {pct: 50, text: "10대 업종 특화 3층 자막 오버레이 그래픽 합성 중..."},
                    {pct: 75, text: "성우 음성(TTS) 및 배경음악 매핑 중..."},
                    {pct: 100, text: "릴스 파일 인코딩 완료! 다운로드 파일을 준비하는 중..."}
                ];
                let idx = 0;
                const timer = setInterval(() => {
                    if (idx < stages.length) {
                        stepText.innerText = stages[idx].text;
                        bar.style.width = stages[idx].pct + "%";
                        idx++;
                    } else {
                        clearInterval(timer);
                        btn.disabled = false;
                        btn.style.opacity = '1';
                        loadBox.classList.add('hidden');
                        alert("🎉 [GitHub Pages 데모] AI 숏폼 영상(샘플) 제작이 완료되었습니다! 로컬 스튜디오에서 실행 시 실제 Veo 3.0 API로 영상을 렌더링합니다.");
                    }
                }, 2000);
                return;
            }

            // Local backend API call to render video using Google Veo
            try {
                let progress = 10;
                const progressInterval = setInterval(() => {
                    if (progress < 90) {
                        progress += 5;
                        bar.style.width = progress + "%";
                        if (progress < 30) stepText.innerText = "Veo 3.0 모델 비디오 씬 생성 중...";
                        else if (progress < 60) stepText.innerText = "TTS 보이스 오디오 및 사운드 효과 병합 중...";
                        else stepText.innerText = "H.264 MP4 렌더링 파일 인코딩 중...";
                    }
                }, 4000);

                const res = await fetch('/api/render', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: currentPackage.id, api_key: apiKey })
                });
                
                clearInterval(progressInterval);
                const data = await res.json();
                
                if (data.success) {
                    bar.style.width = "100%";
                    stepText.innerText = "인코딩 완료! 다운로드 준비 중...";
                    
                    setTimeout(() => {
                        btn.disabled = false;
                        btn.style.opacity = '1';
                        loadBox.classList.add('hidden');
                        
                        const confirmDownload = confirm("🎉 Veo 3.0 AI 숏폼 영상 제작이 완료되었습니다!\\n\\n확인을 누르시면 로컬에 저장된 완성 MP4 파일을 다운로드합니다.");
                        if (confirmDownload) {
                            const a = document.createElement('a');
                            a.href = data.video_url;
                            a.download = `veo_shorts_${currentPackage.id}.mp4`;
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                        }
                    }, 1000);
                } else {
                    throw new Error(data.msg || "비디오 렌더링에 실패했습니다.");
                }
            } catch (err) {
                btn.disabled = false;
                btn.style.opacity = '1';
                loadBox.classList.add('hidden');
                alert("❌ 비디오 렌더링 실패: " + err.message);
            }
        }

        function checkAuthWrapper() {
            initApiKeyInput();
            checkAuth();
        }

        window.addEventListener('DOMContentLoaded', checkAuthWrapper);
    </script>
"""

    # Replace original script block in html
    # Find the start of <!-- MAIN APP JAVASCRIPT --> and the end of </html>
    script_start_idx = html.find('<!-- MAIN APP JAVASCRIPT -->')
    if script_start_idx != -1:
        html = html[:script_start_idx] + js_code + '\n</body>\n</html>'

    # Save to root folder
    with open('index.html', 'w', encoding='utf-8') as f_out:
        f_out.write(html)
        
    print("Static compilation complete! index.html written to target folder.")

if __name__ == '__main__':
    compile_static()
