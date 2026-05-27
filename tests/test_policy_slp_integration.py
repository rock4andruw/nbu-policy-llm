#!/usr/bin/env python3
"""
測試腳本：Policy + SLP 資料整合
目的：驗證如何將單一 Policy 的資訊與 SLP 資料結合
"""

import json
from datetime import datetime


def seconds_to_time(seconds):
    """將秒數轉換為 HH:MM 格式"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"


def load_slps(slp_file):
    """載入所有 SLP 資料"""
    slps = []
    with open(slp_file, 'r') as f:
        content = f.read()
        objects = content.strip().split('\n}')
        for obj in objects:
            if obj.strip():
                try:
                    slps.append(json.loads(obj + '\n}'))
                except:
                    pass
    return slps


def find_policy(policies_data, policy_name):
    """尋找指定的 policy"""
    policies = policies_data['policies']
    for p in policies:
        if p.get('class_name') == policy_name:
            return p
    return None


def format_policy_with_slp(policy, slps):
    """格式化 Policy 資訊並嘗試關聯 SLP"""

    output = []
    output.append("=" * 70)
    output.append(f"Policy + SLP 整合報告")
    output.append("=" * 70)

    # 基本資訊
    output.append(f"\n📋 Policy 基本資訊")
    output.append(f"   名稱: {policy['class_name']}")
    output.append(f"   類型: {policy['pinfo']['PolicyTypeText']}")
    output.append(f"   狀態: {'✅ 啟用' if policy['pinfo']['active'] == 1 else '❌ 停用'}")
    output.append(f"   Category ID: {policy['pinfo'].get('classID', 'N/A')}")

    # 客戶端
    if policy.get('clients'):
        output.append(f"\n🖥️  客戶端 (共 {len(policy['clients'])} 個)")
        for client in policy['clients'][:5]:
            output.append(f"   - {client['hostname']} ({client.get('ext_info', 'N/A')})")

    # Schedule 資訊
    schedules = policy.get('schedule', [])
    if schedules:
        output.append(f"\n⏰ 排程資訊 (共 {len(schedules)} 個)")
        for i, sch in enumerate(schedules):
            output.append(f"\n   Schedule {i+1}: {sch.get('sched_name', sch.get('name', 'N/A'))}")

            # 排程類型
            schedule_types = {
                0: "Full Backup",
                1: "Differential Incremental",
                2: "Cumulative Incremental",
                3: "User Backup",
                4: "User Archive"
            }
            sch_type_num = sch.get('sched_type', sch.get('type', 0))
            sch_type = schedule_types.get(sch_type_num, f"Type {sch_type_num}")
            output.append(f"      類型: {sch_type}")

            # 頻率
            freq = sch.get('frequency', 0)
            if freq == 86400:
                freq_text = "每天"
            elif freq == 604800:
                freq_text = "每週"
            elif freq == 3600:
                freq_text = "每小時"
            else:
                freq_text = f"{freq} 秒"
            output.append(f"      頻率: {freq_text}")

            # 時間視窗
            if sch.get('days'):
                day = sch['days'][0]
                start_time = seconds_to_time(day.get('open', 0))
                duration_hours = day.get('duration', 0) / 3600
                output.append(f"      時間: {start_time} (持續 {duration_hours:.1f} 小時)")

            # 保留等級
            retention = sch.get('retention', [0])[0]
            output.append(f"      保留: Level {retention}")

            # Residence (Storage Unit)
            residence = sch.get('res', 'NetBackup')
            output.append(f"      儲存單元: {residence}")

            # 搜尋相關 SLP
            output.append(f"\n      🔗 相關 SLP 搜尋:")
            related_slps = []
            for slp in slps:
                for op in slp.get('Operations', []):
                    if residence.lower() in op.get('Residence', '').lower():
                        related_slps.append(slp)
                        break

            if related_slps:
                output.append(f"         找到 {len(related_slps)} 個可能相關的 SLP:")
                for slp in related_slps[:3]:
                    output.append(f"         - {slp['SlpName']}")
                    for op in slp.get('Operations', [])[:2]:
                        output.append(f"            步驟 {op['OperationIndex']}: {op['UseForText']} -> {op['Residence']}")
            else:
                output.append(f"         ⚠️  未找到直接關聯的 SLP")
                output.append(f"         (Storage Unit '{residence}' 可能未使用 SLP 管理)")

    # 備份路徑
    if policy.get('include'):
        output.append(f"\n📁 備份路徑 (共 {len(policy['include'])} 個)")
        for path in policy['include'][:10]:
            output.append(f"   - {path}")

    # 特殊功能
    pinfo = policy['pinfo']
    features = []
    if pinfo.get('client_compress') == 1:
        features.append("客戶端壓縮")
    if pinfo.get('client_encrypt') == 1:
        features.append("客戶端加密")
    if pinfo.get('UseAccelerator'):
        features.append("加速器")
    if pinfo.get('collect_tir_info') == 1:
        features.append("TIR 資訊收集")

    if features:
        output.append(f"\n⚙️  特殊功能")
        for f in features:
            output.append(f"   ✅ {f}")

    return "\n".join(output)


def main():
    # 設定檔案路徑
    POLICIES_FILE = '/Users/andruw/Documents/nbu ai/policies.json'
    SLP_FILE = '/Users/andruw/Documents/nbu ai/slp.json'
    TEST_POLICY = '21C_WIN_DATA_21sunlike'

    print(f"🔄 載入資料...")

    # 載入資料
    with open(POLICIES_FILE, 'r') as f:
        policies_data = json.load(f)

    slps = load_slps(SLP_FILE)

    print(f"   ✅ 載入 {len(policies_data['policies'])} 個 policies")
    print(f"   ✅ 載入 {len(slps)} 個 SLPs")

    # 尋找測試 policy
    policy = find_policy(policies_data, TEST_POLICY)

    if not policy:
        print(f"\n❌ 找不到 policy: {TEST_POLICY}")
        return

    # 格式化輸出
    print(f"\n")
    report = format_policy_with_slp(policy, slps)
    print(report)

    # 儲存報告
    output_file = f'/Users/andruw/Documents/nbu ai/test_output_{TEST_POLICY}_with_slp.txt'
    with open(output_file, 'w') as f:
        f.write(report)
        f.write(f"\n\n生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"\n\n💾 報告已儲存: {output_file}")


if __name__ == '__main__':
    main()
