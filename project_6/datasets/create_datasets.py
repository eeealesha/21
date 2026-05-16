#!/usr/bin/env python3
"""
Генератор датасетов для Проекта 6: Data-Driven подход
Клиника «Здоровье+» — анализ оттока пациентов
"""
import random
import os
import math
import csv
from datetime import date, timedelta

random.seed(42)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Константы ─────────────────────────────────────────────────────────────
END_DATE      = date(2024, 12, 31)
START_DATE    = date(2022, 1,  1)
CHURN_CUTOFF  = 180   # дней с последнего визита → пациент считается ушедшим

M_LAST  = ["Иванов","Петров","Сидоров","Смирнов","Козлов","Новиков","Морозов",
            "Попов","Лебедев","Ковалёв","Орлов","Волков","Соколов","Зайцев","Павлов"]
F_LAST  = ["Иванова","Петрова","Сидорова","Смирнова","Козлова","Новикова","Морозова",
            "Попова","Лебедева","Ковалёва","Орлова","Волкова","Соколова","Зайцева","Павлова"]
M_FIRST = ["Александр","Дмитрий","Михаил","Андрей","Сергей","Алексей","Иван",
            "Артём","Николай","Евгений","Павел","Максим","Роман","Кирилл"]
F_FIRST = ["Анна","Мария","Елена","Ольга","Наталья","Екатерина","Татьяна",
            "Ирина","Светлана","Юлия","Виктория","Ксения","Дарья","Алина"]
DISTRICTS    = ["Центральный","Северный","Южный","Западный","Восточный","Замоскворечье"]
SPECIALTIES  = ["Терапия","Хирургия","Неврология","Кардиология","Педиатрия"]
BRANCHES     = ["Клиника «Центр»","Клиника «Запад»","Клиника «Север»","Клиника «Юг»"]


def rand_name(gender: str) -> str:
    if gender == "М":
        return f"{random.choice(M_FIRST)} {random.choice(M_LAST)}"
    return f"{random.choice(F_FIRST)} {random.choice(F_LAST)}"


def revenue_for(specialty: str) -> float:
    mapping = {
        "Терапия":     lambda: random.gauss(2000, 400),
        "Хирургия":    lambda: math.exp(random.gauss(9.3, 0.3)),
        "Неврология":  lambda: random.gauss(4200, 600),
        "Кардиология": lambda: random.gauss(5200, 800),
        "Педиатрия":   lambda: random.gauss(1700, 300),
    }
    return round(max(300.0, mapping[specialty]()), 2)


def churn_propensity(age: int, insurance: str) -> float:
    """Базовая вероятность оттока на основе демографии пациента."""
    p = 0.38
    if insurance == "ДМС":
        p -= 0.16   # ДМС-пациенты более лояльны
    elif insurance == "ОМС":
        p += 0.14   # ОМС — больше альтернатив, ниже лояльность
    if age > 65:
        p += 0.14   # пожилые пациенты чаще прекращают посещения
    elif 25 <= age <= 45:
        p -= 0.10   # активная рабочая аудитория — наиболее лояльна
    return max(0.06, min(0.88, p))


# ── Пул врачей (24 врача) ─────────────────────────────────────────────────
doctors = []
doc_id = 1
for spec in SPECIALTIES:
    for _ in range(4):
        gender = "М"
        fn = random.choice(M_FIRST)
        ln = random.choice(M_LAST)
        branch = random.choice(BRANCHES)
        hire = date(2010, 1, 1) + timedelta(
            days=random.randint(0, (date(2023, 12, 31) - date(2010, 1, 1)).days)
        )
        doctors.append({
            "doctor_id":   doc_id,
            "doctor_name": f"{fn} {ln}",
            "specialty":   spec,
            "branch":      branch,
            "hire_date":   hire.isoformat(),
        })
        doc_id += 1

doc_by_spec = {s: [d for d in doctors if d["specialty"] == s] for s in SPECIALTIES}

# ── Генерация пациентов ───────────────────────────────────────────────────
patients = []
for pid in range(1, 301):
    gender = random.choice(["М", "Ж"])
    age    = random.randint(18, 80)
    ins    = random.choices(
        ["ОМС", "ДМС", "Платно"],
        weights=[50, 30, 20],
    )[0]
    reg = date(2022, 1, 1) + timedelta(days=random.randint(0, 364))
    patients.append({
        "patient_id":        pid,
        "patient_name":      rand_name(gender),
        "age":               age,
        "gender":            gender,
        "district":          random.choice(DISTRICTS),
        "registration_date": reg.isoformat(),
        "insurance_type":    ins,
        "_churn_p":          churn_propensity(age, ins),  # используется только для генерации
    })

# ── Генерация визитов ─────────────────────────────────────────────────────
# Логика: пациенты с высоким churn_p получат последний визит > 180 дней до END_DATE.
# Wait times: пациенты с высоким churn_p получат более высокое среднее время ожидания
# → логистическая регрессия на avg_wait_time будет значима.

visits = []
visit_id = 1

for p in patients:
    cp = p["_churn_p"]

    # Количество визитов: обратно пропорционально оттоку
    n_visits = max(1, round(random.gauss(5.5 - 3.0 * cp, 1.5)))

    # Определяем дату последнего визита
    is_churned = random.random() < cp
    if is_churned:
        # Последний визит более 180 дней назад
        gap = random.randint(CHURN_CUTOFF + 1, 700)
    else:
        # Последний визит в пределах 180 дней
        gap = random.randint(7, CHURN_CUTOFF - 1)

    last_visit_date = END_DATE - timedelta(days=gap)
    # Не раньше даты регистрации
    reg_date = date.fromisoformat(p["registration_date"])
    last_visit_date = max(last_visit_date, reg_date + timedelta(days=7))

    # Генерируем все визиты в диапазоне [reg_date, last_visit_date]
    visit_range = (last_visit_date - reg_date).days
    if visit_range <= 0:
        visit_dates = [last_visit_date]
    else:
        raw_dates = sorted(
            set([last_visit_date] + [
                reg_date + timedelta(days=random.randint(0, visit_range))
                for _ in range(n_visits - 1)
            ])
        )
        visit_dates = raw_dates[-n_visits:]  # берём n_visits последних

    # Базовое время ожидания: пациенты с высоким cp → больше ожидают
    base_wait = round(20 + 55 * cp)   # range: ~26..69 мин

    for i, vdate in enumerate(visit_dates):
        specialty = random.choice(SPECIALTIES)
        doc = random.choice(doc_by_spec[specialty])
        # Cancel rate: коррелирует с churn_p
        cancel = random.random() < (0.10 + 0.25 * cp)
        status = "Отменён" if cancel else "Проведён"
        rev  = revenue_for(specialty) if not cancel else 0.0
        wait = max(0, round(random.gauss(base_wait, 12))) if not cancel else 0

        visits.append({
            "visit_id":     visit_id,
            "patient_id":   p["patient_id"],
            "visit_date":   vdate.isoformat(),
            "specialty":    specialty,
            "status":       status,
            "revenue":      rev,
            "wait_time_min": wait,
            "doctor_id":    doc["doctor_id"],
            "is_repeat":    1 if i > 0 else 0,
        })
        visit_id += 1

# ── Сохранение patients.csv ───────────────────────────────────────────────
PAT_COLS = ["patient_id","patient_name","age","gender","district",
            "registration_date","insurance_type"]

patients_path = os.path.join(SCRIPT_DIR, "patients.csv")
with open(patients_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=PAT_COLS)
    writer.writeheader()
    for p in patients:
        writer.writerow({k: p[k] for k in PAT_COLS})

# ── Сохранение visits.csv ─────────────────────────────────────────────────
VIS_COLS = ["visit_id","patient_id","visit_date","specialty","status",
            "revenue","wait_time_min","doctor_id","is_repeat"]

visits_path = os.path.join(SCRIPT_DIR, "visits.csv")
with open(visits_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=VIS_COLS)
    writer.writeheader()
    writer.writerows(visits)

# ── Статистика для проверки ───────────────────────────────────────────────
from collections import defaultdict
last_by_patient = defaultdict(lambda: date(2000, 1, 1))
for v in visits:
    d = date.fromisoformat(v["visit_date"])
    if d > last_by_patient[v["patient_id"]]:
        last_by_patient[v["patient_id"]] = d

churned_count = sum(1 for pid, ld in last_by_patient.items()
                    if (END_DATE - ld).days > CHURN_CUTOFF)

print(f"patients.csv:  {len(patients)} строк")
print(f"visits.csv:    {len(visits)} строк (~{len(visits)/len(patients):.1f} визитов/пациент)")
print(f"Churn rate:    {churned_count}/{len(patients)} = {churned_count/len(patients)*100:.1f}%")
print("Датасеты успешно созданы.")
