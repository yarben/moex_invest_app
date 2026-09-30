from flask import Flask, render_template, request, redirect
import json
import psycopg2

app = Flask(__name__)


def get_connection():
    return psycopg2.connect(
        dbname="invest_db",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )

def format_billions(value):

    if value is None:
        return "—"

    return f"{round(float(value) / 1_000_000_000):,}".replace(",", " ") + " млрд ₽"

def format_number(value):

    if value is None:
        return "—"

    return f"{round(float(value)):,}".replace(",", " ")

@app.route("/manage")
def manage():

    token = request.args.get("token")

    if not token:
        return "Нет токена"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        select id, email
        from users
        where manage_token = %s
    """, (token,))

    user = cursor.fetchone()

    if not user:

        cursor.close()
        conn.close()

        return "Неверная ссылка"

    user_id = user[0]
    email = user[1]

    cursor.execute("""
        select
            sub.id,
            st.ticker,
            st.name,
            sub.conditions_json,
            sub.is_active
        from subscriptions sub
        join stocks st
            on sub.stock_id = st.id
        where sub.user_id = %s
        order by st.ticker
    """, (user_id,))

    rows = cursor.fetchall()

    subs = []

    for row in rows:
        subs.append({
            "id": row[0],
            "ticker": row[1],
            "name": row[2],
            "conditions": row[3],
            "is_active": row[4]
        })

    cursor.close()
    conn.close()

    return render_template(
        "manage.html",
        subs=subs,
        token=token,
        email=email
    )


@app.route("/delete_subscription")
def delete_subscription():

    sub_id = request.args.get("id")
    token = request.args.get("token")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        select id
        from users
        where manage_token = %s
    """, (token,))

    user = cursor.fetchone()

    if not user:

        cursor.close()
        conn.close()

        return "Неверный токен"

    user_id = user[0]

    cursor.execute("""
        delete from subscriptions
        where id = %s
        and user_id = %s
    """, (
        sub_id,
        user_id
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(f"/manage?token={token}")


@app.route("/subscribe", methods=["POST"])
def subscribe():
    ticker = request.form["ticker"].upper()

    email = request.form["email"]
    positive_e = "positiveE" in request.form
    positive_fcf = "positiveFCF" in request.form
    metrics = request.form.getlist(
        "metric[]"
    )

    operators = request.form.getlist(
        "operator[]"
    )

    values = request.form.getlist(
        "value[]"
    )

    conditions_json = []
    for metric, operator, value in zip(
        metrics,
        operators,
        values
    ):

        conditions_json.append({
            "metric": metric,
            "operator": operator,
            "value": float(value)
        })

    subscription_data = {

        "conditions": conditions_json,
        "positive_e": positive_e,
        "positive_fcf": positive_fcf
    }
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        insert into users(email)
        values(%s)
        on conflict(email) do nothing
    """, (email,))

    cursor.execute("""
        select id
        from users
        where email = %s
    """, (email,))

    user_id = cursor.fetchone()[0]

    cursor.execute("""
        select id
        from stocks
        where ticker = %s
    """, (ticker,))

    stock_id = cursor.fetchone()[0]

    cursor.execute("""
        insert into subscriptions
        (
            user_id,
            stock_id,
            conditions_json,
            is_active
        )
        values (%s, %s, %s, TRUE)
    """, (
        user_id,
        stock_id,
        json.dumps(subscription_data)
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(
        f"/?ticker={ticker}&subscribed=1"
)

@app.route("/activate_subscription")
def activate_subscription():

    sub_id = request.args.get("id")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        select is_active
        from subscriptions
        where id = %s
    """, (sub_id,))

    row = cursor.fetchone()

    if not row:
        conn.close()
        return "not found", 404

    current_active = row[0]

    new_active = not current_active

    cursor.execute("""
        update subscriptions
        set is_active = %s
        where id = %s
    """, (new_active, sub_id))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(request.referrer)

@app.route("/")
def home():

    ticker = request.args.get(
        "ticker",
        "SBER"
    ).upper()

    period = request.args.get(
        "period",
        "day"
    )

    metric = request.args.get(
        "metric",
        "price"
    ).lower()

    compare = request.args.get(
        "compare",
        ""
    )

    compare_tickers = [
        t.strip().upper()
        for t in compare.split(",")
        if t.strip()
    ]

    all_tickers = [ticker]

    for t in compare_tickers:
        if t not in all_tickers:
            all_tickers.append(t)

    subscribed = request.args.get(
        "subscribed"
    )

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        select
            id,
            ticker,
            name
        from stocks
        where ticker = %s
    """, (ticker,))

    stock = cur.fetchone()

    if not stock:

        cur.close()
        conn.close()

        return "нет такого тикера"

    stock_id = stock[0]
    stock_ticker = stock[1]
    stock_name = stock[2]

    stock_display_name = (
        f"{stock_name} ({stock_ticker})"
    )

    cur.execute("""
        select max(timestamp)
        from prices
        where stock_id = %s
    """, (stock_id,))

    latest_timestamp = cur.fetchone()[0]

    if not latest_timestamp:

        cur.close()
        conn.close()

        return "нет данных по акции"

    cur.execute("""
        select
            f.equity,
            f.total_assets,
            f.net_earnings,
            f.total_debt,
            f.net_debt,
            f.free_cash_flow,
            f.revenue,
            f.free_float_percent,
            m.volume,
            m.turnover,
            sch.shares_outstanding
        from fundamentals f

        left join market_stats m
            on f.stock_id = m.stock_id

        left join (
            select distinct on (stock_id)
                stock_id,
                shares_outstanding
            from share_capital_history
            order by stock_id, effective_from desc
        ) sch
            on f.stock_id = sch.stock_id

        where f.stock_id = %s

        order by f.report_date desc

        limit 1
    """, (stock_id,))

    fundamentals = cur.fetchone()

    cur.execute("""
        select
            dividend_amount,
            dividend_record_date,
            dividend_streak
        from market_stats
        where stock_id = %s
    """, (stock_id,))

    dividend_data = cur.fetchone()

    day_interval = "1 day"

    cur.execute("""
        select price
        from prices
        where stock_id = %s
        and timestamp >= %s::timestamp - interval %s
        order by timestamp
    """, (
        stock_id,
        latest_timestamp,
        day_interval
    ))

    day_data = cur.fetchall()

    day_prices = [
        float(x[0])
        for x in day_data
    ]

    interval = {
        "day": "1 day",
        "week": "7 days",
        "month": "30 days"
    }.get(period, "1 day")

    cur.execute("""
        select
            price,
            timestamp
        from prices
        where stock_id = %s
        and timestamp >= %s::timestamp - interval %s
        order by timestamp
    """, (
        stock_id,
        latest_timestamp,
        interval
    ))

    data = cur.fetchall()

    # история количества акций
    cur.execute("""
        select
            effective_from,
            shares_outstanding
        from share_capital_history
        where stock_id = %s
        order by effective_from
    """, (stock_id,))

    share_history = cur.fetchall()


    # история фундаментала
    cur.execute("""
        select
            report_date,
            equity,
            net_earnings
        from fundamentals
        where stock_id = %s
        order by report_date
    """, (stock_id,))

    fundamentals_history = cur.fetchall()

    colors = [
        "#1976d2",
        "#d32f2f",
        "#2e7d32",
        "#f57c00",
        "#7b1fa2",
        "#455a64"
    ]

    chart_datasets = []

    all_tickers = [ticker] + compare_tickers

    timestamps = [
        x[1].strftime("%Y-%m-%d %H:%M")
        for x in data
    ]

    prices = []
    pe_values = []
    pb_values = []

    for dataset_index, current_ticker in enumerate(all_tickers):

        cur.execute("""
            select id
            from stocks
            where ticker = %s
        """, (current_ticker,))

        row = cur.fetchone()

        if not row:
            continue

        current_stock_id = row[0]

        cur.execute("""
            select max(timestamp)
            from prices
            where stock_id = %s
        """, (current_stock_id,))

        current_latest_timestamp = cur.fetchone()[0]

        if not current_latest_timestamp:
            continue

        cur.execute("""
            select
                price,
                timestamp
            from prices
            where stock_id = %s
            and timestamp >= %s::timestamp - interval %s
            order by timestamp
        """, (
            current_stock_id,
            current_latest_timestamp,
            interval
        ))

        current_data = cur.fetchall()

        cur.execute("""
            select
                effective_from,
                shares_outstanding
            from share_capital_history
            where stock_id = %s
            order by effective_from
        """, (current_stock_id,))

        current_share_history = cur.fetchall()

        cur.execute("""
            select
                report_date,
                equity,
                net_earnings
            from fundamentals
            where stock_id = %s
            order by report_date
        """, (current_stock_id,))

        current_fund_history = cur.fetchall()

        current_prices = []
        current_pe = []
        current_pb = []

        share_index = 0
        fund_index = 0

        current_shares = None
        current_equity = None
        current_net_earnings = None

        for price, ts in current_data:

            price = float(price)

            while (
                share_index < len(current_share_history)
                and current_share_history[share_index][0] <= ts
            ):

                current_shares = float(
                    current_share_history[share_index][1]
                )

                share_index += 1

            while (
                fund_index < len(current_fund_history)
                and current_fund_history[fund_index][0] <= ts.date()
            ):

                current_equity = current_fund_history[fund_index][1]

                current_net_earnings = current_fund_history[fund_index][2]

                fund_index += 1

            current_prices.append(price)

            market_cap = None

            if current_shares:

                market_cap = (
                    price * current_shares
                )

            pe = None
            pb = None

            if (
                market_cap
                and current_net_earnings
                and current_net_earnings != 0
            ):
                pe = round(
                    market_cap
                    / float(current_net_earnings),
                    2
                )

            if (
                market_cap
                and current_equity
                and current_equity != 0
            ):
                pb = round(
                    market_cap
                    / float(current_equity),
                    2
                )

            current_pe.append(pe)
            current_pb.append(pb)

        if current_ticker == ticker:

            prices = current_prices
            pe_values = current_pe
            pb_values = current_pb

        if metric == "price":

            values = current_prices

        elif metric == "pe":

            values = current_pe

        else:

            values = current_pb

        chart_datasets.append({
            "label": current_ticker,
            "data": values,
            "borderColor": colors[
                dataset_index % len(colors)
            ],
            "borderWidth": 2,
            "pointRadius": 0,
            "pointHoverRadius": 4,
            "fill": False,
            "tension": 0
        })

    chart_values = prices

    if len(prices) >= 2:

        change = round(
            prices[-1] - prices[0],
            2
        )

        change_percent = round(
            (
                change / prices[0]
            ) * 100,
            2
        )

    else:

        change = 0
        change_percent = 0

    last_price = (
        prices[-1]
        if prices
        else 0
    )

    cur.execute("""
        select
            equity,
            total_assets,
            net_earnings,
            total_debt,
            net_debt,
            free_cash_flow,
            revenue,
            free_float_percent
        from fundamentals
        where stock_id = %s
        order by report_date desc
        limit 1
    """, (stock_id,))

    fund_row = cur.fetchone()

    cur.execute("""
        select
            volume,
            turnover,
            dividend_amount,
            dividend_record_date,
            dividend_streak
        from market_stats
        where stock_id = %s
    """, (stock_id,))

    market_row = cur.fetchone()

    cur.execute("""
        select shares_outstanding
        from share_capital_history
        where stock_id = %s
        order by effective_from desc
        limit 1
    """, (stock_id,))

    shares_row = cur.fetchone()

    if fund_row:

        equity = fund_row[0]
        total_assets = fund_row[1]
        net_earnings = fund_row[2]
        total_debt = fund_row[3]
        net_debt = fund_row[4]
        free_cash_flow = fund_row[5]
        revenue = fund_row[6]
        free_float_percent = fund_row[7]

    else:

        equity = None
        total_assets = None
        net_earnings = None
        total_debt = None
        net_debt = None
        free_cash_flow = None
        revenue = None
        free_float_percent = None

    if market_row:

        volume = market_row[0]
        turnover = market_row[1]

        dividend_amount = market_row[2]
        dividend_record_date = market_row[3]
        dividend_streak = market_row[4]

    else:

        volume = None
        turnover = None

        dividend_amount = None
        dividend_record_date = None
        dividend_streak = None

    shares_outstanding = (
        shares_row[0]
        if shares_row
        else None
    )

    if dividend_amount and prices:

        dividend_yield = round(
            (
                float(dividend_amount)
                / float(prices[-1])
            ) * 100,
            2
        )

    else:

        dividend_yield = None


    market_cap = (
        last_price * float(shares_outstanding)
        if last_price and shares_outstanding
        else None
    )

    p_e = (
        round(
            market_cap / float(net_earnings),
            2
        )
        if market_cap
        and net_earnings
        and float(net_earnings) != 0
        else "—"
    )

    p_b = (
        round(
            market_cap / float(equity),
            2
        )
        if market_cap
        and equity
        and float(equity) != 0
        else "—"
    )

    roe = (
        round(
            float(net_earnings)
            / float(equity)
            * 100,
            2
        )
        if net_earnings
        and equity
        and float(equity) != 0
        else "—"
    )

    p_s = (
        round(
            market_cap / float(revenue),
            2
        )
        if market_cap
        and revenue
        and float(revenue) != 0
        else "—"
    )

    fcf_e = (
        round(
            float(free_cash_flow)
            / float(net_earnings),
            2
        )
        if free_cash_flow
        and net_earnings
        and float(net_earnings) != 0
        else "—"
    )

    net_debt_e = (
        round(
            float(net_debt)
            / float(net_earnings),
            2
        )
        if net_debt
        and float(net_debt) >= 0
        and net_earnings
        and float(net_earnings) != 0
        else "—"
    )

    liquidity = (
        round(
            float(volume)
            * float(free_float_percent)
            / 61200,
            2
        )
        if volume
        and free_float_percent
        else None
    )

    cur.execute("""
        select
            f.net_earnings,
            f.equity,
            sch.shares_outstanding
        from fundamentals f
        left join (
            select distinct on (stock_id)
                stock_id,
                shares_outstanding
            from share_capital_history
            order by stock_id, effective_from desc
        ) sch
            on sch.stock_id = f.stock_id
        where f.stock_id = %s
    """, (stock_id,))

    fundamentals = cur.fetchone()

    pe_ratio = None
    pb_ratio = None

    if fundamentals and last_price:

        net_earnings = fundamentals[0]
        equity = fundamentals[1]
        shares_outstanding = fundamentals[2]

        if shares_outstanding:

            market_cap = (
                last_price
                * float(shares_outstanding)
            )

            if net_earnings and net_earnings != 0:

                pe_ratio = round(
                    market_cap
                    / float(net_earnings),
                    2
                )

            if equity and equity != 0:

                pb_ratio = round(
                    market_cap
                    / float(equity),
                    2
                )

    cur.execute("""
        select
            ticker,
            name
        from stocks
        order by ticker
    """)

    tickers = [
        {
            "ticker": row[0],
            "label": (
                f"{row[1]} ({row[0]})"
                if row[1]
                else row[0]
            )
        }
        for row in cur.fetchall()
    ]

    cur.execute("""
        select
            s.ticker,
            p.price,

            case
                when f.net_earnings is not null
                     and f.equity is not null
                     and f.equity != 0
                then round(
                    (
                        f.net_earnings
                        / f.equity
                        * 100
                    )::numeric,
                    2
                )
                else null
            end as roe,

            case
                when f.net_earnings is not null
                     and f.net_earnings != 0
                     and sch.shares_outstanding is not null
                then round(
                    (
                        (
                            p.price * sch.shares_outstanding
                        ) / f.net_earnings
                    )::numeric,
                    2
                )
                else null
            end as pe,

            case
                when f.equity is not null
                     and f.equity != 0
                     and sch.shares_outstanding is not null
                then round(
                    (
                        (
                            p.price * sch.shares_outstanding
                        ) / f.equity
                    )::numeric,
                    2
                )
                else null
            end as pb

        from stocks s

        join (
            select distinct on (stock_id)
                stock_id,
                price
            from prices
            order by stock_id, timestamp desc
        ) p
            on p.stock_id = s.id

        left join (
            select distinct on (stock_id)
                stock_id,
                net_earnings,
                equity
            from fundamentals
            order by stock_id, report_date desc
        ) f
            on f.stock_id = s.id

        left join (
            select distinct on (stock_id)
                stock_id,
                shares_outstanding
            from share_capital_history
            order by stock_id, effective_from desc
        ) sch
            on sch.stock_id = s.id

        order by pe desc
    """)

    market_table = cur.fetchall()

    stocks_table = []

    for row in market_table:
        stocks_table.append({
            "ticker": row[0],
            "price": row[1],
            "roe": row[2],
            "pe": row[3],
            "pb": row[4]
        })

    cur.close()
    conn.close()

    equity_display = format_billions(equity)
    total_assets_display = format_billions(total_assets)
    revenue_display = format_billions(revenue)
    net_earnings_display = format_billions(net_earnings)
    total_debt_display = format_billions(total_debt)
    net_debt_display = format_billions(net_debt)
    free_cash_flow_display = format_billions(free_cash_flow)
    liquidity_display = format_number(liquidity)
    turnover_display = format_number(turnover)
    volume_display = format_number(volume)
    shares_outstanding_display = format_number(shares_outstanding)

    dividend_amount_display = (
        f"{dividend_amount} ₽"
        if dividend_amount is not None
        else "—"
    )

    dividend_yield_display = (
        f"{dividend_yield}%"
        if dividend_yield is not None
        else "—"
    )

    dividend_record_date_display = (
        dividend_record_date.strftime("%d.%m.%Y")
        if dividend_record_date
        else "—"
    )

    dividend_streak_display = (
        f"{dividend_streak} лет"
        if dividend_streak is not None
        else "—"
    )

    return render_template(
        "index.html",
        ticker=ticker,
        stock_name=stock_name,
        stock_display_name=stock_display_name,
        prices=prices,
        chart_values=json.dumps(chart_values),
        timestamps=json.dumps(timestamps),
        tickers=tickers,
        last_price=last_price,
        change=change,
        change_percent=change_percent,
        period=period,
        metric=metric,
        subscribed=subscribed,
        pe_ratio=pe_ratio,
        pb_ratio=pb_ratio,
        p_e=p_e,
        p_b=p_b,
        roe=roe,
        p_s=p_s,
        fcf_e=fcf_e,
        net_debt_e=net_debt_e,
        liquidity=liquidity_display,
        equity=equity_display,
        total_assets=total_assets_display,
        revenue=revenue_display,
        net_earnings=net_earnings_display,
        total_debt=total_debt_display,
        net_debt=net_debt_display,
        free_cash_flow=free_cash_flow_display,
        free_float_percent=free_float_percent,
        volume=volume_display,
        turnover=turnover_display,
        shares_outstanding=shares_outstanding_display,
        dividend_amount=dividend_amount_display,
        dividend_yield=dividend_yield_display,
        dividend_record_date=dividend_record_date_display,
        dividend_streak=dividend_streak_display,
        liquidity_value=liquidity,
        dividend_yield_value=dividend_yield,
        dividend_streak_value=dividend_streak,
        market_table=market_table,
        stocks_table=stocks_table,
        chart_datasets=chart_datasets
    )


if __name__ == "__main__":
    app.run(debug=True)