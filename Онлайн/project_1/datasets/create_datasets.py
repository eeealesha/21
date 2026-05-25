#!/usr/bin/env python3
"""
Генератор датасета для Проекта 1: Введение и Основы работы с данными
Клиника «Здоровье+» — намеренно «грязная» выгрузка для упражнений по очистке
"""
import random
import os
import csv
import math
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

# Специализации (совпадают с проектами 2–6)
SPECIALTIES_CLEAN = ["Терапия","Хирургия","Неврология","Кардиология","Педиатрия"]

# Намеренно «грязные» варианты написания специализаций (будут смешаны)
SPECIALTIES_DIRTY = {
    "Терапия":     ["Терапия","терапия","ТЕРАПИЯ","терапия "],
    "Хирургия":    ["Хирургия","ХИРУРГИЯ","хирургия","Хирургия "],
    "Неврология":  ["Неврология","неврология","НЕВРОЛОГИЯ"],
    "Кардиология": ["Кардиология","кардиология","КАРДИОЛОГИЯ"],
    "Педиатрия":   ["Педиатрия","педиатрия","ПЕДИАТРИЯ"],
}

# Намеренно «грязные» варианты статусов (будут смешаны)
STATUS_DIRTY = {
    "Проведён": ["проведен","ПРОВЕДЕН","Проведен","Проведён","Выполнен"],
    "Отменён":  ["ОТМЕНА","отменен","Отменен","отмена","Отменён"],
}

CANCEL_PROB = {
    "Терапия":     0.10,
    "Хирургия":    0.22,
    "Неврология":  0.15,
    "Кардиология": 0.12,
    "Педиатрия":   0.18,
}

START_DATE = date(2023, 1, 1)
END_DATE   = date(2023, 12, 31)
DATE_RANGE = (END_DATE - START_DATE).days


def rand_patient_name(gender: str) -> str:
    if gender == "М":
        return f"{random.choice(M_FIRST)} {random.choice(M_LAST)}"
    return f"{random.choice(F_FIRST)} {random.choice(F_LAST)}"


def revenue_for(specialty: str, conducted: bool) -> float:
    if not conducted:
        return 0.0
    # Хирургия намеренно выше Терапии → задание 6 (сравнение t-test/Mann-Whitney)
    mapping = {
        "Терапия":     lambda: random.gauss(2500, 500),
        "Хирургия":    lambda: math.exp(random.gauss(9.0, 0.25)),  # лог-нормальное, ~8000
        "Неврология":  lambda: random.gauss(4500, 700),
        "Кардиология": lambda: random.gauss(5200, 800),
        "Педиатрия":   lambda: random.gauss(2000, 400),
    }
    return round(max(300.0, mapping[specialty]()), 2)


# ── Пул врачей ────────────────────────────────────────────────────────────
# 10 врачей, часть с префиксом «Др.» (задание 2)
DOCTORS_CLEAN = [
    ("Илья Купитман",    "Хирургия"),
    ("Александр Рихтер", "Хирургия"),
    ("Сергей Воронов",   "Терапия"),
    ("Наталья Белова",   "Терапия"),
    ("Михаил Орлов",     "Неврология"),
    ("Елена Смирнова",   "Неврология"),
    ("Андрей Зайцев",    "Кардиология"),
    ("Юлия Соколова",    "Кардиология"),
    ("Иван Попов",       "Педиатрия"),
    ("Дарья Козлова",    "Педиатрия"),
]

# Индексы врачей, которые получат префикс «Др.» (≈ половина)
DR_PREFIX_INDICES = {0, 1, 4, 6, 8}

spec_to_docs = {}
for i, (name, spec) in enumerate(DOCTORS_CLEAN):
    spec_to_docs.setdefault(spec, []).append(i)


def dirty_doctor_name(idx: int) -> str:
    name = DOCTORS_CLEAN[idx][0]
    return f"Др. {name}" if idx in DR_PREFIX_INDICES else name


# ── Генерация строк ───────────────────────────────────────────────────────
rows = []
visit_id = 10001

# 60 визитов на специализацию → 300 строк основных данных
for spec in SPECIALTIES_CLEAN:
    doc_indices = spec_to_docs[spec]
    for _ in range(60):
        gender = random.choice(["М", "Ж"])
        patient_name = rand_patient_name(gender)
        age = random.randint(18, 80)
        visit_date = START_DATE + timedelta(days=random.randint(0, DATE_RANGE))
        is_cancelled = random.random() < CANCEL_PROB[spec]

        # Грязный статус
        clean_status = "Отменён" if is_cancelled else "Проведён"
        dirty_status = random.choice(STATUS_DIRTY[clean_status])

        # Грязная специализация
        dirty_spec = random.choice(SPECIALTIES_DIRTY[spec])

        # Врач (иногда с «Др.»)
        doc_idx = random.choice(doc_indices)
        doctor_name = dirty_doctor_name(doc_idx)

        wait = random.randint(5, 90) if not is_cancelled else 0
        rev = revenue_for(spec, not is_cancelled)

        rows.append({
            "ID_визита":           f"V-{visit_id}",
            "Дата_приема":         visit_date.strftime("%d.%m.%Y"),
            "ФИО_пациента":        patient_name,
            "Пол":                 gender,
            "Возраст":             age,
            "ФИО_врача":           doctor_name,
            "Направление_врача":   dirty_spec,
            "Время_ожидания_мин":  wait,
            "Выручка_руб":         rev,
            "Статус_визита":       dirty_status,
        })
        visit_id += 1

# Инъекция пропусков в Возраст (задание 2: заполнить медианой)
for i in random.sample(range(len(rows)), 20):
    rows[i]["Возраст"] = ""

# Инъекция полных дубликатов (задание 2: удалить дубликаты)
duplicates = random.sample(rows[:150], 15)
rows.extend(duplicates)

# Перемешиваем, чтобы дубликаты не были все в конце
random.shuffle(rows)

# ── Сохранение ────────────────────────────────────────────────────────────
COLS = ["ID_визита","Дата_приема","ФИО_пациента","Пол","Возраст",
        "ФИО_врача","Направление_врача","Время_ожидания_мин","Выручка_руб","Статус_визита"]

out_path = os.path.join(SCRIPT_DIR, "raw_clinic_data.csv")

# UTF-8-BOM для корректного открытия в Windows Excel
with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=COLS, delimiter=";")
    writer.writeheader()
    writer.writerows(rows)

# ── Статистика ────────────────────────────────────────────────────────────
total = len(rows)
with_dr = sum(1 for r in rows if r["ФИО_врача"].startswith("Др."))
missing_age = sum(1 for r in rows if r["Возраст"] == "")
statuses = {}
for r in rows:
    statuses[r["Статус_визита"]] = statuses.get(r["Статус_визита"], 0) + 1

print(f"raw_clinic_data.csv: {total} строк")
print(f"  — Врачи с «Др.»:  {with_dr}")
print(f"  — Пропуски Возраст: {missing_age}")
print(f"  — Дубликаты:        15")
print(f"  — Вариантов статуса: {len(statuses)}")
print("Датасет успешно создан.")
