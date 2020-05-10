''' Implements a NOW TV / Sky EPG client. '''

import logging
import requests
import datetime
import simplecache

from resources.lib.nowtv import constants
from resources.lib.nowtv import exceptions


class Client(object):
    ''' Implements a NOW TV / Sky EPG client. '''

    def __init__(self):
        self.cache = simplecache.SimpleCache()
        # TODO: Fix this.
        self.logger = logging.getLogger('plugin.video.nowtv.epg')
        self.headers = constants.HTTP_HEADERS

    def nownext(self, service_keys):
        '''
        Attempts to query for the 'now and next' EPG data for the provided
        service key.

        Args:
            service_keys (list of str): A list of service keys to query for,
                this may be an empty list to query for all service keys.

        Returns:
            A list of 'now and next' information - as returned by the EPG API.
        '''
        # Bolt on additional headers.
        headers = constants.HTTP_HEADERS
        headers['Accept'] = '*/*'
        headers['Referer'] = 'https://www.nowtv.com/gb/watch/'

        try:
            request = requests.get(
                '{0}/{1}'.format(
                    constants.URI_EPG_NOWNEXT,
                    ','.join(service_keys),
                ),
                headers=headers,
            )
            request.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise exceptions.BaseError(err)

        return request.json()

    def schedule(self, date, service_key):
        '''
        Attempts to query for the schedule for the provided service key on
        the given date.

        Args:
            date (str): The yyyymmdd format date to query for data for.
            service_key (str): The service key to query for schedule data for.

        Returns:
            A list of schedule information - as returned by the EPG API.
        '''
        # Bolt on additional headers.
        headers = constants.HTTP_HEADERS
        headers['Accept'] = '*/*'
        headers['Referer'] = 'https://www.nowtv.com/gb/watch/'

        # Check and return from cache first - if current.
        if self.cache.get(constants.CACHE_KEY_SCHEDULE.format(service_key)):
            self.logger.debug(
                'Using schedule for %s from cache',
                service_key
            )
            return self.cache.get(
                constants.CACHE_KEY_SCHEDULE.format(service_key)
            )

        try:
            request = requests.get(
                '{0}/{1}/{2}'.format(
                    constants.URI_EPG_SCHEDULE,
                    date,
                    service_key,
                ),
                headers=headers,
            )
            request.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise exceptions.BaseError(err)

        # Push into cache, and return.
        self.cache.set(
            constants.CACHE_KEY_SCHEDULE.format(service_key),
            request.json()['schedule'],
            expiration=datetime.timedelta(
                hours=constants.CACHE_LIFETIME_SCHEDULE,
            )
        )
        return request.json()['schedule']

    def channels(self, sections, format_type='SD'):
        '''
        Attempt to query the EPG for channel metadata.

        Args:
            sections (list of str): A list of channel sections to query for,
                this may be an empty list to query for all sections.
            format_type (str): The format to retrieve information for, this
                may be empty (default: SD).

        Returns:
            A list of channel information - formatted to only include channel
                data, and not 'atlas' metadata.
        '''
        # Bolt on additional headers.
        headers = constants.HTTP_HEADERS
        headers['Accept'] = '*/*'
        headers['Referer'] = 'https://www.nowtv.com/gb/sign-in'

        # Check and return from cache first - if current.
        if self.cache.get(constants.CACHE_KEY_CHANNELDATA):
            self.logger.debug('Using channel data for from cache')
            return self.cache.get(constants.CACHE_KEY_CHANNELDATA)

        try:
            request = requests.get(
                constants.URI_ATLAS_LINEAR_CHAN,
                params={
                    'section': ','.join(sections),
                    'formatType': format_type
                },
                headers=headers,
            )
            request.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise exceptions.BaseError(err)

        # Construct a list of useful data for each channel.
        channels = []
        for channel in request.json():
            if 'attributes' in channel:
                channels.append(channel['attributes'])

        # Push into cache, and return.
        self.cache.set(
            constants.CACHE_KEY_CHANNELDATA,
            channels,
            expiration=datetime.timedelta(
                hours=constants.CACHE_LIFETIME_CHANNELDATA,
            )
        )
        return channels
