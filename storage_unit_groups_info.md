# Storage Unit Groups 資訊

**生成時間**: 2026-05-26  
**資料來源**: slp.json (163 SLPs)

---

## 📊 總覽

| 項目 | 數量 |
|------|------|
| Storage Unit Groups | 8 個 |
| 一般 Storage Units | 30 個 |
| 總計 | 38 個 |

---

## 🎯 Storage Unit Groups 詳細清單

### 1. **s01_SSD_msdp_stu_group** ⭐ (最常使用)
- **用途**: BACKUP
- **使用數**: 53 個 SLP
- **Retention Levels**: 9, 26
- **範例 SLP**:
  - 0_NBU_Catalog
  - 1_Daily_Dup_s01_02_AWS
  - 1_Daily_Dup_s01_02_GCS

### 2. **s02_SSD_msdp_gcs-stu_group**
- **用途**: DUPLICATE (GCS 複製)
- **使用數**: 16 個 SLP
- **Retention Levels**: 0, 1, 2
- **範例 SLP**:
  - 1_Daily_Dup_s01_02_GCS
  - 1_Daily_Dup_s01_03_GCS

### 3. **s02_SSD_msdp_aws-stu_group**
- **用途**: DUPLICATE (AWS 複製)
- **使用數**: 12 個 SLP
- **Retention Levels**: 0, 1, 2
- **範例 SLP**:
  - 1_Daily_Dup_s01_02_AWS
  - 1_Daily_Dup_s01_03_AWS

### 4. **v01_backupVM_group**
- **用途**: BACKUP (虛擬機備份)
- **使用數**: 5 個 SLP
- **Retention Levels**: 3
- **範例 SLP**:
  - 3_Monthly_02_backupVM
  - 3_Monthly_Dup_02_AWS_backupVM

### 5. **s03_SSD_tape_hcart3_group**
- **用途**: DUPLICATE (磁帶複製)
- **使用數**: 2 個 SLP
- **Retention Levels**: 1, 3
- **範例 SLP**:
  - 0_NBU_Catalog
  - 1_Full_Diff_Daily_Dup_s01_04_tape

### 6. **v01c_backupVM_group**
- **用途**: DUPLICATE (VM 複製)
- **使用數**: 2 個 SLP
- **Retention Levels**: 3

### 7. **v01c_backupVM_group_gcs**
- **用途**: DUPLICATE (VM GCS 複製)
- **使用數**: 2 個 SLP
- **Retention Levels**: 3

### 8. **02_tape_hcart3_group**
- **用途**: DUPLICATE (磁帶)
- **使用數**: 1 個 SLP
- **Retention Levels**: 3

---

## 🏗️ 架構分析

### 儲存層級結構：
```
s01_SSD_msdp_stu_group (主要備份)
    ↓ 
s02_SSD_msdp_gcs-stu_group (GCS 雲端複製)
s02_SSD_msdp_aws-stu_group (AWS 雲端複製)
s03_SSD_tape_hcart3_group (磁帶複製)
```

### 用途分類：
- **BACKUP (主要備份)**: 2 個 groups (s01, v01)
- **DUPLICATE (複製)**: 6 個 groups (雲端、磁帶、VM)

---

## 💡 關鍵發現

1. **主要備份儲存**: `s01_SSD_msdp_stu_group` 是最常使用的 (53 個 SLP)
2. **雲端備份策略**: 有 AWS 和 GCS 兩個雲端複製群組
3. **多層保護**: 典型的 3-2-1 備份策略（本地 SSD → 雲端 → 磁帶）
4. **VM 專用群組**: 虛擬機有獨立的備份群組

---

## 📋 一般 Storage Units (非 group)

總共 30 個，包含：
- **Media Server 類**: m02_bksvr02, m03_bksvr03, m04_bksvr04, m05_bksvr05
- **重複資料刪除**: bksvr02_msdp-stu, bksvr03_msdp-stu 等
- **雲端儲存**: mc01_bksvrc01, bksvrs01_aws_raw-stu 等

---

**說明**: Storage Unit Groups 可以包含多個實際的 Storage Units，提供負載平衡和容錯能力。
