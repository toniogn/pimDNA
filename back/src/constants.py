import os
from datetime import timedelta

AUTH0_DOMAIN = ""
API_AUDIENCE = ""
ALGORITHMS = ["RS256"]

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
POSTGRES_SSL = os.getenv("POSTGRES_SSL", "disable")
SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}?sslmode={POSTGRES_SSL}"

CURRENCY = "euro"
STRIPE_KEY = ""

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "edb4665177b5c387009d8bde66bc107a818670914321e19227870759c34b4dee"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRATION = timedelta(minutes=30)
