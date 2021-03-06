## Automatic Patchers

This directory contains a number of scripts to facilitate the automatic
patching of PE (`.exe`) and ASAR files. This includes a Python native `asar`
module which allows unpacking and packing of ASARs.

It should be noted that these patchers will only work with known versions of
the given artifacts.

## Dependencies

Dependencies for these scripts have been kept to a minimum. However, there are
still a few which must be installed before they can be used:

```
pip install -r requirements.txt
```

## Patch Loader (`patch_loader.py`)

This script will patch the specified `NOW TV Player.exe` in order to remove the
signature check used to validate the ASAR. This is required so that modified
ASARs can be loaded, which is required in order to patch the UX related
concerns covered in the main project [README.md](../README.md#UX).

This patch is simply NOPing out the `jz` instruction after the call to the
method which appears to be responsible for loading and validating the ASAR
signature file (`.sig`).

![Loader Patch](../images/Loader-Check.png?raw=true)

**Please Note:** It should be noted that this patch opens up the ASAR to being
modified on disk. This could allow for modification of the ASAR by by some
rouge process or a malicious actor which could result in malicious code
execution.

## Patch ASAR (`patch_asar.py`)

This script will attempt to perform the following steps:

  1. Extract the specified `app.asar`.
  2. Decrypt the contents of `bundle.js` to `bundle.plain.js`
  3. patch `electron.js` to load a plain-text `bundle.plain.js` instead of its
     encrypted counterpart.
  4. Patch the `bundle.plain.js` to fix up UX related concerns.
  5. Rebundle ASAR into `app.patch.asar`, ready for use.

In order to run succesfully, the `app.asar` and the `node_modules` directory
from `%APPDATA%/NOW TV/NOW TV Player/resources/` should be copied into this
directory, or the `--input` flag modified to point to correct `app.asar` path.

Once patching is complete, simply copy the output `app.patch.asar` over the top
of the `app.asar` in `%APPDATA%/NOW TV/NOW TV Player/resources/` and you should
be ready to go!
