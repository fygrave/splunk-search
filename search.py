import argparse
import sys

import ConfigParser


def read_cybox(input_file, isJson):
    pass


def read_openioc(input_file):
    pass


def search_splunk(data):
    pass


def main():
    config = ConfigParser.ConfigParser()

    parser = argparse.ArgumentParser(description="Search Splunk for indicators in CybOX or OpenIOC files")
    parser.addargument('input_file', help="Input file")
    parser.addargument('-t', '--filetype', help="Type of file (optional). If specified, must be one of: cybox, cybox-json, openioc")

    args = parser.parse_args()
    ioc_data = {}

    if args.filetype == "cybox":
        ioc_data = read_cybox(args.input_file, False)
    elif args.filetype == "cybox-json":
        ioc_data = read_cybox(args.input_file, True)
    elif args.filetype == "openioc":
        ioc_data = read_openioc(args.input_file)
    else:
        sys.stderr.write("File type not properly specified, see --help for more.")
        return False

    search_splunk(ioc_data)


if __name__== "__main__":
    main()
