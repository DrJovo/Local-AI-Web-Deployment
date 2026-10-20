import psycopg2
from psycopg2 import sql

ADMIN_DB = "postgres"
ADMIN_USER = "postgres"
ADMIN_PASSWORD = "your_postgres_admin_password"

APP_USER = "local_ai_user"
APP_PASSWORD = "strong_password_here"
APP_DB = "local_ai_db"

conn = psycopg2.connect(
    dbname=ADMIN_DB,
    user=ADMIN_USER,
    password=ADMIN_PASSWORD,
    host="localhost",
    port=5432,
)
conn.autocommit = True
cur = conn.cursor()

cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (APP_USER,))
if cur.fetchone() is None:
    cur.execute(
        sql.SQL("CREATE USER {} WITH PASSWORD %s").format(sql.Identifier(APP_USER)),
        [APP_PASSWORD],
    )

cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (APP_DB,))
if cur.fetchone() is None:
    cur.execute(
        sql.SQL("CREATE DATABASE {} OWNER {}").format(
            sql.Identifier(APP_DB),
            sql.Identifier(APP_USER),
        )
    )

cur.execute(
    sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
        sql.Identifier(APP_DB),
        sql.Identifier(APP_USER),
    )
)

cur.close()
conn.close()