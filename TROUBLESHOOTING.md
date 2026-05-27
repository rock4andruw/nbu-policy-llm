# 常見問題排除指南

**適用於**: NetBackup Policy LLM 專案  
**版本**: 1.0

---

## 🔴 路徑相關問題

### 問題 1: FileNotFoundError - 找不到檔案

**錯誤訊息**:
```
FileNotFoundError: [Errno 2] No such file or directory: '/Users/andruw/Documents/nbu ai/policies.json'
```

#### 原因

Python 腳本使用了硬編碼路徑，不同使用者的路徑不同。

#### 解決方法 ✅

**最新版本已修正**！請確認你使用的是最新版 `generate_final_csv_complete.py`。

最新版本會自動使用腳本所在目錄，支援任何使用者路徑：
- ✅ `/Users/andruw/Documents/nbu ai/` - 開發者路徑
- ✅ `/Users/john/Documents/nbu ai/` - 其他使用者
- ✅ `C:\Users\Mary\Documents\nbu ai\` - Windows 使用者

#### 手動確認

```bash
# 檢查 Python 腳本版本（應包含 import os）
head -15 generate_final_csv_complete.py

# 應該看到：
# import os
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
```

#### 如果還是失敗

確認你在正確的目錄執行：

**macOS/Linux**:
```bash
# 切換到專案目錄
cd ~/Documents/nbu\ ai

# 確認必要檔案存在
ls -lh policies.json slp.json retention_level.json

# 執行
python3 generate_final_csv_complete.py
```

**Windows**:
```cmd
REM 切換到專案目錄
cd "C:\Users\你的使用者名稱\Documents\nbu ai"

REM 確認必要檔案存在
dir policies.json slp.json retention_level.json

REM 執行
python generate_final_csv_complete.py
```

---

## 🔴 檔案缺失問題

### 問題 2: 找不到 policies.json 或 slp.json

**錯誤訊息**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'policies.json'
```

#### 原因

這兩個檔案需要從 NBU Server 導出，不包含在 Git 專案中。

#### 解決方法 ✅

**步驟 1: 在 NBU Server 上導出**

```bash
# SSH 登入 NetBackup Master Server
ssh root@your-nbu-server.company.com

cd /tmp

# 導出 policies
bppllist -allpolicies -json > policies.json

# 導出 SLP
/usr/openv/netbackup/bin/admincmd/nbstlutil list -slp -json > slp.json

# 確認檔案
ls -lh policies.json slp.json
```

**步驟 2: 傳輸到本機**

**macOS/Linux**:
```bash
cd ~/Documents/nbu\ ai
scp root@your-nbu-server:/tmp/policies.json ./
scp root@your-nbu-server:/tmp/slp.json ./
```

**Windows**: 使用 WinSCP 或 FileZilla 下載

詳細說明: [NBU_SERVER_COMMANDS.md](NBU_SERVER_COMMANDS.md)

---

### 問題 3: 找不到 retention_level.json

**錯誤訊息**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'retention_level.json'
```

#### 原因

此檔案包含公司內部資料，未上傳到 GitHub。

#### 解決方法 ✅

**選項 1: 從舊電腦複製**
```bash
# 從舊電腦或同事的電腦複製
scp user@old-computer:~/Documents/nbu\ ai/retention_level.json ./
```

**選項 2: 從共享資料夾取得**

詢問 NetBackup 管理員或團隊成員取得此檔案。

**選項 3: 從 Git 歷史恢復**（如果之前有提交）

⚠️ 注意：此檔案可能包含敏感資料，已從 Git 移除。

---

## 🔴 Python 相關問題

### 問題 4: 找不到 Python

**錯誤訊息**:

**Windows**:
```
'python' 不是內部或外部命令、可執行的程式或批次檔。
```

**macOS**:
```
command not found: python3
```

#### 解決方法 ✅

**Windows**:
1. 前往 https://www.python.org/downloads/
2. 下載並安裝 Python 3.x
3. ⚠️ **重要**: 安裝時勾選 "Add Python to PATH"
4. 重新開啟命令提示字元
5. 驗證: `python --version`

**macOS**:
```bash
# 使用 Homebrew 安裝
brew install python3

# 或從官網下載
# https://www.python.org/downloads/macos/
```

---

### 問題 5: JSON 格式錯誤

**錯誤訊息**:
```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

#### 原因

JSON 檔案可能：
- 是空檔案
- 格式不正確
- 下載不完整

#### 解決方法 ✅

**驗證 JSON 格式**:

**macOS/Linux**:
```bash
# 檢查檔案大小
ls -lh policies.json slp.json

# 檢查 JSON 格式
python3 -m json.tool policies.json > /dev/null
python3 -m json.tool slp.json > /dev/null

# 查看前幾行
head -20 policies.json
```

**Windows**:
```cmd
REM 檢查檔案大小
dir policies.json slp.json

REM 檢查 JSON 格式
python -m json.tool policies.json > nul
python -m json.tool slp.json > nul
```

**如果格式錯誤**: 重新從 NBU Server 導出

---

## 🔴 執行權限問題

### 問題 6: Permission denied（僅 macOS/Linux）

**錯誤訊息**:
```
-bash: ./process_local_json.sh: Permission denied
```

#### 解決方法 ✅

```bash
# 給予執行權限
chmod +x process_local_json.sh

# 再次執行
./process_local_json.sh
```

---

## 🔴 輸出問題

### 問題 7: CSV 檔案異常

**症狀**:
- CSV 只有幾行
- CSV 欄位數不對
- CSV 沒有資料

#### 檢查步驟

**1. 確認 CSV 行數**:

```bash
# macOS/Linux
wc -l policies_llm_final.csv
# 應該 > 1000

# Windows
find /c /v "" policies_llm_final.csv
```

**2. 確認欄位數**:

```bash
# macOS/Linux
head -1 policies_llm_final.csv | awk -F',' '{print NF}'
# 應該是 30

# Windows
# 用 Excel 開啟檢查
```

**3. 檢查原始資料**:

```bash
# 確認 policies.json 有資料
python3 -c "import json; print(len(json.load(open('policies.json'))['policies']))"
# 應該顯示數百個
```

---

## 🔴 編碼問題

### 問題 8: 中文亂碼

**症狀**: CSV 中的中文顯示為亂碼

#### 解決方法 ✅

**使用正確的編輯器開啟**:
- ✅ VS Code（設定 UTF-8）
- ✅ Sublime Text（設定 UTF-8）
- ⚠️ Excel（可能需要匯入而非直接開啟）

**Excel 正確開啟方式**:
1. 開啟 Excel
2. 資料 → 從文字/CSV
3. 選擇 `policies_llm_final.csv`
4. 檔案原始格式：**65001: Unicode (UTF-8)**
5. 匯入

---

## 🔴 環境問題

### 問題 9: 多個 Python 版本衝突

**症狀**: 執行時找不到模組或版本不對

#### 解決方法 ✅

**確認使用的 Python 版本**:

```bash
# macOS/Linux
which python3
python3 --version

# Windows
where python
python --version
```

**使用絕對路徑執行**:

```bash
# 使用特定版本
/usr/local/bin/python3 generate_final_csv_complete.py

# Windows
C:\Python311\python.exe generate_final_csv_complete.py
```

---

## 📞 取得協助

如果以上方法都無法解決問題：

1. **檢查日誌**: 完整的錯誤訊息
2. **確認環境**:
   ```bash
   python3 --version
   pwd  # 或 Windows: cd
   ls -la  # 或 Windows: dir
   ```
3. **參考文檔**:
   - [SETUP.md](SETUP.md) - 設定指南
   - [USAGE_WORKFLOW.md](USAGE_WORKFLOW.md) - 使用流程
   - [NBU_SERVER_COMMANDS.md](NBU_SERVER_COMMANDS.md) - NBU 操作
4. **聯絡**:
   - NetBackup 管理員
   - 專案維護者
   - 團隊成員

---

## 🔧 環境診斷腳本

快速診斷環境問題：

**macOS/Linux**:
```bash
#!/bin/bash
echo "=== 環境診斷 ==="
echo "Python 版本:"
python3 --version
echo -e "\n當前目錄:"
pwd
echo -e "\n必要檔案:"
ls -lh policies.json slp.json retention_level.json generate_final_csv_complete.py 2>&1
echo -e "\n磁碟空間:"
df -h . | tail -1
```

**Windows**:
```cmd
@echo off
echo === 環境診斷 ===
echo Python 版本:
python --version
echo.
echo 當前目錄:
cd
echo.
echo 必要檔案:
dir policies.json slp.json retention_level.json generate_final_csv_complete.py
echo.
echo 磁碟空間:
dir
```

---

**最後更新**: 2026-05-27  
**維護者**: NetBackup Team
