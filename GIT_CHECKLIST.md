# Git 版本控制 - 檔案整理清單

**日期**: 2026-05-27

---

## ✅ 應該提交到 Git 的檔案

### 📋 核心文檔 (必要)
```
✅ README.md                          (6.3K)  - 專案說明
✅ USER_GUIDE.md                      (15K)   - 使用說明
✅ llm_system_prompt.md               (9.4K)  - LLM System Prompt
✅ project_status_summary.md          (7.5K)  - 專案彙整
✅ storage_unit_groups_info.md        (2.7K)  - Storage Groups 說明
✅ .gitignore                         (新建)  - Git 忽略清單
```

### 🎯 核心產出 (必要)
```
✅ policies_llm_final.csv             (852K)  - 主要知識庫 ⭐
✅ generate_final_csv_complete.py     (14K)   - CSV 生成腳本 ⭐
✅ retention_level.json               (13K)   - 保留等級對照表
```

### 📚 參考文件 (可選)
```
✅ skill.md                           (6.4K)  - 技能規劃文檔
```

---

## ❌ 不應提交到 Git 的檔案

### 原始資料 (太大 + 敏感)
```
❌ policies.json                      (5.7M)  - 太大，且包含實際配置
❌ policy_20260203.json               (5.6M)  - 舊版本，已過時
❌ slp.json                           (256K)  - 原始資料
```
**理由**: 
- 檔案過大不適合 Git
- 可能包含敏感資訊（主機名、路徑等）
- 應從 NetBackup 實時導出，不需要版本控制

### 測試與樣本檔案
```
❌ test_*.py                          (多個)  - 測試腳本
❌ *_sample.csv                       (多個)  - 測試樣本
❌ correct_sample_with_slp.csv        (2.2K)
❌ final_sample_complete.csv          (3.3K)
❌ sample_policies_with_slp.csv       (1.4K)
```
**理由**: 開發過程的測試檔案，非最終產出

### 舊版腳本
```
❌ generate_correct_csv_sample.py     (11K)   - 舊版生成腳本
❌ test_csv_with_slp_sample.py        (13K)   - 舊版測試
❌ test_21sunlike_with_mock_data.py   (7.6K)
❌ test_policy_slp_integration.py     (6.3K)
❌ test_policy_slp_retention.py       (8.5K)
```
**理由**: 已被 generate_final_csv_complete.py 取代

### 舊版模板
```
❌ policy_ai_template.json            (6.2K)
❌ policy_ai_template_md.md           (4.1K)
```
**理由**: 早期設計，已不使用

### 其他目錄
```
❌ output/                            - 舊版輸出（52K 行的 MD 檔案）
❌ 原廠文件/                          - NetBackup 官方文檔（PDF 太大）
❌ docs/official/                     - 同上
```

---

## 📦 建議的 Git 結構

```
nbu-policy-llm/
├── .gitignore                        # Git 忽略清單
├── README.md                         # 專案說明
├── USER_GUIDE.md                     # 使用說明
├── GIT_CHECKLIST.md                  # 本文件
│
├── docs/                             # 文檔目錄
│   ├── llm_system_prompt.md         # LLM System Prompt
│   ├── project_status_summary.md    # 專案彙整
│   ├── storage_unit_groups_info.md  # Storage Groups 說明
│   └── skill.md                     # 技能規劃
│
├── data/                             # 資料目錄
│   ├── policies_llm_final.csv       # 主要知識庫 ⭐
│   └── retention_level.json         # 保留等級對照表
│
└── scripts/                          # 腳本目錄
    └── generate_final_csv_complete.py  # CSV 生成腳本
```

---

## 🚀 整理步驟

### 步驟 1: 建立目錄結構
```bash
cd "/Users/andruw/Documents/nbu ai"
mkdir -p docs data scripts
```

### 步驟 2: 移動檔案到對應目錄
```bash
# 文檔
mv llm_system_prompt.md docs/
mv project_status_summary.md docs/
mv storage_unit_groups_info.md docs/
mv skill.md docs/

# 資料
mv policies_llm_final.csv data/
mv retention_level.json data/

# 腳本
mv generate_final_csv_complete.py scripts/
```

### 步驟 3: 刪除不需要的檔案（可選）
```bash
# 刪除測試檔案
rm -f test_*.py *_sample.csv

# 刪除舊版腳本
rm -f generate_correct_csv_sample.py
rm -f test_csv_with_slp_sample.py

# 刪除舊版模板
rm -f policy_ai_template.json
rm -f policy_ai_template_md.md

# 刪除舊版資料
rm -f policy_20260203.json
```

### 步驟 4: 初始化 Git
```bash
git init
git add .gitignore
git add README.md USER_GUIDE.md GIT_CHECKLIST.md
git add docs/ data/ scripts/
git commit -m "Initial commit: NetBackup Policy LLM Knowledge Base v1.0.0

- 主要知識庫: policies_llm_final.csv (1,429 筆資料)
- 完整文檔: 使用說明、System Prompt、專案彙整
- 生成腳本: 整合 Policy + SLP + Retention Level
- 功能: 自動判定保留天數來源 (91.3% SLP, 8.7% Policy)
"
```

### 步驟 5: 查看狀態
```bash
git status
git log --oneline
```

---

## 🎯 重要提醒

### 不要提交敏感資訊
- ❌ 實際的 policies.json / slp.json（包含主機名、路徑等）
- ❌ 任何包含密碼、金鑰的檔案
- ❌ 內部 IP 位址、網域名稱

### CSV 檔案的處理
- ✅ **policies_llm_final.csv** 可以提交（已脫敏）
- ❌ 如果包含敏感主機名，需先處理：
  ```bash
  # 檢查是否有敏感資訊
  grep -i "password\|secret\|key" policies_llm_final.csv
  ```

### 更新 .gitignore
確認 `.gitignore` 包含：
```
# 原始資料
policies.json
slp.json
policy_*.json

# 測試檔案
test_*.py
*_sample.csv

# 舊版輸出
output/

# 原廠文件
原廠文件/
docs/official/
```

---

## 📊 檔案統計

### 提交到 Git 的檔案
```
文檔:    5 個檔案  (~45K)
資料:    2 個檔案  (~865K)
腳本:    1 個檔案  (~14K)
設定:    2 個檔案  (.gitignore, GIT_CHECKLIST.md)
────────────────────────────
總計:    10 個檔案 (~924K)
```

### 排除的檔案
```
原始資料: 3 個檔案   (~11.6M) - policies.json, slp.json 等
測試檔案: 8 個檔案   (~60K)   - test_*.py, *_sample.csv
舊版檔案: 5 個檔案   (~50K)   - 舊版腳本和模板
舊版目錄: output/    (~52K 行 MD)
```

---

## ✅ 最終檢查清單

提交前確認：
- [ ] README.md 已更新
- [ ] .gitignore 已建立
- [ ] 敏感資訊已移除
- [ ] 檔案已整理到對應目錄
- [ ] 測試檔案已刪除或忽略
- [ ] 原始資料檔案已排除
- [ ] Git commit message 有意義

---

## 🔗 準備推送到 GitHub

完成本地提交後：

```bash
# 1. 在 GitHub 建立新倉庫（不要初始化 README）

# 2. 連接遠端倉庫
git remote add origin https://github.com/你的帳號/nbu-policy-llm.git

# 3. 推送
git branch -M main
git push -u origin main
```

---

**檢查完成日期**: ______  
**提交者**: ______  
**確認無敏感資訊**: ☐
