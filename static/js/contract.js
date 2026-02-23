// 移工勞動契約 VC 發行頁面 JavaScript

// 即時驗證：輸入時顯示紅框/綠框 + 按鈕狀態切換
function updateSubmitButton() {
    const form = document.getElementById('contractForm');
    const btn = form.querySelector('button[type="submit"]');
    if (form.checkValidity()) {
        btn.disabled = false;
        btn.classList.remove('btn-submit-disabled');
    } else {
        btn.disabled = true;
        btn.classList.add('btn-submit-disabled');
    }
}

// 契約到期時間必須晚於今天
function validateContractExpiry() {
    const expiry = document.querySelector('[name="contract_expiry"]');
    const today = new Date().toISOString().split('T')[0];
    if (expiry.value && expiry.value <= today) {
        expiry.setCustomValidity('契約到期時間必須晚於今天');
    } else {
        expiry.setCustomValidity('');
    }
}

document.querySelector('[name="contract_expiry"]').addEventListener('change', function() {
    validateContractExpiry();
    updateSubmitButton();
});

document.getElementById('contractForm').addEventListener('input', function() {
    this.classList.add('was-validated');
    updateSubmitButton();
});

// 頁面載入時先設為灰色
document.addEventListener('DOMContentLoaded', updateSubmitButton);

// 勞動契約表單提交
document.getElementById('contractForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    // 格式不對就擋住，不送 API
    if (!e.target.checkValidity()) {
        e.target.classList.add('was-validated');
        return;
    }

    const formData = new FormData(e.target);
    const data = {
        vc_type: 'contract',
        worker_name: formData.get('worker_name'),
        company_name: formData.get('company_name'),
        company_telephone: formData.get('company_telephone'),
        company_address: formData.get('company_address'),
        job_title: formData.get('job_title'),
        monthly_wages: formData.get('monthly_wages'),
        contract_expiry: formData.get('contract_expiry'),
        agency_name: formData.get('agency_name'),
        agency_telephone: formData.get('agency_telephone')
    };

    console.log("📤 送出的契約資料:", data);
    await issueCredential(data, e.target);
});

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

// 顯示 QR Code Modal
function showQRCodeModal(result) {
    // 設定憑證類型名稱
    document.getElementById('vcTypeName').textContent = result.vc_name;

    // 設定交易序號 (判斷標籤類型以正確填入)
    const txElement = document.getElementById('transactionId');
    if (txElement) {
        if (txElement.tagName === 'INPUT') {
            txElement.value = result.transaction_id;
        } else {
            txElement.textContent = result.transaction_id;
        }
    }

    // 設定 DeepLink
    const deepLinkInput = document.getElementById('deepLinkUrl');
    if (deepLinkInput) {
        deepLinkInput.value = result.deep_link || '';
    }

    // 清除舊的 QR Code
    const qrContainer = document.getElementById('qrCodeDisplay');
    qrContainer.innerHTML = '';

    // 產生新的 QR Code
    if (result.qr_code) {
        // 如果 API 返回 base64 圖片
        const img = document.createElement('img');
        // 自動判斷是否補 Base64 前綴，防止雙重前綴導致破圖
        img.src = result.qr_code.startsWith('data:image') ? result.qr_code : 'data:image/png;base64,' + result.qr_code;
        img.style.width = '280px';
        img.style.height = '280px';
        img.classList.add('img-fluid', 'mx-auto', 'd-block', 'shadow-sm');
        qrContainer.appendChild(img);
    } else if (result.deep_link && typeof QRCode !== 'undefined') {
        // 如果只有 DeepLink，用前端生成 QR Code
        new QRCode(qrContainer, {
            text: result.deep_link,
            width: 280,
            height: 280,
            colorDark: '#000000',
            colorLight: '#ffffff'
        });
    }

    // 顯示 Modal
    const modal = new bootstrap.Modal(document.getElementById('qrModal'));
    modal.show();
}

// 複製 DeepLink
function copyDeepLink() {
    const deepLinkInput = document.getElementById('deepLinkUrl');
    if (!deepLinkInput || !deepLinkInput.value) return;

    deepLinkInput.select();
    deepLinkInput.setSelectionRange(0, 99999);

    navigator.clipboard.writeText(deepLinkInput.value).then(() => {
        const copyBtn = event.target.closest('button');
        const originalHTML = copyBtn.innerHTML;

        copyBtn.innerHTML = '<i class="fas fa-check"></i> 已複製';
        copyBtn.classList.replace('btn-outline-primary', 'btn-success');

        setTimeout(() => {
            copyBtn.innerHTML = originalHTML;
            copyBtn.classList.replace('btn-success', 'btn-outline-primary');
        }, 2000);
    }).catch(err => {
        console.error('複製失敗:', err);
        alert('複製失敗，請手動複製');
    });
}