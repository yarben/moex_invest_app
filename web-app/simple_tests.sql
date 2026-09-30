-- select email
-- from users
-- where email like '%test.com';

-- select stock_id, target_price
-- from subscriptions
-- where target_price between 100 and 1000;

-- select u.email, s.stock_id
-- from users u
-- join subscriptions s on u.id = s.user_id;

-- select *
-- from auth_tokens
-- where expires_at > now()
-- order by expires_at;

-- select stock_id
-- from subscriptions
-- where condition = 'above'
-- order by target_price desc;

-- select distinct stock_id
-- from subscriptions;

-- select *
-- from subscriptions
-- where stock_id in (65, 33);

-- select email
-- from users
-- order by email asc
-- limit 3;

-- select *
-- from subscriptions
-- where user_id = 1
-- order by target_price desc;

-- select *
-- from auth_tokens
-- where expires_at < now();
