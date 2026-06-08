import sqlite3, random, uuid
from datetime import datetime, timedelta

DB = "intelligence_assets.db"
ROWS = 15000

codenames = [
    "Phantom Jackal","Night Cobra","Silent Falcon","Ghost Orchid","Iron Krait",
    "Shadow Lynx","Black Komodo","Silver Panther","Crimson Fox","Blue Viper"
]

affiliations = ["RAW","IB","CIA","Mossad","GRU","FSB","MI6","ISI","MSS","DGSE"]
roles = ["Field Agent","Handler","Spy","Infiltrator","Sleeper Cell"]
priorities = ["Low","Medium","High","Critical"]
clearances = ["Confidential","Secret","Top Secret","Ultra-Black"]
statuses = ["Active","Undercover","Missing","Compromised","Terminated"]
infil_groups = ["Red Scorpion","Dark Hydra","Night Serpents","Silent Rift","Ghost Legion"]
comms = ["Daily","Weekly","Monthly","On Trigger"]
cities = ["Bangalore","Delhi","Moscow","Tel Aviv","Beijing","Karachi","London","Berlin","Tokyo","Dubai"]

def rand_time():
    now = datetime.utcnow()
    delta = timedelta(days=random.randint(0, 300), hours=random.randint(0, 23))
    return (now - delta).isoformat()

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS intelligence_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id TEXT,
    codename TEXT,
    real_name TEXT,
    nationality TEXT,
    affiliation TEXT,
    threat_level INTEGER,
    clearance_level TEXT,
    status TEXT,
    last_known_location TEXT,
    mission_role TEXT,
    mission_priority TEXT,
    handler_name TEXT,
    comms_frequency TEXT,
    infiltration_group TEXT,
    operation_code TEXT,
    last_contact_ts TEXT,
    reliability_score REAL,
    extraction_needed INTEGER,
    notes TEXT,
    updated_at TEXT
);
""")

for i in range(ROWS):
    asset_id = "AST-" + str(uuid.uuid4())[:8].upper()
    codename = random.choice(codenames)
    real_name = f"Agent {random.randint(100,999)}"
    nationality = random.choice(["IN","US","RU","CN","ISR","UK","PK","FR","JP"])
    affiliation = random.choice(affiliations)
    threat = random.randint(1,10)
    clearance = random.choice(clearances)
    status = random.choice(statuses)
    location = random.choice(cities) + ", " + random.choice(["IN","RU","US","ISR","CN","PK","UK"])
    role = random.choice(roles)
    priority = random.choice(priorities)
    handler = "Officer " + str(random.randint(10,99))
    comm = random.choice(comms)
    group = random.choice(infil_groups)
    op = "OP-" + str(uuid.uuid4())[:6].upper()
    last_contact = rand_time()
    reliability = round(random.uniform(0.1,1.0),3)
    extract = 1 if threat > 7 and reliability < 0.5 else 0
    notes = "" if random.random() > 0.95 else "High-risk field intel"
    updated = rand_time()

    cur.execute("""
        INSERT INTO intelligence_assets (
            asset_id,codename,real_name,nationality,affiliation,
            threat_level,clearance_level,status,last_known_location,
            mission_role,mission_priority,handler_name,comms_frequency,
            infiltration_group,operation_code,last_contact_ts,
            reliability_score,extraction_needed,notes,updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """,
    (asset_id,codename,real_name,nationality,affiliation,threat,clearance,status,
     location,role,priority,handler,comm,group,op,last_contact,
     reliability,extract,notes,updated))

conn.commit()
conn.close()

print("intelligence_assets.db created with 15000 spy records.")
