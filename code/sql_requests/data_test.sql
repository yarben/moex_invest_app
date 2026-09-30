-- insert into users (email) values
-- ('ivan.petrov@mail.com'),
-- ('anna.sidorova@mail.com'),
-- ('petr.ivanov@mail.com'),
-- ('alex@test.com'),
-- ('kate@test.com'),
-- ('max@test.com');

-- insert into subscriptions (user_id, stock_id, target_price, condition) values
-- (1, 65, 330, 'above'),
-- (1, 149, 120, 'below'),
-- (1, 70, 6000, 'above'),

-- (2, 65, 300, 'below'),
-- (2, 70, 6500, 'above'),

-- (3, 149, 130, 'above'),

-- (4, 65, 350, 'above'),
-- (4, 149, 115, 'below'),

-- (5, 70, 5500, 'below');

-- insert into auth_tokens (user_id, token, expires_at) values
-- (1, 'token_ivan', now() + interval '10 minutes'),
-- (2, 'token_anna', now() + interval '5 minutes'),
-- (3, 'token_petr', now() - interval '1 hour'),
-- (4, 'token_alex', now() + interval '15 minutes'),
-- (5, 'token_kate', now() + interval '30 minutes');