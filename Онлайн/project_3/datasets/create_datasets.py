#!/usr/bin/env python3
"""
Генератор датасетов для Проекта 3: Python + Pandas
Клиника «Здоровье+»
"""
import random
import os
import sys
import math
import csv
from datetime import date, timedelta

random.seed(42)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── fpdf2 guard ────────────────────────────────────────────────────────
try:
    from fpdf import FPDF
except ImportError:
    print("ОШИБКА: библиотека fpdf2 не установлена.")
    print("Запусти: pip install fpdf2")
    sys.exit(1)

# ── Name pools (same as project_2) ────────────────────────────────────
M_LAST  = ["Иванов","Петров","Сидоров","Смирнов","Козлов","Новиков","Морозов",
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

SPECIALTIES = ["Терапия","Хирургия","Неврология","Кардиология","Педиатрия"]

BRANCHES = ["Клиника «Центр»","Клиника «Запад»","Клиника «Север»","Клиника «Юг»"]
BRANCH_CITY = {
    "Клиника «Центр»": "Москва",
    "Клиника «Запад»": "Москва",
    "Клиника «Север»": "Санкт-Петербург",
    "Клиника «Юг»":    "Казань",
}

SPECIALTY_SERVICES = {
    "Терапия":     ["Первичный приём терапевта","Повторный приём терапевта","Выписка направлений"],
    "Хирургия":    ["Плановая операция","Экстренная операция","Послеоперационный осмотр"],
    "Неврология":  ["Первичный приём невролога","ЭЭГ","Лечебный массаж"],
    "Кардиология": ["ЭКГ и консультация","Суточное мониторирование","Нагрузочный тест"],
    "Педиатрия":   ["Приём педиатра","Профилактический осмотр","Вакцинация"],
}

CANCEL_PROB = {
    "Терапия":     0.10,
    "Хирургия":    0.30,
    "Неврология":  0.18,
    "Кардиология": 0.15,
    "Педиатрия":   0.20,
}

SALARY_RANGE = {
    "Терапия":     (800,  1200),
    "Хирургия":    (4000, 6000),
    "Неврология":  (1500, 2500),
    "Кардиология": (2000, 3000),
    "Педиатрия":   (700,  1100),
}


def revenue_for(specialty: str) -> float:
    if specialty == "Терапия":
        r = random.gauss(2000, 350)
    elif specialty == "Хирургия":
        r = math.exp(random.gauss(9.4, 0.3))
    elif specialty == "Неврология":
        r = random.gauss(4500, 600)
    elif specialty == "Кардиология":
        r = random.gauss(5500, 800)
    else:  # Педиатрия
        r = random.gauss(1800, 300)
    return round(max(500.0, min(50000.0, r)), 2)


def rand_full_name(gender: str) -> str:
    if gender == "М":
        return f"{random.choice(M_FIRST)} {random.choice(M_LAST)}"
    return f"{random.choice(F_FIRST)} {random.choice(F_LAST)}"


# ── Doctor pool (30 doctors, 6 per specialty) ─────────────────────────
doctors = []
doc_id = 1
for spec in SPECIALTIES:
    for _ in range(6):
        branch = random.choice(BRANCHES)
        gender = "М"  # all doctors are male names for simplicity
        fn = random.choice(M_FIRST)
        ln = random.choice(M_LAST)
        hire = date(2010, 1, 1) + timedelta(days=random.randint(0, (date(2023,12,31)-date(2010,1,1)).days))
        lo, hi = SALARY_RANGE[spec]
        salary = round(random.uniform(lo, hi), 2)
        doctors.append({
            "doctor_id":       doc_id,
            "first_name":      fn,
            "last_name":       ln,
            "doctor_name":     f"{fn} {ln}",
            "specialty":       spec,
            "branch":          branch,
            "city":            BRANCH_CITY[branch],
            "hire_date":       hire.isoformat(),
            "salary_per_visit": salary,
        })
        doc_id += 1

doc_by_specialty = {spec: [d for d in doctors if d["specialty"] == spec] for spec in SPECIALTIES}

# ── Generate clinic_visits.csv ─────────────────────────────────────────

START_VISIT = date(2022, 1, 1)
END_VISIT   = date(2024, 12, 31)
VISIT_RANGE = (END_VISIT - START_VISIT).days

visits = []
visit_id = 1

for spec in SPECIALTIES:
    spec_docs = doc_by_specialty[spec]
    for _ in range(100):
        doc = random.choice(spec_docs)
        gender = random.choice(["М", "Ж"])
        patient_name = rand_full_name(gender)
        age_val = random.randint(5, 85)
        district = random.choice(DISTRICTS)
        visit_date = START_VISIT + timedelta(days=random.randint(0, VISIT_RANGE))
        status = "Отменён" if random.random() < CANCEL_PROB[spec] else "Проведён"
        service = random.choice(SPECIALTY_SERVICES[spec])
        revenue = revenue_for(spec)
        wait = random.randint(10, 90)
        visits.append({
            "visit_id":       visit_id,
            "patient_id":     random.randint(1, 250),
            "patient_name":   patient_name,
            "age":            age_val,
            "gender":         gender,
            "district":       district,
            "doctor_id":      doc["doctor_id"],
            "doctor_name":    doc["doctor_name"],
            "specialty":      spec,
            "branch":         doc["branch"],
            "visit_date":     visit_date.isoformat(),
            "status":         status,
            "service":        service,
            "revenue":        revenue,
            "wait_time_min":  wait,
        })
        visit_id += 1

# Inject missing values: 20 for age, 15 for district
age_null_indices    = random.sample(range(len(visits)), 20)
district_null_indices = random.sample(range(len(visits)), 15)
for i in age_null_indices:
    visits[i]["age"] = ""
for i in district_null_indices:
    visits[i]["district"] = ""

# Ensure at least 25 rows with wait_time_min > 60
over60 = [v for v in visits if v["wait_time_min"] > 60]
if len(over60) < 25:
    sample = random.sample([v for v in visits if v["wait_time_min"] <= 60], 25 - len(over60))
    for v in sample:
        v["wait_time_min"] = random.randint(61, 90)

visits_path = os.path.join(SCRIPT_DIR, "clinic_visits.csv")
if os.path.exists(visits_path):
    os.remove(visits_path)

VISIT_COLS = ["visit_id","patient_id","patient_name","age","gender","district",
              "doctor_id","doctor_name","specialty","branch","visit_date",
              "status","service","revenue","wait_time_min"]

with open(visits_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=VISIT_COLS)
    writer.writeheader()
    writer.writerows(visits)

# ── Generate clinic_staff.csv ──────────────────────────────────────────

staff_path = os.path.join(SCRIPT_DIR, "clinic_staff.csv")
if os.path.exists(staff_path):
    os.remove(staff_path)

STAFF_COLS = ["doctor_id","first_name","last_name","specialty","branch","city","hire_date","salary_per_visit"]

with open(staff_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=STAFF_COLS)
    writer.writeheader()
    for d in doctors:
        writer.writerow({k: d[k] for k in STAFF_COLS})

# ── Generate quarterly_report.pdf ──────────────────────────────────────

# Locate DejaVuSans.ttf for Cyrillic support
font_path = None
try:
    import matplotlib
    candidate = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf", "DejaVuSans.ttf")
    if os.path.exists(candidate):
        font_path = candidate
except ImportError:
    pass

if font_path is None:
    for candidate in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        os.path.expanduser("~/.fonts/DejaVuSans.ttf"),
    ]:
        if os.path.exists(candidate):
            font_path = candidate
            break

if font_path is None:
    print("ОШИБКА: Не найден шрифт с поддержкой кириллицы.")
    print("Установи matplotlib: pip install matplotlib")
    sys.exit(1)

TABLE_DATA = [
    # [specialty, Q1, Q2, Q3, Q4, total]
    ["  Терапия  ",    " 98 ", "105", "107", " 92 ", "402"],
    ["Хирургия",       "—",    " 34 ", "41",  "38",  "113"],
    ["Неврология",     "45",   "52",  " 48 ", "50",  "195"],
    ["Кардиология",    "61",   "58",  "63",   "—",   "182"],
    ["Педиатрия",      "72",   " 69 ","74",   "78",  "293"],
    ["Итого",          "276",  "318", "333",  "258", "1200"],  # intentional wrong total (correct: 1185)
]
HEADERS = ["Специализация", "Q1 2023", "Q2 2023", "Q3 2023", "Q4 2023", "Итого"]

pdf_path = os.path.join(SCRIPT_DIR, "quarterly_report.pdf")
if os.path.exists(pdf_path):
    os.remove(pdf_path)

pdf = FPDF()
pdf.add_page()
pdf.add_font("DejaVu", "", font_path)
pdf.set_font("DejaVu", size=14)

# Title
pdf.set_fill_color(240, 240, 240)
pdf.cell(0, 10, "Квартальный отчёт: Клиника «Здоровье+» — 2023 год",
         new_x="LMARGIN", new_y="NEXT", align="C")
pdf.set_font("DejaVu", size=11)
pdf.cell(0, 8, "Количество визитов по специализациям",
         new_x="LMARGIN", new_y="NEXT", align="C")
pdf.ln(4)

# Table header
pdf.set_font("DejaVu", size=10)
col_widths = [52, 28, 28, 28, 28, 26]
pdf.set_fill_color(200, 220, 255)
for i, h in enumerate(HEADERS):
    pdf.cell(col_widths[i], 8, h, border=1, fill=True, align="C")
pdf.ln()

# Table rows
pdf.set_fill_color(255, 255, 255)
for row in TABLE_DATA:
    for i, cell in enumerate(row):
        pdf.cell(col_widths[i], 8, cell, border=1, align="C")
    pdf.ln()

pdf.output(pdf_path)

# ── Summary ────────────────────────────────────────────────────────────
print(f"clinic_visits.csv:  {len(visits)} строк")
print(f"clinic_staff.csv:   {len(doctors)} строк")
print(f"quarterly_report.pdf: создан")
print("Датасеты успешно созданы.")
