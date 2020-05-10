''' Implements exceptions for NOW TV. '''


class BaseError(Exception):
    ''' An exception from which all should inherit. '''
    pass


class SigninError(BaseError):
    ''' Indicates an error occured during the signin flow. '''
    pass


class TokenExpiredError(BaseError):
    ''' Indicates that the provided authentication token has expired. '''
    pass


class SessionError(BaseError):
    ''' Indicates that no current, or valid, authentication session exists. '''
    pass
