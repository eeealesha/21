# Peer-to-Peer Review Checklist: Project 2 (SQL Basics)

introduction: |
  Привет! P2P-проверка по SQL — это отличный шанс посмотреть, как другие решают те же задачи. SQL гибок, и одну задачу можно решить разными способами (например, через JOIN или через подзапрос). Твоя цель — проверить работоспособность, чистоту кода и понимание пиром базовых концепций реляционных баз данных.

quick_actions:
  - flag: EMPTY_WORK
    condition: "В репозитории нет папки `src`, отсутствуют файлы `.sql`, или работа велась не в ветке `develop`."
  - flag: CHEAT
    condition: "Пир не может объяснить, чем `WHERE` отличается от `HAVING`, или не понимает, как работает `JOIN`, написанный в его собственном скрипте."

sections:
  - name: "Задание 1: Базовый скрининг"
    weight: 10
    tasks:
      - description: "Открой файл `task1_basic.sql`. В запросе используются `SELECT`, `FROM`, `WHERE` и `ORDER BY`."
        type: visual
      - description: "Проверь, что в `WHERE` корректно отфильтрован рейтинг ('G', 'PG') и продолжительность (BETWEEN 90 AND 120)."
        type: technical
      - description: "В запросе используется оператор `DISTINCT` для исключения дубликатов."
        type: technical
      - description: "**Критерий понимания:** Спроси пира: 'В каком порядке база данных обрабатывает этот запрос? Что срабатывает сначала — `SELECT` или `WHERE`?' (Ожидаемый ответ: FROM -> WHERE -> SELECT -> DISTINCT -> ORDER BY)."
        type: discussion

  - name: "Задание 2: Агрегация"
    weight: 15
    tasks:
      - description: "Открой `task2_aggregation.sql`. Присутствует группировка `GROUP BY customer_id`."
        type: visual
      - description: "Для фильтрации групп используется `HAVING count(*) > 30`, а не `WHERE`."
        type: technical
      - description: "**Критерий понимания:** 'Почему мы не могли использовать `WHERE count(*) > 30` для фильтрации в этом запросе?'"
        type: discussion

  - name: "Задание 3: JOINs"
    weight: 20
    tasks:
      - description: "В файле `task3_joins.sql` есть 2 запроса. Первый использует два `INNER JOIN` (или просто `JOIN`) для связки трех таблиц."
        type: technical
      - description: "Во втором запросе используется `LEFT JOIN` и фильтрация `IS NULL` по ключу правой таблицы для нахождения фильмов без инвентаря."
        type: technical
      - description: "**Code Review:** Таблицам присвоены понятные алиасы (например, `film f`, `category c`)."
        type: visual
      - description: "**Критерий понимания:** 'В чем принципиальная разница между `INNER JOIN` и `LEFT JOIN` на примере второго запроса?'"
        type: discussion

  - name: "Задание 4: Подзапросы"
    weight: 15
    tasks:
      - description: "Открой `task4_subqueries.sql`. Внутри конструкции `WHERE` (или `HAVING`) есть скобки с еще одним `SELECT`."
        type: visual
      - description: "Подзапрос корректно вычисляет `AVG(amount)` из таблицы `payment`."
        type: technical
      - description: "**Критерий понимания:** 'Можно ли было решить эту задачу вообще без подзапроса? Почему?'"
        type: discussion

  - name: "Задание 5: Конструкции и Даты"
    weight: 15
    tasks:
      - description: "В файле `task5_conditions.sql` корректно написана конструкция `CASE WHEN ... THEN ... ELSE ... END` для трех категорий длительности."
        type: technical
      - description: "Для извлечения дня недели используется встроенная функция PostgreSQL (например, `EXTRACT(DOW FROM ...)` или `TO_CHAR`)."
        type: technical
      - description: "Во втором запросе присутствует агрегация `SUM` и `GROUP BY` по извлеченному дню недели."
        type: technical

  - name: "Задание 6: Оконные функции"
    weight: 25
    tasks:
      - description: "Открой `task6_windows.sql`. В первом запросе используется конструкция `OVER (PARTITION BY ... ORDER BY ...)`."
        type: technical
      - description: "Запрос корректно ограничивает выдачу (Top-3). Для этого оконная функция обернута в CTE (конструкция `WITH`) или подзапрос `FROM ()`."
        type: technical
      - description: "Во втором запросе присутствует функция `LAG()` для доступа к выручке предыдущего месяца."
        type: technical
      - description: "**Критерий понимания:** 'Чем оконная функция принципиально отличается от обычного `GROUP BY`?' (Ожидаемый ответ: Оконная функция не схлопывает строки, а добавляет расчет в каждую исходную строку)."
        type: discussion

