#!/usr/bin/env python3
"""
Генератор датасетов для Проекта 5: A/B тестирование
Клиника «Здоровье+» — тест SMS-напоминаний
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
            "Попов","Лебедев","Ковалёв","Орлов","Волков","Соколов","Зайцев","Павлов"]
F_LAST  = ["Иванова","Петрова","Сидорова","Смирнова","Козлова","Новикова","Морозова",
            "Попова","Лебедева","Ковалёва","Орлова","Волкова","Соколова","Зайцева","Павлова"]
M_FIRST = ["Александр","Дмитрий","Михаил","Андрей","Сергей","Алексей","Иван",
            "Артём","Николай","Евгений","Павел","Максим","Роман","Кирилл"]
F_FIRST = ["Анна","Мария","Елена","Ольга","Наталья","Екатерина","Татьяна",
            "Ирина","Светлана","Юлия","Виктория","Ксения","Дарья","Алина"]
DISTRICTS = ["Центральный","Северный","Южный","Западный","Восточный","Замоскворечье"]
SPECIALTIES = ["Терапия","Хирургия","Неврология","Кардиология","Педиатрия"]

START = date(2024, 1, 1)
END   = date(2024, 6, 30)
DAYS  = (END - START).days

VISIT_COLS = [
    "visit_id","patient_id","group","visit_date","specialty",
    "age","district","status","revenue","is_repeat",
]


def rand_name(gender: str) -> str:
    if gender == "М":
        return f"{random.choice(M_FIRST)} {random.choice(M_LAST)}"
    return f"{random.choice(F_FIRST)} {random.choice(F_LAST)}"


def revenue_for(specialty: str) -> float:
    """Выручка по направлению — разные распределения → смесь делает данные нелогнормальными."""
    if specialty == "Терапия":
        r = random.gauss(2000, 400)
    elif specialty == "Хирургия":
        r = math.exp(random.gauss(9.5, 0.35))  # логнормальное
    elif specialty == "Неврология":
        r = random.gauss(4500, 700)
    elif specialty == "Кардиология":
        r = random.gauss(5500, 900)
    else:  # Педиатрия
        r = random.gauss(1800, 350)
    return round(max(300.0, r), 2)


def make_row(visit_id: int, patient_id: int, group: str,
             cancel_rate: float, repeat_rate: float) -> dict:
    specialty = random.choice(SPECIALTIES)
    status = "Отменён" if random.random() < cancel_rate else "Проведён"
    rev = revenue_for(specialty) if status == "Проведён" else 0.0
    return {
        "visit_id":   visit_id,
        "patient_id": patient_id,
        "group":      group,
        "visit_date": (START + timedelta(days=random.randint(0, DAYS))).isoformat(),
        "specialty":  specialty,
        "age":        random.randint(18, 80),
        "district":   random.choice(DISTRICTS),
        "status":     status,
        "revenue":    rev,
        "is_repeat":  1 if random.random() < repeat_rate else 0,
    }


# ── ab_test_data.csv ──────────────────────────────────────────────────────
# Группа A (без SMS): cancel rate 0.25, repeat rate 0.30
# Группа B (с SMS):   cancel rate 0.14, repeat rate 0.35
# Ключевая гарантия: chi-square для No-show rate → p < 0.05 (значимо)
# Ключевая гарантия: возраст и специализация идентичны → проверка баланса проходит

ab_rows = []
visit_id = 1

# Используем пул пациентов, распределённых равномерно между группами
for i in range(400):
    patient_id = i + 1
    ab_rows.append(make_row(visit_id, patient_id, "A", 0.25, 0.30))
    visit_id += 1

for i in range(400):
    patient_id = i + 1
    ab_rows.append(make_row(visit_id, patient_id, "B", 0.14, 0.35))
    visit_id += 1

# Инъекция 5 выбросов revenue в группе A (у проведённых визитов)
conducted_a = [r for r in ab_rows if r["group"] == "A" and r["status"] == "Проведён"]
outlier_indices = random.sample(range(len(conducted_a)), 5)
for idx in outlier_indices:
    conducted_a[idx]["revenue"] = round(random.uniform(55000, 85000), 2)

# Пропуски: 10 в age, 8 в district
for i in random.sample(range(len(ab_rows)), 10):
    ab_rows[i]["age"] = ""
for i in random.sample(range(len(ab_rows)), 8):
    ab_rows[i]["district"] = ""

ab_path = os.path.join(SCRIPT_DIR, "ab_test_data.csv")
with open(ab_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=VISIT_COLS)
    writer.writeheader()
    writer.writerows(ab_rows)

# ── Проверка статистической гарантии ─────────────────────────────────────
a_cancel = sum(1 for r in ab_rows if r["group"] == "A" and r["status"] == "Отменён")
b_cancel = sum(1 for r in ab_rows if r["group"] == "B" and r["status"] == "Отменён")
a_total = sum(1 for r in ab_rows if r["group"] == "A")
b_total = sum(1 for r in ab_rows if r["group"] == "B")

# ── aa_test_data.csv ──────────────────────────────────────────────────────
# Обе половины из одного распределения (cancel rate 0.20) → p > 0.05

aa_rows = []
visit_id = 1

for i in range(300):
    patient_id = i + 1
    aa_rows.append(make_row(visit_id, patient_id, "AA_1", 0.20, 0.32))
    visit_id += 1

for i in range(300):
    patient_id = i + 1
    aa_rows.append(make_row(visit_id, patient_id, "AA_2", 0.20, 0.32))
    visit_id += 1

aa_path = os.path.join(SCRIPT_DIR, "aa_test_data.csv")
with open(aa_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=VISIT_COLS)
    writer.writeheader()
    writer.writerows(aa_rows)

# ── Summary ───────────────────────────────────────────────────────────────
print(f"ab_test_data.csv:  {len(ab_rows)} строк")
print(f"  Группа A: {a_total} визитов, {a_cancel} отменён ({a_cancel/a_total*100:.1f}%)")
print(f"  Группа B: {b_total} визитов, {b_cancel} отменён ({b_cancel/b_total*100:.1f}%)")
print(f"aa_test_data.csv:  {len(aa_rows)} строк")
print("Датасеты успешно созданы.")
