import sqlite3
import random
import os
from datetime import date, timedelta

random.seed(42)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clinic.db")

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

# ── Schema ────────────────────────────────────────────────────────────

cur.executescript("""
CREATE TABLE specialties (
    specialty_id   INTEGER PRIMARY KEY,
    specialty_name TEXT NOT NULL
);

CREATE TABLE branches (
    branch_id   INTEGER PRIMARY KEY,
    branch_name TEXT NOT NULL,
    city        TEXT NOT NULL
);

CREATE TABLE patients (
    patient_id  INTEGER PRIMARY KEY,
    first_name  TEXT NOT NULL,
    last_name   TEXT NOT NULL,
    birth_date  TEXT NOT NULL,
    gender      TEXT NOT NULL,
    district    TEXT NOT NULL
);

CREATE TABLE doctors (
    doctor_id    INTEGER PRIMARY KEY,
    first_name   TEXT NOT NULL,
    last_name    TEXT NOT NULL,
    specialty_id INTEGER NOT NULL REFERENCES specialties(specialty_id),
    hire_date    TEXT NOT NULL,
    branch_id    INTEGER NOT NULL REFERENCES branches(branch_id)
);

CREATE TABLE services (
    service_id   INTEGER PRIMARY KEY,
    service_name TEXT NOT NULL,
    base_price   REAL NOT NULL,
    specialty_id INTEGER NOT NULL REFERENCES specialties(specialty_id)
);

CREATE TABLE appointments (
    appointment_id    INTEGER PRIMARY KEY,
    patient_id        INTEGER NOT NULL REFERENCES patients(patient_id),
    doctor_id         INTEGER NOT NULL REFERENCES doctors(doctor_id),
    appointment_date  TEXT NOT NULL,
    status            TEXT NOT NULL,
    revenue           REAL NOT NULL,
    wait_time_minutes INTEGER NOT NULL,
    service_id        INTEGER NOT NULL REFERENCES services(service_id)
);
""")

# ── Reference data ────────────────────────────────────────────────────

SPECIALTIES = [
    (1, "Терапия"),
    (2, "Хирургия"),
    (3, "Неврология"),
    (4, "Кардиология"),
    (5, "Педиатрия"),
    (6, "Стоматология"),
]
cur.executemany("INSERT INTO specialties VALUES (?,?)", SPECIALTIES)

BRANCHES = [
    (1, "Клиника «Центр»", "Москва"),
    (2, "Клиника «Запад»",  "Москва"),
    (3, "Клиника «Север»",  "Санкт-Петербург"),
    (4, "Клиника «Юг»",     "Казань"),
]
cur.executemany("INSERT INTO branches VALUES (?,?,?)", BRANCHES)

# 3 services per specialty; last 3 (IDs 16,17,18) are intentionally never assigned
SERVICES = [
    (1,  "Первичный приём терапевта",       1500.0, 1),
    (2,  "Повторный приём терапевта",        1200.0, 1),
    (3,  "Выписка направлений и справок",   900.0,  1),
    (4,  "Плановая операция",               12000.0, 2),
    (5,  "Экстренная операция",             18000.0, 2),
    (6,  "Послеоперационный осмотр",        3000.0,  2),
    (7,  "Первичный приём невролога",        3500.0, 3),
    (8,  "ЭЭГ (электроэнцефалография)",     4200.0, 3),
    (9,  "Лечебный массаж (курс)",          5500.0, 3),
    (10, "ЭКГ и консультация кардиолога",   3800.0, 4),
    (11, "Суточное мониторирование (Холтер)", 6500.0, 4),
    (12, "Нагрузочный тест (велоэргометрия)", 5200.0, 4),
    (13, "Приём педиатра",                  1400.0, 5),
    (14, "Профилактический осмотр ребёнка", 1800.0, 5),
    (15, "Вакцинация",                      1100.0, 5),
    (16, "Профессиональная чистка зубов",   3500.0, 6),  # never assigned
    (17, "Отбеливание зубов",               7800.0, 6),  # never assigned
    (18, "Имплантация зуба",               45000.0, 6),  # never assigned
]
cur.executemany("INSERT INTO services VALUES (?,?,?,?)", SERVICES)

# ── Patients ──────────────────────────────────────────────────────────

M_LAST = ["Иванов","Петров","Сидоров","Смирнов","Козлов","Новиков","Морозов",
           "Попов","Лебедев","Ковалёв","Орлов","Волков","Соколов","Зайцев",
           "Павлов","Семёнов","Голубев","Виноградов","Богданов","Воробьёв"]
F_LAST  = ["Иванова","Петрова","Сидорова","Смирнова","Козлова","Новикова","Морозова",
           "Попова","Лебедева","Ковалёва","Орлова","Волкова","Соколова","Зайцева",
           "Павлова","Семёнова","Голубева","Виноградова","Богданова","Воробьёва"]
M_FIRST = ["Александр","Дмитрий","Михаил","Андрей","Сергей","Алексей","Иван",
           "Артём","Николай","Евгений","Павел","Владимир","Максим","Роман","Кирилл"]
F_FIRST = ["Анна","Мария","Елена","Ольга","Наталья","Екатерина","Татьяна",
           "Ирина","Светлана","Юлия","Виктория","Ксения","Дарья","Алина","Валерия"]
DISTRICTS = ["Центральный","Северный","Южный","Западный","Восточный","Замоскворечье"]

START_BIRTH = date(1950, 1, 1)
END_BIRTH   = date(2010, 12, 31)
BIRTH_RANGE = (END_BIRTH - START_BIRTH).days

patients = []
for pid in range(1, 251):
    gender = random.choice(["М", "Ж"])
    if gender == "М":
        fn = random.choice(M_FIRST)
        ln = random.choice(M_LAST)
    else:
        fn = random.choice(F_FIRST)
        ln = random.choice(F_LAST)
    bd = START_BIRTH + timedelta(days=random.randint(0, BIRTH_RANGE))
    dist = random.choice(DISTRICTS)
    # Ensure at least 30 patients in 'Центральный' for Task 1
    if pid <= 30:
        dist = "Центральный"
    patients.append((pid, fn, ln, bd.isoformat(), gender, dist))

cur.executemany("INSERT INTO patients VALUES (?,?,?,?,?,?)", patients)

# ── Doctors ───────────────────────────────────────────────────────────
# 24 doctors, 4 per specialty; doctors 23 and 24 will get 0 appointments

START_HIRE = date(2015, 1, 1)
HIRE_RANGE = (date(2023, 12, 31) - START_HIRE).days

doctors = []
for did in range(1, 25):
    spec_id = ((did - 1) % 6) + 1
    branch_id = random.randint(1, 4)
    fn = random.choice(M_FIRST)
    ln = random.choice(M_LAST)
    hd = START_HIRE + timedelta(days=random.randint(0, HIRE_RANGE))
    # Ensure some doctors hired after 2020-01-01 for Task 1
    if did <= 8:
        hd = date(2020, 1, 1) + timedelta(days=random.randint(0, (date(2023,12,31)-date(2020,1,1)).days))
    doctors.append((did, fn, ln, spec_id, hd.isoformat(), branch_id))

cur.executemany("INSERT INTO doctors VALUES (?,?,?,?,?,?)", doctors)

# ── Appointments ──────────────────────────────────────────────────────
# Doctors 23 and 24 excluded → 0 appointments
# Services 16, 17, 18 excluded → 0 assignments
# Available doctors: 1–22
# Available services: 1–15 (filtered by specialty)

START_APT = date(2022, 1, 1)
END_APT   = date(2024, 6, 30)
APT_RANGE = (END_APT - START_APT).days

SPECIALTY_SERVICES = {
    1: [1, 2, 3],
    2: [4, 5, 6],
    3: [7, 8, 9],
    4: [10, 11, 12],
    5: [13, 14, 15],
    6: [],  # Dentistry services intentionally not assigned
}

# Map doctor_id → specialty_id
doc_spec = {d[0]: d[3] for d in doctors}

# Eligible doctors: IDs 1–22, excluding dentists (specialty 6 → no services)
eligible_docs = [d[0] for d in doctors if d[0] <= 22 and SPECIALTY_SERVICES.get(d[3], [])]

def pick_doctor_and_service():
    doc_id = random.choice(eligible_docs)
    spec = doc_spec[doc_id]
    svc_id = random.choice(SPECIALTY_SERVICES[spec])
    return doc_id, svc_id

appointments = []
apt_id = 1

# Give first 50 patients 3–6 appointments each (guaranteed for Task 6 window functions)
for pid in range(1, 51):
    n = random.randint(3, 6)
    for _ in range(n):
        doc_id, svc_id = pick_doctor_and_service()
        base = next(s[2] for s in SERVICES if s[0] == svc_id)
        revenue = round(base * random.uniform(0.85, 1.20), 2)
        status = "Проведён" if random.random() < 0.82 else "Отменён"
        apt_date = START_APT + timedelta(days=random.randint(0, APT_RANGE))
        wait = random.randint(10, 90)
        appointments.append((apt_id, pid, doc_id, apt_date.isoformat(), status, revenue, wait, svc_id))
        apt_id += 1

# Give remaining patients 0–2 appointments each
for pid in range(51, 251):
    n = random.randint(0, 2)
    for _ in range(n):
        doc_id, svc_id = pick_doctor_and_service()
        base = next(s[2] for s in SERVICES if s[0] == svc_id)
        revenue = round(base * random.uniform(0.85, 1.20), 2)
        status = "Проведён" if random.random() < 0.82 else "Отменён"
        apt_date = START_APT + timedelta(days=random.randint(0, APT_RANGE))
        wait = random.randint(10, 90)
        appointments.append((apt_id, pid, doc_id, apt_date.isoformat(), status, revenue, wait, svc_id))
        apt_id += 1

# Ensure appointments with revenue > 3000 and status='Отменён' exist (Task 1, Q2)
for _ in range(15):
    doc_id, svc_id = pick_doctor_and_service()
    base = next(s[2] for s in SERVICES if s[0] == svc_id)
    revenue = round(max(3100.0, base * random.uniform(0.9, 1.2)), 2)
    apt_date = START_APT + timedelta(days=random.randint(0, APT_RANGE))
    base = next(s[2] for s in SERVICES if s[0] == svc_id)
    revenue = round(max(3100.0, base * random.uniform(0.9, 1.2)), 2)
    apt_date = START_APT + timedelta(days=random.randint(0, APT_RANGE))
    wait = random.randint(10, 75)
    pid = random.randint(1, 250)
    appointments.append((apt_id, pid, doc_id, apt_date.isoformat(), "Отменён", revenue, wait, svc_id))
    apt_id += 1

# Ensure wait_time > 60 minutes entries exist (Task 5, comfort_level)
for _ in range(20):
    doc_id, svc_id = pick_doctor_and_service()
    base = next(s[2] for s in SERVICES if s[0] == svc_id)
    revenue = round(base * random.uniform(0.9, 1.2), 2)
    apt_date = START_APT + timedelta(days=random.randint(0, APT_RANGE))
    wait = random.randint(61, 120)
    pid = random.randint(1, 250)
    appointments.append((apt_id, pid, doc_id, apt_date.isoformat(), "Проведён", revenue, wait, svc_id))
    apt_id += 1

cur.executemany(
    "INSERT INTO appointments VALUES (?,?,?,?,?,?,?,?)",
    appointments
)

# ── Injection: 3 patients with >90 day gaps between visits (Task 6 LEAD) ──

gap_patients = [1, 2, 3]
# Use only doctors with non-empty service lists for gap injection
eligible_gap_docs = [d[0] for d in doctors if SPECIALTY_SERVICES.get(doc_spec[d[0]], [])]
for pid in gap_patients:
    # Remove existing appointments for this patient and insert ordered ones with a gap
    cur.execute("DELETE FROM appointments WHERE patient_id = ?", (pid,))
    base_date = date(2022, 3, 1)
    apt_dates = [base_date, base_date + timedelta(days=100), base_date + timedelta(days=130)]
    for i in range(3):
        apt_date = apt_dates[i]
        doc_id = eligible_gap_docs[i % len(eligible_gap_docs)]
        spec = doc_spec[doc_id]
        svc_list = SPECIALTY_SERVICES[spec]
        svc_id = svc_list[0]
        base_price = next(s[2] for s in SERVICES if s[0] == svc_id)
        revenue = round(base_price * random.uniform(0.9, 1.1), 2)
        wait = random.randint(15, 50)
        cur.execute(
            "INSERT INTO appointments VALUES (?,?,?,?,?,?,?,?)",
            (apt_id, pid, doc_id, apt_date.isoformat(), "Проведён", revenue, wait, svc_id)
        )
        apt_id += 1

# ── Injection: RANK tie — two cardiologists with equal total revenue ──

# Find two cardiologists (specialty_id=4, doctors not 23/24)
cur.execute("""
    SELECT d.doctor_id, COALESCE(SUM(a.revenue), 0) as total
    FROM doctors d
    LEFT JOIN appointments a ON d.doctor_id = a.doctor_id
    WHERE d.specialty_id = 4 AND d.doctor_id < 23
    GROUP BY d.doctor_id
    ORDER BY total DESC
    LIMIT 2
""")
cardio_rows = cur.fetchall()

if len(cardio_rows) >= 2:
    doc1_id, rev1 = cardio_rows[0]
    doc2_id, rev2 = cardio_rows[1]
    diff = rev1 - rev2
    if diff > 0:
        # Add one appointment to doc2 that closes the gap
        # Find a cardiology service
        card_svcs = SPECIALTY_SERVICES[4]
        svc_id = card_svcs[0]
        apt_date = date(2023, 6, 15)
        cur.execute(
            "INSERT INTO appointments VALUES (?,?,?,?,?,?,?,?)",
            (apt_id, 10, doc2_id, apt_date.isoformat(), "Проведён", round(diff, 2), 20, svc_id)
        )
        apt_id += 1

conn.commit()

# ── Summary ───────────────────────────────────────────────────────────

def count(table):
    return cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

print(f"База данных успешно создана: {DB_PATH}")
print(f"  specialties:  {count('specialties')} строк")
print(f"  branches:     {count('branches')} строк")
print(f"  services:     {count('services')} строк  (услуги 16–18 без приёмов)")
print(f"  patients:     {count('patients')} строк")
print(f"  doctors:      {count('doctors')} строк  (врачи 23–24 без приёмов)")
print(f"  appointments: {count('appointments')} строк")

conn.close()
