"""Authentication dependency module."""
import jwt
import requests
from fastapi import Header, HTTPException
from jwt import PyJWKClient
from requests import Response
from sqlalchemy.orm import Query, Session
from sqlalchemy.orm.exc import NoResultFound

from ..api.utils import User as APIUser
from ..constants import ALGORITHMS, API_AUDIENCE, AUTH0_DOMAIN
from ..database.models import User as DBUser
from ..logger import Logger

logger = Logger(__name__)


def validate_token(authorization: str = Header(...)) -> None:
    """Validate jwt authentication token.

    Args:
        authorization: Authorization header.

    Raises:
        HTTPException: Invalid or expired token.
    """
    token = authorization.split(" ")[-1]
    jwks_client = PyJWKClient("https://" + AUTH0_DOMAIN + "/.well-known/jwks.json")
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        jwt.decode(
            token,
            signing_key.key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
        )
    except jwt.ExpiredSignatureError as expired_signature:
        exception = HTTPException(
            401,
            "signature has expired",
        )
        logger.exception(exception)
        raise exception from expired_signature
    except (jwt.DecodeError, jwt.InvalidTokenError) as invalid_token:
        exception = HTTPException(
            401,
            "invalid token",
        )
        logger.exception(exception)
        raise exception from invalid_token


class AuthenticatedUser:
    """Authenticated user class."""

    def __init__(self, authorization: str = Header(...)) -> None:
        """Initialize authenticated user.

        Decode jwt token and initialize attributes.

        Args:
            authorization: Authorization header.
        """
        self.token = authorization.split(" ")[-1]
        decoded_token = self.decode_jwt_token()
        self.auth0_id = decoded_token["sub"]
        self.initial_connection = decoded_token["iat"]

    def decode_jwt_token(self) -> str:
        """Decode jwt token.

        Returns:
            str: Decoded token.
        """
        decoded_token = jwt.decode(
            self.token,
            audience=API_AUDIENCE,
            options={"verify_signature": False},
        )
        return decoded_token

    def create_in_db(self, db_session: Session) -> DBUser:
        """Create user in database.

        Args:
            db_session: Database session.

        Returns:
            DBUser: User object.
        """
        logger.info("log in for the first time")
        response: Response = requests.get(
            f"https://{AUTH0_DOMAIN}/userinfo",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        auth0_info = response.json()
        db_user = DBUser(
            auth0_id=self.auth0_id,
            name=auth0_info["name"],
            email=auth0_info["email"],
        )
        db_session.add(db_user)
        db_session.commit()
        return db_user

    def get_from_db(self, db_session: Session) -> DBUser:
        """Get user from database based on auth0 id.

        Args:
            db_session: Database session.

        Returns:
            DBUser: User object.
        """
        query: Query = db_session.query(DBUser).filter_by(auth0_id=self.auth0_id)
        return query.one()

    def get_from_or_create_in_db(self, db_session: Session) -> APIUser:
        """Get user from database or create one if it does not exist.

        Args:
            db_session: Database session.

        Returns:
            APIUser: User object.
        """
        try:
            db_user = self.get_from_db(db_session)
        except NoResultFound:
            db_user = self.create_in_db(db_session)
        else:
            logger.info("log in as a known user")
        return APIUser.from_orm(db_user)
