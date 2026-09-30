import psycopg2

conn = psycopg2.connect(
    dbname="invest_db",
    user="postgres",
    password="1234",
    host="localhost",
    port="5432"
)

print("Подключение успешно!")
conn.close()