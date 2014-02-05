import argparse
import json
import sys

import splunklib.binding as splunk_binding
import cybox.bindings.cybox_core as cybox_core_binding
from cybox.core import Observables
from lxml import etree

import ConfigParser


def read_cybox(input_file, isJson):
    if not isJson:
        # Based on https://github.com/CybOXProject/python-cybox/blob/master/examples/parse_xml.py
        observables_obj = cybox_core_binding.parse(input_file)
        observables = Observables.from_obj(observables_obj)
        return observables.to_dict()
    else:
        with open(input_file, 'r') as f:
            return json.load(input_file)


def read_openioc(input_file):
    with open(input_file, 'r') as f:
        ioc_tree etree.parse(f)
    return False

def search_splunk(data):
    pass


def main():
    config = ConfigParser.ConfigParser()

    parser = argparse.ArgumentParser(description="Search Splunk for indicators in CybOX or OpenIOC files")
    parser.add_argument('input_file', help="Input file")
    parser.add_argument('-t', '--filetype', choices=['cybox', 'cybox-json', 'openioc'],
                       help="Type of file (optional). If specified, must be one of: cybox, cybox-json, openioc")

    args = parser.parse_args()
    ioc_data = {}

    if args.filetype == "cybox":
        ioc_data = read_cybox(args.input_file, False)
    elif args.filetype == "cybox-json":
        ioc_data = read_cybox(args.input_file, True)
    elif args.filetype == "openioc":
        ioc_data = read_openioc(args.input_file)
    else:
        # Should never reach this due to the choices parameter specified for add_argument()
        sys.stderr.write("File type not properly specified, see --help for more.")
        return

    host = config.get('Splunk', 'host')
    port = config.getint('Splunk', 'port')
    username = config.get('Splunk', 'username')
    password = config.get('Splunk', 'password')
    try:
        splunk_connection = splunk_binding.connect(host=host, port=port, username=username, password=password)
    else:
        sys.stderr.write('Could not connect to %s:%d as %s' % (host, port, username))
        return

    if ioc_data:
        search_splunk(ioc_data)


if __name__ == "__main__":
    main()
