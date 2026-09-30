CREATE TABLE market_stats (

    -- Уникальный идентификатор записи
    id SERIAL PRIMARY KEY,

    -- ID акции из таблицы stocks
    -- На одну акцию хранится одна актуальная запись market_stats
    stock_id INTEGER NOT NULL UNIQUE,

    -- Объём торгов за предыдущий торговый день
    -- Количество акций в штуках
    volume BIGINT,

    -- Денежный оборот торгов за предыдущий торговый день
    -- В рублях
    turnover NUMERIC(20,2),

    -- Размер ближайшего объявленного дивиденда
    -- На одну акцию
    -- Например:
    -- 35.00 ₽
    dividend_amount NUMERIC(20,2),

    -- Дата закрытия реестра (дата отсечки)
    -- По ней определяется кто получит дивиденды
    dividend_record_date DATE,

    -- Стабильность выплаты дивидендов
    -- Сколько лет подряд компания выплачивала дивиденды без пропусков
    -- Например:
    -- 7 = 7 лет подряд
    dividend_streak INTEGER,

    -- Дата последнего обновления биржевых данных
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_market_stats_stock
        FOREIGN KEY (stock_id)
        REFERENCES stocks(id)
        ON DELETE CASCADE

);