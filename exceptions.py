from fastapi import HTTPException, status


def invalid_credentials_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )

    return credentials_exception


def invalid_token_exception():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect user name or password"
    )


def invalid_user_name():
    raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="User name should be greater than 0 & less than 15"
        )
