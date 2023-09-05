class AuthenticationError(Exception):
    "Exception for Non-Authorized users"


class InvalidArg(AuthenticationError):
    pass

class UnExpectedError(InvalidArg):
    pass
