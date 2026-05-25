"""
Генератор датасета для оффлайн-интенсива «Управление на основе данных».

Создаёт три «снимка» одного и того же набора данных:
    dataset_v1.csv — День 1. Сырые агрегированные годовые показатели по 24 МО
                     (12 в Регионе А и 12 в Регионе Б) с намеренными ошибками ввода.
    dataset_v2.csv — День 2. Очищенный набор + помесячная динамика, кадры,
                     оборудование, время до манипуляции.
    dataset_v3.csv — День 3. То же, что v2 + плановые показатели, ряд предыдущего
                     года, привязка к Федпроекту.

Все файлы воспроизводимы (random.seed(42)).

Запуск: python3 create_datasets.py
Файлы создаются рядом со скриптом.
"""

import csv
import random
from pathlib import Path

random.seed(42)

OUTPUT_DIR = Path(__file__).resolve().parent

# ---------- Справочники ----------

REGIONS = {
    "Регион А": {"prefix": "А", "letality_mean": 4.5, "vacancy_mean": 8, "equipment_age_mean": 3.5},
    "Регион Б": {"prefix": "Б", "letality_mean": 6.8, "vacancy_mean": 22, "equipment_age_mean": 7.5},
}

MO_TYPES = [
    ("Районная больница", 0.9),
    ("Городская больница", 1.0),
    ("Краевой центр", 1.4),
    ("Межрайонный центр", 1.1),
]

MONTHS = [
    "январь", "февраль", "март", "апрель", "май", "июнь",
    "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь",
]


# ---------- Генерация списка МО ----------

def build_mo_list():
    """Возвращает список из 24 МО (по 12 в каждом регионе) с базовыми атрибутами."""
    mos = []
    for region, params in REGIONS.items():
        for i in range(1, 13):
            mo_type, capacity_factor = random.choice(MO_TYPES)
            district = f"Район-{params['prefix']}{i:02d}"
            population = int(random.gauss(80_000 * capacity_factor, 25_000))
            population = max(15_000, population)
            elderly_share = round(random.gauss(0.22 if region == "Регион А" else 0.28, 0.04), 3)
            elderly_share = max(0.10, min(0.42, elderly_share))
            mos.append({
                "mo_id": f"МО-{params['prefix']}{i:02d}",
                "mo_name": f"{mo_type} «{district}»",
                "region": region,
                "district": district,
                "population": population,
                "elderly_share": elderly_share,
                "capacity_factor": capacity_factor,
                "letality_mean": params["letality_mean"] * random.uniform(0.85, 1.20),
                "vacancy_mean": params["vacancy_mean"] * random.uniform(0.7, 1.4),
                "equipment_age_mean": params["equipment_age_mean"] * random.uniform(0.8, 1.3),
            })
    return mos


# ---------- v1: сырые годовые агрегаты с ошибками ----------

def write_dataset_v1(mos):
    """Годовой агрегат по 24 МО. Сырые данные с ошибками ввода — для Дня 1."""
    path = OUTPUT_DIR / "dataset_v1.csv"
    rows = []
    for mo in mos:
        admitted = int(random.gauss(mo["population"] * 0.04, mo["population"] * 0.01))
        admitted = max(500, admitted)
        deaths = int(admitted * (mo["letality_mean"] / 100) * random.uniform(0.9, 1.1))
        transferred = int(admitted * random.uniform(0.02, 0.06))
        discharged = admitted - deaths - transferred

        # Намеренные ошибки: смешанные регистры, опечатки, пропуски
        region_value = mo["region"]
        if random.random() < 0.15:
            region_value = region_value.lower()
        if random.random() < 0.05:
            region_value = region_value.upper()

        rows.append({
            "mo_id": mo["mo_id"],
            "mo_name": mo["mo_name"],
            "region": region_value,
            "district": mo["district"],
            "population": mo["population"] if random.random() > 0.04 else "",  # пропуски
            "elderly_share": round(mo["elderly_share"], 3),
            "admitted_total": admitted,
            "discharged": discharged,
            "transferred": transferred,
            "deaths": deaths,
            # Летальность специально с разной точностью и иногда как строка с запятой
            "letality_pct": (
                f"{deaths / admitted * 100:.2f}".replace(".", ",") if random.random() < 0.2
                else round(deaths / admitted * 100, 2)
            ),
        })

    # ---- 8 классов намеренных дефектов в v1 (для Дня 1, Задание 5) ----
    # Часть уже встроена выше (регистры region, пропуски population, смешанный
    # формат letality_pct). Здесь — оставшиеся 5 классов на конкретных строках.
    # 1) Полный дубликат строки
    rows.append(dict(rows[7]))
    # 2) Опечатка в mo_name (детерминированно — индекс 3)
    rows[3]["mo_name"] = rows[3]["mo_name"].replace("Районная", "Раонная")
    # 3) population как строка с приблизительным значением (индекс 11)
    rows[11]["population"] = "≈85000"
    # 4) Отрицательный transferred (индекс 14) — явная ошибка ввода
    rows[14]["transferred"] = -3
    # 5) Заведомо неверная letality_pct (индекс 19) — десятичная ошибка (×1000)
    deaths_19 = rows[19]["deaths"]
    admitted_19 = rows[19]["admitted_total"]
    rows[19]["letality_pct"] = round(deaths_19 / admitted_19 * 1000, 2)
    # 6) Принудительный пропуск population (детерминированно, индекс 8)
    rows[8]["population"] = ""

    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path, len(rows)


# ---------- v2: помесячная динамика + кадры + оборудование ----------

def write_dataset_v2(mos):
    """Помесячная динамика за 24 месяца по 24 МО + кадры + оборудование + время до манипуляции."""
    path = OUTPUT_DIR / "dataset_v2.csv"
    rows = []
    for mo in mos:
        # Снимок состояния кадров и оборудования (статичен по году, помесячно повторяется)
        for year in (2023, 2024):
            for month_idx, month in enumerate(MONTHS, start=1):
                # Сезонность: зима и лето чуть выше летальность
                season_factor = 1.0 + 0.12 * (1 if month_idx in (1, 2, 12, 7) else 0)
                admitted = int(random.gauss(mo["population"] * 0.04 / 12, mo["population"] * 0.005))
                admitted = max(40, admitted)
                base_letality = mo["letality_mean"] / 100 * season_factor
                deaths = int(admitted * base_letality * random.uniform(0.85, 1.15))
                transferred = int(admitted * random.uniform(0.02, 0.06))
                discharged = admitted - deaths - transferred

                # Кадры: вакансии по реанимации — ключевой драйвер
                vac_reanim = round(mo["vacancy_mean"] * random.uniform(0.8, 1.2), 1)
                vac_cardio = round(mo["vacancy_mean"] * random.uniform(0.5, 1.0), 1)
                vac_surgeon = round(mo["vacancy_mean"] * random.uniform(0.4, 0.9), 1)

                # Оборудование: возраст + единицы
                ivl_units = max(1, int(random.gauss(8 * mo["capacity_factor"], 2)))
                ct_units = max(0, int(random.gauss(2 * mo["capacity_factor"], 1)))
                angiograph_units = max(0, int(random.gauss(1.0 if mo["region"] == "Регион А" else 0.5, 0.6)))
                ivl_avg_age = round(random.gauss(mo["equipment_age_mean"], 1.5), 1)

                # Время до манипуляции: зависит от вакансий реанимации
                time_to_ivl = round(random.gauss(35 + vac_reanim * 1.5, 8), 1)
                time_to_ivl = max(8, time_to_ivl)

                rows.append({
                    "mo_id": mo["mo_id"],
                    "region": mo["region"],
                    "district": mo["district"],
                    "year": year,
                    "month": month,
                    "month_idx": month_idx,
                    "population": mo["population"],
                    "elderly_share": round(mo["elderly_share"], 3),
                    "admitted": admitted,
                    "discharged": discharged,
                    "transferred": transferred,
                    "deaths": deaths,
                    "letality_pct": round(deaths / admitted * 100, 2),
                    "vacancy_reanim_pct": vac_reanim,
                    "vacancy_cardio_pct": vac_cardio,
                    "vacancy_surgeon_pct": vac_surgeon,
                    "ivl_units": ivl_units,
                    "ct_units": ct_units,
                    "angiograph_units": angiograph_units,
                    "ivl_avg_age_years": ivl_avg_age,
                    "time_to_ivl_min": time_to_ivl,
                })

    # ---- 8 классов намеренных дефектов в v2 (для Дня 2, Задание 1) ----
    # МИАЦ доставил «чистые» данные, но при автогенерации просочились реальные
    # для медицинской отчётности дефекты — задача группы их найти.

    def find_idx(mo_id, year, month):
        """Найти индекс строки по ключу."""
        for i, r in enumerate(rows):
            if r["mo_id"] == mo_id and r["year"] == year and r["month"] == month:
                return i
        raise KeyError(f"row not found: {mo_id} {year} {month}")

    # 1) «Восстановленные» time_to_ivl_min в 3 МО Региона Б за апрель-май 2024.
    #    Маркер — необычная точность (3 знака после запятой), что должно
    #    броситься в глаза при сортировке. Это содержательная аномалия.
    #    Пишем строкой с явным форматом, чтобы trailing zeros не обрезались
    #    при сериализации в CSV.
    for mo_id in ("МО-Б04", "МО-Б09", "МО-Б11"):
        for month in ("апрель", "май"):
            i = find_idx(mo_id, 2024, month)
            rows[i]["time_to_ivl_min"] = f"{rows[i]['time_to_ivl_min'] * 0.91:.3f}"

    # 2) Дубликат строки (МО-А05, март 2024)
    rows.append(dict(rows[find_idx("МО-А05", 2024, "март")]))

    # 3) Отрицательная вакансия (МО-Б02, июнь 2024) — явная ошибка ввода
    rows[find_idx("МО-Б02", 2024, "июнь")]["vacancy_reanim_pct"] = -1.0

    # 4) Аномально низкое time_to_ivl_min = 4 (МО-А03, январь 2024 и МО-А08, март 2024)
    rows[find_idx("МО-А03", 2024, "январь")]["time_to_ivl_min"] = 4.0
    rows[find_idx("МО-А08", 2024, "март")]["time_to_ivl_min"] = 4.0

    # 5) Подозрительно низкая летальность 0.0 при deaths=0 (5 строк)
    for mo_id, year, month in [
        ("МО-А11", 2023, "февраль"),
        ("МО-Б07", 2023, "июль"),
        ("МО-А02", 2024, "октябрь"),
        ("МО-Б12", 2024, "август"),
        ("МО-А09", 2024, "ноябрь"),
    ]:
        i = find_idx(mo_id, year, month)
        rows[i]["deaths"] = 0
        rows[i]["letality_pct"] = 0.0

    # 6) ivl_units = 0 в 2 МО (несогласованность: при этом time_to_ivl_min > 0)
    for mo_id in ("МО-Б06", "МО-А12"):
        i = find_idx(mo_id, 2024, "декабрь")
        rows[i]["ivl_units"] = 0

    # 7) Опечатки в названиях месяцев (3 строки)
    rows[find_idx("МО-А01", 2023, "сентябрь")]["month"] = "сентябь"
    rows[find_idx("МО-Б05", 2024, "январь")]["month"] = "янврь"
    rows[find_idx("МО-Б08", 2023, "ноябрь")]["month"] = "нобярь"

    # 8) Тип-микс: одна строка с population как строка "н/д"
    rows[find_idx("МО-Б10", 2024, "июль")]["population"] = "н/д"

    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path, len(rows)


# ---------- v3: + плановые + исторический ряд + Федпроект ----------

def write_dataset_v3(mos):
    """v2 + плановые показатели + годовая историческая сводка за 2022 + привязка к Федпроекту."""
    path = OUTPUT_DIR / "dataset_v3.csv"
    rows = []
    for mo in mos:
        # 2022 — историческая базовая точка
        for month_idx, month in enumerate(MONTHS, start=1):
            admitted = int(random.gauss(mo["population"] * 0.04 / 12, mo["population"] * 0.005))
            admitted = max(40, admitted)
            base_letality = mo["letality_mean"] / 100 * random.uniform(1.05, 1.20)  # 2022 был хуже
            deaths = int(admitted * base_letality * random.uniform(0.85, 1.15))
            transferred = int(admitted * random.uniform(0.02, 0.06))
            discharged = admitted - deaths - transferred

            rows.append(_v3_row(mo, 2022, month, month_idx, admitted, discharged, transferred, deaths,
                                planned_letality=None, federal_project="Развитие здравоохранения"))

        # 2023–2024 — те же значения, что в v2, плюс плановые
        for year in (2023, 2024):
            for month_idx, month in enumerate(MONTHS, start=1):
                season_factor = 1.0 + 0.12 * (1 if month_idx in (1, 2, 12, 7) else 0)
                admitted = int(random.gauss(mo["population"] * 0.04 / 12, mo["population"] * 0.005))
                admitted = max(40, admitted)
                base_letality = mo["letality_mean"] / 100 * season_factor
                deaths = int(admitted * base_letality * random.uniform(0.85, 1.15))
                transferred = int(admitted * random.uniform(0.02, 0.06))
                discharged = admitted - deaths - transferred

                # Плановый показатель: для Региона А он близок к факту, для Региона Б — амбициозно ниже
                if mo["region"] == "Регион А":
                    planned = round(mo["letality_mean"] * random.uniform(0.95, 1.02), 2)
                else:
                    planned = round(mo["letality_mean"] * random.uniform(0.70, 0.85), 2)

                rows.append(_v3_row(mo, year, month, month_idx, admitted, discharged, transferred, deaths,
                                    planned_letality=planned, federal_project="Развитие здравоохранения"))

    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path, len(rows)


def _v3_row(mo, year, month, month_idx, admitted, discharged, transferred, deaths,
            planned_letality, federal_project):
    vac_reanim = round(mo["vacancy_mean"] * random.uniform(0.8, 1.2), 1)
    vac_cardio = round(mo["vacancy_mean"] * random.uniform(0.5, 1.0), 1)
    vac_surgeon = round(mo["vacancy_mean"] * random.uniform(0.4, 0.9), 1)
    ivl_units = max(1, int(random.gauss(8 * mo["capacity_factor"], 2)))
    ct_units = max(0, int(random.gauss(2 * mo["capacity_factor"], 1)))
    angiograph_units = max(0, int(random.gauss(1.0 if mo["region"] == "Регион А" else 0.5, 0.6)))
    ivl_avg_age = round(random.gauss(mo["equipment_age_mean"], 1.5), 1)
    time_to_ivl = max(8, round(random.gauss(35 + vac_reanim * 1.5, 8), 1))

    return {
        "mo_id": mo["mo_id"],
        "region": mo["region"],
        "district": mo["district"],
        "year": year,
        "month": month,
        "month_idx": month_idx,
        "population": mo["population"],
        "elderly_share": round(mo["elderly_share"], 3),
        "admitted": admitted,
        "discharged": discharged,
        "transferred": transferred,
        "deaths": deaths,
        "letality_pct_fact": round(deaths / admitted * 100, 2),
        "letality_pct_plan": planned_letality if planned_letality is not None else "",
        "vacancy_reanim_pct": vac_reanim,
        "vacancy_cardio_pct": vac_cardio,
        "vacancy_surgeon_pct": vac_surgeon,
        "ivl_units": ivl_units,
        "ct_units": ct_units,
        "angiograph_units": angiograph_units,
        "ivl_avg_age_years": ivl_avg_age,
        "time_to_ivl_min": time_to_ivl,
        "federal_project": federal_project,
    }


# ---------- Точка входа ----------

def main():
    mos = build_mo_list()
    print(f"Сгенерировано МО: {len(mos)} (12 на регион)")

    p1, n1 = write_dataset_v1(mos)
    print(f"  {p1.name:20s} {n1} строк")

    p2, n2 = write_dataset_v2(mos)
    print(f"  {p2.name:20s} {n2} строк (24 МО × 24 месяца)")

    p3, n3 = write_dataset_v3(mos)
    print(f"  {p3.name:20s} {n3} строк (24 МО × 36 месяцев)")

    print("Готово. Все три CSV рядом со скриптом.")


if __name__ == "__main__":
    main()
