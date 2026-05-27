#!/usr/bin/env python3
"""
Policy + SLP 保留等級整合測試
重點：從 SLP 中取得實際的 RetentionLevel
"""

import json
from datetime import datetime


def load_slps(slp_file):
    """載入所有 SLP 資料，建立名稱索引"""
    slps = {}
    with open(slp_file, 'r') as f:
        content = f.read()
        objects = content.strip().split('\n}')
        for obj in objects:
            if obj.strip():
                try:
                    slp = json.loads(obj + '\n}')
                    slps[slp['SlpName']] = slp
                except:
                    pass
    return slps


def seconds_to_time(seconds):
    """將秒數轉換為 HH:MM 格式"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"


def get_slp_retention_info(slp_name, slps_dict):
    """從 SLP 取得 RetentionLevel 資訊"""
    if not slp_name or slp_name not in slps_dict:
        return None

    slp = slps_dict[slp_name]
    operations = slp.get('Operations', [])

    if not operations:
        return None

    # 通常取第一個 Operation 的 RetentionLevel
    op = operations[0]
    return {
        'retention_level': op.get('RetentionLevel'),
        'retention_type': op.get('RetentionTypeText'),
        'use_for': op.get('UseForText'),
        'residence': op.get('Residence'),
        'volume_pool': op.get('VolumePool'),
        'operations_count': len(operations)
    }


def analyze_policy_with_slp(policy, slps_dict):
    """分析 Policy 並整合 SLP 保留資訊"""

    output = []
    output.append("=" * 80)
    output.append(f"Policy + SLP 保留等級分析")
    output.append("=" * 80)

    # 基本資訊
    output.append(f"\n📋 Policy: {policy['class_name']}")
    output.append(f"   類型: {policy['pinfo']['PolicyTypeText']}")
    output.append(f"   狀態: {'✅ 啟用' if policy['pinfo']['active'] == 1 else '❌ 停用'}")

    # 客戶端
    if policy.get('clients'):
        output.append(f"\n🖥️  客戶端: {len(policy['clients'])} 個")
        for client in policy['clients'][:3]:
            output.append(f"   - {client['hostname']}")

    # Schedule 分析
    schedules = policy.get('schedule', [])
    if schedules:
        output.append(f"\n⏰ 排程分析 (共 {len(schedules)} 個)")

        for i, sch in enumerate(schedules):
            output.append(f"\n{'─' * 80}")
            output.append(f"Schedule {i+1}: {sch.get('sched_name', 'N/A')}")
            output.append(f"{'─' * 80}")

            # 排程類型
            schedule_types = {
                0: "Full Backup",
                1: "Differential Incremental",
                2: "Cumulative Incremental"
            }
            sch_type = sch.get('sched_type', 0)
            output.append(f"   類型: {schedule_types.get(sch_type, f'Type {sch_type}')}")

            # 頻率
            freq = sch.get('frequency', 0)
            freq_map = {86400: "每天", 604800: "每週", 3600: "每小時", 2592000: "每月"}
            freq_text = freq_map.get(freq, f"{freq} 秒")
            output.append(f"   頻率: {freq_text}")

            # 時間視窗
            if sch.get('days'):
                day = sch['days'][0]
                start_time = seconds_to_time(day.get('open', 0))
                duration_hours = day.get('duration', 0) / 3600
                output.append(f"   時間: {start_time} (持續 {duration_hours:.1f} 小時)")

            # ⭐⭐⭐ 關鍵：Residence 和 RetentionLevel 陣列
            output.append(f"\n   📦 儲存和保留設定:")

            residence_array = sch.get('residence', [])
            retention_array = sch.get('retention_level', [])

            # 顯示陣列結構
            output.append(f"\n      Policy 內建資訊:")
            output.append(f"         Residence 陣列:      {residence_array[:3]}... (共 {len(residence_array)} 個)")
            output.append(f"         Retention Level 陣列: {retention_array[:3]}... (共 {len(retention_array)} 個)")

            # 分析每個副本
            output.append(f"\n      副本分析:")

            max_copies = min(len(residence_array), len(retention_array), 3)  # 最多顯示 3 個副本

            for copy_idx in range(max_copies):
                residence_name = residence_array[copy_idx] if copy_idx < len(residence_array) else None
                policy_retention = retention_array[copy_idx] if copy_idx < len(retention_array) else None

                if residence_name:
                    output.append(f"\n      ┌─ 副本 {copy_idx + 1}")
                    output.append(f"      │  Policy 資訊:")
                    output.append(f"      │     - Residence: {residence_name}")
                    output.append(f"      │     - Retention Level: {policy_retention}")

                    # ⭐ 從 SLP 取得實際 RetentionLevel
                    slp_info = get_slp_retention_info(residence_name, slps_dict)

                    if slp_info:
                        output.append(f"      │")
                        output.append(f"      │  🔗 SLP 資訊: ({residence_name})")
                        output.append(f"      │     - ⭐ 實際 RetentionLevel: Level {slp_info['retention_level']}")
                        output.append(f"      │     - Retention Type: {slp_info['retention_type']}")
                        output.append(f"      │     - 用途: {slp_info['use_for']}")
                        output.append(f"      │     - 儲存位置: {slp_info['residence']}")
                        output.append(f"      │     - Volume Pool: {slp_info['volume_pool']}")

                        if slp_info['operations_count'] > 1:
                            output.append(f"      │     - Operations: {slp_info['operations_count']} 個步驟 (多層備份)")

                        # 對比
                        if policy_retention != slp_info['retention_level']:
                            output.append(f"      │")
                            output.append(f"      │  ⚠️  注意: Policy 的 retention_level ({policy_retention}) 與 SLP 不同 ({slp_info['retention_level']})")
                            output.append(f"      │           應以 SLP 的 RetentionLevel 為準")
                    else:
                        output.append(f"      │")
                        output.append(f"      │  ❌ 未找到對應的 SLP")
                        output.append(f"      │     可能原因: {residence_name} 不是 SLP 名稱，或是直接的儲存單元名稱")

                    output.append(f"      └─")
                elif copy_idx == 0:
                    # 第一個副本沒有 residence（使用預設）
                    output.append(f"\n      副本 1: 使用預設儲存 (NetBackup)")
                    output.append(f"         Retention Level: {policy_retention}")

    # 備份路徑
    if policy.get('include'):
        output.append(f"\n\n📁 備份路徑: {len(policy['include'])} 個")
        for path in policy['include'][:5]:
            output.append(f"   - {path}")

    return "\n".join(output)


def main():
    POLICIES_FILE = '/Users/andruw/Documents/nbu ai/policies.json'
    SLP_FILE = '/Users/andruw/Documents/nbu ai/slp.json'

    print("🔄 載入資料...")

    # 載入 SLP（建立索引）
    slps_dict = load_slps(SLP_FILE)
    print(f"   ✅ 載入 {len(slps_dict)} 個 SLPs")

    # 載入 Policies
    with open(POLICIES_FILE, 'r') as f:
        policies_data = json.load(f)

    print(f"   ✅ 載入 {len(policies_data['policies'])} 個 Policies")

    # 測試案例
    test_cases = [
        'PIC_NBU_Catalog_Online_bksvr',  # 有 residence 的 policy
        '21C_MSSQL_Online_21sunlike',    # 你提供的範例
    ]

    print(f"\n🧪 測試 {len(test_cases)} 個 policies\n")

    for test_name in test_cases:
        # 尋找 policy
        policy = None
        for p in policies_data['policies']:
            if p.get('class_name') == test_name:
                policy = p
                break

        if not policy:
            print(f"❌ 找不到 policy: {test_name}\n")
            continue

        # 分析
        report = analyze_policy_with_slp(policy, slps_dict)
        print(report)
        print("\n\n")

        # 儲存報告
        output_file = f'/Users/andruw/Documents/nbu ai/test_retention_{test_name}.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
            f.write(f"\n\n生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        print(f"💾 報告已儲存: {output_file}\n")


if __name__ == '__main__':
    main()
