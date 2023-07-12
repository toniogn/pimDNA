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

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "edb4665177b5c387009d8bde66bc107a818670914321e19227870759c34b4dee"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
