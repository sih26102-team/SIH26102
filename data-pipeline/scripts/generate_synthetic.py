import os
import random
import pandas as pd
from datetime import datetime, timedelta

def generate_data():
    print("Generating CivicShield Synthetic Data using REAL MPLADS allocations...")
    
    raw_csv_path = os.path.join(os.path.dirname(__file__), "..", "raw_data", "real_mplads_data.csv")
    out_dir = os.path.join(os.path.dirname(__file__), "..", "processed_data")
    os.makedirs(out_dir, exist_ok=True)
    
    # Read raw data
    try:
        raw_df = pd.read_csv(raw_csv_path, dtype=str)
    except Exception as e:
        print(f"Failed to read real data: {e}")
        return

    # Filter out grand total or empty
    raw_df = raw_df[raw_df['Sr. No.'] != 'Grand Total']
    raw_df = raw_df.dropna(subset=['State', "Hon'ble Members of Parliaments"])

    states = []
    districts = []
    constituencies = []
    mps = []
    agencies = []
    projects = []
    expenditures = []

    state_map = {}
    district_map = {}
    constituency_map = {}
    agency_map = {}
    
    state_id_counter = 1
    dist_id_counter = 1
    const_id_counter = 1
    mp_id_counter = 1
    agency_id_counter = 1
    prj_id_counter = 1
    exp_id_counter = 1

    categories = ['Infrastructure', 'Water & Sanitation', 'Healthcare', 'Education', 'Roads & Pathways']
    statuses = ['completed', 'ongoing', 'stalled', 'sanctioned', 'recommended']

    for _, row in raw_df.iterrows():
        state_name = row.get('State', '').strip()
        mp_name = row.get("Hon'ble Members of Parliaments", '').strip()
        const_name = row.get('Constituency', '').strip()
        allocated_amt_str = str(row.get('Allocated AMOUNT ( ₹ )', '0')).replace(',', '').strip()
        if not allocated_amt_str or allocated_amt_str == 'nan':
            allocated_amt = 0.0
        else:
            try:
                allocated_amt = float(allocated_amt_str)
            except:
                allocated_amt = 0.0
                
        if not state_name or not mp_name:
            continue

        # 1. State
        if state_name not in state_map:
            state_map[state_name] = state_id_counter
            states.append({'state_id': state_id_counter, 'state_name': state_name})
            state_id_counter += 1
        s_id = state_map[state_name]
        
        # 2. District & Constituency (Mapping 1:1 for simplicity if district not provided)
        dist_name = const_name or f"Dist-{mp_name}"
        if dist_name not in district_map:
            district_map[dist_name] = dist_id_counter
            districts.append({'district_id': dist_id_counter, 'district_name': dist_name, 'state_id': s_id})
            dist_id_counter += 1
        d_id = district_map[dist_name]

        if const_name not in constituency_map:
            constituency_map[const_name] = const_id_counter
            constituencies.append({'constituency_id': const_id_counter, 'constituency_name': const_name, 'district_id': d_id})
            const_id_counter += 1
        c_id = constituency_map[const_name]
        
        # 3. Agency
        if d_id not in agency_map:
            agency_map[d_id] = agency_id_counter
            agencies.append({
                'agency_id': agency_id_counter, 
                'agency_name': f"PWD {dist_name}", 
                'agency_type': 'Government', 
                'district_id': d_id, 
                'status': 'ACTIVE'
            })
            agency_id_counter += 1
        a_id = agency_map[d_id]

        # 4. MP
        m_id = mp_id_counter
        mps.append({
            'mp_id': m_id,
            'name': mp_name,
            'constituency_id': c_id,
            'state_id': s_id,
            'parliamentary_house': 'Lok Sabha',
            'active_period': '2024-2029'
        })
        mp_id_counter += 1

        # 5. Projects
        # Split allocated amount into 2 projects per MP
        if allocated_amt > 0:
            p1_amt = round(allocated_amt * random.uniform(0.3, 0.7), 2)
            p2_amt = allocated_amt - p1_amt
            project_amts = [p1_amt, p2_amt]
        else:
            project_amts = [5000000.0, 2500000.0]

        for sanc in project_amts:
            project_id = f"PRJ-2026-{prj_id_counter:04d}"
            prj_id_counter += 1
            
            category = random.choice(categories)
            status = random.choice(statuses)
            rel = sanc if status == 'completed' else (sanc * 0.7 if status in ['ongoing', 'stalled'] else 0)
            
            progress = 0.0
            exp = 0.0
            
            is_anomaly = random.random() < 0.1
            if is_anomaly:
                anomaly_type = random.choice(["HIGH_SPEND_LOW_PROGRESS", "STALLED_LONG_TIME"])
                if anomaly_type == "HIGH_SPEND_LOW_PROGRESS":
                    status = 'ongoing'
                    exp = round(rel * 0.95, 2)
                    progress = round(random.uniform(2.0, 10.0), 2)
                else:
                    status = 'stalled'
                    exp = round(rel * 0.5, 2)
                    progress = round(random.uniform(20.0, 40.0), 2)
            else:
                if status == 'completed':
                    progress = 100.0
                    exp = rel
                elif status == 'ongoing':
                    progress = round(random.uniform(10.0, 90.0), 2)
                    exp = round(rel * (progress / 100.0) * random.uniform(0.9, 1.1), 2)
                elif status == 'stalled':
                    progress = round(random.uniform(10.0, 80.0), 2)
                    exp = round(rel * (progress / 100.0), 2)
            
            exp = min(exp, rel)
            rel = min(rel, sanc)

            sanction_date = datetime(2024, 1, 15) + timedelta(days=random.randint(0, 100))
            start_date = sanction_date + timedelta(days=random.randint(10, 30)) if status != 'recommended' else None
            
            projects.append({
                'project_id': project_id,
                'project_title': f"{category} Work {prj_id_counter}",
                'description': f"Construction and development of {category.lower()} facilities.",
                'mp_id': m_id,
                'constituency_id': c_id,
                'state_id': s_id,
                'district_id': d_id,
                'agency_id': a_id,
                'category': category,
                'sanctioned_amount': sanc,
                'cost_estimate': sanc,
                'released_amount': rel,
                'expenditure': exp,
                'project_status': status,
                'sanction_date': sanction_date.strftime('%Y-%m-%d'),
                'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
                'expected_completion_date': (sanction_date + timedelta(days=365)).strftime('%Y-%m-%d'),
                'actual_completion_date': (start_date + timedelta(days=200)).strftime('%Y-%m-%d') if status == 'completed' else None,
                'progress_percentage': progress,
                'latitude': round(random.uniform(17.0, 28.0), 4),
                'longitude': round(random.uniform(72.0, 88.0), 4),
                'data_source': 'REAL_MPLADS'
            })
            
            if exp > 0:
                num_tx = random.randint(1, 3)
                split_amount = round(exp / num_tx, 2)
                tx_date = start_date
                for t in range(num_tx):
                    tx_date += timedelta(days=30)
                    expenditures.append({
                        'expenditure_id': exp_id_counter,
                        'project_id': project_id,
                        'transaction_ref': f"TXN-{random.randint(100000, 999999)}",
                        'amount': split_amount,
                        'date': tx_date.strftime('%Y-%m-%d'),
                        'expenditure_type': 'CIVIL_WORK',
                        'status': 'CLEARED',
                        'source': 'PFMS_MOCK'
                    })
                    exp_id_counter += 1

    # Inject PRJ-2026-1042 for demo exactly at index 42
    if len(projects) > 42:
        projects[42].update({
            'project_id': 'PRJ-2026-1042',
            'project_title': 'Community Hall Construction',
            'description': 'Building a multi-purpose community hall in local area.',
            'category': 'Infrastructure',
            'sanctioned_amount': 5000000.0,
            'cost_estimate': 5000000.0,
            'released_amount': 4500000.0,
            'expenditure': 4200000.0,
            'project_status': 'ongoing',
            'sanction_date': '2023-01-10',
            'start_date': '2023-02-15',
            'expected_completion_date': '2024-01-09',
            'actual_completion_date': None,
            'progress_percentage': 15.0, # Massive mismatch: 84% spend, 15% progress
            'data_source': 'PROTOTYPE_SYNTHETIC'
        })
    
    pd.DataFrame(states).to_csv(os.path.join(out_dir, "states.csv"), index=False)
    pd.DataFrame(districts).to_csv(os.path.join(out_dir, "districts.csv"), index=False)
    pd.DataFrame(constituencies).to_csv(os.path.join(out_dir, "constituencies.csv"), index=False)
    pd.DataFrame(mps).to_csv(os.path.join(out_dir, "mps.csv"), index=False)
    pd.DataFrame(agencies).to_csv(os.path.join(out_dir, "agencies.csv"), index=False)
    pd.DataFrame(projects).to_csv(os.path.join(out_dir, "projects.csv"), index=False)
    pd.DataFrame(expenditures).to_csv(os.path.join(out_dir, "expenditures.csv"), index=False)
    
    print(f"Generated data using real MPs. Total projects: {len(projects)}")

if __name__ == "__main__":
    generate_data()
