''' Implements commonly used constants for NOW TV. '''

# Define a common UA.
USER_AGENT = ' '.join(
    [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4)',
        'AppleWebKit/537.36 (KHTML, like Gecko)',
        'Chrome/81.0.4044.92 Safari/537.36',
    ]
)

# Ensure NOW TV client headers are properly presented.
HTTP_HEADERS = {
    'User-Agent': USER_AGENT,
    'X-SkyOTT-Platform': 'PC',
    'X-SkyOTT-Territory': 'GB',
    'X-SkyOTT-Provider': 'NOWTV',
    'X-SkyOTT-Device': 'COMPUTER',
    'X-SkyOTT-Proposition': 'NOWTV',
    'Sec-Fetch-Site': 'same-site',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
}

# Define cache keys and their lifetimes - in hours.
CACHE_KEY_SSO_TOKEN = 'nowtv.sso.token'
CACHE_KEY_OTT_TOKEN = 'nowtv.ott.token'
CACHE_KEY_CHANNELDATA = 'nowtv.channeldata'
CACHE_KEY_SCHEDULE = 'nowtv.schedule.{0}'

CACHE_LIFETIME_SSO_TOKEN = 1
CACHE_LIFETIME_OTT_TOKEN = 4
CACHE_LIFETIME_SCHEDULE = 1
CACHE_LIFETIME_CHANNELDATA = 8

# Define URLs for IDAPI.
URI_IDAPI_BASE = 'https://uiapi.id.nowtv.com'
URI_IDAPI_SIGNIN = '{0}/signin/service/international'.format(URI_IDAPI_BASE)

# Define URLs for OTT.
URI_OTT_BASE = 'https://auth.client.ott.sky.com'
URI_OTT_AUTH_TOKENS = '{0}/auth/tokens'.format(URI_OTT_BASE)
URI_OTT_AUTH_USERS_ME = '{0}/auth/users/me'.format(URI_OTT_BASE)

# Define URLs for Atlas (?).
URI_ATLAS_BASE = 'https://ie.api.atom.nowtv.com/adapter-atlas/v3'
URI_ATLAS_LINEAR_CHAN = '{0}/query/linear_channels'.format(URI_ATLAS_BASE)

# Define URLs EPG.
URI_EPG_BASE = 'https://roi.epgsky.com/atlantis'
URI_EPG_NOWNEXT = '{0}/linear/nownext'.format(URI_EPG_BASE)
URI_EPG_SCHEDULE = '{0}/linear/schedule'.format(URI_EPG_BASE)

# Define URLs for OO Gateway (?).
URI_OOGATEWAY_BASE = 'https://agg.oogwayintl.sky.com'
URI_OOGATEWAY_PROFILE = '{0}/public/profile'.format(URI_OOGATEWAY_BASE)

# Keep track of known error codes during login.
ERROR_SSO_TOKEN_EXPIRED = 'OVP_00306'
ERROR_OOGATEWAY_TOKEN_EXPIRED = 1301
