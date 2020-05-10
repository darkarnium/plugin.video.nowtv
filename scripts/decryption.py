'''
This script / module is intended to decrypt the bundle.js inside of the NOW TV
Player ASAR. This operation is usually performed by the 'keystore.node' module
called via FFI from electron.js when the application is loaded.
'''

import os
import sys
import logging
import argparse

from Crypto.Cipher import AES

# From keystore constants.
IV_LENGTH = 12
AUTH_TAG_LENGTH = 16
CIPHERTEXT_FLAG_LENGTH = 8

# AES 256 GCM - via keystore.node (0x10001809)
AES_MODE = AES.MODE_GCM

# AES Key - via keystore.node (0x10001928)
AES_KEY_BYTES = bytearray(
    [
        0x4E, 0x4E, 0x51, 0x67,
        0x4E, 0x42, 0x4C, 0x53,
        0x46, 0x49, 0x6E, 0x74,
        0x74, 0x39, 0x38, 0x32,
        0x58, 0x44, 0x57, 0x4C,
        0x38, 0x62, 0x48, 0x2B,
        0x70, 0x37, 0x4D, 0x55,
        0x4D, 0x76, 0x37, 0x4D,
    ]
)


def decrypt(ciphertext):
    '''
    Attempt to decrypt the provided ciphertext using our known encryption key.

    Args:
        ciphertext (str): The cipher-text to attempt to decrypt.

    Returns:
        str: The plain-text content of the encrypted content.
    '''
    # Extract the IV, Ciphertext, and AuthTag.
    iv = ciphertext[0:IV_LENGTH]
    tag = ciphertext[-AUTH_TAG_LENGTH:]
    ciphertext = ciphertext[20:len(ciphertext) - AUTH_TAG_LENGTH]

    # Attempt decryption.
    cipher = AES.new(AES_KEY_BYTES, AES_MODE, nonce=iv)
    return cipher.decrypt_and_verify(ciphertext, tag)


def decrypt_file(input_file, output_file):
    '''
    Wrappers the decrypt function to allow for operation on files.

    Args:
        input_file (str): The path to the file containing the ciphertext.
        output_file (str): The path to write the plain-text to.
    '''
    input_path = os.path.abspath(input_file)
    output_path = os.path.abspath(output_file)

    # Attempt to read in the ciphertext.
    raw_bytes = bytes()
    with open(input_path, 'rb') as fin:
        raw_bytes = fin.read()

    # Attempt decryption.
    plaintext = decrypt(raw_bytes)

    # Write out the plain-text.
    with open(output_path, 'wb') as fout:
        fout.write(plaintext)


def main(args):
    '''
    Attempts to load the provided bundle as cipher-text, decrypt it using
    a known key and IV, and output the plain-text to file.

    Args:
        args (...): A set of arguments parsed by the Python argparse module.
    '''
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(process)d - [%(levelname)s] %(message)s',
    )
    logger = logging.getLogger(__name__)

    try:
        decrypt_file(args.input, args.output)
    except IOError as err:
        logger.error('Unable to read file for read / write: %s', err)
        sys.exit(-1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='NOW TV bundle.js decryptor',
    )
    parser.add_argument(
        '--output',
        help='Where to write the decrypted contents (default: bundle.dec.js)',
        default='bundle.dec.js'
    )
    parser.add_argument(
        '--input',
        help='Where to read the encrypted contents (default: bundle.js)',
        default='bundle.js'
    )
    main(parser.parse_args())
