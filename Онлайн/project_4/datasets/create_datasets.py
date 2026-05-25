#!/usr/bin/env python3
"""
Генератор датасетов для Проекта 4: Визуализация данных и Dashboards
Клиника «Здоровье+»
"""
import random
import os
import math
import csv
from datetime import date, timedelta

random.seed(42)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Name pools ────────────────────────────────────────────────────────────
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

SPECIALTIES = ["Терапия","Хирургия","Неврология","Кардиология","Педиатрия","Стоматология"]

BRANCHES = ["Клиника «Центр»","Клиника «Запад»","Клиника «Север»","Клиника «Юг»"]

# Разные вероятности отмены → на pie chart и bar chart будут контрастные данные
CANCEL_PROB = {
    "Терапия":     0.10,
    "Хирургия":    0.30,
    "Неврология":  0.18,
    "Кардиология": 0.15,
    "Педиатрия":   0.20,
    "Стоматология":0.12,
}

SALARY_RANGE = {
    "Терапия":     (800,  1200),
    "Хирургия":    (4000, 6000),
    "Неврология":  (1500, 2500),
    "Кардиология": (2000, 3000),
    "Педиатрия":   (700,  1100),
    "Стоматология":(2500, 4000),
}


def revenue_for(specialty: str) -> float:
    """Выручка проведённого визита по направлению."""
    if specialty == "Терапия":
        r = random.gauss(2000, 350)
    elif specialty == "Хирургия":
        r = math.exp(random.gauss(9.4, 0.3))   # логнормальное — высокий разброс
    elif specialty == "Неврология":
        r = random.gauss(4500, 600)
    elif specialty == "Кардиология":
        r = random.gauss(5500, 800)
    elif specialty == "Педиатрия":
        r = random.gauss(1800, 300)
    else:   # Стоматология
        r = random.gauss(7000, 1200)
    return round(max(500.0, min(80000.0, r)), 2)


def rand_full_name(gender: str) -> str:
    if gender == "М":
        return f"{random.choice(M_FIRST)} {random.choice(M_LAST)}"
    return f"{random.choice(F_FIRST)} {random.choice(F_LAST)}"


# ── Doctor pool: 4 врача на специализацию, всего 24 ──────────────────────
doctors = []
doc_id = 1
for spec in SPECIALTIES:
    for _ in range(4):
        branch = random.choice(BRANCHES)
        fn = random.choice(M_FIRST)
        ln = random.choice(M_LAST)
        hire = date(2010, 1, 1) + timedelta(
            days=random.randint(0, (date(2023, 12, 31) - date(2010, 1, 1)).days)
        )
        lo, hi = SALARY_RANGE[spec]
        salary = round(random.uniform(lo, hi), 2)
        doctors.append({
            "doctor_id":        doc_id,
            "doctor_name":      f"{fn} {ln}",
            "specialty":        spec,
            "branch":           branch,
            "hire_date":        hire.isoformat(),
            "salary_per_visit": salary,
        })
        doc_id += 1

doc_by_specialty = {
    spec: [d for d in doctors if d["specialty"] == spec]
    for spec in SPECIALTIES
}

# ── Generate clinic_visits.csv ────────────────────────────────────────────
# Весь 2024 год → месячный тренд виден на line chart

START_VISIT = date(2024, 1, 1)
END_VISIT   = date(2024, 12, 31)
VISIT_RANGE = (END_VISIT - START_VISIT).days

visits = []
visit_id = 1

# ~83 визита на направление × 6 = ~500 строк
for spec in SPECIALTIES:
    spec_docs = doc_by_specialty[spec]
    for _ in range(83):
        doc = random.choice(spec_docs)
        gender = random.choice(["М", "Ж"])
        patient_name = rand_full_name(gender)
        age_val = random.randint(5, 85)
        district = random.choice(DISTRICTS)
        visit_date = START_VISIT + timedelta(days=random.randint(0, VISIT_RANGE))
        status = "Отменён" if random.random() < CANCEL_PROB[spec] else "Проведён"

        # Отменённые визиты: выручка и ожидание = 0
        if status == "Проведён":
            rev = revenue_for(spec)
            wait = random.randint(5, 90)
        else:
            rev = 0.0
            wait = 0

        visits.append({
            "visit_id":      visit_id,
            "visit_date":    visit_date.isoformat(),
            "patient_id":    random.randint(1, 300),
            "patient_name":  patient_name,
            "age":           age_val,
            "gender":        gender,
            "district":      district,
            "doctor_id":     doc["doctor_id"],
            "doctor_name":   doc["doctor_name"],
            "specialty":     spec,
            "branch":        doc["branch"],
            "status":        status,
            "revenue":       rev,
            "wait_time_min": wait,
        })
        visit_id += 1

# Инъекция пропусков: 15 в age, 10 в district — для Task 2 (EDA с пропусками)
for i in random.sample(range(len(visits)), 15):
    visits[i]["age"] = ""
for i in random.sample(range(len(visits)), 10):
    visits[i]["district"] = ""

VISIT_COLS = [
    "visit_id","visit_date","patient_id","patient_name","age","gender","district",
    "doctor_id","doctor_name","specialty","branch","status","revenue","wait_time_min",
]

visits_path = os.path.join(SCRIPT_DIR, "clinic_visits.csv")
with open(visits_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=VISIT_COLS)
    writer.writeheader()
    writer.writerows(visits)

# ── Generate clinic_staff.csv ─────────────────────────────────────────────
STAFF_COLS = ["doctor_id","doctor_name","specialty","branch","hire_date","salary_per_visit"]

staff_path = os.path.join(SCRIPT_DIR, "clinic_staff.csv")
with open(staff_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=STAFF_COLS)
    writer.writeheader()
    for d in doctors:
        writer.writerow({k: d[k] for k in STAFF_COLS})

# ── Summary ───────────────────────────────────────────────────────────────
print(f"clinic_visits.csv:  {len(visits)} строк")
print(f"clinic_staff.csv:   {len(doctors)} строк")
print("Датасеты успешно созданы.")
