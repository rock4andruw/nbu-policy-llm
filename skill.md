# NBU 10 專案技能樹

## 專案概述
此專案專注於 NetBackup (NBU) 10 的管理、監控和自動化工具開發，以及 AI 知識庫整合。

## 核心技能領域

### 1. NetBackup 基礎知識
- [x] **NBU 架構理解**
  - [x] Master Server、Media Server、Client 角色區分
  - [x] Catalog 和磁帶管理概念
  - [x] Storage Unit 和 Volume Pool 配置

- [x] **政策管理**
  - [x] Policy Types (MS-Windows, UNIX, MS-SQL, Oracle 等)
  - [x] Schedule 配置和排程邏輯
  - [x] Retention Level 設定
  - [ ] Backup Copy 和 SLP 概念

### 2. 命令列工具精通
- [x] **核心命令**
  - [x] `bppllist` - 政策列表和詳細資訊
  - [x] `bppllist -allpolicies` - 所有政策概覽
  - [ ] `bpplclients` - 客戶端管理
  - [ ] `bpimagelist` - 影像管理
  - [ ] `bplist` - 備份檔案列表
  - [ ] `bpmedia` - 磁帶管理

- [ ] **監控命令**
  - [ ] `bpdbjobs` - 作業監控
  - [ ] `bperror` - 錯誤日誌查看
  - [x] `bpretlevel` - 保留層級管理
  - [x] `bpstulist` - 儲存單元狀態

### 3. 腳本開發能力
- [x] **Python 開發**
  - [x] NetBackup 輸出解析 (`parse_bppllist.py`)
  - [x] 自動化腳本開發
  - [x] 報表生成工具
  - [ ] API 整合 (如適用)

- [x] **Shell 腳本**
  - [x] 系統監控腳本
  - [x] 自動化維護腳本
  - [x] 批次作業處理
  - [x] NBU 10.1.1 內部格式解析
  - [x] 欄位探索工具

### 4. 資料分析和報表
- [x] **政策分析**
  - [x] 政策效能分析
  - [x] 儲存使用率報表
  - [x] 備份成功率統計
  - [ ] 容量規劃分析

- [ ] **監控儀表板**
  - [ ] 即時狀態監控
  - [ ] 趨勢分析圖表
  - [ ] 警報系統整合

### 5. 故障排除和最佳實踐
- [x] **問題診斷**
  - [x] 常見錯誤碼理解
  - [x] 日誌分析技巧
  - [x] 效能瓶頸識別
  - [ ] 網路連線問題排查

- [x] **最佳實踐**
  - [x] 政策設計原則
  - [x] 儲存優化策略
  - [x] 官方文檔標準對齊
  - [ ] 安全性配置
  - [ ] 災難回復規劃

## 進階技能

### 6. AI 知識庫整合
- [x] **AI 格式開發**
  - [x] NetBackup 政策 JSON 標準格式
  - [x] 符合 Veritas 官方標準的輸出
  - [x] 欄位對應表 (內部格式 ↔ 標準格式)
  - [x] 政策類型和排程類型定義

- [x] **System Prompt 開發**
  - [x] NetBackup AI 助手 System Prompt
  - [x] 使用者情境處理 (HA 環境、備份時間查詢)
  - [x] 限制和邊界設定 (僅回答 NBU 問題)
  - [x] 口語化中文介面設計

- [x] **知識庫模板**
  - [x] `policy_ai_template.json` - 標準 AI 格式模板
  - [x] 搜尋索引和問答對設計

- [x] **LLM 知識庫生成** (2026-05-19 完成)
  - [x] 資料清洗和格式化 (`llm_policy_formatter_v2.py`)
  - [x] 時間資訊解析和轉換
  - [x] Retention Level 正確解釋
  - [x] Markdown 和 CSV 雙格式輸出
  - [x] 634 policies 完整處理 (1.3MB MD + 651KB CSV)
  - [x] Vertex AI 平台適配（不支援 JSON）

### 7. 整合和自動化
- [ ] **系統整合**
  - [ ] 與監控系統整合 (Nagios, Zabbix)
  - [ ] 與日誌系統整合 (ELK Stack)
  - [ ] 與通知系統整合 (Email, Slack)
  - [ ] 與 CMDB 整合

- [x] **DevOps 實踐**
  - [x] Infrastructure as Code (IaC)
  - [x] CI/CD 管線整合
  - [ ] 容器化部署
  - [x] 版本控制管理

### 8. 效能優化
- [x] **備份優化**
  - [x] 備份速度調校
  - [x] 網路頻寬管理
  - [x] 並行作業優化
  - [x] 增量備份策略

- [x] **儲存優化**
  - [x] 重複資料刪除概念
  - [x] 壓縮策略
  - [x] 保留策略設計
  - [ ] 雲端儲存整合

## 專案實作

### 已完成項目
- [x] 基礎專案結構建立
- [x] `bppllist` 欄位分析文檔 (`bppllist_field_reference.md`)
- [x] Python 解析器開發 (`parse_bppllist.py`, `parse_policy.py`)
- [x] NBU 10.1.1 專用解析器 (`nbu_10_1_1_parser.sh`)
- [x] 內部格式解析器 (`parse_internal_format.sh`)
- [x] 欄位探索工具 (`discover_bppllist_fields.sh`)
- [x] AI 友好格式生成器 (`generate_ai_readable.sh`)
- [x] **官方文檔分析**
  - [x] NetBackup 8.0/9.1/10.1.1/11 文檔版本分析
  - [x] bpflist 官方命令文檔發現和解析
  - [x] 欄位定義和標準格式對齊
- [x] **AI 知識庫建設**
  - [x] 標準 JSON 格式模板 (`policy_ai_template.json`)
  - [x] System Prompt 開發 (3 個版本)
  - [x] 使用者情境處理 (HA 環境、備份時間)
  - [x] 合規性和驗證標準
- [x] **LLM 知識庫專案** (2026-05-19)
  - [x] 634 policies 資料清洗和格式化
  - [x] 備份時間解析（frequency, time window）
  - [x] Retention Level 正確處理
  - [x] 中文化 Markdown 知識庫 (1.3 MB)
  - [x] 結構化 CSV 資料表 (651 KB, 1,430 筆)
  - [x] 口語化 System Prompt 設計
  - [x] Vertex AI 平台適配

### 進行中
- [ ] LLM 知識庫部署到 Vertex AI
- [ ] 實際查詢測試和優化

### 計劃中
- [ ] NetBackup 11 Admin Guide 深入分析
- [ ] 更多政策類型驗證
- [ ] REST API 服務
- [ ] 資料庫整合
- [ ] 機器學習預測模型（預測備份失敗）
- [ ] 行動應用開發

## 學習資源

### 官方文檔
- [NetBackup 10.0 Documentation](https://www.veritas.com/support/en_US/doc/123533878-127136857-0)
- [Command Reference Guide](https://www.veritas.com/support/)
- [Best Practices Guide](https://www.veritas.com/)

### 專案內部文檔
- `bppllist_field_reference.md` - 欄位參考指南
- `NBU_10_1_1_Guide.md` - NBU 10.1.1 專用指南
- `Document_Version_Analysis.md` - 版本相容性分析
- `AI_Format_Update_Summary.md` - AI 格式更新總結
- NetBackup Administration Guide
- Backup and Recovery Best Practices
- Enterprise Storage Management

### 社群資源
- Veritas Community Forums
- Stack Overflow NetBackup 標籤
- Reddit r/sysadmin
- 專業認證課程

## 認證目標
- [ ] Veritas Certified Specialist (VCS)
- [ ] Veritas Certified Professional (VCP)
- [ ] Veritas Certified Expert (VCE)

## 技能評估等級
- **初級 (1-3)**: 基礎操作和概念理解
- **中級 (4-6)**: 獨立工作和故障排除
- **高級 (7-8)**: 系統設計和優化
- **專家 (9-10)**: 架構設計和顧問級別

## 持續學習計劃
1. **每月**: 完成一個新的腳本工具開發
2. **每季**: 深入研究一個特定功能領域
3. **半年**: 參加相關認證考試
4. **每年**: 參與大型專案實作或技術分享

---

*最後更新: 2026-05-19*
*版本: 3.0*
*主要更新: 完成 LLM 知識庫專案 - 634 policies 完整處理和 Vertex AI 適配*
