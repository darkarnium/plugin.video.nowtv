![Latest Release](https://img.shields.io/github/v/release/darkarnium/plugin.video.nowtv)
![Python application](https://github.com/darkarnium/plugin.video.nowtv/workflows/style/badge.svg?branch=master)
![License](https://img.shields.io/github/license/darkarnium/plugin.video.nowtv)

## NOW TV for Kodi

A simple Kodi add-on which wraps the NOW TV Player to integrate with Kodi.

![uEPG View](images/uEPG-View.png?raw=true)

## Disclaimer

The names NOW TV, Sky, as well as related names, marks, emblems and images
are are property of their respective owners. This add-on is developed by a
third-party and is in no way affiliated, authorised, supported or endorsed by
the respective rights owners.

**A valid and current NOW TV subscription is required for this add-on to work.**
**This add-on is simply a wrapper around the official NOW TV native player.**

## Support

This plugin has been tested and is confirmed working on Kodi "Leia" (18.X).
Please be aware that this add-on is currently only supported by Kodi
[running on Windows](#linux-or-macos-support).

## Installation

**Please see the 'dependencies' section below first!**

Once dependencies are installed, this add-on can be installed by downloading
the latest release from this GitHub repository, and installing into Kodi using
'Install from zip file' in the Add-On section.

Once installed, credentials for your NOW TV account and the path to the
`NOW TV Player.exe` needs to be specified in the add-on settings before this
add-on can be used.

## Dependencies

This plugin has a dependency on [uEPG](https://git.io/JfC65) in order to render
the interactive EPG. As this is listed as a dependency in the `addon.xml` this
will be automatically installed if [Lunatixz](https://github.com/Lunatixz/)
[beta repository](http://tinyurl.com/y2obmbfx) has been installed as a
repository source in Kodi.

In addition to the above, the Windows native NOW TV Player application MUST
be installed. This is required for playback of content.

## UX

Currently, the NOW TV Player does not appear to contain a mechanism to allow
deeplinks to force the player to open full screen. As a result, use with an
out-of-the-box NOW TV Player results in a less than optimal user experience
as the NOW TV Player will launch in windowed mode over the top of Kodi.

This can be remediated by performing the following steps:

1. Ensure required Python modules for the patching process are installed via
   `pip install -r scripts/requirements.txt`.
2. Run `scripts/patch_loader.py` to patch out the ASAR signature checks in the
   `NOW TV Player.exe` loader.
3. Run `scripts/patch_bundle.py` to decrypt the `bundle.js` from the ASAR, and
   splice in full-screen support.
   * Optionally, you can provide the `--oi-you-got-a-license-for-that` to
     'disable' Parental PIN entry - see below. 

**PLEASE NOTE:** Due to the ASAR format allowing for reference of files OUTSIDE
of the archive, the contents of the `app.asar.unpacked/` directory beside the
`app.asar` from the NOW TV Player **MUST** also be present next to the
`app.asar` to patch. If this isn't done, then patching will fail.

Due to an apparent OFCOM requirement, you need to enter a "Parental PIN" in
order to watch ["live channels on the Sky Cinema pass"](https://help.nowtv.com/article/what-is-a-parental-pin).
However, by specifying the `--oi-you-got-a-license-for-that` flag when patching
the bundle an additional script will be installed to automatically enter a PIN
of `0000` when the NOW TV Player loads.

Of course, you'll need to ensure your Parental PIN is set to `0000` in your
NOW TV [account settings](https://account.nowtv.com/settings) or this won't
work :)

## Packaging

In order to package for installation, the following can be run from the root
of this repository. Please note, it's better to simply download the latest
release from the releases section of this repository. These instructions are
only provided for completeness. 

```
cd ..
rm -f plugin.video.nowtv.zip

zip -r \
    --exclude=*.vscode* \
    --exclude=*.git* \
    --exclude=*.pyo* \
    --exclude=*.pyc* \
    plugin.video.nowtv.zip ./plugin.video.nowtv/
```

## FAQ

### The NOW TV Player isn't opening fullscreen?

Please see the "UX" section above :)

### Are you stealing my credentials?

Good thought, but nope! If you have concerns, please have a poke around the
source tree. Credentials are saved in Kodi and referenced as part of the SSO
client (in `resources/lib/nowtv/`) in order to mint new OTT tokens.

### Linux or macOS Support?

Linux support is currently not possible as no NOW TV provided binaries exist
for Linux.

As for macOS, this is definitely possible with a small amount of work in this
add-on. However, patching of the macOS loader to achieve better UX - per the
notes above - will require a set of patches for the macOS loader.

PRs are most certainly accepted!

### What about Kodi Native Playback?

The NOW TV Player for Windows is an Electron application which utilises a
VideoGuard enabled overlay in order to implement DRM. As these features use
pre-compiled native binaries for the target system (macOS, Windows, etc) native
integration with Kodi is unlikely.

This said, it appears that the HD ("Boost") enabled streams (Roku) are provided
using Microsoft PlayReady technology. With the correct hardware for development
it may be possible to investigate Kodi integration using these endpoints
instead - which would have the added benefit of providing access to content at
1080P.

### Wait, Python 2? What year is it?!

Currently, this module is written to use Python 2. This is due to Leia not 
supporting Python 3 out of the box. As the underlying API clients were
originally written for Python 3 porting should be trivial when Python 3
is required for add-ons in a subsequent version.

As a result of the above, all other scripts in this repository have been
developed for Python 2 - in order to reduce confusion.
