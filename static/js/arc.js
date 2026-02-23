// 外僑居留證 VC 發行頁面 JavaScript

// 日期比對驗證：居留期限必須晚於核發日期，且必須晚於今天
function validateDates() {
    const issueDate = document.querySelector('[name="issue_date"]');
    const expiryDate = document.querySelector('[name="expiry_date"]');
    const today = new Date().toISOString().split('T')[0];

    if (expiryDate.value && expiryDate.value <= today) {
        expiryDate.setCustomValidity('居留期限必須晚於今天');
    } else if (issueDate.value && expiryDate.value && expiryDate.value <= issueDate.value) {
        expiryDate.setCustomValidity('居留期限必須晚於核發日期');
    } else {
        expiryDate.setCustomValidity('');
    }
}

document.querySelector('[name="issue_date"]').addEventListener('change', function() {
    validateDates();
    updateSubmitButton();
});
document.querySelector('[name="expiry_date"]').addEventListener('change', function() {
    validateDates();
    updateSubmitButton();
});

// 即時驗證：輸入時顯示紅框/綠框 + 按鈕狀態切換
function updateSubmitButton() {
    const form = document.getElementById('arcForm');
    const btn = form.querySelector('button[type="submit"]');
    if (form.checkValidity()) {
        btn.disabled = false;
        btn.classList.remove('btn-submit-disabled');
    } else {
        btn.disabled = true;
        btn.classList.add('btn-submit-disabled');
    }
}

document.getElementById('arcForm').addEventListener('input', function() {
    this.classList.add('was-validated');
    updateSubmitButton();
});

// 頁面載入時先設為灰色
document.addEventListener('DOMContentLoaded', updateSubmitButton);

// 居留證表單提交
document.getElementById('arcForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    // 格式不對就擋住，不送 API
    if (!e.target.checkValidity()) {
        e.target.classList.add('was-validated');
        return;
    }

    const formData = new FormData(e.target);
    const data = {
        vc_type: 'arc',
        // --- 核心修改：增加抓取姓名欄位 ---
        worker_name: formData.get('worker_name'), 
        // ------------------------------
        ui_num: formData.get('ui_num'),
        issue_date: formData.get('issue_date'),
        expiry_date: formData.get('expiry_date'),
        card_num: formData.get('card_num')
    };

    console.log("📤 送出的資料內容:", data); // 建議留著這行方便 Debug
    await issueCredential(data, e.target);
});

// 其餘 issueCredential, showQRCodeModal, copyDeepLink 函數保持不變...

// 發行憑證函數
async function issueCredential(data, form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;

    // 顯示載入狀態
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>發行中...';

    try {
        const response = await fetch('/api/issue_credential', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            // 顯示成功結果
            showQRCodeModal(result);

            // 重置表單
            form.reset();
        } else {
            // 顯示錯誤
            alert('發行失敗: ' + (result.error || '未知錯誤'));
        }
    } catch (error) {
        console.error('發行錯誤:', error);
        alert('系統錯誤: ' + error.message);
    } finally {
        // 恢復按鈕狀態
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

function showQRCodeModal(result) {
    document.getElementById('vcTypeName').textContent = result.vc_name;
    
    // 填入交易序號與 DeepLink
    if (document.getElementById('transactionId')) {
        const el = document.getElementById('transactionId');
        el.tagName === 'INPUT' ? el.value = result.transaction_id : el.textContent = result.transaction_id;
    }
    if (document.getElementById('deepLinkUrl')) {
        document.getElementById('deepLinkUrl').value = result.deep_link;
    }

    const qrContainer = document.getElementById('qrCodeDisplay');
    qrContainer.innerHTML = '';

    if (result.qr_code) {
        const img = document.createElement('img');
        // 自動判斷是否補 Base64 前綴
        img.src = result.qr_code.startsWith('data:image') ? result.qr_code : 'data:image/png;base64,' + result.qr_code;
        img.style.width = '280px';
        img.style.height = '280px';
        img.classList.add('img-fluid', 'mx-auto', 'd-block');
        qrContainer.appendChild(img);
    }
    
    const modal = new bootstrap.Modal(document.getElementById('qrModal'));
    modal.show();
}

// 複製 DeepLink
function copyDeepLink() {
    const deepLinkInput = document.getElementById('deepLinkUrl');
    deepLinkInput.select();
    deepLinkInput.setSelectionRange(0, 99999);

    navigator.clipboard.writeText(deepLinkInput.value).then(() => {
        const copyBtn = event.target.closest('button');
        const originalHTML = copyBtn.innerHTML;

        copyBtn.innerHTML = '<i class="fas fa-check"></i> 已複製';
        copyBtn.classList.add('btn-success');
        copyBtn.classList.remove('btn-outline-primary');

        setTimeout(() => {
            copyBtn.innerHTML = originalHTML;
            copyBtn.classList.remove('btn-success');
            copyBtn.classList.add('btn-outline-primary');
        }, 2000);
    }).catch(err => {
        console.error('複製失敗:', err);
        alert('複製失敗，請手動複製');
    });
}
