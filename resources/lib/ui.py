''' Provides wrappers for interacting with the Kodi UI. '''

import xbmc
import xbmcgui
import urllib

from contextlib import contextmanager


def toast(title, message, time=300):
    '''
    Creates an XBMC toast style notification with the provided information.

    Args:
        title (str): The title of the notification.
        message (str): The body of the notification.
        time (int): The duration of the notification in seconds (default: 300)
    '''
    xbmc.executebuiltin(
        'Notification({0},{1},{2},)'.format(
            title,
            message,
            time,
        )
    )


def epg(json, skin_path=None):
    '''
    Renders an EPG using uEPG.

    Args:
        json (str): A stringified JSON object containing the EPG data.
        skin_path (str): An optional path to the skin to use for uEPG.
    '''
    uepg = 'RunScript(script.module.uepg,json={}&include_hdhr={}'.format(
        urllib.quote(json),
        False,
    )

    # TODO: This is gross, fix me.
    if skin_path:
        uepg += '&skin_path={}'.format(skin_path)

    uepg += ')'
    xbmc.executebuiltin(uepg)


def update(path, replace=True):
    '''
    Calls Container.Update with the provided path, and replace set to the
    respective value.

    Args:
        path (str): The Path to update the UI container to.
        replace (bool): Whether to replace the view (default: True)
    '''
    if replace:
        xbmc.executebuiltin('Container.Update({0},replace)'.format(path))
    else:
        xbmc.executebuiltin('Container.Update({0})'.format(path))


def directory_item(name):
    '''
    Returns a ListItem for a directory, with the given name and parameters.

    Args:
        name (str): The name of the directory.
    '''
    return xbmcgui.ListItem(name)


def home():
    '''
    Takes our ball and goes Home.
    '''
    xbmc.executebuiltin('XBMC.ActivateWindow(Home)')


@contextmanager
def busy():
    '''
    Implements a context manager to display a busy dialog until the given
    operation has complete. This code sample was copied from a comment from
    Roman_V_M on forum.kodi.tv.
    '''
    xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    try:
        yield
    finally:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
