'''
plugin.video.nowtv

A simple Kodi add-on which wraps 'NOW TV Player' to integrate with Kodi.
'''

import os
import shlex
import json
import urlparse
import datetime
import xbmcaddon
import xbmcplugin
import simplecache
import subprocess

from resources.lib import ui
from resources.lib import view
from resources.lib import nowtv
from resources.lib import logger


class Plugin(object):
    ''' Implements the plugin, called by Kodi at plugin run time. '''

    def __init__(self, args):
        '''
        Args:
            args (list of str): A list of arguments provided by the trampoline.
        '''
        self.addon = xbmcaddon.Addon(id='plugin.video.nowtv')
        self.logger = logger.get(self.addon.getAddonInfo('id'))
        self.cache = simplecache.SimpleCache()

        # Parse arguments.
        self.uri = str(args[0])
        self.handle = int(args[1])
        self.parameters = dict(urlparse.parse_qs(args[2][1:]))

        # Setup all clients.
        self.sso = nowtv.sso.Client()
        self.ott = nowtv.ott.Client()
        self.epg = nowtv.epg.Client()

    def setting(self, name):
        '''
        Attempts to retrieve the value of a given setting by name. If not set
        or no setting exists, an exception will be raised.

        Args:
            name (str): The name of the setting to retrieve.

        Returns:
            The value of the setting - as set in the Kodi plugin settings
                interface.
        Raises:
            AttributeError: The setting was not found, or did not have a value.
        '''
        value = self.addon.getSetting(name)
        if not value:
            raise AttributeError(
                'Setting {0} not present, or not set'.format(name)
            )
        return value

    def run(self):
        '''
        Plugin entrypoint, called by Kodi on launch.
        '''
        xbmcplugin.setContent(self.handle, 'videos')
        xbmcplugin.endOfDirectory(self.handle)

        # Determine if we need to start playback or launch the EPG.
        if 'playback' in self.parameters:
            self.start_player(self.parameters['service_key'][0])

        # EPG.
        self.start_guide()

    def start_player(self, service_key):
        '''
        Attempt to spawn an instance of the external NowTV player, passing in
        the required token and service key based on the user selection.

        Args:
            service_key (str): The service key of the channel to play.
        '''
        launcher = [os.path.normpath(self.setting('launcher'))]
        deeplink = shlex.split(
            "--deeplink nowtvplayer://live/{0}?messoToken={1}".format(
                service_key,
                self.sso.token,
            ),
        )
        launcher.extend(deeplink)

        with ui.busy():
            subprocess.call(launcher)

    def start_guide(self):
        '''
        Start the EPG.
        '''
        with ui.busy():
            # Gated loop is in order to allow a retry if the SSO tokens have
            # expired, without forcing the user to restart the plugin.
            authenticated = False
            entitlements = None
            while not authenticated:
                # See if there is a cached SSO token for use, otherwise request
                # a new one.
                if not self.sso.token:
                    try:
                        self.logger.warning('Requesting a new SSO token')
                        self.sso.authenticate(
                            username=self.setting('username'),
                            password=self.setting('password'),
                        )
                        self.logger.warning('Cached newly created SSO token')
                    except nowtv.exceptions.BaseError as err:
                        self.logger.error(err)
                        ui.toast('Error', err)
                        return False

                # Check whether the SSO token is valid.
                try:
                    self.sso.profile()
                except nowtv.exceptions.TokenExpiredError:
                    self.logger.warning('SSO token expired, refetching')
                    self.sso.token = None
                    continue

                # See if there is a cached OTT token for use, otherwise request
                # a new one.
                if not self.ott.token:
                    try:
                        self.logger.warning('Requesting a new OTT token')
                        self.ott.authenticate(sso_token=self.sso.token)
                    except nowtv.exceptions.BaseError as err:
                        self.logger.error(err)
                        ui.toast('Error', err)
                        return False

                # Check whether the OTT token is valid.
                try:
                    entitlements = self.ott.entitlements()
                except nowtv.exceptions.TokenExpiredError:
                    self.logger.warning('OTT token expired, refetching')
                    self.ott.token = None
                    continue

                # If we got here then our tokens are valid \o/
                authenticated = True

            # Fetch data from the EPG - which does not require authentication.
            date = datetime.datetime.now().strftime('%Y%m%d')
            guide = []
            try:
                for channel in self.epg.channels(sections=entitlements):
                    channeldata = view.channeldata(channel)
                    guidedata = view.guidedata(
                        self.epg.schedule(
                            date=date,
                            service_key=channel['serviceKey'],
                        ),
                        plugin_uri=self.uri,
                    )

                    # Splice guidedata into channel, and push into guide.
                    channeldata['guidedata'] = guidedata
                    guide.append(channeldata)
            except nowtv.exceptions.BaseError as err:
                self.logger.error(err)
                ui.toast('Error', err)
                return False

        # Render the EPG using the uEPG module.
        ui.epg(
            json.dumps(guide),
            skin_path=self.addon.getAddonInfo('path'),
        )
