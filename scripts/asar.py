''' This module is intended to unpack and repack ASAR format archives. '''

import re
import os
import json
import errno
import shutil
import struct
import collections


_Archive = collections.namedtuple('Archive', ['entries', 'content'])
class Archive(_Archive):  # noqa: E302
    '''
    An object which contains ASAR compatible archived data and a dictionary of
    associated metadata to track each entry offset and size.

    Args:
        entries (dict): A dictionary of archive entries.
        content (bytearray): A bytearray containing the archive data.
    '''
    pass


def _parse_header(header):
    '''
    Attempts to recursively parse an ASAR header into a dictionary of files,
    their sizes, and offsets.

    Args:
        header (dict): A dictionary of header data to process. This may be the
            entire header or just a chunk - in order to support recursion.
    '''
    candidates = {}

    for p_name, p_meta in header.iteritems():
        # Recurse on the presence of a files entry.
        if 'files' in p_meta:
            for c_name, c_meta in _parse_header(p_meta['files']).iteritems():
                candidates['{0}/{1}'.format(p_name, c_name)] = c_meta
        else:
            # Otherwise, just track as a file in the current context.
            candidates[p_name] = p_meta

    return candidates


def _generate_archive(input_path):
    '''
    Attempts to generate an archive in memory of all of the content under the
    provided input_path.

    Args:
        input_path (str): The path to the directory to archive.

    Returns:
        Archive: A namedtuple containing the archive content as a bytearray,
            and a dictionary of entries - including sizes and offsets.
    '''
    entries = {}
    content = bytearray()

    for (path, dir_names, file_names) in os.walk(input_path):
        for file_name in file_names:
            file_start = len(content)
            file_path = os.path.join(path, file_name)

            # Skip if the file is a symlink.
            if os.path.islink(file_path):
                continue

            # Read the entire file into the byte-array. For large archives this
            # will eat a lot of memory.
            with open(file_path, 'rb') as fin:
                content.extend(bytearray(fin.read()))

            # Determine the archive relative path for the file - including
            # whether the top-level directory should be packed.
            parent = input_path.split('/')[-1]
            archive_path = re.sub(r'^{0}'.format(input_path), '', file_path)
            archive_path = archive_path.lstrip('/')

            if parent:
                archive_path = "{0}/{1}".format(parent, archive_path)

            # Track the entry for the header.
            entries[archive_path] = {
                "offset": str(file_start),
                "size": len(content) - file_start
            }

    return Archive(entries, content)


def _add_header_entry(entry, header, meta):
    '''
    Provides a recursive function to build-out an hierarchy from the provided
    file paths, with the deepest entry containing the file metadata.

    Args:
        entry (str): A string representation of the current directory.
        header (dict): The header entry to append to.
        meta (dict): The metadata to append to the file entry.
    '''
    components = entry.split('/')

    # This could be handled by default dict, but this keeps things simple.
    if "files" not in header:
        header["files"] = {}

    # While we have nested entries left...
    if len(components) > 1:
        # Reverse the order of the path (x/y/ becomes /y/x).
        components.reverse()

        cwd = components.pop()
        if cwd not in header["files"]:
            header["files"][cwd] = {}

        # Flip the ordering back, and rejoin as a path before recursing on the
        # remaining children.
        components.reverse()
        _add_header_entry('/'.join(components), header["files"][cwd], meta)
    else:
        # It looks like we're at the end of the path (the file).
        header["files"][components[0]] = meta


def _generate_header(entries):
    '''
    Attempts to generate an ASAR compatible JSON file header from a list of
    file entries.

    Args:
        entries (dict): A list of archive file entries - including offset and
            size information.
    Returns:
        str: A stringified JSON header for the ASAR.
    '''
    header = {}
    for entry in entries:
        _add_header_entry(entry, header, entries[entry])

    return json.dumps(header, separators=(',', ':'))


def unpack(input_path, output_path, filename=None):
    '''
    Attempts to unpack the specified ASAR to the given output directory. An
    optional 'file' parameter can be used to extract single files from the
    archive.

    Args:
        input_path (str): The path to the ASAR to unpack.
        output_path (str): The path to the directory unpack the ASAR into.
        filename (str): An optional single file to extract from the ASAR.
    '''
    buffer = bytearray()

    with open(input_path, 'rb') as fin:
        buffer.extend(fin.read())

    # Determine the geometry of the header.
    (pickle_size, header_sz) = struct.unpack('<II', buffer[0:8])
    (pickle_size, document_sz) = struct.unpack('<II', buffer[8:16])

    # Determine where the header JSON starts and ends.
    header_start = 16
    header_end = document_sz + header_start

    # Determine where the content section starts - ensuring that we take 32-bit
    # alignment / padding into account.
    content_start = header_end
    while content_start % 4 != 0:
        content_start += 1

    # As the header is JSON, we can just cast to string from the bytearray.
    header = json.loads(str(buffer[header_start:header_end]))

    for file, meta in _parse_header(header['files']).iteritems():
        directory = os.path.dirname(file)

        # Allow for optional extraction of a single file by path, in which case
        # the directory hierarchy will NOT be created.
        if filename:
            if file == filename:
                file = os.path.basename(file)
                directory = None
            else:
                continue

        # If the meta section contains 'unpacked' then the file is not actually
        # in the archive (?!).
        file_outside_archive = False

        if 'unpacked' in meta and meta['unpacked']:
            file_outside_archive = True

        # Ensure the required directory structure is hydrated.
        if directory:
            try:
                os.makedirs(os.path.join(output_path, directory))
            except OSError as err:
                # Ignore the exception if it's due to a leaf being already
                # present.
                if err.errno == errno.EEXIST:
                    pass
                else:
                    raise err

        # Attempt to extract the file and write to the given path.
        if file_outside_archive:
            shutil.copy2(
                os.path.join(os.path.dirname(input_path), file),
                os.path.join(output_path, file),
            )
        else:
            # Determine the correct location for each file. The actual offset
            # is actually the offset from the header, plus the size of the
            # header.
            file_start = content_start + int(meta['offset'])
            file_end = file_start + meta['size']

            with open(os.path.join(output_path, file), 'wb') as fout:
                fout.write(buffer[file_start:file_end])


def pack(input_path, output_path):
    '''
    Attempts to pack the specified file path into an ASAR.

    Args:
        input_path (str): The path to the directory to pack into an ASAR.
        output_path (str): The path to the ASAR file to generate.
    '''
    archive = _generate_archive(input_path)
    header = _generate_header(archive.entries)

    # Use the document size to calculate an aligned header size.
    document_sz = len(header)
    header_sz = document_sz + 4

    while header_sz % 4 > 0:
        header_sz += 1

    # Create a Chromium-Pickle like header.
    pickle = bytearray(
        struct.pack('<IIII', 0x4, header_sz + 4, header_sz, document_sz)
    )
    pickle.extend(header.encode())

    # Pad the header with NULLs until 32-bit aligned before appending the
    # content.
    while len(pickle) % 4 > 1:
        pickle.extend([0x0])

    # Finally, append the content / archive and write to file.
    pickle.extend(archive.content)
    with open(output_path, 'wb') as fout:
        fout.write(pickle)

    return
