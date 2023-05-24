"""API module."""
import stripe
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..constants import STRIPE_KEY

app = FastAPI()
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
stripe.api_key = STRIPE_KEY

__all__ = ["app"]