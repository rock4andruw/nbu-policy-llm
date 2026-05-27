# NetBackup Policy LLM 知識庫專案 - 現況彙整

**彙整日期**: 2026-05-27

---

## 📊 專案目標

將 NetBackup 10.1.1 的 634 個備份策略轉換為 LLM 可查詢的知識庫，支援用戶查詢備份配置、保留期限、排程時間等資訊。

---

## 🎯 目前完成狀態

### 1. 資料來源 ✅
- **policies.json** (5.7MB): 634 個 policies 的完整配置
- **slp.json** (256KB): 163 個 Storage Lifecycle Policies
- **retention_level.json**: 103 個保留等級對照表

### 2. 核心腳本 ✅
**檔案**: `generate_final_csv_complete.py`

**功能**:
- 整合 Policy、SLP、Retention Level 三種資料
- 自動判定保留天數來源（SLP vs Policy）
- 處理 03_DataDomain_group 等特殊儲存配置
- 生成 30 個欄位的完整資料

**判定邏輯**:
```python
if pinfo.residence in slp.json:
    使用 SLP 的 retention_level
else:
    使用 Policy 的 retention_level  # 如 03_DataDomain_group
```

### 3. 輸出檔案 ✅

#### A. **policies_llm_final.csv** ⭐ 主要成果
- **路徑**: `/Users/andruw/Documents/nbu ai/policies_llm_final.csv`
- **筆數**: 1,429 行
- **欄位數**: 30 個
- **生成日期**: 2026-05-27

**欄位結構**:
```
基本資訊 (7): document_type, policy_name, policy_type, status, 
              client_hostname, client_os, storage_residence_name

排程資訊 (4): schedule_name, schedule_type, frequency_text, backup_time

🎯 最終保留資訊 (4) - 供 LLM 優先使用:
   - retention_source (SLP/Policy)
   - final_retention_level
   - final_retention_period
   - final_retention_label

📝 Policy 保留資訊 (3): policy_retention_level/period/label
⭐ SLP 保留資訊 (6): slp_name, slp_retention_level/type/period/label, 
                    slp_actual_storage

其他 (6): storage_pool, backup_paths, features,
         search_keywords, query_examples, generation_date
```

**統計結果**:
- 使用 SLP retention: 1,304 筆 (91.3%)
- 使用 Policy retention: 125 筆 (8.7%)
  - 其中 03_DataDomain_group: 113 筆 ✓
  - 其中 10_AWS_S3_raw: 10 筆 ✓
  - 其中 bksvr02_msdp_aws-stu: 1 筆 ✓
  - 其中 bksvrc02_msdp-stu: 1 筆 ✓

#### B. **llm_system_prompt.md** ⭐ LLM 指導文件
- **路徑**: `/Users/andruw/Documents/nbu ai/llm_system_prompt.md`
- **用途**: LLM 的 System Prompt，說明如何使用知識庫
- **重點**: 
  - 強調優先使用 `final_retention_label`
  - 詳細的欄位說明和使用指南
  - 包含實際對話範例
  - 術語解釋和回答風格指導

#### C. **storage_unit_groups_info.md** ✅ 補充文件
- **路徑**: `/Users/andruw/Documents/nbu ai/storage_unit_groups_info.md`
- **用途**: Storage Unit Groups 的詳細說明
- **內容**: 8 個 Storage Unit Groups 的用途、使用統計、架構分析

### 4. 舊版輸出 ⚠️ 已過時

#### **policies_all_combined.md** (舊版本)
- **路徑**: `/Users/andruw/Documents/nbu ai/output/formatted_v2_fixed/`
- **生成日期**: 2026-05-19（8 天前）
- **行數**: 52,254 行
- **格式**: Markdown

**特點**:
- 每個 policy 一個獨立的 Markdown section
- 包含詳細的表格和列表格式
- 僅包含 policy 本身的資訊，**未整合 SLP**
- **未實作保留天數判定邏輯**
- **沒有 final_retention_* 欄位**

**問題**:
1. ❌ 資訊不完整：缺少 SLP 整合
2. ❌ 保留期限顯示不正確：只顯示 "Level 0" 而非實際期限
3. ❌ 沒有判定邏輯：無法處理 03_DataDomain_group
4. ❌ 檔案過大：52K 行，不易處理
5. ❌ 資料過時：早於 CSV 8 天

---

## 🤔 是否還需要 policies_all_combined.md？

### ❌ 不建議繼續使用舊版 MD 的理由

#### 1. **功能重複且過時**
- CSV 已包含所有必要資訊
- CSV 版本更新（含 SLP 整合和判定邏輯）
- MD 版本缺少關鍵的 final_retention_* 欄位

#### 2. **CSV 格式優勢**
| 特性 | CSV | Markdown |
|------|-----|----------|
| 結構化查詢 | ✅ 易於過濾、排序 | ❌ 需要文字搜尋 |
| 平台支援 | ✅ Vertex AI, LangChain, LlamaIndex | ⚠️ 需額外處理 |
| 資料更新 | ✅ 逐行更新 | ❌ 需重新生成全檔 |
| 檔案大小 | ✅ 相對小 (~500KB) | ❌ 較大 (52K 行) |
| 欄位擴充 | ✅ 易於新增欄位 | ❌ 需修改格式 |
| 判定邏輯 | ✅ 已實作 | ❌ 未實作 |

#### 3. **維護成本**
- 維護兩種格式需要雙倍工作
- MD 格式需要重新實作 SLP 整合
- MD 格式需要重新實作判定邏輯

### ✅ 如果需要 MD 格式的建議

**情境 1: 需要人類可讀的文檔**
- 建議生成 **每個 policy 獨立的 MD 檔案**（已存在於 `output/formatted_v2_fixed/`）
- 不需要 52K 行的 combined 版本

**情境 2: 特定平台需求**
- 某些 RAG 平台可能偏好 Markdown
- 建議從 CSV 轉換，而非重新生成
- 可以寫一個簡單的 CSV → MD 轉換腳本

**情境 3: 需要更新的 MD**
如果確實需要，應該：
1. 修改現有的生成腳本，整合 SLP 資料
2. 加入 final_retention_* 資訊
3. 保持與 CSV 同步更新

---

## 💡 建議的專案方向

### 短期（本週）

1. **✅ 已完成**: 
   - CSV 生成腳本（含判定邏輯）
   - System Prompt 文檔
   - Storage Unit Groups 說明

2. **⏳ 待完成**:
   - [ ] 上傳 `policies_llm_final.csv` 到 Vertex AI
   - [ ] 測試 LLM 查詢功能
   - [ ] 驗證保留期限回答正確性
   - [ ] 收集實際使用反饋

### 中期（本月）

3. **功能優化**:
   - [ ] 建立 API 查詢介面
   - [ ] 加入更多查詢範例
   - [ ] 優化 System Prompt（基於使用反饋）

4. **資料更新**:
   - [ ] 建立自動更新流程（從 NetBackup 導出 → 生成 CSV）
   - [ ] 版本控制機制

### 長期

5. **進階功能**:
   - [ ] 支援自然語言複雜查詢
   - [ ] 備份策略推薦
   - [ ] 異常偵測（如保留期限設定異常）

---

## 📁 專案檔案清單

### 核心檔案 ⭐
```
/Users/andruw/Documents/nbu ai/
├── policies_llm_final.csv              # 主要知識庫 (1,429 行)
├── llm_system_prompt.md                # LLM System Prompt
├── generate_final_csv_complete.py      # CSV 生成腳本
├── storage_unit_groups_info.md         # Storage Unit Groups 說明
└── project_status_summary.md           # 本文件
```

### 資料來源
```
├── policies.json                        # 634 policies (5.7MB)
├── slp.json                            # 163 SLPs (256KB)
└── retention_level.json                # 103 retention levels
```

### 舊版檔案 (已過時)
```
├── output/formatted_v2_fixed/
│   ├── policies_all_combined.md        # ⚠️ 舊版 (52K 行, 2026-05-19)
│   └── *_policy.md                     # 634 個獨立 MD 檔案
```

---

## 🎯 結論與建議

### 關於 policies_all_combined.md

**建議**: ❌ **不需要重新生成**

**理由**:
1. CSV 格式已滿足需求且功能更完整
2. 舊版 MD 缺少 SLP 整合和判定邏輯
3. 維護兩種格式成本高
4. 主流 LLM 平台都支援 CSV

**替代方案**:
- **主要**: 使用 `policies_llm_final.csv` + `llm_system_prompt.md`
- **輔助**: 保留獨立的 policy MD 檔案供人類查閱（如需要）
- **未來**: 如有特殊需求，可從 CSV 轉換為 MD

### 下一步行動建議

**優先級 1 - 驗證與測試**:
1. 上傳 CSV 到 Vertex AI
2. 測試查詢功能
3. 驗證保留期限回答準確性

**優先級 2 - 文檔完善**:
1. 更新 README.md（加入專案現況）
2. 建立使用手冊
3. 記錄測試結果

**優先級 3 - 自動化**:
1. 建立資料更新腳本
2. 設定定期更新排程

---

**版本**: 1.0  
**作者**: Claude + Andruw  
**最後更新**: 2026-05-27
