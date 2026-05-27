# NetBackup Policy LLM 知識庫

> 將 NetBackup 10.1.1 備份策略轉換為 LLM 可查詢的知識庫

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/yourusername/nbu-policy-llm)
[![NetBackup](https://img.shields.io/badge/NetBackup-10.1.1-green.svg)](https://www.veritas.com/product/backup-and-recovery/netbackup)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

---

## 📖 專案簡介

本專案將 NetBackup 備份策略配置轉換為結構化的 CSV 格式，支援在 Vertex AI、LangChain、LlamaIndex 等 RAG 平台上進行自然語言查詢。

### ✨ 特色

- ✅ **完整整合**: Policy + SLP + Retention Level 三種資料源
- ✅ **智能判定**: 自動判定保留天數來源（SLP 或 Policy）
- ✅ **中文支援**: 保留期限顯示中文標籤（如"保留 1 週"）
- ✅ **特殊處理**: 正確處理 DataDomain 等直接儲存配置
- ✅ **平台友善**: CSV 格式，支援主流 RAG 平台

### 📊 統計資料

```
策略數量:     634 個 policies
資料筆數:     1,429 行
欄位數量:     30 個
SLP 覆蓋率:   91.3% (1,304/1,429)
直接儲存配置: 8.7% (125/1,429)
資料來源:     NetBackup 10.1.1
最後更新:     2026-05-27
```

---

## 🚀 快速開始

### 新電腦設定

如果你是第一次使用本專案，請先參考：

📘 **[SETUP.md](SETUP.md) - 新電腦完整設定指南**
- Windows 和 macOS 環境設定
- Python 安裝步驟
- 必要檔案下載
- 完整操作流程

### 日常使用流程

#### 步驟 1: 從 NBU Server 導出資料

在 NetBackup Master Server 上執行：

```bash
cd /tmp
bppllist -allpolicies -json > policies.json
/usr/openv/netbackup/bin/admincmd/nbstlutil list -slp -json > slp.json
```

詳細說明: [NBU_SERVER_COMMANDS.md](NBU_SERVER_COMMANDS.md)

#### 步驟 2: 傳輸到本機

**macOS**:
```bash
cd ~/Documents/nbu\ ai
scp root@nbu-server:/tmp/policies.json ./
scp root@nbu-server:/tmp/slp.json ./
```

**Windows**: 使用 WinSCP 下載兩個 JSON 檔案

#### 步驟 3: 本地處理

**macOS**:
```bash
./process_local_json.sh
```

**Windows**: 雙擊 `process_local_json.bat`

#### 步驟 4: 上傳到知識庫

將產生的 `policies_llm_final.csv` 上傳到公司知識庫平台（Vertex AI 等）。

### 測試查詢

```
Q: "21C_MSSQL_Online_21sunlike 的備份保留多久？"
A: 保留 1 週

Q: "哪些策略在凌晨 3 點執行？"
A: [列出相關策略]
```

📚 **完整文檔**:
- [SETUP.md](SETUP.md) - 新電腦設定指南
- [USAGE_WORKFLOW.md](USAGE_WORKFLOW.md) - 詳細使用流程
- [USER_GUIDE.md](USER_GUIDE.md) - 知識庫使用說明
- [NBU_SERVER_COMMANDS.md](NBU_SERVER_COMMANDS.md) - NBU Server 操作

---

## 📁 專案結構

```
nbu ai/
├── README.md                          # 專案說明（本文件）
├── SETUP.md                           # 新電腦設定指南 ⭐ 新
├── USAGE_WORKFLOW.md                  # 完整使用流程 ⭐ 新
├── NBU_SERVER_COMMANDS.md             # NBU Server 操作指南 ⭐ 新
├── USER_GUIDE.md                      # 知識庫使用說明 ⭐
├── llm_system_prompt.md               # LLM System Prompt ⭐
│
├── process_local_json.sh              # macOS/Linux 處理腳本 🆕
├── process_local_json.bat             # Windows 處理腳本 🆕
├── generate_final_csv_complete.py     # Python 主程式
│
├── policies_llm_final.csv             # 輸出的知識庫檔案 ⭐
├── retention_level.json               # 保留等級對照表
│
├── tests/                             # 測試目錄 🆕
│   ├── README.md                      # 測試說明
│   ├── test_policy_slp_retention.py   # 保留邏輯測試
│   └── test_policy_slp_integration.py # 整合測試
│
├── storage_unit_groups_info.md        # Storage Unit Groups 說明
├── project_status_summary.md          # 專案現況彙整
└── .gitignore                         # Git 忽略清單

資料來源（不納入版本控制）:
├── policies.json                      # NetBackup Policies (5.7MB)
├── slp.json                          # Storage Lifecycle Policies (256KB)
└── backups/                          # 自動備份目錄
```

---

## 🎯 核心檔案

### 1. policies_llm_final.csv ⭐
**主要知識庫檔案**
- 1,429 行 × 30 欄位
- UTF-8 編碼
- 包含最終判定的保留期限

### 2. llm_system_prompt.md ⭐
**LLM System Prompt 設定**
- 角色定義與回答指南
- 30 個欄位的詳細說明
- 實際對話範例
- 術語解釋

### 3. generate_final_csv_complete.py
**資料生成腳本**
- 整合三種資料來源
- 實作保留天數判定邏輯
- 轉換為中文標籤

---

## 📋 資料結構

### 欄位分類（30 個欄位）

| 類別 | 欄位數 | 說明 |
|------|--------|------|
| 基本資訊 | 7 | policy_name, policy_type, status, client_hostname 等 |
| 排程資訊 | 4 | schedule_type, frequency_text, backup_time 等 |
| **⭐ 最終保留資訊** | **4** | **retention_source, final_retention_label 等（LLM 優先使用）** |
| Policy 保留資訊 | 3 | policy_retention_level/period/label |
| SLP 保留資訊 | 6 | slp_name, slp_retention_level/type/period/label 等 |
| 其他資訊 | 6 | storage_pool, backup_paths, features 等 |

### 🎯 重要欄位

**LLM 回答保留期限問題時，應優先使用**:
- `final_retention_label`: 保留 1 週 / 保留 3 個月 / 保留 無限期
- `retention_source`: SLP / Policy

---

## 🔧 維護與更新

### 更新資料流程

```bash
# 1. 從 NetBackup 導出資料
bppllist -allpolicies -json > policies.json
nbstlutil list -slp -json > slp.json

# 2. 重新生成 CSV
python3 generate_final_csv_complete.py

# 3. 驗證資料
wc -l policies_llm_final.csv

# 4. 提交變更
git add policies_llm_final.csv
git commit -m "Update: 重新生成 CSV ($(date +%Y-%m-%d))"
```

### 建議更新頻率
- **開發環境**: 每週
- **正式環境**: 每月或 Policy 有重大變更時

---

## 📖 使用範例

### 查詢保留期限
```
Q: "21C_MSSQL_Online_21sunlike 這個策略的備份會保留多久？"
A: 21C_MSSQL_Online_21sunlike 策略的備份保留期限是 **保留 1 週**。
   這個保留設定來自 SLP: 1_Daily_04
```

### 查詢策略配置
```
Q: "bksvr 這台主機有哪些備份策略？"
A: 找到以下備份 bksvr 主機的策略：
   1. PIC_NBU_Catalog_Online_bksvr (NBU-Catalog, 保留 1 週)
   2. 0000_TEST_policy (Standard, 保留 2 週)
   ...
```

### 比較分析
```
Q: "21sunlike-bk 的 MSSQL 和檔案備份有什麼差異？"
A: [比較兩種策略的保留期限、排程時間、SLP 等]
```

更多範例請參考 [USER_GUIDE.md](USER_GUIDE.md)

---

## 🤝 貢獻

### 問題回報
如遇到問題，請提供：
1. 問題描述
2. 查詢語句
3. 預期結果 vs 實際結果
4. CSV 檔案版本（generation_date）

### 功能建議
歡迎提出新功能建議或改進意見。

---

## 📝 版本歷史

### v1.0.0 (2026-05-27)
- ✅ 初始版本發布
- ✅ 整合 Policy + SLP + Retention Level
- ✅ 實作保留天數判定邏輯
- ✅ 支援中文保留期限標籤
- ✅ 正確處理 DataDomain 等特殊配置
- ✅ 完整文檔（使用說明、System Prompt）

---

## 📄 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

---

## 🔗 相關連結

- [詳細使用說明](USER_GUIDE.md)
- [LLM System Prompt](llm_system_prompt.md)
- [專案現況彙整](project_status_summary.md)
- [Storage Unit Groups 說明](storage_unit_groups_info.md)
- [NetBackup 官網](https://www.veritas.com/product/backup-and-recovery/netbackup)
- [Vertex AI 文檔](https://cloud.google.com/vertex-ai/docs)

---

## 📧 聯絡資訊

如有任何問題或建議，請聯絡專案維護團隊。

---

**專案狀態**: ✅ 生產就緒  
**版本**: 1.0.0  
**最後更新**: 2026-05-27
