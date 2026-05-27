# 新電腦設定指南

**適用於**: Windows 和 macOS  
**目標**: 設定 NetBackup Policy 知識庫處理環境

---

## 📋 前置需求

### Python 3 安裝

#### Windows

1. 前往 https://www.python.org/downloads/
2. 下載最新的 Python 3.x（建議 3.9 或以上）
3. 執行安裝程式
4. ⚠️ **重要**: 勾選 "Add Python to PATH"
5. 點擊 "Install Now"

**驗證安裝**:
```cmd
python --version
```

#### macOS

**方法 1: 使用 Homebrew（推薦）**:
```bash
# 安裝 Homebrew（如果還沒有）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安裝 Python 3
brew install python3
```

**方法 2: 從官網下載**:
```
https://www.python.org/downloads/macos/
```

**驗證安裝**:
```bash
python3 --version
```

---

## 📁 步驟 1: 建立專案目錄

### Windows
```cmd
cd C:\Users\%USERNAME%\Documents
mkdir "nbu ai"
cd "nbu ai"
```

### macOS
```bash
cd ~/Documents
mkdir "nbu ai"
cd "nbu ai"
```

---

## 📥 步驟 2: 下載專案檔案

### 方法 A: 從 GitHub 下載（推薦）⭐

#### Windows

**使用瀏覽器**:
1. 前往 https://github.com/rock4andruw/nbu-policy-llm
2. 點擊綠色的 "Code" 按鈕
3. 選擇 "Download ZIP"
4. 解壓縮到 `C:\Users\你的使用者名稱\Documents\nbu ai`

**使用 Git**（如果已安裝）:
```cmd
cd C:\Users\%USERNAME%\Documents
git clone https://github.com/rock4andruw/nbu-policy-llm.git "nbu ai"
```

#### macOS

**使用終端機**:
```bash
cd ~/Documents
git clone https://github.com/rock4andruw/nbu-policy-llm.git "nbu ai"
cd "nbu ai"
```

**使用瀏覽器**:
1. 前往 https://github.com/rock4andruw/nbu-policy-llm
2. 點擊 "Code" → "Download ZIP"
3. 解壓縮到 `~/Documents/nbu ai`

---

### 方法 B: 手動下載核心檔案

如果無法使用 Git，只下載必要檔案：

#### 🔴 必要檔案（4 個）

從 GitHub 手動下載：

1. **Windows**: `process_local_json.bat`  
   **macOS**: `process_local_json.sh`  
   → https://github.com/rock4andruw/nbu-policy-llm

2. **generate_final_csv_complete.py**  
   → 點擊 "Raw" 按鈕，另存新檔

3. **retention_level.json**  
   → ⚠️ **未在 GitHub 上**（包含公司資料）  
   → 需要從舊電腦、同事或內部共享資料夾取得

#### 🟡 建議檔案（4 個）

4. **README.md** - 專案說明
5. **NBU_SERVER_COMMANDS.md** - NBU Server 操作指南  
6. **USAGE_WORKFLOW.md** - 使用流程
7. **llm_system_prompt.md** - 知識庫 System Prompt

---

## 📂 步驟 3: 驗證檔案結構

### Windows
```cmd
cd "C:\Users\%USERNAME%\Documents\nbu ai"
dir
```

### macOS
```bash
cd ~/Documents/nbu\ ai
ls -la
```

應該至少有以下檔案：

```
nbu ai/
├── process_local_json.bat          ✅ Windows 使用
├── process_local_json.sh           ✅ macOS 使用
├── generate_final_csv_complete.py  ✅ 必要
├── retention_level.json            ✅ 必要（需另外取得）
├── README.md                       ⭐ 建議
├── NBU_SERVER_COMMANDS.md         ⭐ 建議
├── USAGE_WORKFLOW.md              ⭐ 建議
└── llm_system_prompt.md           ⭐ 建議
```

---

## 🔧 步驟 4: 設定執行權限（僅 macOS）

### macOS

```bash
cd ~/Documents/nbu\ ai
chmod +x process_local_json.sh
```

### Windows

不需要額外設定，`.bat` 檔案可直接執行。

---

## 🧪 步驟 5: 測試環境

### Windows
```cmd
cd "C:\Users\%USERNAME%\Documents\nbu ai"

REM 測試 Python
python --version

REM 測試腳本語法
python -m py_compile generate_final_csv_complete.py
```

### macOS
```bash
cd ~/Documents/nbu\ ai

# 測試 Python
python3 --version

# 測試腳本語法
python3 -m py_compile generate_final_csv_complete.py
```

如果沒有錯誤訊息，環境設定完成！✅

---

## 📥 步驟 6: 從 NBU Server 取得資料

### 6.1 在 NBU Server 上執行

詳細說明請參考 [NBU_SERVER_COMMANDS.md](NBU_SERVER_COMMANDS.md)

```bash
# 在 NetBackup Master Server (Linux) 上執行
cd /tmp
bppllist -allpolicies -json > policies.json
/usr/openv/netbackup/bin/admincmd/nbstlutil list -slp -json > slp.json
```

### 6.2 傳輸到你的電腦

#### Windows

**方法 1: 使用 WinSCP**
1. 下載安裝 WinSCP: https://winscp.net/
2. 連線到 NBU Server（主機、帳號、密碼）
3. 導航到 `/tmp` 目錄
4. 拖拽 `policies.json` 和 `slp.json` 到本機專案目錄

**方法 2: 使用 PSCP**（PuTTY 命令列工具）
```cmd
cd "C:\Users\%USERNAME%\Documents\nbu ai"
pscp root@nbu-server:/tmp/policies.json .
pscp root@nbu-server:/tmp/slp.json .
```

#### macOS

```bash
cd ~/Documents/nbu\ ai

# 使用 SCP 下載
scp root@nbu-server:/tmp/policies.json ./
scp root@nbu-server:/tmp/slp.json ./

# 驗證
ls -lh policies.json slp.json
```

---

## ▶️ 步驟 7: 執行處理

### Windows

**方法 1: 雙擊執行（推薦）**

直接雙擊 `process_local_json.bat`

**方法 2: 命令列執行**
```cmd
cd "C:\Users\%USERNAME%\Documents\nbu ai"
process_local_json.bat
```

### macOS

```bash
cd ~/Documents/nbu\ ai
./process_local_json.sh
```

---

## ✅ 步驟 8: 驗證輸出

執行成功後會產生：

```
✅ policies_llm_final.csv         知識庫 CSV 檔案
✅ backups/                       備份目錄（如有舊檔）
```

### Windows
```cmd
REM 檢查檔案
dir policies_llm_final.csv

REM 查看前幾行
type policies_llm_final.csv | more
```

### macOS
```bash
# 檢查檔案
ls -lh policies_llm_final.csv

# 查看前幾行
head -5 policies_llm_final.csv
```

---

## 📤 步驟 9: 上傳到知識庫

1. 將 `policies_llm_final.csv` 上傳到公司知識庫平台
2. 設定 System Prompt（使用 `llm_system_prompt.md` 的內容）
3. 測試查詢功能

詳細說明請參考 [USER_GUIDE.md](USER_GUIDE.md)

---

## 🔍 常見問題排除

### 問題 1: 找不到 Python

#### Windows
**錯誤訊息**: `'python' 不是內部或外部命令...`

**解決方法**:
1. 重新安裝 Python，**務必勾選** "Add Python to PATH"
2. 或手動加入環境變數：
   - 搜尋「環境變數」→ 編輯系統變數 PATH
   - 加入：`C:\Python311\` 和 `C:\Python311\Scripts\`

#### macOS
**錯誤訊息**: `command not found: python3`

**解決方法**:
```bash
# 使用 Homebrew 安裝
brew install python3

# 確認安裝路徑
which python3
```

---

### 問題 2: 找不到 retention_level.json

**錯誤訊息**: 
- Windows: `[錯誤] 找不到 retention_level.json`
- macOS: `[✗] 找不到 retention_level.json`

**原因**: 此檔案包含公司內部資料，未上傳到 GitHub

**解決方法**:
- 從舊電腦複製
- 跟同事索取
- 從公司內部共享資料夾取得
- 聯絡 NetBackup 管理員

---

### 問題 3: 找不到 policies.json 或 slp.json

**原因**: 這兩個檔案需要從 NBU Server 導出

**解決方法**:
1. 參考步驟 6 和 [NBU_SERVER_COMMANDS.md](NBU_SERVER_COMMANDS.md)
2. 在 NBU Server 上執行導出命令
3. 使用 SCP/WinSCP 傳輸到本機

---

### 問題 4: CSV 生成失敗

**檢查 JSON 格式**:

#### Windows
```cmd
python -m json.tool policies.json > nul
python -m json.tool slp.json > nul
```

#### macOS
```bash
python3 -m json.tool policies.json > /dev/null
python3 -m json.tool slp.json > /dev/null
```

如果顯示錯誤，需要重新從 NBU Server 導出。

---

### 問題 5: 權限錯誤（macOS）

**錯誤訊息**: `Permission denied: ./process_local_json.sh`

**解決方法**:
```bash
chmod +x process_local_json.sh
./process_local_json.sh
```

---

## 📋 完整檢查清單

設定完成後，確認以下項目：

### 通用檢查
- [ ] Python 3.x 已安裝
- [ ] 專案目錄已建立
- [ ] 核心檔案已下載（bat/sh + py）
- [ ] retention_level.json 已取得
- [ ] policies.json 已從 NBU Server 取得
- [ ] slp.json 已從 NBU Server 取得

### Windows 專用
- [ ] Python 已加入 PATH
- [ ] process_local_json.bat 可執行

### macOS 專用
- [ ] process_local_json.sh 有執行權限
- [ ] 使用 python3 命令（不是 python）

### 執行驗證
- [ ] 執行處理腳本成功
- [ ] policies_llm_final.csv 已產生
- [ ] CSV 有 30 個欄位
- [ ] 資料筆數正常（> 1000 筆）

---

## 🎯 快速參考

### Windows 完整流程

```cmd
REM 1. 建立目錄
cd C:\Users\%USERNAME%\Documents
mkdir "nbu ai"
cd "nbu ai"

REM 2. 下載檔案（從 GitHub 或手動）

REM 3. 從 NBU Server 取得 JSON（使用 WinSCP）

REM 4. 執行處理
process_local_json.bat

REM 5. 檢查輸出
dir policies_llm_final.csv
```

### macOS 完整流程

```bash
# 1. 建立目錄
cd ~/Documents
mkdir "nbu ai"
cd "nbu ai"

# 2. 下載專案
git clone https://github.com/rock4andruw/nbu-policy-llm.git .

# 3. 設定權限
chmod +x process_local_json.sh

# 4. 從 NBU Server 取得 JSON
scp root@nbu-server:/tmp/policies.json ./
scp root@nbu-server:/tmp/slp.json ./

# 5. 執行處理
./process_local_json.sh

# 6. 檢查輸出
ls -lh policies_llm_final.csv
```

---

## 📚 延伸閱讀

- [README.md](README.md) - 專案概述
- [NBU_SERVER_COMMANDS.md](NBU_SERVER_COMMANDS.md) - NBU Server 操作詳解
- [USAGE_WORKFLOW.md](USAGE_WORKFLOW.md) - 完整工作流程
- [USER_GUIDE.md](USER_GUIDE.md) - 知識庫使用指南

---

## 📞 需要協助？

如果遇到問題：
1. 檢查本文的「常見問題排除」
2. 查看 [USAGE_WORKFLOW.md](USAGE_WORKFLOW.md) 的除錯章節
3. 聯絡 NetBackup 管理員或專案維護者

---

**最後更新**: 2026-05-27  
**維護者**: NetBackup Team
