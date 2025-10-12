
# Custom Exception Classes

class BaseExceptionClass(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class Environment_Variable_Exception(BaseExceptionClass):
    pass 


class InUseError(BaseExceptionClass):
    pass

class InvalidToken(BaseExceptionClass):
    pass


class TokenExpired(BaseExceptionClass):
    pass


class NotFoundError(BaseExceptionClass):
    pass


class AlreadyExistsError(BaseExceptionClass):
    pass


class InvalidEmailPassword(BaseExceptionClass):
    pass


class BadRequest(BaseExceptionClass):
    pass


class NotVerified(BaseExceptionClass):
    pass


class EmailVerificationError(BaseExceptionClass):
    pass


class DatabaseError(BaseExceptionClass):
    pass


class ServerError(BaseExceptionClass):
    pass


class NotActive(BaseExceptionClass):
    pass