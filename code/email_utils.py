import os
import smtplib

from dotenv import load_dotenv

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

EMAIL_LOGIN = os.getenv("EMAIL_LOGIN")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_email(
    to_email,
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
):

    subject = (
        f"{ticker}: выполнены условия уведомления"
    )

    metric_names = {
        "price": "Цена",
        "pe": "P/E",
        "pb": "P/B",
        "ps": "P/S",
        "fcf_e": "FCF/E",
        "net_debt_e": "Net Debt/E",
        "liquidity": "Liquidity",
        "dividend_yield": "Dividend Yield",
        "dividend_streak": "Dividend Streak"
    }

    operator_names = {
        "above": "выше",
        "below": "ниже"
    }

    conditions_html = ""

    for item in conditions:

        if item.get("type") == "positive_e":

            conditions_html += """
            <li>
                Неотрицательный E
            </li>
            """
            continue

        if item.get("type") == "positive_fcf":

            conditions_html += """
            <li>
                Неотрицательный FCF
            </li>
            """
            continue

        metric = metric_names.get(
            item["metric"],
            item["metric"]
        )

        operator = operator_names.get(
            item["operator"],
            item["operator"]
        )

        conditions_html += f"""
        <li>
            {metric}
            {operator}
            <b>{item["value"]}</b>
        </li>
        """

    html = f"""
    <html>
    <body style="
        font-family: Arial;
        background-color: #f4f6f8;
        padding: 20px;
    ">

        <div style="
            background: white;
            padding: 20px;
            border-radius: 10px;
            max-width: 500px;
            margin: auto;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        ">

            <h2 style="color:#2e7d32;">
                Уведомление по акции {ticker}
            </h2>

            <div style="
                background:#f7f9fc;
                padding:15px;
                border-radius:10px;
                margin-bottom:20px;
            ">

                <div><b>Цена:</b> {price} ₽</div>
                <div><b>P/E:</b> {pe if pe is not None else "—"}</div>
                <div><b>P/B:</b> {pb if pb is not None else "—"}</div>
                <div><b>P/S:</b> {ps if ps is not None else "—"}</div>
                <div><b>FCF/E:</b> {fcf_e if fcf_e is not None else "—"}</div>
                <div><b>Net Debt/E:</b> {net_debt_e if net_debt_e is not None else "—"}</div>
                <div><b>Liquidity:</b> {liquidity if liquidity is not None else "—"}</div>
                <div><b>Dividend Yield:</b> {dividend_yield if dividend_yield is not None else "—"}%</div>
                <div><b>Dividend Streak:</b> {dividend_streak if dividend_streak is not None else "—"} лет</div>

            </div>

            <p>
                Выполнены все условия:
            </p>

            <ul>
                {conditions_html}
            </ul>
            <div style="margin-top: 30px;">

                <a
                    href="{manage_link}"
                    style="
                        background:#1565c0;
                        color:white;
                        padding:12px 18px;
                        text-decoration:none;
                        border-radius:8px;
                        display:inline-block;
                        font-weight:bold;
                    "
                >
                    Управление подписками
                </a>

            </div>
            <hr>

            <p style="color: gray; font-size: 13px;">
                Система мониторинга MOEX
            </p>

        </div>

    </body>
    </html>
    """

    msg = MIMEMultipart()

    msg["Subject"] = subject
    msg["From"] = EMAIL_LOGIN
    msg["To"] = to_email
    msg["Reply-To"] = EMAIL_LOGIN

    msg.attach(MIMEText(html, "html", "utf-8"))

    try:

        server = smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            timeout=10
        )

        server.login(
            EMAIL_LOGIN,
            EMAIL_PASSWORD
        )

        server.sendmail(
            EMAIL_LOGIN,
            to_email,
            msg.as_string()
        )

        server.quit()

        print(f"письмо отправлено: {to_email}")

    except Exception as e:
        print("ошибка отправки:", e)