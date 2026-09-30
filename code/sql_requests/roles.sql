-- create role admin login password 'admin123';
-- create role app_user login password 'app123';
-- create role read_only login password 'read123';

-- grant all privileges on all tables in schema public to admin;

-- grant select, insert on users to app_user;
-- grant select, insert, delete on subscriptions to app_user;
-- grant select, insert on auth_tokens to app_user;
-- grant select, insert on prices to app_user;
-- grant select on stocks to app_user;
-- revoke delete on users from app_user;
-- revoke update on users from app_user;

-- grant select on users to read_only;
-- grant select on subscriptions to read_only;
-- grant select on prices to read_only;
-- grant select on stocks to read_only;