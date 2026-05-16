-- Пример оформления файла для Задания 1.
-- Это шаблон — он показывает только ФОРМАТ записи запросов.
-- Конкретные вопросы и условия — в readme.md.
-- Не копируй — напиши свои запросы самостоятельно!

-- Вопрос 1:
-- Пример: выбрать все строки из таблицы patients с условием по столбцу district,
-- отсортированные по фамилии от А до Я.
SELECT patient_id, first_name, last_name, district
FROM patients
WHERE district = 'Название_района'
ORDER BY last_name ASC;

-- Вопрос 2:
-- Пример: выбрать записи из таблицы appointments с двумя условиями одновременно.
SELECT appointment_id, appointment_date, revenue
FROM appointments
WHERE status = 'Нужный_статус'
  AND revenue > 0; -- замени 0 на нужное пороговое значение

-- Вопрос 3:
-- Пример: получить уникальный список значений из столбца.
SELECT DISTINCT название_столбца AS псевдоним
FROM название_таблицы;

-- Вопрос 4:
-- Пример: отсортировать по убыванию и ограничить количество строк.
SELECT id_столбец, числовой_столбец
FROM название_таблицы
ORDER BY числовой_столбец DESC
LIMIT 10;

-- Вопрос 5:
-- Пример: фильтрация по дате.
-- В SQLite даты хранятся как текст в формате 'YYYY-MM-DD' — сравнение работает лексикографически.
SELECT doctor_id, first_name, last_name, hire_date
FROM doctors
WHERE hire_date > 'YYYY-MM-DD' -- замени на нужную дату
ORDER BY hire_date DESC;
