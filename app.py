from flask import Flask, render_template, request, jsonify, session
import requests
import uuid
import json
from datetime import datetime, timedelta
import qrcode
import base64
from io import BytesIO

def generate_qr_code(text):
    """生成 QR Code 圖片並返回 base64"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

app = Flask(__name__)
@app.after_request
def inject_translate_script(response):
    if response.mimetype != 'text/html':
        return response

    translate_html = '''
    <div id="google_translate_element" style="display:none;"></div>
    
    <div id="hcap-translate-portal" class="notranslate">
        <div id="drag-handle" title="按住拖拽"><i class="fas fa-grip-vertical"></i></div>
        <div class="lang-items-container">
            <div class="lang-item"><button class="lang-node" data-lang="zh-TW">CH</button><span class="lang-desc">繁體中文</span></div>
            <div class="lang-item"><button class="lang-node" data-lang="en">EN</button><span class="lang-desc">English</span></div>
            <div class="lang-item"><button class="lang-node" data-lang="vi">VN</button><span class="lang-desc">Tiếng Việt</span></div>
            <div class="lang-item"><button class="lang-node" data-lang="id">ID</button><span class="lang-desc">Indonesia</span></div>
            <div class="lang-item"><button class="lang-node" data-lang="th">TH</button><span class="lang-desc">ภาษาไทย</span></div>
        </div>
    </div>

    <style>
        /* --- 終極暴力消滅 Google 橫條 (Banner) --- */
        html { top: 0px !important; }
        body { top: 0px !important; position: static !important; }
        .goog-te-banner-frame { display: none !important; visibility: hidden !important; height: 0 !important; }
        .skiptranslate { display: none !important; }
        #goog-gt-tt, .goog-te-balloon-frame, .goog-tooltip { display: none !important; }
        font { background-color: transparent !important; box-shadow: none !important; }

        /* --- 翻譯控制面板樣式 --- */
        #hcap-translate-portal {
            position: fixed; top: 30px; right: 30px; display: flex; align-items: center; gap: 15px;
            padding: 15px 20px; background: rgba(255, 255, 255, 0.4); backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px); border-radius: 25px; box-shadow: 0 12px 40px rgba(0,0,0,0.15);
            border: 1px solid rgba(255,255,255,0.5); z-index: 2147483647; transform-origin: top right;
            transition: transform 0.1s ease-out; animation: floatIn 1s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        #drag-handle { cursor: move; color: #4a5568; padding: 10px 5px; font-size: 20px; }
        .lang-items-container { display: flex; gap: 15px; }
        .lang-item { display: flex; flex-direction: column; align-items: center; gap: 6px; }
        .lang-node {
            width: 55px; height: 55px; border-radius: 15px; border: none;
            background: #ffffff; color: #2d3748; font-size: 16px; font-weight: 800;
            cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: 0.3s;
        }
        .lang-node:hover { transform: translateY(-8px); background: #667eea; color: white; }
        .lang-node.active { background: #4a5568; color: white; }
        .lang-desc { font-size: 11px; font-weight: 600; color: #2d3748; }

        @keyframes floatIn {
            from { opacity: 0; transform: translateY(-40px) scale(0.9); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }
        .language-selector { display: none !important; }
    </style>

    <script type="text/javascript">
        function googleTranslateElementInit() {
            new google.translate.TranslateElement({
                pageLanguage: 'zh-TW', includedLanguages: 'zh-TW,en,vi,id,th', autoDisplay: false
            }, 'google_translate_element');
        }
        setInterval(function() {
            const banner = document.querySelector(".goog-te-banner-frame");
            if (banner) { banner.style.display = 'none'; banner.remove(); }
            document.documentElement.style.top = '0px'; document.body.style.top = '0px';
        }, 100);
        function syncTranslate(lang) {
            const combo = document.querySelector('.goog-te-combo');
            if (combo) {
                combo.value = lang; combo.dispatchEvent(new Event('change'));
                document.querySelectorAll('.lang-node').forEach(b => {
                    b.classList.toggle('active', b.dataset.lang === lang);
                });
            } else { setTimeout(() => syncTranslate(lang), 500); }
        }
        const portal = document.getElementById('hcap-translate-portal');
        const handle = document.getElementById('drag-handle');
        let isDragging = false; let offset = [0, 0];
        handle.addEventListener('mousedown', (e) => {
            isDragging = true; offset = [portal.offsetLeft - e.clientX, portal.offsetTop - e.clientY];
            portal.style.transition = 'none';
        });
        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                portal.style.left = (e.clientX + offset[0]) + 'px'; portal.style.top = (e.clientY + offset[1]) + 'px';
                portal.style.right = 'auto'; portal.style.bottom = 'auto';
            }
        });
        document.addEventListener('mouseup', () => { isDragging = false; portal.style.transition = 'transform 0.1s ease-out'; });
        let scale = 1;
        portal.addEventListener('wheel', (e) => {
            e.preventDefault(); scale += e.deltaY * -0.0008; scale = Math.min(Math.max(.5, scale), 1.8); 
            portal.style.transform = `scale(${scale})`;
        });
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.lang-node');
            if (btn) {
                const lang = btn.dataset.lang; localStorage.setItem('hcap_language', lang); syncTranslate(lang);
            }
        });
        window.addEventListener('load', () => {
            const savedLang = localStorage.getItem('hcap_language');
            if (savedLang && savedLang !== 'zh-TW') syncTranslate(savedLang);
        });
    </script>
    <script type="text/javascript" src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
    '''
    
    content = response.get_data(as_text=True)
    response.set_data(content.replace('</body>', translate_html + '</body>'))
    return response
app.secret_key = 'your-secret-key-change-this-in-production'

# ========================================
# 發行端 API 設定
# ========================================
ISSUER_API_BASE = 'https://issuer-sandbox.wallet.gov.tw'

# ⚠️ 請確認這組 Token 是從「發行端沙盒」>「API 金鑰管理」剛剛產生的
# 如果還是 401，請去官網重新產生一組並貼在這裡
ISSUER_ACCESS_TOKEN = 'ha1Odrd90eAf4O6aNCgfz0bvG0CnGObF'

# ========================================
# VC 憑證設定 (設定檔)
# ========================================
# 這裡設定了兩個 key ('contract', 'arc')，防止前端傳來不同類型時報錯
# 但內容全部指向你建立的 'hcapdemo' 模板
VC_CONFIG = {
    'contract': {
        'credential_id': '00000000_employee_contract', # 你的新模板 ID
        'name': '移工勞動契約',
        'icon': 'fa-file-contract',
        'color': 'primary',
        'fields': {
            'worker_name': '英文姓名',
            'company_name': '公司名稱',
            'company_telephone': '公司電話',
            'company_address': '公司地址',
            'job_title': '職位名稱',
            'monthly_wages': '月薪',
            'contract_expiry': '契約到期時間',
            'agency_name': '仲介公司名稱',
            'agency_telephone': '仲介電話'
        },
        'validity_days': 365 # 1 年
    },
    'arc': {
        'credential_id': '00000000_alien_resident_certificate_',
        'name': '外僑居留證',
        'icon': 'fa-id-card',
        'color': 'info',
        'fields': {
            'worker_name': '英文姓名',
            'ui_num': '統一證號',
            'issue_date': '核發日期',
            'expiry_date': '居留期限',
            'card_num': '卡片編號'
        },
        'validity_days': 365
    }
}

# ========================================
# 路由 - 頁面
# ========================================

@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')

@app.route('/issue/arc')
def issue_arc():
    """發行外僑居留證頁面"""
    return render_template('arc.html')

@app.route('/issue/contract')
def issue_contract():
    """發行移工勞動契約頁面"""
    return render_template('contract.html')

@app.route('/issue')
def issue():
    """發行憑證頁面（舊版，保留兼容性）"""
    # 根據參數決定顯示哪個頁面
    vc_type = request.args.get('type', 'contract')
    if vc_type == 'arc':
        return render_template('arc.html')
    else:
        return render_template('contract.html')

# ========================================
# API - 發行憑證 (根據Swagger文件修正)
# ========================================

@app.route('/api/issue_credential', methods=['POST'])
def issue_credential():
    try:
        data = request.get_json()
        vc_type = data.get('vc_type', 'contract')
        config = VC_CONFIG.get(vc_type, VC_CONFIG['contract'])
        
        # 1. 準備 Payload 欄位
        fields_list = []
        
        if config['credential_id'] == '00000000_employee_contract':
            # 💡 針對勞動契約的 8 個欄位進行打包
            # 注意：ename 必須與你後台建立模板時輸入的英文名稱完全一致
            contract_fields = [
                'worker_name', 'company_name', 'company_telephone', 
                'company_address', 'job_title', 'monthly_wages', 
                'contract_expiry', 'agency_name', 'agency_telephone'
            ]
            for field in contract_fields:
                val = data.get(field, '')
                # 特別處理姓名：HTML 傳 worker_name，但模板 ename 是 name
                if field == 'worker_name' and not val:
                    val = data.get('worker_name', '')
                
                fields_list.append({
                    "ename": field,
                    "content": str(val) # 強制轉字串，符合 API 要求
                })
                
        elif config['credential_id'] == '00000000_alien_resident_certificate_':
            # ARC 邏輯 (維持你剛才成功的橫線日期格式)
            arc_fields = ['worker_name', 'ui_num', 'issue_date', 'expiry_date', 'card_num']
            for field in arc_fields:
                fields_list.append({
                    "ename": field,
                    "content": data.get(field, '')
                })
        
        # 2. 準備 API 請求 (發行日與過期日採 YYYYMMDD)
        today = datetime.now().strftime("%Y%m%d")
        expired_dt = datetime.now() + timedelta(days=config['validity_days'])
        expired_date = expired_dt.strftime("%Y%m%d")

        api_payload = {
            "vcUid": config['credential_id'],
            "issuanceDate": today,
            "expiredDate": expired_date,
            "fields": fields_list
        }

        # 3. 設定 Header
        headers = {
            "Access-Token": ISSUER_ACCESS_TOKEN,
            "Content-Type": "application/json"
        }

        # 4. 執行請求
        api_url = f"{ISSUER_API_BASE}/api/qrcode/data"
        print(f"\n🚀 正在發行: {config['name']} ({config['credential_id']})")
        print(api_payload)
        
        resp = requests.post(api_url, headers=headers, json=api_payload, timeout=10)
        result = resp.json()
        
        print(f"📥 API 回應狀態碼: {resp.status_code}")

        if resp.status_code in [200, 201] and 'transactionId' in result:
            qr_code = result.get('qrCode')
            if qr_code and not qr_code.startswith('data:image'):
                qr_code = 'data:image/png;base64,' + qr_code

            # 儲存發行記錄至 Session
            records = session.get('issuance_records', [])
            records.append({
                'transaction_id': result['transactionId'],
                'vc_type': vc_type,
                'vc_name': config['name'],
                'timestamp': datetime.now().isoformat(),
                'personal_data': {item['ename']: item['content'] for item in fields_list}
            })
            session['issuance_records'] = records

            return jsonify({
                'success': True,
                'transaction_id': result['transactionId'],
                'qr_code': qr_code,
                'deep_link': result.get('deepLink'),
                'vc_name': config['name']
            })
        else:
            # 錯誤處理
            error_msg = result.get('message', result.get('response', {}).get('message', '發行失敗'))
            print(f"❌ 錯誤原因: {error_msg}")
            return jsonify({'success': False, 'error': error_msg}), 400

    except Exception as e:
        print(f"💥 系統錯誤: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get_issuance_records', methods=['GET'])
def get_issuance_records():
    """
    取得發行記錄
    """
    try:
        records = session.get('issuance_records', [])
        return jsonify({
            'success': True,
            'records': records
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/info')
def info():
    """
    顯示系統介紹頁面（特色與使用流程）
    """
    return ('', 404)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)