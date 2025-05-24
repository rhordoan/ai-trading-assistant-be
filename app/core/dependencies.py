# app/core/dependencies.py

from fastapi import Depends, HTTPException, Cookie
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.crud import user as crud_user
from app.models.user import User


def get_current_user(
    access_token: str = Cookie(None, alias="access_token"),
    db: Session = Depends(get_db),
) -> User:
    """
    Retrieve the current user based on the access token cookie.
    Raises:
      - 401 if missing or invalid token
      - 404 if the user record doesn’t exist
    """
    if access_token is None:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    try:
        payload = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        email: str = payload.get("sub")
        if email is None:
            raise JWTError()
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = crud_user.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
