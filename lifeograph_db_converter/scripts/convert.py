#!/bin/env python3
import argparse
import sys

from lifeograph_db_converter.formats import LifeographDb110Format, JsonFormat


FORMAT_MAP = {'lifeog110': LifeographDb110Format,
              'json': lambda password, **_: JsonFormat()}


def run(src_file=None,
        dst_file=None,
        from_format=None,
        to_format=None,
        password=None,
        ):
    # Init formats
    # TODO: Pass password and possible future args in some more appropriate way
    src = FORMAT_MAP[from_format](password=password)
    dst = FORMAT_MAP[to_format](password=password)
    # Read source data
    if src_file:
        with open(src_file, 'rb') as f:
            src_data = f.read()
    else:
        src_data = sys.stdin.read()
    # Convert
    dst_data = dst.dump(
        dst.encode(
            src.decode(
                src.parse(src_data)
            )
        )
    )
    # Write destination data
    if dst_file:
        with open(src_file, 'wb') as f:
            f.write(dst_data)
    else:
        sys.stdout.write(dst_data)


def main():
    parser = argparse.ArgumentParser(description='Lifeograph diary DB converter')
    parser.add_argument('-sf', '--src-file', type=str, help='Source file. If not defined, stdin will be used.')
    parser.add_argument('-df', '--dst-file', type=str, help='Destination file. If not defined, stdout will be used.')
    parser.add_argument('-ff', '--from-format', type=str, help='Source format', required=True, choices=FORMAT_MAP.keys())
    parser.add_argument('-tf', '--to-format', type=str, help='Destination format', required=True, choices=FORMAT_MAP.keys())
    parser.add_argument('-p', '--password', type=str, help='Password. Only for encrypted lifeograph native formats (src or dst).')
    args = parser.parse_args()
    run(**dict(args._get_kwargs()))


if __name__ == '__main__':
    main()
