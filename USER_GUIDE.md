# NetBackup Policy LLM 知識庫 - 使用說明

**版本**: 1.0.0  
**最後更新**: 2026-05-27  
**適用平台**: Vertex AI, LangChain, LlamaIndex 等支援 CSV 的 RAG 平台

---

## 📖 目錄

1. [專案簡介](#專案簡介)
2. [快速開始](#快速開始)
3. [核心檔案說明](#核心檔案說明)
4. [資料結構](#資料結構)
5. [使用 Vertex AI](#使用-vertex-ai)
6. [使用其他平台](#使用其他平台)
7. [查詢範例](#查詢範例)
8. [維護與更新](#維護與更新)
9. [常見問題](#常見問題)
10. [技術支援](#技術支援)

---

## 專案簡介

### 目標
將 NetBackup 10.1.1 的 634 個備份策略轉換為 LLM 可查詢的知識庫，支援自然語言查詢備份配置、保留期限、排程時間等資訊。

### 特色
- ✅ **完整整合**: Policy + SLP + Retention Level 三種資料
- ✅ **智能判定**: 自動判定保留天數來源（SLP 或 Policy）
- ✅ **中文支援**: 保留期限顯示中文標籤（如"保留 1 週"）
- ✅ **特殊處理**: 正確處理 DataDomain 等直接儲存配置
- ✅ **平台友善**: CSV 格式，支援主流 RAG 平台

### 統計資料
- **策略數量**: 634 個 policies
- **資料筆數**: 1,429 行（每個 schedule × client 一筆）
- **欄位數量**: 30 個欄位
- **SLP 覆蓋率**: 91.3% (1,304/1,429)
- **直接儲存配置**: 8.7% (125/1,429)

---

## 快速開始

### 步驟 1: 準備檔案

確認以下檔案存在：

```bash
cd "/Users/andruw/Documents/nbu ai"
ls -lh policies_llm_final.csv llm_system_prompt.md
```

**預期輸出**:
```
-rw-r--r--  1 andruw  staff   500K May 27 xx:xx policies_llm_final.csv
-rw-r--r--  1 andruw  staff    15K May 27 xx:xx llm_system_prompt.md
```

### 步驟 2: 檢視資料

**查看前 5 筆資料**:
```bash
head -6 policies_llm_final.csv | column -t -s ','
```

**統計筆數**:
```bash
wc -l policies_llm_final.csv
# 預期輸出: 1430 (含標題行)
```

### 步驟 3: 部署到 LLM 平台

選擇以下任一平台：
- [Vertex AI](#使用-vertex-ai) (推薦)
- [LangChain](#使用-langchain)
- [LlamaIndex](#使用-llamaindex)

---

## 核心檔案說明

### 1. policies_llm_final.csv ⭐
**用途**: 主要知識庫檔案  
**大小**: ~500KB  
**筆數**: 1,429 行  
**編碼**: UTF-8

**欄位結構**: 30 個欄位，分為 6 大類
- 基本資訊 (7)
- 排程資訊 (4)
- 最終保留資訊 (4) ← **LLM 應優先使用**
- Policy 保留資訊 (3)
- SLP 保留資訊 (6)
- 其他資訊 (6)

### 2. llm_system_prompt.md ⭐
**用途**: LLM System Prompt 設定  
**重點內容**:
- 角色定義
- 欄位說明
- 回答指南（含正確/錯誤範例）
- 實際對話範例
- 術語解釋

**使用方式**: 將此檔案內容複製到 LLM 平台的 System Prompt 欄位

### 3. generate_final_csv_complete.py
**用途**: CSV 生成腳本  
**功能**:
- 整合三種資料來源
- 實作判定邏輯
- 轉換保留期限為中文

**重新生成資料**:
```bash
python3 generate_final_csv_complete.py
```

### 4. storage_unit_groups_info.md
**用途**: Storage Unit Groups 補充說明  
**內容**: 8 個 Storage Unit Groups 的詳細資訊、使用統計、架構分析

---

## 資料結構

### 欄位清單（30 個）

#### 基本資訊 (7)
| 欄位名稱 | 說明 | 範例 |
|---------|------|------|
| document_type | 文件類型 | NetBackup Policy |
| policy_name | 策略名稱 | 21C_MSSQL_Online_21sunlike |
| policy_type | 策略類型 | MS-SQL-Server |
| status | 狀態 | Active / Inactive |
| client_hostname | 客戶端主機 | 21sunlike-bk |
| client_os | 作業系統 | Windows-x64 |
| storage_residence_name | 儲存位置 | 1_Daily_04 |

#### 排程資訊 (4)
| 欄位名稱 | 說明 | 範例 |
|---------|------|------|
| schedule_name | 排程名稱 | Daily_Full |
| schedule_type | 排程類型 | Full Backup |
| frequency_text | 頻率 | 每天 |
| backup_time | 時間窗口 | 每天 03:00~07:00 |

#### ⭐ 最終保留資訊 (4) - LLM 優先使用
| 欄位名稱 | 說明 | 範例 | 優先級 |
|---------|------|------|--------|
| retention_source | 來源 | SLP / Policy | 參考 |
| final_retention_level | 最終等級 | Level 0 | 參考 |
| final_retention_period | 期限(英) | 1 week | 次要 |
| final_retention_label | 期限(中) | 保留 1 週 | **⭐ 最優先** |

#### Policy 保留資訊 (3) - 詳細資訊
| 欄位名稱 | 說明 |
|---------|------|
| policy_retention_level | Policy 等級 |
| policy_retention_period | Policy 期限(英) |
| policy_retention_label | Policy 期限(中) |

#### SLP 保留資訊 (6) - 詳細資訊
| 欄位名稱 | 說明 |
|---------|------|
| slp_name | SLP 名稱 |
| slp_retention_level | SLP 等級 |
| slp_retention_type | SLP 類型 (FIXED/CAPACITY) |
| slp_actual_storage | 實際儲存位置 |
| slp_retention_period | SLP 期限(英) |
| slp_retention_label | SLP 期限(中) |

#### 其他資訊 (6)
| 欄位名稱 | 說明 |
|---------|------|
| storage_pool | 儲存池 |
| backup_paths | 備份路徑（分號分隔） |
| features | 特殊功能（壓縮、加密等） |
| search_keywords | 搜尋關鍵字 |
| query_examples | 範例問題 |
| generation_date | 資料生成日期 |

---

## 使用 Vertex AI

### 步驟 1: 建立 Vertex AI Search 資料存放區

1. 前往 **Google Cloud Console** → **Vertex AI Search**
2. 點擊「建立資料存放區」
3. 選擇資料類型：**「非結構化文件」**
4. 資料來源：**「Cloud Storage」** 或 **「本機上傳」**

### 步驟 2: 上傳 CSV

**方法 A: 使用 Cloud Storage**
```bash
# 1. 建立 bucket (如果沒有)
gsutil mb gs://your-netbackup-kb/

# 2. 上傳 CSV
gsutil cp policies_llm_final.csv gs://your-netbackup-kb/

# 3. 在 Vertex AI 中指定 bucket 路徑
```

**方法 B: 直接上傳**
- 在 Vertex AI 介面中選擇「上傳檔案」
- 選擇 `policies_llm_final.csv`

### 步驟 3: 設定 System Prompt

1. 建立 Vertex AI Agent Builder 應用程式
2. 在「Prompt 設定」中貼上 `llm_system_prompt.md` 的內容
3. 調整以下設定：
   - **Temperature**: 0.2 (較精確)
   - **Max Output Tokens**: 1024
   - **Top P**: 0.95

### 步驟 4: 測試查詢

測試以下問題：
```
1. "21C_MSSQL_Online_21sunlike 的備份保留多久？"
   預期: 保留 1 週

2. "PIC_NBU_Catalog_Online_bksvr_datadomain 使用什麼儲存？"
   預期: 03_DataDomain_group，保留 1 週

3. "哪些策略在凌晨 3 點執行？"
   預期: 列出多個策略
```

---

## 使用其他平台

### LangChain

```python
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

# 1. 載入 CSV
loader = CSVLoader(
    file_path='policies_llm_final.csv',
    encoding='utf-8'
)
documents = loader.load()

# 2. 建立向量資料庫
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(documents, embeddings)

# 3. 建立 QA Chain
llm = ChatOpenAI(model_name="gpt-4", temperature=0.2)
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    chain_type="stuff"
)

# 4. 查詢
question = "21C_MSSQL_Online_21sunlike 的備份保留多久？"
answer = qa_chain.run(question)
print(answer)
```

### LlamaIndex

```python
from llama_index import SimpleDirectoryReader, VectorStoreIndex
from llama_index.readers import CSVReader

# 1. 載入 CSV
documents = CSVReader().load_data(
    file='policies_llm_final.csv'
)

# 2. 建立索引
index = VectorStoreIndex.from_documents(documents)

# 3. 查詢
query_engine = index.as_query_engine()
response = query_engine.query(
    "21C_MSSQL_Online_21sunlike 的備份保留多久？"
)
print(response)
```

---

## 查詢範例

### 基礎查詢

#### 1. 查詢保留期限 ⭐ 最常見
```
Q: "21C_MSSQL_Online_21sunlike 這個策略的備份會保留多久？"
A: 保留 1 週（來自 SLP: 1_Daily_04）

Q: "PIC_NBU_Catalog_Online_bksvr_datadomain 的資料保存多久？"
A: 保留 1 週（來自 Policy，使用 03_DataDomain_group）
```

#### 2. 查詢策略配置
```
Q: "21C_WIN_DATA_21sunlike 是什麼策略？"
A: Standard 類型的備份策略，每天 03:00~07:00 執行 Full Backup，
   保留 3 個月，客戶端為 21sunlike-bk (Windows-x64)

Q: "bksvr 這台主機有哪些備份策略？"
A: [列出所有 client_hostname = bksvr 的策略]
```

#### 3. 查詢時間排程
```
Q: "哪些策略在凌晨 3 點執行？"
A: [列出 backup_time 包含 03:00 的策略]

Q: "每小時執行的備份有哪些？"
A: [列出 frequency_text = "每 1 小時" 的策略]
```

### 進階查詢

#### 4. 比較分析
```
Q: "21sunlike-bk 的 MSSQL 和檔案備份有什麼差異？"
A: [比較保留期限、排程時間、SLP 等差異]

Q: "使用 03_DataDomain_group 的策略有哪些？"
A: [列出 storage_residence_name = 03_DataDomain_group 的策略]
```

#### 5. 統計查詢
```
Q: "有多少策略保留 1 週？"
A: [統計 final_retention_label = "保留 1 週" 的數量]

Q: "MS-SQL-Server 類型的策略有幾個？"
A: [統計 policy_type = "MS-SQL-Server" 的數量]
```

#### 6. 功能查詢
```
Q: "哪些策略啟用了客戶端壓縮？"
A: [列出 features 包含 "客戶端壓縮" 的策略]

Q: "停用的策略有哪些？"
A: [列出 status = "Inactive" 的策略]
```

---

## 維護與更新

### 定期更新流程

#### 步驟 1: 從 NetBackup 導出資料
```bash
# 在 NetBackup Master Server 執行
bppllist -allpolicies -json > policies.json
/usr/openv/netbackup/bin/admincmd/nbstlutil list -slp -json > slp.json
```

#### 步驟 2: 複製到本機
```bash
scp root@netbackup-server:/path/to/policies.json ./
scp root@netbackup-server:/path/to/slp.json ./
```

#### 步驟 3: 重新生成 CSV
```bash
cd "/Users/andruw/Documents/nbu ai"
python3 generate_final_csv_complete.py
```

#### 步驟 4: 驗證資料
```bash
# 檢查筆數
wc -l policies_llm_final.csv

# 檢查 retention_source 分佈
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
        print(f"{src}: {count} ({count/len(data)*100:.1f}%)")
EOF
```

#### 步驟 5: 更新到平台
- 上傳新的 CSV 到 Vertex AI 或其他平台
- 重新索引資料
- 執行測試查詢

### 版本控制

**使用 Git 追蹤變更**:
```bash
# 提交更新
git add policies_llm_final.csv
git commit -m "Update: 重新生成 CSV (2026-05-27)"

# 檢視歷史
git log --oneline policies_llm_final.csv
```

---

## 常見問題

### Q1: 為什麼有些策略顯示 "N/A"？
**A**: 表示該欄位在 NetBackup 配置中未設定。常見情況：
- `slp_name = N/A`: 使用直接儲存配置（如 03_DataDomain_group）
- `backup_time = N/A`: 排程未設定時間窗口

### Q2: retention_source 是 "Policy" 和 "SLP" 有什麼差別？
**A**: 
- **SLP** (91.3%): 使用 Storage Lifecycle Policy 管理保留期限
- **Policy** (8.7%): 使用 Policy 本身的設定，通常是直接儲存配置（如 DataDomain）

### Q3: 為什麼需要同時保留 policy_retention_* 和 slp_retention_*？
**A**: 
- 讓用戶了解完整資訊
- 追溯判定邏輯
- 除錯和驗證

實際回答用戶時，LLM 只需使用 `final_retention_label`。

### Q4: 如何處理保留期限 "無限期"？
**A**: 
- `final_retention_label = "保留 無限期"`
- 表示備份不會自動過期，需手動刪除

### Q5: CSV 檔案可以用 Excel 開啟嗎？
**A**: 可以，但注意：
- 編碼必須是 UTF-8
- Excel 可能無法正確顯示中文（建議用 Google Sheets 或 Numbers）

### Q6: 如何新增自訂欄位？
**A**: 修改 `generate_final_csv_complete.py`:
```python
# 在 row 字典中新增欄位
row['custom_field'] = your_value
```

### Q7: 資料多久更新一次？
**A**: 建議：
- **開發環境**: 每週
- **正式環境**: 每月或當 Policy 有重大變更時

### Q8: 如何處理敏感資訊？
**A**: 
- CSV 中不包含密碼、金鑰等敏感資訊
- 如需過濾特定資料，修改生成腳本
- 部署時注意檔案權限

---

## 技術支援

### 檔案位置
```
專案目錄: /Users/andruw/Documents/nbu ai/

核心檔案:
├── policies_llm_final.csv          # 知識庫
├── llm_system_prompt.md            # System Prompt
├── generate_final_csv_complete.py  # 生成腳本
├── USER_GUIDE.md                   # 本文件
└── project_status_summary.md       # 專案彙整
```

### 相關文件
- [LLM System Prompt](llm_system_prompt.md) - 詳細的 Prompt 設定指南
- [專案彙整](project_status_summary.md) - 專案現況與技術細節
- [Storage Unit Groups 說明](storage_unit_groups_info.md) - 儲存架構說明

### 問題回報
如遇到問題，請提供：
1. 問題描述
2. 查詢語句
3. 預期結果 vs 實際結果
4. CSV 檔案版本（generation_date）

### 版本資訊
```
版本: 1.0.0
發布日期: 2026-05-27
資料來源: NetBackup 10.1.1
策略數量: 634
資料筆數: 1,429
```

---

## 附錄

### A. 完整欄位對照表

| # | 欄位名稱 | 類型 | 範例 | 用途 |
|---|---------|------|------|------|
| 1 | document_type | 固定值 | NetBackup Policy | 文件分類 |
| 2 | policy_name | 字串 | 21C_MSSQL_Online_21sunlike | 策略識別 |
| 3 | policy_type | 字串 | MS-SQL-Server | 策略類型 |
| 4 | status | Active/Inactive | Active | 啟用狀態 |
| 5 | client_hostname | 字串 | 21sunlike-bk | 客戶端識別 |
| 6 | client_os | 字串 | Windows-x64 | 作業系統 |
| 7 | storage_residence_name | 字串 | 1_Daily_04 | 儲存位置 |
| 8 | schedule_name | 字串 | Daily_Full | 排程名稱 |
| 9 | schedule_type | 字串 | Full Backup | 備份類型 |
| 10 | frequency_text | 字串 | 每天 | 執行頻率 |
| 11 | backup_time | 字串 | 每天 03:00~07:00 | 時間窗口 |
| 12 | retention_source | SLP/Policy | SLP | **來源** |
| 13 | final_retention_level | 字串 | Level 0 | **最終等級** |
| 14 | final_retention_period | 字串 | 1 week | **期限(英)** |
| 15 | final_retention_label | 字串 | 保留 1 週 | **⭐期限(中)** |
| 16-18 | policy_retention_* | - | - | Policy 詳細 |
| 19-24 | slp_* | - | - | SLP 詳細 |
| 25-30 | storage_pool, backup_paths, etc. | - | - | 其他資訊 |

### B. 保留期限對照表

| Level | 英文 | 中文 |
|-------|------|------|
| 0 | 1 week | 保留 1 週 |
| 1 | 2 weeks | 保留 2 週 |
| 2 | 3 weeks | 保留 3 週 |
| 3 | 1 month | 保留 1 個月 |
| 4 | 2 months | 保留 2 個月 |
| 5 | 3 months | 保留 3 個月 |
| 6 | 6 months | 保留 6 個月 |
| 8 | 1 year | 保留 1 年 |
| 9 | infinite | 保留 無限期 |
| 24 | 5 years | 保留 5 年 |
| ... | ... | ... |

完整對照表請參考 `retention_level.json`

---

**文件版本**: 1.0.0  
**最後更新**: 2026-05-27  
**維護者**: NetBackup Team
