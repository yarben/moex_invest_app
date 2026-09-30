CREATE TABLE fundamentals (

    -- Уникальный идентификатор записи
    id SERIAL PRIMARY KEY,

    -- ID акции из таблицы stocks
    -- Внешний ключ: stocks.id
    stock_id INTEGER NOT NULL,

    -- Дата публикации отчёта компанией
    -- Например:
    -- 2025-03-18 → дата выхода годового отчета за 2024 год
    report_date DATE NOT NULL,

    -- Тип отчётного периода
    -- year = годовой
    -- quarter = квартальный
    -- half_year = полугодовой
    period_type VARCHAR(20) NOT NULL DEFAULT 'year',

    -- Собственный капитал компании (Equity / Book Value)
    -- Берётся из баланса:
    -- "Итого капитал" / "Собственный капитал"
    -- Хранится в рублях
    equity NUMERIC(20,2),

    -- Общая стоимость активов компании (Total Assets)
    -- Берётся из баланса:
    -- "Итого активы"
    -- Хранится в рублях
    total_assets NUMERIC(20,2),

    -- Чистая прибыль компании (Net Earnings / Net Income)
    -- Берётся из отчета о финансовых результатах:
    -- "Чистая прибыль"
    -- Хранится в рублях
    net_earnings NUMERIC(20,2),

    -- Общий долг компании (Total Debt)
    -- Обычно:
    -- долгосрочные обязательства + краткосрочные обязательства
    -- Хранится в рублях
    total_debt NUMERIC(20,2),

    -- Чистый долг (Net Debt)
    -- Обычно:
    -- Total Debt - денежные средства и эквиваленты
    -- Может быть отрицательным
    -- Хранится в рублях
    net_debt NUMERIC(20,2),

    -- Свободный денежный поток (Free Cash Flow)
    -- Обычно:
    -- операционный денежный поток - капитальные затраты
    -- Может отсутствовать в отчетности → NULL
    -- Хранится в рублях
    free_cash_flow NUMERIC(20,2),

    -- Выручка компании
    -- Для банков допускается использовать:
    -- операционные доходы / чистый процентный доход
    -- Поле называется revenue для единообразия
    -- Хранится в рублях
    revenue NUMERIC(20,2),

    -- Дата создания записи
    created_at TIMESTAMP DEFAULT NOW(),

    -- Дата последнего обновления записи
    updated_at TIMESTAMP DEFAULT NOW(),

	-- Коэффициент free-float
	-- Доля акций в свободном обращении
	free_float_percent NUMERIC,


    CONSTRAINT fk_fundamentals_stock
        FOREIGN KEY (stock_id)
        REFERENCES stocks(id)
        ON DELETE CASCADE,

    -- Запрещает дублирование отчётов:
    -- одна акция + одна дата отчёта = одна запись
    CONSTRAINT uq_fundamentals_report
        UNIQUE (
            stock_id,
            report_date
        )

);