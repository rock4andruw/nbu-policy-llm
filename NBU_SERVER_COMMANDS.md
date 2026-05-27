# NBU Server 端執行命令

**適用於**: NetBackup Master Server (Linux)  
**目的**: 產生 policies.json 和 slp.json 供 Client 端處理

---

## 🖥️ 在 NBU Server 上執行

### 1. 登入 NetBackup Master Server

```bash
# SSH 登入
ssh root@your-nbu-server.company.com

# 或直接在 Server 終端機操作
```

### 2. 切換到工作目錄

```bash
# 建議使用 /tmp 或其他臨時目錄
cd /tmp

# 或使用自訂目錄
mkdir -p /export/nbu_json
cd /export/nbu_json
```

### 3. 導出 Policies 資料

```bash
# 方法 1: 使用 bppllist (如果已在 PATH)
bppllist -allpolicies -json > policies.json

# 方法 2: 使用完整路徑
/usr/openv/netbackup/bin/admincmd/bppllist -allpolicies -json > policies.json
```

**預期輸出**:
- 檔案大小: 約 5-10 MB (視 policy 數量而定)
- 檔案內容: JSON 格式，包含所有 policy 配置

### 4. 導出 SLP 資料

```bash
# 使用 nbstlutil 命令
/usr/openv/netbackup/bin/admincmd/nbstlutil list -slp -json > slp.json
```

**預期輸出**:
- 檔案大小: 約 200-500 KB
- 檔案內容: JSON 格式，包含所有 SLP 配置

### 5. 驗證檔案

```bash
# 檢查檔案是否存在且有內容
ls -lh policies.json slp.json

# 預期輸出類似:
# -rw-r--r-- 1 root root 5.7M May 27 10:30 policies.json
# -rw-r--r-- 1 root root 256K May 27 10:30 slp.json

# 驗證 JSON 格式是否正確
python3 -m json.tool policies.json > /dev/null && echo "✓ policies.json 格式正確"
python3 -m json.tool slp.json > /dev/null && echo "✓ slp.json 格式正確"
```

---

## 📦 傳輸檔案到 Client 端

### 方法 1: 從 Client 端使用 SCP (macOS/Linux)

在你的 **Mac** 上執行：

```bash
# 切換到專案目錄
cd "/Users/andruw/Documents/nbu ai"

# 下載 policies.json
scp root@your-nbu-server.company.com:/tmp/policies.json ./

# 下載 slp.json
scp root@your-nbu-server.company.com:/tmp/slp.json ./

# 驗證
ls -lh policies.json slp.json
```

### 方法 2: 使用 WinSCP (Windows)

1. 打開 WinSCP
2. 連線到 NBU Server:
   - 主機名稱: `your-nbu-server.company.com`
   - 使用者名稱: `root`
   - 密碼: (你的密碼)
3. 導航到 `/tmp` 目錄
4. 拖拽 `policies.json` 和 `slp.json` 到本機專案目錄

### 方法 3: 使用 FileZilla (Windows/macOS)

1. 打開 FileZilla
2. 設定 SFTP 連線到 NBU Server
3. 下載兩個 JSON 檔案到本機

### 方法 4: 使用 PSCP (Windows 命令列)

在 Windows **命令提示字元** 中執行：

```cmd
cd "C:\Users\YourName\Documents\nbu ai"

pscp root@your-nbu-server.company.com:/tmp/policies.json .
pscp root@your-nbu-server.company.com:/tmp/slp.json .
```

---

## ✅ 完整流程示例

### 範例 1: 快速執行（單一命令）

```bash
# 在 NBU Server 上一次執行完成
cd /tmp && \
  bppllist -allpolicies -json > policies.json && \
  /usr/openv/netbackup/bin/admincmd/nbstlutil list -slp -json > slp.json && \
  ls -lh *.json
```

### 範例 2: 完整工作流程

```bash
# ========================================
# 步驟 1: 在 NBU Server 上執行
# ========================================
ssh root@bksvr.company.com

cd /tmp
bppllist -allpolicies -json > policies.json
/usr/openv/netbackup/bin/admincmd/nbstlutil list -slp -json > slp.json
ls -lh policies.json slp.json
exit

# ========================================
# 步驟 2: 在 Mac 上傳輸檔案
# ========================================
cd "/Users/andruw/Documents/nbu ai"
scp root@bksvr.company.com:/tmp/policies.json ./
scp root@bksvr.company.com:/tmp/slp.json ./

# ========================================
# 步驟 3: 在 Mac 上處理
# ========================================
./process_local_json.sh
```

---

## 🔍 常見問題排除

### 問題 1: bppllist 命令找不到

**錯誤訊息**:
```
bash: bppllist: command not found
```

**解決方法**:
```bash
# 使用完整路徑
/usr/openv/netbackup/bin/admincmd/bppllist -allpolicies -json > policies.json
```

### 問題 2: 權限不足

**錯誤訊息**:
```
bppllist: cannot get policy information
```

**解決方法**:
- 確認使用 root 或有權限的帳號執行
- 確認 NetBackup 服務正在運行

### 問題 3: JSON 格式錯誤

**驗證方法**:
```bash
# 檢查檔案前幾行
head -20 policies.json

# 應該看到 JSON 格式的內容，例如:
# {
#   "policies": [
#     {
#       "policyName": "...",
#       ...
```

### 問題 4: SCP 連線失敗

**Windows 用戶**: 改用 WinSCP 圖形介面工具  
**macOS 用戶**: 確認 SSH 可正常連線

```bash
# 測試 SSH 連線
ssh root@your-nbu-server.company.com "echo 'Connection OK'"
```

---

## 📝 自動化建議（進階）

如果需要定期執行，可在 NBU Server 上建立排程腳本：

```bash
# 在 NBU Server 上建立腳本
cat > /usr/local/bin/export_nbu_json.sh << 'EOF'
#!/bin/bash
OUTPUT_DIR=/export/nbu_json
TIMESTAMP=$(date +%Y%m%d)

mkdir -p $OUTPUT_DIR

bppllist -allpolicies -json > $OUTPUT_DIR/policies_${TIMESTAMP}.json
/usr/openv/netbackup/bin/admincmd/nbstlutil list -slp -json > $OUTPUT_DIR/slp_${TIMESTAMP}.json

# 建立最新版本的符號連結
ln -sf $OUTPUT_DIR/policies_${TIMESTAMP}.json $OUTPUT_DIR/policies.json
ln -sf $OUTPUT_DIR/slp_${TIMESTAMP}.json $OUTPUT_DIR/slp.json

echo "Exported at $(date)" >> $OUTPUT_DIR/export.log
EOF

chmod +x /usr/local/bin/export_nbu_json.sh

# 加入 crontab (每週一早上 6 點執行)
echo "0 6 * * 1 /usr/local/bin/export_nbu_json.sh" | crontab -
```

---

**最後更新**: 2026-05-27  
**維護者**: NetBackup Team
