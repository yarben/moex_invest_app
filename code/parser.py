import os
import sys
import requests
import psycopg2
import traceback
import json
from datetime import datetime, timedelta
from psycopg2.extras import execute_values

from email_utils import send_email


conn = psycopg2.connect(
    dbname="invest_db",
    user="postgres",
    password="1234",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()

LOCK_FILE = "parser.lock"

URL = (
    "https://iss.moex.com/iss/"
    "engines/stock/markets/shares/"
    "boards/tqbr/securities.json"
)

CANDLES_URL = (
    "https://iss.moex.com/iss/"
    "engines/stock/markets/shares/"
    "boards/tqbr/securities"
)


if os.path.exists(LOCK_FILE):
    print("парсер уже запущен")
    sys.exit()

with open(LOCK_FILE, "w") as f:
    f.write("running")


def load_stocks():

    cursor.execute("""
        select ticker, id
        from stocks
    """)

    return dict(cursor.fetchall())


def get_subscriptions(stock_id):

    cursor.execute("""
        select
            s.id,
            s.user_id,
            s.conditions_json,
            u.email,
            s.is_active
        from subscriptions s

        join users u
            on u.id = s.user_id

        where s.stock_id = %s
    """, (stock_id,))

    return cursor.fetchall()


def check_and_notify(
    stock_id,
    ticker,
    price,
    pe,
    pb,
    ps,
    net_debt_e,
    fcf_e,
    liquidity,
    dividend_streak,
    dividend_yield,
    net_earnings,
    free_cash_flow
):

    subscriptions = get_subscriptions(stock_id)

    metrics = {
        "price": price,
        "pe": pe,
        "pb": pb,
        "ps": ps,
        "net_debt_e": net_debt_e,
        "fcf_e": fcf_e,
        "liquidity": liquidity,
        "dividend_streak": dividend_streak,
        "dividend_yield": dividend_yield
    }

    for (
        sub_id,
        user_id,
        conditions_json,
        email,
        active
    ) in subscriptions:

        if not active:
            continue

        conditions = conditions_json["conditions"]

        positive_e = conditions_json.get(
            "positive_e",
            False
        )

        positive_fcf = conditions_json.get(
            "positive_fcf",
            False
        )
        print("positive_e =", positive_e)
        print("positive_fcf =", positive_fcf)
        print("net_earnings =", net_earnings)
        print("free_cash_flow =", free_cash_flow)
        all_conditions_met = True

        if positive_e:

            if (
                net_earnings is None
                or net_earnings < 0
            ):

                all_conditions_met = False

        if positive_fcf:

            if (
                free_cash_flow is None
                or free_cash_flow < 0
            ):

                all_conditions_met = False

        if not all_conditions_met:
            continue

        for condition_data in conditions:

            metric = condition_data["metric"]
            operator = condition_data["operator"]
            target = float(condition_data["value"])

            current_value = metrics.get(metric)

            print("-----")
            print("metric =", metric)
            print("operator =", operator)
            print("target =", target)
            print("current_value =", current_value)

            if current_value is None:

                all_conditions_met = False
                break

            if operator == "above":

                if current_value <= target:

                    all_conditions_met = False
                    break

            elif operator == "below":

                if current_value >= target:

                    all_conditions_met = False
                    break

        if not all_conditions_met:
            continue

        print(
            f"сработало: {ticker} → {email}"
        )

        cursor.execute("""
            select manage_token
            from users
            where id = %s
        """, (user_id,))

        manage_token = cursor.fetchone()[0]

        manage_link = (
            f"http://127.0.0.1:5000/manage"
            f"?token={manage_token}"
        )

        send_email(
            email,
            ticker,
            price,
            pe,
            pb,
            ps,
            fcf_e,
            net_debt_e,
            liquidity,
            dividend_yield,
            dividend_streak,
            conditions,
            manage_link
        )

        cursor.execute("""
            update subscriptions
            set is_active = false
            where id = %s
        """, (sub_id,))




def fetch_all():

    stocks_map = load_stocks()

    r = requests.get(URL)
    r.raise_for_status()

    data = r.json()

    columns = data["marketdata"]["columns"]
    rows = data["marketdata"]["data"]

    idx_sec = columns.index("SECID")
    idx_last = columns.index("LAST")

    result = []

    for row in rows:

        ticker = row[idx_sec].upper()
        price = row[idx_last]

        if ticker not in stocks_map:
            continue

        if price is None:
            continue

        result.append((
            ticker,
            float(price)
        ))

    return result


def fetch_market_stats(ticker):

    url = (
        f"{CANDLES_URL}/{ticker}.json"
    )

    r = requests.get(
        url,
        timeout=15
    )

    r.raise_for_status()

    data = r.json()

    market = {}
    security = {}

    if data["marketdata"]["data"]:

        market = dict(zip(
            data["marketdata"]["columns"],
            data["marketdata"]["data"][0]
        ))

    if data["securities"]["data"]:

        security = dict(zip(
            data["securities"]["columns"],
            data["securities"]["data"][0]
        ))

    return {
        "shares_outstanding":
            security.get("ISSUESIZE"),

        "volume":
            market.get("VOLTODAY"),

        "turnover":
            market.get("VALTODAY")
    }


def fetch_dividend_info(ticker):

    url = (
        f"https://iss.moex.com/iss/"
        f"securities/{ticker}/dividends.json"
    )

    try:

        r = requests.get(
            url,
            timeout=15
        )

        r.raise_for_status()

        data = r.json()

        rows = data["dividends"]["data"]
        columns = data["dividends"]["columns"]

        if not rows:

            return {
                "dividend_amount": None,
                "dividend_record_date": None,
                "dividend_streak": None
            }

        latest = dict(zip(
            columns,
            rows[-1]
        ))

        return {
            "dividend_amount":
                latest.get("value"),

            "dividend_record_date":
                latest.get(
                    "registryclosedate"
                ),

            "dividend_streak":
                len(rows)
        }

    except Exception as e:

        print(
            f"ошибка dividends {ticker}: {e}"
        )

        return {
            "dividend_amount": None,
            "dividend_record_date": None,
            "dividend_streak": None
        }


def should_update_daily_stats():

    cursor.execute("""
        select max(updated_at)
        from market_stats
    """)

    last_update = cursor.fetchone()[0]

    if last_update is None:
        return True

    return (
        last_update.date()
        < datetime.now().date()
    )


def update_share_capital(
    stock_id,
    shares_outstanding
):

    if shares_outstanding is None:
        return

    cursor.execute("""
        select shares_outstanding
        from share_capital_history
        where stock_id = %s
        order by effective_from desc
        limit 1
    """, (stock_id,))

    row = cursor.fetchone()

    if row and float(row[0]) == float(shares_outstanding):
        return

    cursor.execute("""
        insert into share_capital_history (
            stock_id,
            shares_outstanding,
            effective_from
        )
        values (%s, %s, now())
    """, (
        stock_id,
        shares_outstanding
    ))


def update_market_stats():

    print("обновление market_stats...")

    stocks_map = load_stocks()

    for ticker, stock_id in stocks_map.items():

        try:

            stats = fetch_market_stats(
                ticker
            )

            dividends = fetch_dividend_info(
                ticker
            )

            update_share_capital(
                stock_id,
                stats["shares_outstanding"]
            )

            cursor.execute("""
                insert into market_stats (
                    stock_id,
                    volume,
                    turnover,
                    dividend_amount,
                    dividend_record_date,
                    dividend_streak,
                    updated_at
                )
                values (
                    %s,%s,%s,%s,%s,%s,now()
                )
                on conflict (stock_id)
                do update set

                    volume = excluded.volume,

                    turnover = excluded.turnover,

                    dividend_amount =
                        excluded.dividend_amount,

                    dividend_record_date =
                        excluded.dividend_record_date,

                    dividend_streak =
                        excluded.dividend_streak,

                    updated_at = now()
            """, (

                stock_id,

                stats["volume"],

                stats["turnover"],

                dividends["dividend_amount"],

                dividends["dividend_record_date"],

                dividends["dividend_streak"]

            ))

            print(f"обновлено {ticker}")

        except Exception as e:

            conn.rollback()

            print(
                f"ошибка market_stats "
                f"{ticker}: {e}"
            )

            traceback.print_exc()

    conn.commit()


def get_last_timestamp():

    cursor.execute("""
        select max(timestamp)
        from prices
    """)

    return cursor.fetchone()[0]


def fetch_candles(
    ticker,
    from_time,
    till_time
):

    url = (
        f"{CANDLES_URL}/{ticker}"
        f"/candles.json"
    )

    result = []
    start = 0

    while True:

        params = {
            "from":
                from_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "till":
                till_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "interval": 1,
            "start": start
        }

        success = False

        for attempt in range(5):

            try:

                r = requests.get(
                    url,
                    params=params,
                    timeout=30
                )

                r.raise_for_status()

                data = r.json()

                success = True

                break

            except Exception as e:

                print(
                    f"{ticker}: попытка "
                    f"{attempt + 1}/5 "
                    f"ошибка: {e}"
                )

        if not success:
            break

        candles = data["candles"]["data"]

        if not candles:
            break

        columns = data["candles"]["columns"]

        idx_close = columns.index("close")
        idx_begin = columns.index("begin")

        for candle in candles:

            close_price = candle[idx_close]

            if close_price is None:
                continue

            result.append((
                float(close_price),

                datetime.fromisoformat(
                    candle[idx_begin]
                ).replace(
                    second=0,
                    microsecond=0
                )
            ))

        start += len(candles)

    return result


def initial_load(days=30):

    print("начальная загрузка истории...")

    now = datetime.now().replace(
        second=0,
        microsecond=0
    )

    from_time = (
        now
        - timedelta(days=days)
    )

    stocks_map = load_stocks()

    rows = []

    for ticker, stock_id in stocks_map.items():

        print(f"загрузка {ticker}...")

        try:

            candles = fetch_candles(
                ticker,
                from_time,
                now
            )

            for price, ts in candles:

                if not market_is_open(ts):
                    continue

                rows.append((
                    stock_id,
                    price,
                    ts
                ))

        except Exception as e:

            print(
                f"ошибка {ticker}: {e}"
            )

    if rows:

        execute_values(
            cursor,
            """
            insert into prices
            (stock_id, price, timestamp)
            values %s
            on conflict (stock_id, timestamp)
            do nothing
            """,
            rows
        )

        conn.commit()

        print(
            f"загружено: {len(rows)}"
        )


def recover_missing_data():

    last_ts = get_last_timestamp()

    if not last_ts:
        return

    now = datetime.now().replace(
        second=0,
        microsecond=0
    )

    diff = now - last_ts

    if diff.total_seconds() < 240:
        return

    if diff.days > 3:
        return

    print(
        f"recovery с {last_ts}"
    )

    stocks_map = load_stocks()

    rows = []

    for ticker, stock_id in stocks_map.items():

        try:

            candles = fetch_candles(
                ticker,
                last_ts,
                now
            )

            for price, ts in candles:

                if not market_is_open(ts):
                    continue

                rows.append((
                    stock_id,
                    price,
                    ts
                ))

        except Exception as e:

            print(
                f"ошибка recovery "
                f"{ticker}: {e}"
            )

    if rows:

        execute_values(
            cursor,
            """
            insert into prices
            (stock_id, price, timestamp)
            values %s
            on conflict (stock_id, timestamp)
            do nothing
            """,
            rows
        )

        conn.commit()


def save_data(items):

    now = datetime.now().replace(
        second=0,
        microsecond=0
    )

    stocks_map = load_stocks()

    for ticker, price in items:

        if ticker not in stocks_map:
            continue

        stock_id = stocks_map[ticker]

        cursor.execute("""
            insert into prices (
                stock_id,
                price,
                timestamp
            )
            values (%s, %s, %s)
            on conflict (
                stock_id,
                timestamp
            )
            do nothing
        """, (
            stock_id,
            price,
            now
        ))

        cursor.execute("""
            select
                f.net_earnings,
                f.equity,
                f.revenue,
                f.net_debt,
                f.free_cash_flow,
                f.free_float_percent,

                sch.shares_outstanding,

                ms.volume,
                ms.dividend_amount,
                ms.dividend_streak

            from fundamentals f

            left join (
                select distinct on (stock_id)
                    stock_id,
                    shares_outstanding
                from share_capital_history
                order by stock_id, effective_from desc
            ) sch
                on sch.stock_id = f.stock_id

            left join market_stats ms
                on ms.stock_id = f.stock_id

            where f.stock_id = %s

            order by f.report_date desc
            limit 1
        """, (stock_id,))

        row = cursor.fetchone()

        pe = None
        pb = None
        ps = None
        net_debt_e = None
        fcf_e = None
        liquidity = None
        dividend_streak = None
        dividend_yield = None

        if row:

            net_earnings = row[0]
            equity = row[1]
            revenue = row[2]
            net_debt = row[3]
            free_cash_flow = row[4]
            free_float_percent = row[5]

            shares_outstanding = row[6]

            volume = row[7]
            dividend_amount = row[8]
            dividend_streak = row[9]

            if shares_outstanding:

                market_cap = (
                    float(price)
                    * float(shares_outstanding)
                )

                if (
                    net_earnings
                    and float(net_earnings) != 0
                ):

                    pe = round(
                        market_cap
                        / float(net_earnings),
                        2
                    )

                    if net_debt is not None:

                        net_debt_e = round(
                            float(net_debt)
                            / float(net_earnings),
                            2
                        )

                    if free_cash_flow is not None:

                        fcf_e = round(
                            float(free_cash_flow)
                            / float(net_earnings),
                            2
                        )

                if (
                    equity
                    and float(equity) != 0
                ):

                    pb = round(
                        market_cap
                        / float(equity),
                        2
                    )

                if (
                    revenue
                    and float(revenue) != 0
                ):

                    ps = round(
                        market_cap
                        / float(revenue),
                        2
                    )

            if (
                volume
                and free_float_percent
            ):

                liquidity = round(
                    float(volume)
                    * float(free_float_percent)
                    / 61200,
                    2
                )

            if (
                dividend_amount
                and price
            ):

                dividend_yield = round(
                    float(dividend_amount)
                    / float(price)
                    * 100,
                    2
                )

        check_and_notify(
            stock_id,
            ticker,
            price,
            pe,
            pb,
            ps,
            net_debt_e,
            fcf_e,
            liquidity,
            dividend_streak,
            dividend_yield,
            net_earnings,
            free_cash_flow
        )

    conn.commit()


def market_is_open(
    check_time=None
):

    if check_time is None:
        check_time = datetime.now()

    if check_time.weekday() >= 5:
        return False

    current_minutes = (
        check_time.hour * 60
        + check_time.minute
    )

    start = 6 * 60 + 50
    end = 23 * 60 + 50

    return (
        start
        <= current_minutes
        <= end
    )


if __name__ == "__main__":

    try:

        if should_update_daily_stats():
            update_market_stats()

        if not market_is_open():

            print("рынок закрыт")

        else:

            cursor.execute("""
                select count(*)
                from prices
            """)

            if cursor.fetchone()[0] == 0:

                initial_load(days=30)

            else:

                print(
                    "проверка пропусков..."
                )

                recover_missing_data()

            data = fetch_all()

            print(
                f"получено: "
                f"{len(data)} акций"
            )

            save_data(data)

            print("сохранено в БД")

    finally:

        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)