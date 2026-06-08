# honeypot_app.py
# Honeypot service (port 5001)
# - Serves 3 distinct decoy personas (finance, scada, military) dynamically
# - Scrambles assets and injects honey-token configuration files
# - Logs accesses to honeypot.db and triggers active warning alarms

from flask import Flask, request, session, render_template, url_for, jsonify, Response
import sqlite3, os, uuid, json, hashlib, random, datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HONEYPOT_DB = os.path.join(BASE_DIR, "honeypot.db")
REAL_DB = os.path.join(BASE_DIR, "intelligence_assets.db")
MAIN_DB = os.path.join(BASE_DIR, "cyber_defense.db")

app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("HONEYPOT_SECRET", "hp-secret-change-me")

# -------------------- DB helpers --------------------
def get_hp_db():
    conn = sqlite3.connect(HONEYPOT_DB, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
    except Exception:
        pass
    return conn

def init_hp_db():
    conn = get_hp_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS honeypot_access (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sid TEXT,
            ip_address TEXT,
            user_agent TEXT,
            endpoint TEXT,
            method TEXT,
            payload TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# -------------------- Dynamic Persona Helpers --------------------
def _get_active_persona():
    try:
        conn = sqlite3.connect(MAIN_DB, timeout=5)
        cur = conn.cursor()
        cur.execute("SELECT val FROM config WHERE key='honeypot_persona'")
        row = cur.fetchone()
        conn.close()
        if row:
            return str(row[0]).strip().lower()
    except Exception:
        pass
    return "finance"

# -------------------- read real intel rows (READ-ONLY) --------------------
INTEL_COLUMNS = [
    "id", "asset_id", "codename", "nationality", "affiliation",
    "threat_level", "status", "last_known_location", "mission_priority",
    "extraction_needed", "last_contact_ts", "reliability_score"
]

def fetch_real_intel_rows(limit=None):
    if not os.path.exists(REAL_DB):
        return []
    try:
        conn = sqlite3.connect(f'file:{REAL_DB}?mode=ro', uri=True)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        candidates = ["intelligence_assets", "admin_intel", "intel", "assets"]
        rows = []
        for table in candidates:
            try:
                if limit:
                    sql = f"SELECT {', '.join(INTEL_COLUMNS)} FROM {table} LIMIT ?"
                    cur.execute(sql, (limit,))
                else:
                    sql = f"SELECT {', '.join(INTEL_COLUMNS)} FROM {table}"
                    cur.execute(sql)
                fetched = [dict(r) for r in cur.fetchall()]
                if fetched:
                    rows = fetched
                    break
            except Exception:
                continue
        conn.close()
        return rows
    except Exception as e:
        print("fetch_real_intel_rows error:", e)
        return []

# -------------------- Scrambling & Generation Logic --------------------
def column_derangement_shuffle(columns_list, seed_int):
    n = len(columns_list)
    if n <= 1:
        return columns_list[:]
    rnd = random.Random(seed_int)
    arr = columns_list[:]
    attempts = 0
    max_attempts = 12
    while attempts < max_attempts:
        rnd.shuffle(arr)
        conflict = False
        for i in range(n):
            if str(arr[i]) == str(columns_list[i]):
                conflict = True
                break
        if not conflict:
            return arr
        attempts += 1
    return columns_list[1:] + columns_list[:1]

def scramble_rows_preserve_values(seed_str, rows):
    if not rows:
        return []
    ordered_rows = [{k: r.get(k, "") for k in INTEL_COLUMNS} for r in rows]
    n = len(ordered_rows)
    fields = [f for f in INTEL_COLUMNS if f != "id"]
    columns = {f: [ordered_rows[i].get(f, "") for i in range(n)] for f in fields}
    seed_int = int(hashlib.sha256(seed_str.encode('utf-8')).hexdigest()[:16], 16)
    permuted_columns = {}
    for f in fields:
        permuted_columns[f] = column_derangement_shuffle(columns[f], seed_int ^ (hash(f) & 0xffffffff))
    scrambled = []
    for i, orig in enumerate(ordered_rows):
        new = dict(orig)
        new["id"] = f"HP-{seed_int % 100000}-{i+1}"
        for f in fields:
            new_val = permuted_columns[f][i]
            if str(new_val) == str(orig.get(f, "")):
                j = (i + 1) % n
                new_val = permuted_columns[f][j]
            new[f] = new_val
        scrambled.append(new)
    return scrambled

def get_scrambled_persona_rows(sid, persona, limit=12):
    seed_int = int(hashlib.sha256(sid.encode('utf-8')).hexdigest()[:16], 16)
    rnd = random.Random(seed_int)
    real_rows = fetch_real_intel_rows()
    count = max(limit, len(real_rows) if real_rows else 12)
    
    rows = []
    if persona == "scada":
        device_ids = ["PLC-NODE-01", "PLC-NODE-02", "ICS-RTU-09", "SCADA-PUMP-04", "PLC-FLOW-12", "VALVE-CONTROLLER-03"]
        locations = ["Mumbai Hub", "Delhi Grid", "Bangalore Station", "Chennai Valve A", "Pune Pipeline", "Kolkata Generator"]
        for i in range(count):
            row_id = f"HP-SCADA-{100000 + (seed_int % 10000) + i}"
            rows.append({
                "id": row_id,
                "device_id": rnd.choice(device_ids),
                "register_addr": f"4000{rnd.randint(1,9)}",
                "coil_status": rnd.choice(["CLOSED", "OPEN", "ACTIVE", "BYPASS", "TRIPPED"]),
                "valve_pos": f"{rnd.randint(0, 100)}%",
                "temperature": f"{round(rnd.uniform(45.0, 98.0), 1)}°C",
                "pressure_psi": f"{rnd.randint(120, 480)} PSI",
                "safety_status": rnd.choice(["SAFE", "SAFE", "SAFE", "ATTACK_WARNING", "STANDBY"]),
                "location": rnd.choice(locations),
                "last_reading_ts": (datetime.datetime.utcnow() - datetime.timedelta(seconds=rnd.randint(5, 300))).strftime('%Y-%m-%d %H:%M:%S')
            })
    elif persona == "military":
        call_signs = ["Viper-1", "Phoenix", "Ghost-Rider", "Shadow-6", "Centurion", "Apex-Predator", "Reaper-09"]
        ranks = ["Captain", "Lieutenant", "Major", "Commander", "Specialist", "Agent"]
        weapons = ["Active (Patriot)", "Standby (AAM-5)", "None", "Disabled", "Engaged (CIWS)", "Armed"]
        for i in range(count):
            row_id = f"HP-TACTICAL-{200000 + (seed_int % 10000) + i}"
            rows.append({
                "id": row_id,
                "asset_id": f"MIL-ASSET-{rnd.randint(7000, 9999)}",
                "call_sign": rnd.choice(call_signs),
                "clearance_level": f"LEVEL-{rnd.choice(['V', 'IV', 'TS/SCI', 'SECRET'])}",
                "rank": rnd.choice(ranks),
                "coordinates": f"{round(rnd.uniform(8.0, 37.0), 4)}N, {round(rnd.uniform(68.0, 97.0), 4)}E",
                "active_weapon": rnd.choice(weapons),
                "contact_ts": (datetime.datetime.utcnow() - datetime.timedelta(minutes=rnd.randint(1, 60))).strftime('%H:%M:%S UTC'),
                "mission_priority": rnd.choice(["CRITICAL", "HIGH", "MEDIUM", "LOW"]),
                "extraction_needed": rnd.choice(["YES", "NO", "PENDING"])
            })
    else:
        real = fetch_real_intel_rows(limit=limit)
        if not real:
            real = load_fixture()
        rows = scramble_rows_preserve_values(sid, real)
        
    return rows

def load_fixture():
    p = os.path.join(BASE_DIR, "fake_assets.json")
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return [
        {"id":"HP-1","asset_id":"A-1001","codename":"alpha","affiliation":"Unknown","threat_level":3,"status":"dormant","last_known_location":"Paris","mission_priority":"Low","extraction_needed":0,"reliability_score":6.7},
        {"id":"HP-2","asset_id":"A-1002","codename":"bravo","affiliation":"Unknown","threat_level":5,"status":"active","last_known_location":"Berlin","mission_priority":"Medium","extraction_needed":0,"reliability_score":5.2},
        {"id":"HP-3","asset_id":"A-1003","codename":"charlie","affiliation":"Unknown","threat_level":8,"status":"active","last_known_location":"NYC","mission_priority":"High","extraction_needed":1,"reliability_score":8.9},
    ]

# -------------------- Logging (honeypot_access) --------------------
@app.before_request
def log_access():
    if request.path.startswith("/static"):
        return
    sid = request.args.get("sid") or session.get("sid") or str(uuid.uuid4())
    session["sid"] = sid
    try:
        conn = get_hp_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO honeypot_access (sid, ip_address, user_agent, endpoint, method, payload)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sid, request.remote_addr, request.headers.get("User-Agent",""), request.path, request.method, json.dumps(request.get_json(silent=True) or dict(request.form) or {})))
        conn.commit(); conn.close()
    except Exception as e:
        print("honeypot log error:", e)

# -------------------- Routes --------------------
@app.route("/", methods=["GET"])
def root_fake_dashboard():
    sid = request.args.get("sid") or session.get("sid") or str(uuid.uuid4())
    session["sid"] = sid
    persona = _get_active_persona()
    preview = get_scrambled_persona_rows(sid, persona, limit=12)
    honeypot_link = url_for("hp_db", sid=sid)
    return render_template("fake_dashboard.html", rows=preview, sid=sid, honeypot_link=honeypot_link, persona=persona)

@app.route("/honeypot_db")
def hp_db():
    sid = request.args.get("sid") or session.get("sid") or str(uuid.uuid4())
    session["sid"] = sid
    persona = _get_active_persona()
    page = int(request.args.get("page", 1))
    PER_PAGE = 200
    scrambled = get_scrambled_persona_rows(sid, persona, limit=PER_PAGE)
    return render_template("honeypot.html", rows=scrambled, sid=sid, page=page, next_page=page + 1, persona=persona)

@app.route("/search", methods=["POST"])
def hp_search():
    sid = request.args.get("sid") or session.get("sid") or str(uuid.uuid4())
    session["sid"] = sid
    persona = _get_active_persona()
    q = (request.form.get("q") or "") if request.form else ""
    
    scrambled = get_scrambled_persona_rows(sid, persona, limit=200)
    if q:
        filtered = [r for r in scrambled if q.lower() in json.dumps(r).lower()]
    else:
        filtered = scrambled
    return render_template("honeypot.html", rows=filtered, sid=sid, q=q, persona=persona)

# -------------------- Honey-Token & Active Beacon --------------------
@app.route("/honeypot/download_token")
def download_honey_token():
    sid = request.args.get("sid") or session.get("sid") or str(uuid.uuid4())
    session["sid"] = sid
    
    token_content = f"""# ABHEDYA SECURITY CONFIGURATION FILE - CLASSIFIED
# INTERNAL USE ONLY - RESTRICTED ACCESS
# GENERATED BY SYSTEM ADMIN - DO NOT DISTRIBUTE

[DATABASE_CREDENTIALS]
host = 10.0.0.12
port = 1433
database = abhedya_defense_prod
username = sa_master
password = admin_master_superpass

[DECOY_BEACON_MONITOR]
# Token signature: {sid}
# Access verification pingback: http://127.0.0.1:5001/honeypot/beacon?sid={sid}&token=HONEY-TOKEN-ACCESS
"""
    
    # Fire alerts if Kafka is online
    try:
        from kafka import KafkaProducer
        import json
        prod = KafkaProducer(bootstrap_servers=["localhost:9092"], value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        alert = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event": "login_fail",  # simulate failed attempt for dashboard trigger
            "username": "HONEY_TOKEN_DOWNLOAD",
            "ip": request.remote_addr,
            "sid": sid
        }
        prod.send("network-traffic", alert)
        prod.close()
    except Exception as e:
        print("Kafka token alert failed:", e)

    from flask import Response
    headers = {
        'Content-Disposition': 'attachment; filename=confidential_database_passwords.txt',
        'Content-Type': 'text/plain'
    }
    return Response(token_content, headers=headers)

@app.route("/honeypot/beacon")
def honeypot_beacon():
    sid = request.args.get("sid") or session.get("sid") or str(uuid.uuid4())
    token = request.args.get("token") or "unknown"
    
    try:
        from kafka import KafkaProducer
        import json
        prod = KafkaProducer(bootstrap_servers=["localhost:9092"], value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        alert = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event": "login_fail",  # simulate failed event to trigger dashboard count and alarms
            "username": "HONEY_TOKEN_BEACON_TRIGGERED",
            "ip": request.remote_addr,
            "sid": sid
        }
        prod.send("network-traffic", alert)
        prod.close()
    except Exception as e:
        print("Kafka beacon alert failed:", e)
        
    return "<h3>Telemetry connection verified. Beacon registered.</h3>", 200

@app.route("/_logs/recent")
def hp_recent_logs():
    conn = get_hp_db(); cur = conn.cursor()
    cur.execute("SELECT id, sid, ip_address, endpoint, method, created_at FROM honeypot_access ORDER BY id DESC LIMIT 200")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route("/honeypot")
def honeypot_alias():
    return hp_db()

@app.route("/admin_requests", methods=["GET","POST"])
def admin_requests():
    return "<h3>Admin requests disabled in honeypot</h3>", 200

if __name__ == "__main__":
    init_hp_db()
    app.run(host="127.0.0.1", port=5001, debug=True)
