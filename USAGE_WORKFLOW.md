# NetBackup Policy 知識庫 - 實際使用流程

**版本**: 1.0  
**日期**: 2026-05-27  
**適用**: NetBackup 10.x

---

## 📋 完整工作流程

```
┌─────────────────┐
│  NetBackup      │
│  Master Server  │
└────────┬────────┘
         │ 1. 導出 JSON
         ▼
┌─────────────────┐
│  policies.json  │
│  slp.json       │
└────────┬────────┘
         │ 2. 自動處理
         ▼
┌─────────────────┐
│ Python 腳本     │
│ 生成 CSV        │
└────────┬────────┘
         │ 3. 產出
         ▼
┌─────────────────┐
│policies_llm     │
│_final.csv       │
└────────┬────────┘
         │ 4. 手動上傳
         ▼
┌─────────────────┐
│  公司知識庫     │
│  (Vertex AI等)  │
└─────────────────┘
```

---

## 🚀 快速開始（本地處理）

### 實際工作流程

```
NBU Server → 導出 JSON → 傳輸到 Client → 本地處理 → 手動上傳知識庫
```

### 步驟 1: 在 NBU Server 導出資料

在 **NetBackup Master Server** 上執行：

```bash
cd /tmp
bppllist -allpolicies -json > policies.json
/usr/openv/netbackup/bin/admincmd/nbstlutil list -slp -json > slp.json
```

### 步驟 2: 傳輸到 Client 端

**macOS**:
```bash
cd "/Users/andruw/Documents/nbu ai"
scp root@nbu-server:/tmp/policies.json ./
scp root@nbu-server:/tmp/slp.json ./
```

**Windows**: 使用 WinSCP 或 FileZilla 下載兩個 JSON 檔案

### 步驟 3: 本地處理（推薦）⭐

**macOS/Linux**:
```bash
cd "/Users/andruw/Documents/nbu ai"
./process_local_json.sh
```

**Windows**:
```cmd
cd "C:\Users\YourName\Documents\nbu ai"
process_local_json.bat
```

**腳本會自動完成**：
1. ✅ 檢查必要檔案（policies.json, slp.json, retention_level.json）
2. ✅ 備份舊的 CSV 檔案
3. ✅ 執行 Python 腳本生成 CSV
4. ✅ 驗證輸出結果

**輸出結果**：
- `policies_llm_final.csv` - 可直接上傳到知識庫
- 舊檔案備份在 `backups/` 目錄

---

## 📖 詳細步驟說明

### 方法 2: 手動執行（逐步操作）

如果需要更細緻的控制，可以手動執行每個步驟。

#### 步驟 1: 從 NetBackup 導出資料

##### 1.1 導出 Policies

**在 NetBackup Master Server 上執行**：

```bash
# 方法 A: 直接在 NBU Server 上執行
bppllist -allpolicies -json > policies.json

# 方法 B: 透過 SSH 遠端執行
ssh root@bksvr.company.com "bppllist -allpolicies -json" > policies.json
```

**輸出**：
- `policies.json` (約 5-10 MB)
- 包含所有 Policy 的完整配置

##### 1.2 導出 SLP (Storage Lifecycle Policies)

```bash
# 方法 A: 直接在 NBU Server 上執行
/usr/openv/netbackup/bin/admincmd/nbstlutil list -slp -json > slp.json

# 方法 B: 透過 SSH 遠端執行
ssh root@bksvr.company.com "/usr/openv/netbackup/bin/admincmd/nbstlutil list -slp -json" > slp.json
```

**輸出**：
- `slp.json` (約 200-500 KB)
- 包含所有 SLP 的配置

##### 1.3 傳輸檔案（如果在遠端執行）

```bash
# 從遠端伺服器複製到本地
scp root@bksvr.company.com:/path/to/policies.json ./
scp root@bksvr.company.com:/path/to/slp.json ./
```

#### 步驟 2: 生成知識庫 CSV

**在本地執行**：

```bash
# 確認檔案存在
ls -lh policies.json slp.json retention_level.json

# 執行 Python 腳本
python3 generate_final_csv_complete.py
```

**輸出資訊範例**：
```
================================================================================
✅ 最終版本：完整保留 Policy + SLP 資訊 + 自動判定邏輯
================================================================================

🔄 載入資料...
   ✅ Policies: 634
   ✅ SLPs: 163
   ✅ Retention Levels: 103

📝 生成完整資料（所有 634 個 policies）...
   ✅ 生成 1429 筆資料

💾 CSV 已儲存: policies_llm_final.csv
   欄位數: 30
   資料筆數: 1429

📊 Retention Source 分佈:
   Policy: 125 筆 (8.7%)
   SLP: 1304 筆 (91.3%)
```

#### 步驟 3: 驗證輸出

```bash
# 檢查檔案大小和行數
wc -l policies_llm_final.csv
ls -lh policies_llm_final.csv

# 查看前 5 行
head -5 policies_llm_final.csv | column -t -s ','

# 驗證欄位數量（應為 30 個）
head -1 policies_llm_final.csv | awk -F',' '{print NF}'
```

#### 步驟 4: 上傳到知識庫

根據你公司使用的平台選擇：

##### A. Vertex AI

```bash
# 1. 上傳到 Cloud Storage
gsutil cp policies_llm_final.csv gs://your-company-kb/

# 2. 在 Vertex AI 中建立資料存放區
# - 登入 Google Cloud Console
# - Vertex AI → Search → 建立資料存放區
# - 選擇 Cloud Storage 路徑

# 3. 設定 System Prompt
# - 複製 llm_system_prompt.md 的內容
# - 貼到 Vertex AI 的 Prompt 設定
```

##### B. 其他內部平台

根據你公司的知識庫平台文檔上傳 CSV 檔案。

---

## ⏰ 定期更新流程

### 建議更新頻率

- **每週更新**: 如果 Policy 變更頻繁
- **每月更新**: 一般維護情況
- **重大變更後**: 新增/刪除大量 Policy 時

### 自動化排程（可選）

使用 cron 定期執行：

```bash
# 編輯 crontab
crontab -e

# 每週一早上 6 點執行
0 6 * * 1 /Users/andruw/Documents/nbu\ ai/nbu_export_and_process.sh bksvr.company.com >> /tmp/nbu_export.log 2>&1

# 每月 1 號執行
0 6 1 * * /Users/andruw/Documents/nbu\ ai/nbu_export_and_process.sh bksvr.company.com >> /tmp/nbu_export.log 2>&1
```

---

## 🔍 驗證與除錯

### 驗證清單

執行完成後，檢查以下項目：

```bash
# 1. 檢查檔案存在
[ -f policies_llm_final.csv ] && echo "✅ CSV 存在" || echo "❌ CSV 不存在"

# 2. 檢查行數（應 > 1000）
LINES=$(wc -l < policies_llm_final.csv)
[ $LINES -gt 1000 ] && echo "✅ 行數正常: $LINES" || echo "⚠️  行數異常: $LINES"

# 3. 檢查欄位數量（應為 30）
FIELDS=$(head -1 policies_llm_final.csv | awk -F',' '{print NF}')
[ $FIELDS -eq 30 ] && echo "✅ 欄位數正確: $FIELDS" || echo "⚠️  欄位數異常: $FIELDS"

# 4. 檢查 retention_source 分佈
echo "📊 Retention Source 分佈:"
python3 << 'EOF'
import csv
with open('policies_llm_final.csv', 'r') as f:
    reader = csv.DictReader(f)
    data = list(reader)
    sources = {}
    for row in data:
        src = row['retention_source']
        sources[src] = sources.get(src, 0) + 1
    for src, count in sources.items():
        print(f"   {src}: {count} ({count/len(data)*100:.1f}%)")
EOF
```

### 常見問題排除

#### 問題 1: bppllist 命令找不到

**錯誤**：
```
bash: bppllist: command not found
```

**解決方法**：
```bash
# 檢查 NetBackup 安裝路徑
ls -la /usr/openv/netbackup/bin/admincmd/

# 使用完整路徑
/usr/openv/netbackup/bin/admincmd/bppllist -allpolicies -json > policies.json
```

#### 問題 2: JSON 格式錯誤

**錯誤**：
```
JSONDecodeError: Expecting value
```

**解決方法**：
```bash
# 檢查 JSON 是否有效
python3 -m json.tool policies.json > /dev/null && echo "✅ JSON 有效" || echo "❌ JSON 無效"

# 如果無效，重新導出
bppllist -allpolicies -json > policies.json
```

#### 問題 3: CSV 行數異常

**問題**：CSV 只有幾十行

**檢查**：
```bash
# 檢查 policies.json
python3 -c "import json; print(len(json.load(open('policies.json'))['policies']))"

# 應該顯示數百個 policies
```

---

## 📊 輸出檔案說明

### policies_llm_final.csv

**格式**: UTF-8 CSV  
**欄位數**: 30  
**記錄數**: 約 1,400+ (取決於 Policy 數量)

**欄位分類**：
1. 基本資訊 (7 欄位)
2. 排程資訊 (4 欄位)
3. ⭐ 最終保留資訊 (4 欄位) - LLM 優先使用
4. Policy 保留資訊 (3 欄位)
5. SLP 保留資訊 (6 欄位)
6. 其他資訊 (6 欄位)

**重要欄位**：
- `final_retention_label`: 保留期限中文標籤（如"保留 1 週"）
- `retention_source`: 來源（SLP 或 Policy）
- `policy_name`: 策略名稱
- `client_hostname`: 客戶端主機

### 備份檔案

自動備份在 `backups/` 目錄：
```
backups/
├── policies.json_20260527_153045
├── slp.json_20260527_153045
└── policies_llm_final.csv_20260527_153045
```

---

## 🎯 使用範例

上傳到知識庫後的查詢範例：

### 範例 1: 查詢保留期限
```
Q: "21C_MSSQL_Online_21sunlike 的備份保留多久？"
A: 保留 1 週（來自 SLP: 1_Daily_04）
```

### 範例 2: 查詢特定主機
```
Q: "bksvr 這台主機有哪些備份策略？"
A: 列出所有 client_hostname = bksvr 的策略
```

### 範例 3: 查詢時間排程
```
Q: "哪些策略在凌晨 3 點執行？"
A: 列出所有 backup_time 包含 03:00 的策略
```

---

## 📝 維護記錄

建議保留執行記錄：

```bash
# 建立執行日誌
cat > execution_log.txt << EOF
執行日期: $(date)
NBU Server: bksvr.company.com
Policies: $(python3 -c "import json; print(len(json.load(open('policies.json'))['policies']))")
輸出行數: $(wc -l < policies_llm_final.csv)
檔案大小: $(du -h policies_llm_final.csv | cut -f1)
執行者: $(whoami)
EOF
```

---

## 🔗 相關資源

- [USER_GUIDE.md](USER_GUIDE.md) - 完整使用說明
- [llm_system_prompt.md](llm_system_prompt.md) - LLM System Prompt
- [README.md](README.md) - 專案說明
- [tests/README.md](tests/README.md) - 測試說明

---

## 📧 支援

如遇問題：
1. 查看錯誤訊息
2. 檢查驗證清單
3. 參考常見問題排除
4. 聯絡 NetBackup 管理員

---

**最後更新**: 2026-05-27  
**維護者**: NetBackup Team
