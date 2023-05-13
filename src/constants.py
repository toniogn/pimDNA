AUTH0_DOMAIN = ""
API_AUDIENCE = ""
ALGORITHMS = ["RS256"]

DB_USER = "postgres"
DB_PASS = "postgres"
DB_SERVICE = "localhost"
DB_PORT = "5432"
DB_NAME = "postgres"
DB_SSL_ENABLED = "disable"
SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_SERVICE}:{DB_PORT}/{DB_NAME}?sslmode={DB_SSL_ENABLED}"

CURRENCY = "euro"
STRIPE_KEY = ""
