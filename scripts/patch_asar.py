'''
This script will attempt to perform the following steps:

  1. Extract the specified `app.asar`.
  2. Decrypt the contents of `bundle.js` to `bundle.plain.js`
  3. patch `electron.js` to load a plain-text `bundle.plain.js` instead of its
     encrypted counterpart.
  4. Patch the `bundle.plain.js` to fix up UX related concerns.
  5. Rebundle ASAR into `app.patch.asar`, ready for use.

'''

import os
import asar
import glob
import patch
import logging
import argparse
import tempfile

from decryption import decrypt_file


def main(args):
    '''
    Main entrypoint of the ASAR patcher.

    Args:
        args (...): A set of arguments parsed by the Python argparse module.
    '''
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(process)d - [%(levelname)s] %(message)s',
    )
    logger = logging.getLogger(__name__)

    # Expand our user provided paths.
    path_input = os.path.abspath(os.path.expanduser(args.input))
    path_output = os.path.abspath(os.path.expanduser(args.output))

    # As we'll be packing and unpacking files, we a temporary location.
    temporary_dir = tempfile.mkdtemp(prefix='nowtv')
    logger.info('Using %s as a temporary directory', temporary_dir)

    # Attempt to extract the encrypted bundle.js, and electron.js
    logger.info('Attempting to extract ASAR')
    asar.unpack(path_input, os.path.join(temporary_dir, 'app'))

    # Decrypt.
    logger.info('Attempting to decrypt bundle.js from ASAR')
    decrypt_file(
        os.path.join(temporary_dir, 'app/dist/src/bundle.js'),
        os.path.join(temporary_dir, 'app/dist/src/bundle.plain.js'),
    )

    # Load and attempt to apply patches.
    for diff in glob.glob('{0}/*.patch'.format(args.patches)):
        logger.info('Attempting to apply patch %s', diff)
        patch.fromfile(diff).apply(strip=1, root=temporary_dir)

    # Finally, apply optional patches.
    if args.oi_you_got_a_license_for_that:
        for diff in glob.glob('{0}/optional/*.patch'.format(args.patches)):
            logger.info('Attempting to apply OPTIONAL patch %s', diff)
            patch.fromfile(diff).apply(strip=1, root=temporary_dir)

    # Rebunble into patched ASAR.
    logger.info('Attempting to write patched ASAR to %s', path_output)
    asar.pack(os.path.join(temporary_dir, 'app/'), path_output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='NOW TV Player ASAR patcher',
    )
    parser.add_argument(
        '--output',
        help='Path to write the new ASAR [default: app.patch.asar]',
        default='app.patch.asar'
    )
    parser.add_argument(
        '--input',
        help='Path to the original ASAR [default: app.asar]',
        default='app.asar'
    )
    parser.add_argument(
        '--patches',
        help='Path to the patch directory [default: ./patches/]',
        default=os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'patches/',
        )
    )
    parser.add_argument(
        '--oi-you-got-a-license-for-that',
        help='Apply optional patches (parental pin entry) [default: False]',
        action='store_true',
        default=False,
    )
    main(parser.parse_args())
