import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    host ="localhost",
    database ="booknest",
    user ="abhi",
    password = "",
)

cursor = conn.cursor(cursor_factory = RealDictCursor)