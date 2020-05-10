''' Implements a NOW TV / Sky SSO client. '''

import requests
import datetime
import simplecache

from resources.lib.nowtv import constants
from resources.lib.nowtv import exceptions


class Client(object):
    ''' Implements a NOW TV / Sky SSO client. '''

    def __init__(self):
        '''
        Provides a SkySSO authentication client, which masquerades as a NOW TV
        browser.
        '''
        self.cache = simplecache.SimpleCache()
        self.headers = constants.HTTP_HEADERS

        # Internal variables for properties.
        if self.cache.get(constants.CACHE_KEY_SSO_TOKEN):
            self._token = self.cache.get(constants.CACHE_KEY_SSO_TOKEN)
        else:
            self._token = None

    def authenticate(self, username, password):
        '''
        Attempt to authenticate with IDAPI to generate a new SSO Token.

        Args:
            username (str): The username to authenticate with.
            password (str): The password to authenticate with.

        Raises:
            SinginError: Indicates the error that occured during signin.
        '''
        # Bolt on additional headers.
        headers = constants.HTTP_HEADERS
        headers['Accept'] = 'application/vnd.siren+json'
        headers['Origin'] = 'https://www.nowtv.com'
        headers['Referer'] = 'https://www.nowtv.com/gb/sign-in'

        try:
            request = requests.post(
                constants.URI_IDAPI_SIGNIN,
                headers=headers,
                data={
                    'rememberMe': 'false',
                    'userIdentifier': username,
                    'password': password,
                }
            )
            request.raise_for_status()
        except requests.exceptions.HTTPError as err:
            # Attempt to process error JSON, if present.
            if hasattr(err, 'response'):
                if hasattr(err.response, 'json'):
                    # Sometimes the response is empty, but a JSON content-type
                    # is set. This breaks the parser.
                    if err.response.content > 1:
                        raise exceptions.SigninError(err.response.json())

            # Otherwise, raise a generic error.
            raise exceptions.SigninError(err)

        # Split out the token and push it into cache.
        try:
            self.token = request.cookies['skySSO']
        except KeyError as err:
            raise exceptions.SigninError(
                'Unable to retrieve skySSO token: {0}'.format(err)
            )

    def profile(self):
        '''
        Attempt to retrieve the profile associated with the current token.

        Returns:
            A dictionary of profile information as returned by the API.

        Raises:
            BaseError: Indicates the unknown error which occurred.
            TokenExpiredError: Indicates that the current token has expired.
        '''
        # Bolt on additional headers.
        headers = constants.HTTP_HEADERS
        headers['Accept'] = 'application/vnd.aggregator.v3+json'
        headers['Referer'] = 'https://www.nowtv.com/gb/watch/home'
        headers['Content-Type'] = 'application/vnd.aggregator.v3+json'
        headers['X-SkyId-Token'] = 'Session {0}'.format(self.token)

        try:
            request = requests.get(
                constants.URI_OOGATEWAY_PROFILE,
                headers=headers,
            )
            request.raise_for_status()
        except requests.exceptions.HTTPError as err:
            # Attempt to process error JSON, if present.
            if hasattr(err, 'response'):
                if hasattr(err.response, 'json'):
                    # Handle 'Profile Not Found'.
                    error_code = err.response.json()['errorcode']
                    if error_code == constants.ERROR_OOGATEWAY_TOKEN_EXPIRED:
                        self.token = None
                        raise exceptions.TokenExpiredError(
                            err.response.json()['message']
                        )

            # Otherwise, raise a generic error.
            raise exceptions.BaseError(err)

        return request.json()

    @property
    def token(self):
        '''
        Implements a getter for the token property.

        Returns:
            str: The current SkySSO userToken.
        '''
        return self._token

    @token.setter
    def token(self, value):
        '''
        Implements a setter for the token property. This method also includes
        cache maintenance.

        Args:
            value (str): The value to set the token to.
        '''
        self._token = value
        self.cache.set(
            constants.CACHE_KEY_SSO_TOKEN,
            value,
            expiration=datetime.timedelta(
                hours=constants.CACHE_LIFETIME_SSO_TOKEN,
            )
        )
