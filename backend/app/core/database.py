import psycopg2

conn = psycopg2.connect(
    host ="localhost",
    database ="booknest",
    user ="abhi",
    password = "",
)

cursor = conn.cursor()