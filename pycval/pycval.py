import hashlib
import logging
import sys


logger = logging.getLogger(__name__)


def validate(thing, algorithm, *, csum_file=None, csum_string=None, **kwargs):
    csum = checksum(thing, algorithm, **kwargs)
    if csum_file:
        return _validate_csumfile(csum, csum_file)
    elif csum_string:
        return _validate_csum_string(csum, csum_string)
    else:
        logger.warning("Nothing to match against!")


def _validate_csumfile(csum, csum_file):
    with open(csum_file) as check_file:
        file_buffer = check_file.read().strip()  # remove linebreak
        return csum == file_buffer


def _validate_csum_string(csum, csum_string):
    return csum == csum_string


def checksum(inp, algorithm, as_string=False, chunksize=8192):

    try:
        algorithm = getattr(hashlib, algorithm)()
    except AttributeError as e:
        logger.error(e)
        sys.exit(1)

    if not as_string:
        try:
            exec_buffer = open(inp, 'rb')
        except (IOError, FileNotFoundError) as e:
            logger.error(e)
            sys.exit(1)
        else:
            while True:
                temp_buffer = exec_buffer.read(chunksize)
                algorithm.update(temp_buffer)
                if not temp_buffer:
                    break
            return algorithm.hexdigest()
        finally:
            exec_buffer.close()
    else:
        inp = inp.encode('utf8')
        algorithm.update(inp)
        return algorithm.hexdigest()
