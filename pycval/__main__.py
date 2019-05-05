import hashlib
import logging
import sys

from .pycval import checksum, validate


base_logger = logging.getLogger(__name__)

stream_handler = logging.StreamHandler()
stream_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s: %(name)s - %(message)s'
)
stream_handler.setFormatter(stream_formatter)
base_logger.addHandler(stream_handler)

if __name__ == '__main__':
    import argparse
    import os

    base_logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description='Checksum validator')

    hash_algorithms = list(hashlib.algorithms_guaranteed)
    common_args = argparse.ArgumentParser(add_help=False)
    common_args.add_argument(
        'input',
        nargs='?',
        help='Source input. This can be a file, a string or stdin',
        default=sys.stdin
    )
    common_args.add_argument(
        '-a',
        '--algorithm',
        choices=hash_algorithms,
        help='Hash algorithm. Possible values: ' + ', '.join(hash_algorithms),
        metavar='',
        required=True
    )
    common_args.add_argument(
        '--debug',
        help='Turn on debugging output',
        action='store_true',
        default=False
    )

    subparsers = parser.add_subparsers(description='Method to use', dest='cmd')

    checksum_arg = subparsers.add_parser('checksum', parents=[common_args])
    checksum_arg.set_defaults(func=checksum)
    checksum_arg.add_argument(
        '-d',
        '--dump',
        help='Dump hash to disk',
        action='store_true'
    )

    validate_arg = subparsers.add_parser('validate', parents=[common_args])
    validate_arg.set_defaults(func=validate)
    validate_arg.add_argument(
        '-f',
        '--file',
        help='Check file'
    )
    validate_arg.add_argument(
        '-s',
        '--string',
        help='Check string'
    )

    args = parser.parse_args()

    base_logger.setLevel(logging.DEBUG if args.debug else logging.WARNING)

    base_logger.debug(f'args = {args}')

    def detect_input(inp):
        """Check if inp is a file, stdin or just a string"""
        _inp = {k: None for k in ['file', 'string', 'stdin']}
        try:
            inp.isatty()
            _inp['stdin'] = inp.read()
            return _inp
        except AttributeError:
            try:
                if not (os.path.exists(inp) and os.path.isfile(inp)):
                    raise FileNotFoundError
                _inp['file'] = inp
                return _inp
            except FileNotFoundError:
                _inp['string'] = inp
                return _inp

    inp = detect_input(args.input)

    base_logger.debug(f'inp = {inp}')

    as_string = False
    if inp.get('stdin') or inp.get('string'):
        as_string = True

    if args.cmd == 'checksum':
        _checksum = args.func(
            *[i for i in inp.values() if i],
            args.algorithm,
            as_string
        )
        if args.dump:
            with open('pycval_output.' + str(args.algorithm), 'w') as out:
                out.write(str(_checksum))
        else:
            print(_checksum)
    elif args.cmd == 'validate':
        _validate = args.func(
            *[i for i in inp.values() if i],
            args.algorithm,
            csum_file=args.file,
            csum_string=args.string,
            as_string=as_string
        )
        print(_validate)
