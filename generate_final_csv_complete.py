#!/usr/bin/env python3
"""
最終版本：完整保留所有資訊
- policy_retention_level (原有)
- SLP 相關資訊 (新增)
- 不做判定，兩者都保留
"""

import json
import csv
from datetime import datetime


def load_slps(slp_file):
    """載入 SLP 資料"""
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


def load_retention_map(retention_file):
    """載入 Retention Level 對照表"""
    with open(retention_file, 'r') as f:
        data = json.load(f)

    retention_map = {}
    for item in data['retention_levels']:
        level = item['level']
        retention_map[level] = {
            'label': item['label'],
            'period': item['period'],
            'units': item['units']
        }
    return retention_map


def get_chinese_label(ret_info):
    """轉換成中文標籤"""
    period = ret_info['period']
    units = ret_info['units']

    if units == 'infinite':
        return '無限期'
    elif units == 'weeks':
        return f'{period} 週'
    elif units == 'months':
        return f'{period} 個月'
    elif units == 'years':
        return f'{period} 年'
    elif units == 'days':
        return f'{period} 天'
    elif units == 'hours':
        return f'{period} 小時'
    else:
        return ret_info['label']


def seconds_to_time(seconds):
    """將秒數轉換為 HH:MM"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"


def get_frequency_text(frequency):
    """頻率轉文字"""
    freq_map = {
        3600: "每 1 小時",
        86400: "每天",
        604800: "每週",
        2592000: "每月"
    }
    return freq_map.get(frequency, f"{frequency} 秒")


def generate_csv_rows(policies_data, slps_dict, retention_map, sample_policies=None):
    """生成 CSV 資料"""
    rows = []

    # 如果指定了樣本，只處理這些 policies
    if sample_policies:
        policies_to_process = []
        for policy_name in sample_policies:
            for p in policies_data['policies']:
                if p.get('class_name') == policy_name:
                    policies_to_process.append(p)
                    break
    else:
        policies_to_process = policies_data['policies']

    for policy in policies_to_process:
        pinfo = policy.get('pinfo', {})
        schedules = policy.get('schedule', [])
        clients = policy.get('clients', [])

        # 從 pinfo.residence 取得 SLP 名稱
        pinfo_residence = pinfo.get('residence', [])
        slp_name = pinfo_residence[0] if pinfo_residence and pinfo_residence[0] else None

        # ⭐ 檢查是否為 SLP（是否存在於 slp.json 中）
        is_slp = slp_name and slp_name in slps_dict

        # 處理每個 schedule 和 client
        for schedule in schedules:
            # ⭐ Policy 的 retention_level（原有欄位）
            schedule_retention = schedule.get('retention_level', [])
            policy_retention_level = schedule_retention[0] if schedule_retention else 0

            # ⭐ SLP 的資訊（新增欄位）
            slp_retention_level = None
            slp_retention_type = None
            slp_actual_storage = None
            slp_retention_period = None
            slp_retention_label = None

            if slp_name and slp_name in slps_dict:
                slp = slps_dict[slp_name]
                ops = slp.get('Operations', [])
                if ops:
                    op = ops[0]
                    slp_retention_level = op.get('RetentionLevel')
                    slp_retention_type = op.get('RetentionTypeText')
                    slp_actual_storage = op.get('Residence')

                    # 從 retention_level.json 查詢 SLP 的保留期限
                    if slp_retention_level in retention_map:
                        ret_info = retention_map[slp_retention_level]
                        slp_retention_period = ret_info['label']
                        slp_retention_label = f"保留 {get_chinese_label(ret_info)}"

            # ⭐ Policy 的保留期限（從 policy retention_level 查詢）
            policy_retention_period = None
            policy_retention_label = None
            if policy_retention_level in retention_map:
                ret_info = retention_map[policy_retention_level]
                policy_retention_period = ret_info['label']
                policy_retention_label = f"保留 {get_chinese_label(ret_info)}"

            # ⭐ 判定最終使用的保留資訊
            if is_slp and slp_retention_level is not None:
                # 情況 1：有 SLP 且 SLP 有 retention → 使用 SLP
                retention_source = "SLP"
                final_retention_level = slp_retention_level
                final_retention_period = slp_retention_period
                final_retention_label = slp_retention_label
            else:
                # 情況 2：無 SLP 或 SLP 無 retention → 使用 Policy
                retention_source = "Policy"
                final_retention_level = policy_retention_level
                final_retention_period = policy_retention_period
                final_retention_label = policy_retention_label

            for client in clients:
                row = {
                    'document_type': 'NetBackup Policy',
                    'policy_name': policy.get('class_name', ''),
                    'policy_type': pinfo.get('PolicyTypeText', ''),
                    'status': 'Active' if pinfo.get('active') == 1 else 'Inactive',
                    'client_hostname': client.get('hostname', ''),
                    'client_os': client.get('ext_info', ''),
                }

                # 新增：儲存位置名稱
                row['storage_residence_name'] = slp_name if slp_name else 'N/A'

                # Schedule 資訊
                schedule_type_map = {
                    0: "Full Backup",
                    1: "Differential Incremental",
                    2: "Cumulative Incremental"
                }
                sch_type = schedule.get('sched_type', 0)
                row['schedule_name'] = schedule.get('label', 'N/A')
                row['schedule_type'] = schedule_type_map.get(sch_type, f'Type {sch_type}')

                # 時間資訊
                freq = schedule.get('frequency', 0)
                row['frequency_text'] = get_frequency_text(freq)

                if schedule.get('days'):
                    day = schedule['days'][0]
                    start = seconds_to_time(day.get('open', 0))
                    end = seconds_to_time(day.get('open', 0) + day.get('duration', 0))
                    row['backup_time'] = f'每天 {start}~{end}'
                else:
                    row['backup_time'] = 'N/A'

                # ⭐ 最終保留資訊（供 LLM 使用）
                row['retention_source'] = retention_source
                row['final_retention_level'] = f"Level {final_retention_level}"
                row['final_retention_period'] = final_retention_period if final_retention_period else 'N/A'
                row['final_retention_label'] = final_retention_label if final_retention_label else 'N/A'

                # ⭐ Policy 保留資訊（詳細資訊）
                row['policy_retention_level'] = f"Level {policy_retention_level}"
                row['policy_retention_period'] = policy_retention_period if policy_retention_period else 'N/A'
                row['policy_retention_label'] = policy_retention_label if policy_retention_label else 'N/A'

                # ⭐ SLP 保留資訊（詳細資訊）
                row['slp_name'] = slp_name if slp_name else 'N/A'
                row['slp_retention_level'] = f"Level {slp_retention_level}" if slp_retention_level is not None else 'N/A'
                row['slp_retention_type'] = slp_retention_type if slp_retention_type else 'N/A'
                row['slp_actual_storage'] = slp_actual_storage if slp_actual_storage else 'N/A'
                row['slp_retention_period'] = slp_retention_period if slp_retention_period else 'N/A'
                row['slp_retention_label'] = slp_retention_label if slp_retention_label else 'N/A'

                # 其他資訊
                row['storage_pool'] = schedule.get('res', 'NetBackup')

                # 備份路徑
                paths = policy.get('include', [])
                row['backup_paths'] = '; '.join(paths[:3]) if paths else 'N/A'

                # 特殊功能
                features = []
                if pinfo.get('client_compress') == 1:
                    features.append('客戶端壓縮')
                if pinfo.get('client_encrypt') == 1:
                    features.append('客戶端加密')
                if pinfo.get('UseAccelerator'):
                    features.append('加速器')
                row['features'] = ', '.join(features) if features else ''

                # ⭐ 原有欄位：search_keywords
                keywords = [
                    policy.get('class_name', ''),
                    client.get('hostname', ''),
                    client.get('ext_info', ''),
                    pinfo.get('PolicyTypeText', ''),
                    slp_name if slp_name else ''
                ]
                row['search_keywords'] = ', '.join([k for k in keywords if k and k != 'N/A'])

                # ⭐ 原有欄位：query_examples
                policy_name_str = policy.get('class_name', '')
                client_name = client.get('hostname', '')
                examples = [
                    f"什麼是 {policy_name_str} 策略？",
                    f"{client_name} 的備份設定是什麼？",
                    f"{pinfo.get('PolicyTypeText', '')} 類型的策略有哪些功能？"
                ]
                row['query_examples'] = '; '.join(examples)

                # ⭐ 原有欄位：generation_date
                row['generation_date'] = datetime.now().strftime('%Y-%m-%d')

                rows.append(row)

    return rows


def main():
    # 檔案路徑
    POLICIES_FILE = '/Users/andruw/Documents/nbu ai/policies.json'
    SLP_FILE = '/Users/andruw/Documents/nbu ai/slp.json'
    RETENTION_FILE = '/Users/andruw/Documents/nbu ai/retention_level.json'

    print("=" * 80)
    print("✅ 最終版本：完整保留 Policy + SLP 資訊 + 自動判定邏輯")
    print("=" * 80)

    # 載入資料
    print("\n🔄 載入資料...")
    with open(POLICIES_FILE, 'r') as f:
        policies_data = json.load(f)

    slps_dict = load_slps(SLP_FILE)
    retention_map = load_retention_map(RETENTION_FILE)

    print(f"   ✅ Policies: {len(policies_data['policies'])}")
    print(f"   ✅ SLPs: {len(slps_dict)}")
    print(f"   ✅ Retention Levels: {len(retention_map)}")

    # 生成完整資料（所有 policies）
    print(f"\n📝 生成完整資料（所有 {len(policies_data['policies'])} 個 policies）...")

    rows = generate_csv_rows(policies_data, slps_dict, retention_map)

    print(f"   ✅ 生成 {len(rows)} 筆資料\n")

    # 儲存 CSV
    output_file = '/Users/andruw/Documents/nbu ai/policies_llm_final.csv'

    if rows:
        fieldnames = rows[0].keys()

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print(f"💾 CSV 已儲存: {output_file}")
        print(f"   欄位數: {len(fieldnames)}")
        print(f"   資料筆數: {len(rows)}")

        # 統計 retention_source 分佈
        print(f"\n📊 Retention Source 分佈:")
        sources = {}
        for row in rows:
            src = row['retention_source']
            sources[src] = sources.get(src, 0) + 1

        for src, count in sorted(sources.items()):
            print(f"   {src}: {count} 筆 ({count/len(rows)*100:.1f}%)")

        # 驗證 03_DataDomain_group
        datadomain_count = sum(1 for r in rows if '03_DataDomain' in r.get('storage_residence_name', ''))
        print(f"\n🔍 使用 03_DataDomain_group: {datadomain_count} 筆")
        if datadomain_count > 0:
            policy_source_count = sum(1 for r in rows
                                     if '03_DataDomain' in r.get('storage_residence_name', '')
                                     and r['retention_source'] == 'Policy')
            print(f"   其中使用 Policy retention: {policy_source_count} 筆 ✓")

        # 顯示欄位列表
        print(f"\n📋 完整欄位列表 ({len(fieldnames)} 個):")
        for i, field in enumerate(fieldnames, 1):
            marker = ""
            if field.startswith('final_retention') or field == 'retention_source':
                marker = " 🎯 最終"
            elif field.startswith('policy_retention'):
                marker = " 📝 Policy"
            elif field.startswith('slp_'):
                marker = " ⭐ SLP"
            elif field in ['search_keywords', 'query_examples', 'generation_date']:
                marker = " 📌 原有"
            print(f"   {i:2d}. {field}{marker}")

        # 顯示範例
        print(f"\n" + "=" * 80)
        print("📊 資料範例")
        print("=" * 80)

        for i, row in enumerate(rows[:2]):
            print(f"\n【範例 {i+1}】 {row['policy_name']}")
            print(f"  客戶端: {row['client_hostname']}")
            print(f"  儲存位置: {row['storage_residence_name']}")
            print(f"  時間: {row['backup_time']}")
            print(f"\n  🎯 最終保留資訊 (供 LLM 使用):")
            print(f"     來源: {row['retention_source']}")
            print(f"     Level: {row['final_retention_level']}")
            print(f"     期限: {row['final_retention_period']}")
            print(f"     標籤: {row['final_retention_label']}")
            print(f"\n  📝 Policy 保留資訊:")
            print(f"     Level: {row['policy_retention_level']}")
            print(f"     期限: {row['policy_retention_period']}")
            print(f"     標籤: {row['policy_retention_label']}")
            print(f"\n  ⭐ SLP 保留資訊:")
            print(f"     SLP: {row['slp_name']}")
            print(f"     Level: {row['slp_retention_level']}")
            print(f"     Type: {row['slp_retention_type']}")
            print(f"     期限: {row['slp_retention_period']}")
            print(f"     標籤: {row['slp_retention_label']}")


if __name__ == '__main__':
    main()
