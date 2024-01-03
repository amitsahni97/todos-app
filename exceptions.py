from fastapi import HTTPException, status


class CustomException(HTTPException):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)


class DuplicateException(CustomException):
    pass


class UnknownErrorException(CustomException):
    pass


class NoRecordFound(CustomException):
    pass


class InvalidCredentialsException(CustomException):
    pass


class ValidateTokenError(CustomException):
    pass

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
