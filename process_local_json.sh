#!/bin/bash
################################################################################
# NetBackup Policy 本地處理腳本 (macOS/Linux)
#
# 用途: 將本地的 policies.json 和 slp.json 轉換為知識庫 CSV
#
# 前置條件:
#   1. policies.json 和 slp.json 已從 NBU Server 複製到本目錄
#   2. retention_level.json 存在於本目錄
#   3. Python 3.x 已安裝
#
# 使用方式:
#   ./process_local_json.sh
#
################################################################################

set -e  # 遇到錯誤立即停止

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 設定變數
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${SCRIPT_DIR}/backups"

# 檔案名稱
POLICIES_JSON="policies.json"
SLP_JSON="slp.json"
RETENTION_JSON="retention_level.json"
OUTPUT_CSV="policies_llm_final.csv"

################################################################################
# 函數定義
################################################################################

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  NetBackup Policy 本地處理工具 (macOS/Linux) v1.0          ${BLUE}║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo -e "${GREEN}▶${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

check_required_files() {
    print_step "步驟 1/4: 檢查必要檔案..."

    local missing_files=0

    if [ ! -f "${SCRIPT_DIR}/${POLICIES_JSON}" ]; then
        print_error "找不到 ${POLICIES_JSON}"
        missing_files=1
    else
        local size=$(du -h "${SCRIPT_DIR}/${POLICIES_JSON}" | cut -f1)
        print_success "${POLICIES_JSON} 存在 (${size})"
    fi

    if [ ! -f "${SCRIPT_DIR}/${SLP_JSON}" ]; then
        print_error "找不到 ${SLP_JSON}"
        missing_files=1
    else
        local size=$(du -h "${SCRIPT_DIR}/${SLP_JSON}" | cut -f1)
        print_success "${SLP_JSON} 存在 (${size})"
    fi

    if [ ! -f "${SCRIPT_DIR}/${RETENTION_JSON}" ]; then
        print_error "找不到 ${RETENTION_JSON}"
        missing_files=1
    else
        print_success "${RETENTION_JSON} 存在"
    fi

    if [ $missing_files -eq 1 ]; then
        echo ""
        print_error "缺少必要檔案，請先完成以下步驟："
        echo ""
        echo "  在 NBU Server 上執行:"
        echo "    bppllist -allpolicies -json > policies.json"
        echo "    nbstlutil list -slp -json > slp.json"
        echo ""
        echo "  傳輸到本機:"
        echo "    scp root@nbu-server:/path/to/policies.json ."
        echo "    scp root@nbu-server:/path/to/slp.json ."
        echo ""
        exit 1
    fi
    echo ""
}

backup_old_files() {
    print_step "步驟 2/4: 備份舊檔案..."

    mkdir -p "${BACKUP_DIR}"

    if [ -f "${SCRIPT_DIR}/${OUTPUT_CSV}" ]; then
        cp "${SCRIPT_DIR}/${OUTPUT_CSV}" "${BACKUP_DIR}/${OUTPUT_CSV}_${TIMESTAMP}"
        print_info "已備份: ${OUTPUT_CSV}"
    else
        print_info "無舊檔案需要備份"
    fi

    print_success "備份完成: ${BACKUP_DIR}"
    echo ""
}

generate_csv() {
    print_step "步驟 3/4: 生成知識庫 CSV..."

    if [ ! -f "${SCRIPT_DIR}/generate_final_csv_complete.py" ]; then
        print_error "找不到生成腳本: generate_final_csv_complete.py"
        exit 1
    fi

    print_info "執行 Python 腳本..."
    cd "${SCRIPT_DIR}"
    python3 generate_final_csv_complete.py

    if [ $? -eq 0 ] && [ -f "${SCRIPT_DIR}/${OUTPUT_CSV}" ]; then
        local lines=$(wc -l < "${SCRIPT_DIR}/${OUTPUT_CSV}")
        local size=$(du -h "${SCRIPT_DIR}/${OUTPUT_CSV}" | cut -f1)
        local records=$((lines - 1))  # 扣除標題行
        print_success "CSV 生成完成: ${records} 筆記錄 (${size})"
    else
        print_error "CSV 生成失敗"
        exit 1
    fi
    echo ""
}

validate_output() {
    print_step "步驟 4/4: 驗證輸出..."

    # 檢查 CSV 格式
    print_info "檢查 CSV 格式..."
    local header_count=$(head -1 "${SCRIPT_DIR}/${OUTPUT_CSV}" | awk -F',' '{print NF}')
    if [ "$header_count" -eq 30 ]; then
        print_success "欄位數量正確: ${header_count} 個"
    else
        print_warning "欄位數量異常: ${header_count} 個（預期 30 個）"
    fi

    # 檢查 retention_source 分佈
    print_info "檢查 retention_source 分佈..."
    python3 << 'EOF'
import csv
with open('policies_llm_final.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    data = list(reader)
    sources = {}
    for row in data:
        src = row.get('retention_source', 'Unknown')
        sources[src] = sources.get(src, 0) + 1

    total = len(data)
    for src, count in sorted(sources.items()):
        pct = count/total*100 if total > 0 else 0
        print(f"     {src}: {count} 筆 ({pct:.1f}%)")
EOF

    echo ""
}

show_summary() {
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}  處理完成！                                                  ${GREEN}║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "📁 輸出檔案:"
    echo "   ${SCRIPT_DIR}/${OUTPUT_CSV}"
    echo ""
    echo "📦 備份位置:"
    echo "   ${BACKUP_DIR}"
    echo ""
    echo "🎯 下一步:"
    echo "   1. 檢查輸出檔案: less ${OUTPUT_CSV}"
    echo "   2. 上傳到公司知識庫"
    echo "   3. 測試查詢功能"
    echo ""
    echo "📝 記錄:"
    echo "   生成時間: ${TIMESTAMP}"
    echo ""
}

################################################################################
# 主程式
################################################################################

main() {
    print_header

    # 環境檢查
    print_step "環境檢查..."
    if ! command -v python3 &> /dev/null; then
        print_error "找不到 Python 3"
        echo "請安裝 Python 3: https://www.python.org/downloads/"
        exit 1
    fi
    print_info "Python: $(python3 --version)"
    echo ""

    # 執行流程
    check_required_files
    backup_old_files
    generate_csv
    validate_output
    show_summary
}

# 執行主程式
main "$@"
