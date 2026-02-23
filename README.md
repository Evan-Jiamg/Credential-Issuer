# 數位憑證發行端系統(ctrl+shift+v)

完整的數位憑證發行端網站，用於發行符合 OID4VCI 標準的可驗證憑證（Verifiable Credentials）。

## 🚀 快速開始

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 啟動服務
python app.py

# 3. 訪問網站
http://localhost:5001
```

## 📦 專案結構

```
credential_issuer/
├── app.py                          # Flask 主程式
├── requirements.txt                # Python 依賴
├── README.md                       # 說明文件
├── templates/                      # HTML 模板
│   ├── index.html                 # 首頁
│   ├── issue.html                 # 發行憑證頁面
│   └── query.html                 # 查詢記錄頁面
└── static/                         # 靜態資源
    ├── css/
    │   └── style.css              # 主樣式表
    └── js/
        ├── issue.js               # 發行頁面邏輯
        └── query.js               # 查詢頁面邏輯
```

## ✨ 功能特色

### 支援的憑證類型

1. **移工勞動契約 VC** (`0029986136_employee_contract`)
   - 移工姓名、職位、月薪
   - 公司名稱、地址、電話
   - 人力仲介資訊

2. **外僑居留證 VC** (`0029986136_alien_resident_certificate`)
   - 統一證號
   - 核發與效期日期
   - 卡片號碼

### 主要功能

- ✅ 即時產生 QR Code
- ✅ DeepLink 支援
- ✅ 發行記錄查詢
- ✅ 響應式設計
- ✅ 完整錯誤處理

## 🔧 設定

### Access Token

編輯 `app.py` 第 13 行：

```python
ISSUER_ACCESS_TOKEN = '您的實際Token'
```

### 埠號

預設: 5001

如需修改，編輯 `app.py` 最後一行：

```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

## 📝 使用說明

1. 訪問首頁選擇憑證類型
2. 填寫完整資料
3. 產生 QR Code
4. 移工掃描 QR Code 領取憑證

## 📂 資料夾結構說明

建立以下資料夾結構：

```
credential_issuer/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── index.html
│   ├── issue.html
│   └── query.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        ├── issue.js
        └── query.js
```

將檔案放入對應位置：
- `templates_index.html` → `templates/index.html`
- `templates_issue.html` → `templates/issue.html`
- `templates_query.html` → `templates/query.html`
- `static_css_style.css` → `static/css/style.css`
- `static_js_issue.js` → `static/js/issue.js`
- `static_js_query.js` → `static/js/query.js`

## ⚠️ 注意事項

- QR Code 有效期限：5 分鐘
- 記錄儲存方式：Session（重啟清除）
- 生產環境建議使用資料庫儲存

## 📞 技術支援

**開發單位**: 國立陽明交通大學 (NYCU)  
**整合系統**: 台灣數位發展部 (MODA) 數位憑證沙盒環境

---

**版本**: v1.0.0  
**最後更新**: 2026-02-07
