''' Implements a NOW TV / Sky OTT client. '''

import json
import requests
import datetime
import simplecache

from hashlib import md5

from resources.lib.nowtv import constants
from resources.lib.nowtv import exceptions


class Client(object):
    ''' Implements a NOW TV / Sky OTT client. '''

    def __init__(self):
        '''
        Provides an OTT (Over-The-Top) client, which masquerades as a NOW TV
        browser.
        '''
        self.cache = simplecache.SimpleCache()
        self.headers = constants.HTTP_HEADERS

        # Internal variables for properties.
        if self.cache.get(constants.CACHE_KEY_OTT_TOKEN):
            self._token = self.cache.get(constants.CACHE_KEY_OTT_TOKEN)
        else:
            self._token = None

    def authenticate(self, sso_token):
        '''
        Attempt to authenticate with OTT to generate a new OTT Token.

        Args:
            sso_token (str): A valid SkySSO Token.

        Raises:
            SinginError: Indicates the error that occured during signin.
            TokenExpiredError: Indicates that the current token has expired.
        '''
        # Payload needs to be built first, as a valid MD5 of the payload must
        # also be submited
        payload = json.dumps(
            {
                'auth': {
                    'authScheme': 'SSO',
                    'authToken': sso_token,
                    'authIssuer': 'NOWTV',
                    'provider': 'NOWTV',
                    'providerTerritory': 'GB',
                    'proposition': 'NOWTV',
                },
                'device': {
                    'type': 'COMPUTER',
                    'platform': 'PC',
                },
            }
        )

        # Bolt on additional headers.
        headers = constants.HTTP_HEADERS
        headers['Content-Type'] = 'application/vnd.tokens.v1+json'
        headers['Accept'] = 'application/vnd.tokens.v1+json'
        headers['Referer'] = 'https://www.nowtv.com/gb/sign-in'
        headers['Content-MD5'] = md5(bytes(payload)).hexdigest()

        try:
            request = requests.post(
                constants.URI_OTT_AUTH_TOKENS,
                headers=headers,
                data=payload,
            )
            request.raise_for_status()
        except requests.exceptions.HTTPError as err:
            # Attempt to process error JSON, if present.
            if hasattr(err, 'response'):
                if hasattr(err.response, 'json'):
                    # Handle 'Security failure'.
                    error_code = err.response.json()['errorCode']
                    if error_code == constants.ERROR_SSO_TOKEN_EXPIRED:
                        self.token = None
                        raise exceptions.TokenExpiredError(
                            err.response.json()['description']
                        )

            # Otherwise, just fail with the HTTP status.
            raise exceptions.SigninError(err)

        # Attempt to catch API changes.
        try:
            self.token = request.json()['userToken']
        except KeyError as err:
            raise exceptions.BaseError(
                'Unable to retrieve user token: {0}'.format(err)
            )

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
            constants.CACHE_KEY_OTT_TOKEN,
            value,
            expiration=datetime.timedelta(
                hours=constants.CACHE_LIFETIME_OTT_TOKEN,
            )
        )

    def userinfo(self):
        '''
        Returns a dict of user information as returned by the API.

        Result:
            dict: A dict of user information

        Raises:
            TokenExpiredError: ....
            BaseError: A generic error occured during the HTTP exchange, this
                may be due to authentication failure, or underlying transport
                issue.
        '''
        # Bolt on additional headers.
        headers = constants.HTTP_HEADERS
        headers['Content-Type'] = 'application/vnd.userinfo.v2+json'
        headers['Accept'] = 'application/vnd.userinfo.v2+json'
        headers['Referer'] = 'https://www.nowtv.com/gb/sign-in'
        headers['Content-MD5'] = md5(bytes('')).hexdigest()
        headers['X-SkyOTT-UserToken'] = self.token

        try:
            request = requests.get(
                constants.URI_OTT_AUTH_USERS_ME,
                headers=headers,
            )
            request.raise_for_status()
        except requests.exceptions.HTTPError as err:
            # Raise the response JSON as the exception body if present.
            if hasattr(err, 'response'):
                if hasattr(err.response, 'json'):
                    # Handle known errors.
                    if err.response.json()['errorCode'] == 'OVP_00007':
                        raise exceptions.TokenExpiredError(
                            err.response.json()['description']
                        )
                    else:
                        raise exceptions.BaseError(
                            err.response.json()['description']
                        )

            # Otherwise, raise a generic error.
            raise exceptions.BaseError(err)

        return request.json()

    def entitlements(self):
        '''
        Returns a list of entitlements for the current user.

        Result:
            list: A list of active entitlements for the account.

        Raises:
            BaseError: A generic error occured during the HTTP exchange, this
                may be due to authentication failure, or underlying transport
                issue.
        '''
        entitlements = set()

        # Make a userinfo request and filter out the relevant data.
        userinfo = self.userinfo()
        for entitlement in userinfo['entitlements']:
            # Skip the SSN entitlement.
            if entitlement['name'] == 'ssn':
                continue

            # Track only if activated.
            if entitlement['state'] == 'ACTIVATED':
                entitlements.add(entitlement['name'])

        return entitlements
