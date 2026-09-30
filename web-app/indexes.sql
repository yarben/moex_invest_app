-- create index idx_subscriptions_user_id on subscriptions(user_id);

-- create index idx_subscriptions_stock_id on subscriptions(stock_id);

-- create index idx_prices_stock_id on prices(stock_id);

-- create index idx_prices_timestamp on prices(timestamp);

-- select
--     tablename,
--     indexname,
--     indexdef
-- from pg_indexes
-- where schemaname = 'public';