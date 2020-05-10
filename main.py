'''
plugin.video.nowtv

A simple Kodi add-on which wraps 'NOW TV Player' to integrate with Kodi.

This script functions as the entrypoint into the plugin, however as we want to
keep this as simple as posible. As a result, this script simply sets up and
calls an instance of our plugin.
'''

from resources.lib.plugin import Plugin

# Kick it.
if __name__ == '__main__':
    instance = Plugin(sys.argv)  # noqa: F821
    instance.run()
