'''
This script will patch the specified `NOW TV Player.exe` in order to remove the
signature check used to validate the ASAR.

This is required to be able to patch the application to enable opening in
full-screen, and to bind-up hot keys to allow exiting the player. This is not
required, but significantly improves the user experience.

It should be noted that this patch opens up the ASAR to being modified on disk.
This may open up the ASAR to being modified to execute malicious code by some
rouge process or a malicious actor with access to the local machine.
'''

import os
import sys
import logging
import argparse
import hashlib

KNOWN_OFFSETS = [
    {
        'hash': '44c01d899bdfd43547c53cc3235801ec8eda19ce',
        'offset': 0x19da0f,
        'patch': bytearray(
            [
                0x90,  # NOP
                0x90,  # NOP
                0x90,  # NOP
                0x90,  # NOP
                0x90,  # NOP
                0x90,  # NOP
            ]
        )
    }
]


def main(args):
    '''
    Attempts to load the provided binary, and patch the required branch at
    known offsets. If the version of the binary is not recognised - which is
    discerned using the SHA1 of the input file - then no operations will be
    performed.

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

    # Load the input file into a bytearray.
    buffer = bytearray()
    logger.info('Attempting to open binary to patch from %s', path_input)
    try:
        with open(path_input, 'rb') as fin:
            buffer.extend(fin.read())
    except IOError as err:
        logger.fatal('Unable to read file, cannot continue: %s', err)
        sys.exit(-1)

    # Hash the file and check against our known offsets.
    hasher = hashlib.sha1(buffer)
    logger.info('SHA1 of %s is %s', path_input, hasher.hexdigest())

    patch = None
    for entry in KNOWN_OFFSETS:
        if entry['hash'] == hasher.hexdigest():
            patch = entry
            break

    if not patch:
        logger.fatal('No known patch for %s, cannot continue :(', path_input)
        sys.exit(-2)

    # Replace and log bytes at offset.
    for seek in range(len(patch['patch'])):
        logger.info(
            'Replacing 0x%02x at 0x%02x with 0x%02x',
            buffer[patch['offset'] + seek],
            patch['offset'] + seek,
            patch['patch'][seek],
        )
        buffer[patch['offset'] + seek] = patch['patch'][seek]

    # Write out the patched binary.
    logger.info('Attempting to write out patched binary to %s', path_output)
    try:
        with open(path_output, 'wb') as fout:
            fout.write(buffer)
    except IOError as err:
        logger.fatal('Unable to write file, cannot continue: %s', err)
        sys.exit(-3)

    logger.info('Patching complete successfully. You should be good to go!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='NOW TV Player ASAR signature check patcher',
    )
    parser.add_argument(
        '--output',
        help='Path to write the new binary (default: NOW TV Player.patch.exe)',
        default='NOW TV Player.patch.exe'
    )
    parser.add_argument(
        '--input',
        help='Path to the original binary (default: NOW TV Player.exe)',
        default='NOW TV Player.exe'
    )
    main(parser.parse_args())
