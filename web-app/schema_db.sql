--
-- PostgreSQL database dump
--

\restrict VzHtyEHpEQQUgPlNZ1YiSZCbbefsmPlpjyfS5WYwOPHe1sKSmTXHL1q9UC75e2b

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

-- Started on 2026-05-18 16:37:36

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 2 (class 3079 OID 45181)
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- TOC entry 4982 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 223 (class 1259 OID 45127)
-- Name: auth_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_tokens (
    id integer NOT NULL,
    user_id integer,
    token text,
    expires_at timestamp without time zone
);


ALTER TABLE public.auth_tokens OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 45126)
-- Name: auth_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auth_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.auth_tokens_id_seq OWNER TO postgres;

--
-- TOC entry 4984 (class 0 OID 0)
-- Dependencies: 222
-- Name: auth_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auth_tokens_id_seq OWNED BY public.auth_tokens.id;


--
-- TOC entry 219 (class 1259 OID 28716)
-- Name: prices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prices (
    id integer NOT NULL,
    price double precision,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    stock_id integer
);


ALTER TABLE public.prices OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 28715)
-- Name: prices_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.prices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prices_id_seq OWNER TO postgres;

--
-- TOC entry 4986 (class 0 OID 0)
-- Dependencies: 218
-- Name: prices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.prices_id_seq OWNED BY public.prices.id;


--
-- TOC entry 221 (class 1259 OID 36908)
-- Name: stocks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stocks (
    id integer NOT NULL,
    ticker character varying(10) NOT NULL
);


ALTER TABLE public.stocks OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 36907)
-- Name: stocks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.stocks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.stocks_id_seq OWNER TO postgres;

--
-- TOC entry 4988 (class 0 OID 0)
-- Dependencies: 220
-- Name: stocks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.stocks_id_seq OWNED BY public.stocks.id;


--
-- TOC entry 227 (class 1259 OID 45155)
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.subscriptions (
    id integer NOT NULL,
    user_id integer,
    target_price numeric,
    condition character varying(10),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    stock_id integer NOT NULL
);


ALTER TABLE public.subscriptions OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 45154)
-- Name: subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subscriptions_id_seq OWNER TO postgres;

--
-- TOC entry 4990 (class 0 OID 0)
-- Dependencies: 226
-- Name: subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.subscriptions_id_seq OWNED BY public.subscriptions.id;


--
-- TOC entry 225 (class 1259 OID 45143)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    manage_token uuid DEFAULT gen_random_uuid()
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 45142)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- TOC entry 4992 (class 0 OID 0)
-- Dependencies: 224
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 4802 (class 2604 OID 45130)
-- Name: auth_tokens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_tokens ALTER COLUMN id SET DEFAULT nextval('public.auth_tokens_id_seq'::regclass);


--
-- TOC entry 4799 (class 2604 OID 28719)
-- Name: prices id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prices ALTER COLUMN id SET DEFAULT nextval('public.prices_id_seq'::regclass);


--
-- TOC entry 4801 (class 2604 OID 36911)
-- Name: stocks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stocks ALTER COLUMN id SET DEFAULT nextval('public.stocks_id_seq'::regclass);


--
-- TOC entry 4806 (class 2604 OID 45158)
-- Name: subscriptions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions ALTER COLUMN id SET DEFAULT nextval('public.subscriptions_id_seq'::regclass);


--
-- TOC entry 4803 (class 2604 OID 45146)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 4818 (class 2606 OID 45134)
-- Name: auth_tokens auth_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_tokens
    ADD CONSTRAINT auth_tokens_pkey PRIMARY KEY (id);


--
-- TOC entry 4820 (class 2606 OID 45136)
-- Name: auth_tokens auth_tokens_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_tokens
    ADD CONSTRAINT auth_tokens_token_key UNIQUE (token);


--
-- TOC entry 4811 (class 2606 OID 28722)
-- Name: prices prices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prices
    ADD CONSTRAINT prices_pkey PRIMARY KEY (id);


--
-- TOC entry 4814 (class 2606 OID 36913)
-- Name: stocks stocks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT stocks_pkey PRIMARY KEY (id);


--
-- TOC entry 4816 (class 2606 OID 36915)
-- Name: stocks stocks_ticker_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stocks
    ADD CONSTRAINT stocks_ticker_key UNIQUE (ticker);


--
-- TOC entry 4828 (class 2606 OID 45163)
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (id);


--
-- TOC entry 4822 (class 2606 OID 45153)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 4824 (class 2606 OID 45151)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4808 (class 1259 OID 45179)
-- Name: idx_prices_stock_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_prices_stock_id ON public.prices USING btree (stock_id);


--
-- TOC entry 4809 (class 1259 OID 45180)
-- Name: idx_prices_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_prices_timestamp ON public.prices USING btree ("timestamp");


--
-- TOC entry 4825 (class 1259 OID 45178)
-- Name: idx_subscriptions_stock_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_subscriptions_stock_id ON public.subscriptions USING btree (stock_id);


--
-- TOC entry 4826 (class 1259 OID 45177)
-- Name: idx_subscriptions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_subscriptions_user_id ON public.subscriptions USING btree (user_id);


--
-- TOC entry 4812 (class 1259 OID 45226)
-- Name: unique_price_point; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX unique_price_point ON public.prices USING btree (stock_id, "timestamp");


--
-- TOC entry 4829 (class 2606 OID 36916)
-- Name: prices fk_stock; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.prices
    ADD CONSTRAINT fk_stock FOREIGN KEY (stock_id) REFERENCES public.stocks(id);


--
-- TOC entry 4830 (class 2606 OID 45172)
-- Name: subscriptions fk_stock; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT fk_stock FOREIGN KEY (stock_id) REFERENCES public.stocks(id);


--
-- TOC entry 4831 (class 2606 OID 45164)
-- Name: subscriptions subscriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 4983 (class 0 OID 0)
-- Dependencies: 223
-- Name: TABLE auth_tokens; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.auth_tokens TO admin;
GRANT SELECT,INSERT ON TABLE public.auth_tokens TO app_user;


--
-- TOC entry 4985 (class 0 OID 0)
-- Dependencies: 219
-- Name: TABLE prices; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.prices TO admin;
GRANT SELECT,INSERT ON TABLE public.prices TO app_user;
GRANT SELECT ON TABLE public.prices TO read_only;


--
-- TOC entry 4987 (class 0 OID 0)
-- Dependencies: 221
-- Name: TABLE stocks; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.stocks TO admin;
GRANT SELECT ON TABLE public.stocks TO app_user;
GRANT SELECT ON TABLE public.stocks TO read_only;


--
-- TOC entry 4989 (class 0 OID 0)
-- Dependencies: 227
-- Name: TABLE subscriptions; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.subscriptions TO admin;
GRANT SELECT,INSERT,DELETE ON TABLE public.subscriptions TO app_user;
GRANT SELECT ON TABLE public.subscriptions TO read_only;


--
-- TOC entry 4991 (class 0 OID 0)
-- Dependencies: 225
-- Name: TABLE users; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.users TO admin;
GRANT SELECT,INSERT ON TABLE public.users TO app_user;
GRANT SELECT ON TABLE public.users TO read_only;


-- Completed on 2026-05-18 16:37:36

--
-- PostgreSQL database dump complete
--

\unrestrict VzHtyEHpEQQUgPlNZ1YiSZCbbefsmPlpjyfS5WYwOPHe1sKSmTXHL1q9UC75e2b

