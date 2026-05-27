# 測試檔案

本目錄包含 NetBackup Policy LLM 專案的測試程式。

---

## 📋 測試項目

### 1. test_policy_slp_retention.py
**用途**: 測試保留天數判定邏輯（SLP vs Policy）

**測試內容**:
- Policy 與 SLP 的資料整合
- Retention Level 的正確轉換
- 保留天數判定邏輯（91.3% SLP, 8.7% Policy）
- 特殊情況處理（如 03_DataDomain_group）

**執行**:
```bash
python3 tests/test_policy_slp_retention.py
```

### 2. test_policy_slp_integration.py
**用途**: 測試 Policy 與 SLP 資料整合

**測試內容**:
- 從 pinfo.residence 正確讀取 SLP 名稱
- SLP 資料查詢和解析
- 資料完整性驗證

**執行**:
```bash
python3 tests/test_policy_slp_integration.py
```

---

## 🚀 使用說明

### 執行測試

**單一測試**:
```bash
# 從專案根目錄執行
cd "/Users/andruw/Documents/nbu ai"
python3 tests/test_policy_slp_retention.py
```

**所有測試**:
```bash
# 執行所有測試
python3 tests/test_policy_slp_retention.py
python3 tests/test_policy_slp_integration.py
```

### 使用 pytest（可選）

如果安裝了 pytest：
```bash
# 安裝 pytest
pip3 install pytest

# 執行測試
pytest tests/ -v
```

---

## 🔧 維護指南

### 何時執行測試

1. **修改主程式後**
   - 修改 `generate_final_csv_complete.py` 後
   - 變更判定邏輯後
   - 新增欄位後

2. **資料格式變更**
   - NetBackup 版本升級
   - JSON 結構改變
   - 新增 SLP 類型

3. **重大更新前**
   - 準備提交到 Git
   - 部署到生產環境前

### 測試失敗處理

如果測試失敗：
1. 檢查 policies.json 和 slp.json 是否為最新
2. 確認 retention_level.json 完整
3. 檢視測試輸出的錯誤訊息
4. 對比主程式的實作邏輯

---

## 📝 測試數據要求

測試需要以下資料檔案（放在專案根目錄）：
```
policies.json           # NetBackup Policies 資料
slp.json               # Storage Lifecycle Policies 資料
retention_level.json   # 保留等級對照表
```

---

## 🎯 測試覆蓋範圍

目前的測試覆蓋：
- ✅ SLP 資料載入和解析
- ✅ Policy 資料讀取
- ✅ Retention Level 轉換
- ✅ 保留天數判定邏輯
- ✅ 特殊儲存配置處理（DataDomain）

未來可擴充：
- [ ] CSV 輸出格式驗證
- [ ] 中文標籤轉換測試
- [ ] 邊界情況測試
- [ ] 效能測試

---

**最後更新**: 2026-05-27  
**維護者**: NetBackup Team
