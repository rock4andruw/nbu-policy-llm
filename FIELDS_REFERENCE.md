# CSV 欄位說明

**版本**: 1.0  
**日期**: 2026-05-28  
**適用**: policies_llm_final.csv

本文件說明 CSV 中各欄位的來源和判定邏輯。

---

## 📊 欄位總覽

CSV 檔案包含 **30 個欄位**，分為以下類別：

1. **基本資訊** (7 個欄位)
2. **排程資訊** (4 個欄位)
3. **最終保留資訊** (4 個欄位) - LLM 優先使用
4. **Policy 保留資訊** (3 個欄位)
5. **SLP 保留資訊** (6 個欄位)
6. **其他資訊** (6 個欄位)

---

## 1️⃣ 基本資訊欄位

### document_type
**固定值**: `NetBackup Policy`

**說明**: 文件類型標識，用於區分不同類型的知識庫資料。

**來源**: 程式碼固定值

---

### policy_name
**來源**: `policies.json → policies[].class_name`

**說明**: NetBackup Policy 的名稱，唯一識別碼。

**範例**:
- `21C_MSSQL_Online_21sunlike`
- `COSMED_AES_MSSQL_Online_full_cosaesdbha`

---

### policy_type
**來源**: `policies.json → policies[].pinfo.PolicyTypeText`

**說明**: Policy 的類型，定義備份的資料類型。

**可能值**:
- `Standard` - 標準檔案系統備份
- `MS-SQL-Server` - SQL Server 資料庫備份
- `Oracle` - Oracle 資料庫備份
- `VMware` - VMware 虛擬機備份
- 其他應用程式類型

**統計** (基於實際資料):
```
Standard:      約 40%
MS-SQL-Server: 約 35%
Oracle:        約 15%
VMware:        約 10%
```

---

### status ⭐
**來源**: `policies.json → policies[].pinfo.active`

**判定邏輯**:
```python
'status': 'Active' if pinfo.get('active') == 1 else 'Inactive'
```

**說明**: Policy 的啟用狀態

| active 值 | Status 輸出 | 說明 |
|-----------|-------------|------|
| `1` | `Active` | Policy 已啟用，會執行備份 |
| `0` | `Inactive` | Policy 已停用，不會執行備份 |

**實際資料統計**:
- `Active`: 58 policies (9.1%)
- `Inactive`: 576 policies (90.9%)

**CSV 輸出統計** (包含多個 schedule/client):
- `Active`: 177 筆 (12.4%)
- `Inactive`: 1,252 筆 (87.6%)

**注意事項**:
- Inactive 的 Policy 不會執行備份，但保留在系統中供參考
- 通常是暫時停用或已不再使用的 Policy

---

### client_hostname
**來源**: `policies.json → policies[].clients[].hostname`

**說明**: 要備份的客戶端主機名稱

**特性**:
- 一個 Policy 可包含多個 clients
- 每個 client 會產生一筆 CSV 記錄
- 因此 CSV 行數 (1,429) > Policy 數量 (634)

**範例**:
- `21sunlike-bk`
- `bksvr`
- `PCSC-AD-B.PCSC.com.tw`

---

### client_os
**來源**: `policies.json → policies[].clients[].ext_info`

**說明**: 客戶端作業系統資訊

**可能值**:
- `Windows-x64` - 64 位元 Windows
- `Linux` - Linux 系統
- `Unix` - Unix 系統
- 空值 - 未指定

---

### storage_residence_name
**來源**: `policies.json → policies[].pinfo.residence[0]`

**說明**: 儲存位置名稱，可能是 SLP 名稱或直接指定的 Storage Unit/Group

**類型**:
1. **SLP 名稱** (91.3%)
   - 例如: `1_Daily_04`, `2_Weekly_05`, `3_Monthly_06`
   - 這些會在 `slp.json` 中有對應的 SLP 配置

2. **直接指定的 Storage Unit/Group** (8.7%)
   - 例如: `03_DataDomain_group`, `10_AWS_S3_raw`
   - 這些不在 `slp.json` 中

---

## 2️⃣ 排程資訊欄位

### schedule_name
**來源**: `policies.json → policies[].schedule[].schedule_name`

**說明**: 排程名稱

**範例**:
- `Full` - 完整備份
- `Daily_Full` - 每日完整備份
- `Inc` - 增量備份

---

### schedule_type
**來源**: `policies.json → policies[].schedule[].schedule_type`

**判定邏輯**:
```python
schedule_type_map = {
    0: "Full Backup",
    1: "Differential Incremental",
    2: "Cumulative Incremental",
    3: "User Backup",
    4: "User Archive"
}
```

**說明**: 備份類型

| 數值 | 類型 | 說明 |
|------|------|------|
| 0 | Full Backup | 完整備份 |
| 1 | Differential Incremental | 差異增量備份 |
| 2 | Cumulative Incremental | 累積增量備份 |
| 3 | User Backup | 使用者備份 |
| 4 | User Archive | 使用者封存 |

---

### frequency_text
**來源**: `policies.json → policies[].schedule[].FrequencyText`

**說明**: 備份頻率的文字描述

**可能值**:
- `Every day` - 每天
- `Every week` - 每週
- `Every month` - 每月
- 自訂頻率

---

### backup_time
**來源**: `policies.json → policies[].schedule[].backup_window`

**格式**: `HH:MM~HH:MM` (24 小時制)

**說明**: 備份時間視窗

**範例**:
- `03:00~07:00` - 凌晨 3 點到 7 點
- `00:00~00:00` - 全天任何時間

---

## 3️⃣ 最終保留資訊欄位 ⭐

這些欄位是 LLM 應該優先使用的，已經自動判定了應該使用 SLP 還是 Policy 的保留設定。

### retention_source
**判定邏輯**:
```python
if is_slp and slp_retention_level is not None:
    retention_source = "SLP"
else:
    retention_source = "Policy"
```

**說明**: 保留天數的來源

| 值 | 說明 | 比例 |
|----|------|------|
| `SLP` | 使用 SLP 的保留設定 | 91.3% |
| `Policy` | 使用 Policy 的保留設定 | 8.7% |

**判定條件**:
1. 檢查 `storage_residence_name` 是否在 `slp.json` 中
2. 如果在 SLP 中且有 retention 設定 → 使用 `SLP`
3. 否則 → 使用 `Policy`

---

### final_retention_level
**格式**: `Level {數字}`

**說明**: 最終判定的保留等級

**範例**:
- `Level 0` - 保留 1 週
- `Level 1` - 保留 2 週
- `Level 8` - 保留 1 個月

---

### final_retention_period
**格式**: `{數字} {units}`

**說明**: 最終判定的保留期限（數值 + 單位）

**範例**:
- `1 week`
- `2 weeks`
- `1 month`
- `3 months`

---

### final_retention_label
**格式**: 中文標籤

**說明**: 最終判定的保留期限（中文顯示）

**範例**:
- `保留 1 週`
- `保留 2 週`
- `保留 1 個月`
- `保留 3 個月`

**重要**: LLM 回答保留期限問題時，應使用此欄位！

---

## 4️⃣ Policy 保留資訊欄位

這些欄位來自 Policy 本身的設定，供參考用。

### policy_retention_level
**來源**: `policies.json → policies[].schedule[].retention_level`

**格式**: `Level {數字}`

---

### policy_retention_period
**來源**: 透過 `retention_level.json` 轉換

---

### policy_retention_label
**來源**: 透過 `retention_level.json` 轉換為中文

---

## 5️⃣ SLP 保留資訊欄位

這些欄位來自 SLP 的設定，供參考用。

### slp_name
**來源**: `policies.json → policies[].pinfo.residence[0]`

**說明**: SLP 名稱（如果使用 SLP）

**範例**:
- `1_Daily_04` - 使用 SLP
- `03_DataDomain_group` - 直接指定 Storage Group（不是 SLP）
- `N/A` - 無儲存設定

---

### slp_retention_level
**來源**: `slp.json → SlpOperations[0].RetentionLevel`

**格式**: `Level {數字}` 或 `N/A`

---

### slp_retention_type
**來源**: `slp.json → SlpOperations[0].RetentionType`

**可能值**:
- `FIXED` - 固定期限
- `EXPIRE_AFTER_COPY` - 複製後過期
- `CAPACITY_MANAGED` - 容量管理
- `N/A` - 不使用 SLP

---

### slp_actual_storage
**來源**: `slp.json → SlpOperations[0].OperationStorageUnit`

**說明**: SLP 實際使用的 Storage Unit

**範例**:
- `s01_SSD_msdp_stu_group`
- `bksvr02_msdp_aws-stu`

---

### slp_retention_period
**來源**: 透過 SLP 的 `RetentionLevel` 轉換

---

### slp_retention_label
**來源**: 透過 SLP 的 `RetentionLevel` 轉換為中文

---

## 6️⃣ 其他資訊欄位

### storage_pool
**來源**: `policies.json → policies[].pinfo.pool`

**說明**: 儲存池名稱（舊版欄位，多數為空）

---

### backup_paths
**來源**: `policies.json → policies[].include[]`

**說明**: 備份路徑清單（逗號分隔）

**範例**:
- `/data`
- `C:\Program Files\`, `D:\Data\`

---

### features
**來源**: `policies.json → policies[].options[]`

**說明**: Policy 啟用的功能選項

---

### search_keywords
**自動生成**: 由 policy_name, client_hostname, policy_type 組成

**說明**: 用於搜尋的關鍵字

---

### query_examples
**自動生成**: 基於 policy_name 的查詢範例

**格式**: `{policy_name} 的備份保留多久？`

---

### generation_date
**來源**: 程式執行時的當前日期

**格式**: `YYYY-MM-DD`

**說明**: CSV 生成日期

---

## 🔍 關鍵判定邏輯

### Status 判定

```python
# 來源欄位
pinfo.active  # 0 或 1

# 判定邏輯
if pinfo.get('active') == 1:
    status = 'Active'    # Policy 已啟用
else:
    status = 'Inactive'  # Policy 已停用
```

### Retention Source 判定

```python
# 步驟 1: 取得 residence 名稱
slp_name = pinfo.get('residence', [None])[0]

# 步驟 2: 檢查是否為 SLP
is_slp = slp_name and slp_name in slps_dict

# 步驟 3: 判定來源
if is_slp and slp_retention_level is not None:
    retention_source = "SLP"
    final_retention = slp_retention
else:
    retention_source = "Policy"
    final_retention = policy_retention
```

---

## 📈 統計數據

### Policy 數量
- 總計: 634 policies

### CSV 記錄數
- 總計: 1,429 筆（因一個 policy 可有多個 client/schedule）

### Status 分佈
- Active: 58 policies (9.1%)
- Inactive: 576 policies (90.9%)

### Retention Source 分佈
- SLP: 1,304 筆 (91.3%)
- Policy: 125 筆 (8.7%)

### 特殊儲存配置
使用直接指定 Storage Unit/Group（不在 SLP 中）:
- `03_DataDomain_group`: 113 筆
- `10_AWS_S3_raw`: 2 筆
- `bksvr02_msdp_aws-stu`: 1 筆
- `bksvrc02_msdp-stu`: 1 筆

---

## 🔗 相關資源

- [USER_GUIDE.md](USER_GUIDE.md) - 使用指南
- [llm_system_prompt.md](llm_system_prompt.md) - LLM System Prompt
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 問題排除

---

**最後更新**: 2026-05-28  
**維護者**: NetBackup Team
