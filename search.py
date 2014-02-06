import argparse
import json
import sys

import splunklib.client as splunk_client
import splunklib.results as splunk_results
import cybox.bindings.cybox_core as cybox_core_binding
from cybox.core import Observables
from cybox.objects.address_object import Address

import ConfigParser


def read_cybox(input_file, isJson):
    if not isJson:
        # Based on https://github.com/CybOXProject/python-cybox/blob/master/examples/parse_xml.py
        cybox_obj = cybox_core_binding.parse(input_file)
        cybox_observables = Observables.from_obj(cybox_obj)
        cybox_data = cybox_observables.to_dict()
    else:
        with open(input_file, 'r') as f:
            cybox_data = json.load(input_file)

    indicator_data = {'ip_addresses': []}

    for each in cybox_data['observables']:
        if each['object']['properties']['category'] == 'ipv4-addr':
            indicator_data['ip_addresses'].append(each['object']['properties']['address_value'])

    return indicator_data


def read_openioc(input_file):
    # Stub
    return False


def search_splunk(connection, data):
    s = "SEARCH "
    for each in data['ip_addresses']:
        if s != "SEARCH ":
            s += " OR "
        s += each
    search_job = connection.jobs.create(s)
    while not search_job.is_done():
        sleep(0.2)
    search_results = splunk_results.ResultsReader(search_job.results())
    for result in search_results:
        if isinstance(result, splunk_results.Message):
            sys.stderr.write("%s: %s" % (result.type, result.message))
        elif isinstance(result, dict):
            print result


def main():
    config = ConfigParser.ConfigParser()

    parser = argparse.ArgumentParser(description="Search Splunk for indicators in CybOX or OpenIOC files")
    parser.add_argument('input_file', help="Input file")
    parser.add_argument('-t', '--filetype', choices=['cybox', 'cybox-json', 'openioc'],
                       help="Type of file (optional). If specified, must be one of: cybox, cybox-json, openioc")

    args = parser.parse_args()

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

    try:
        config.read('.splunkrc')
    except:
        sys.stderr.write("Could not read config file .splunkrc")
        return

    host = config.get('Splunk', 'host')
    port = config.getint('Splunk', 'port')
    username = config.get('Splunk', 'username')
    password = config.get('Splunk', 'password')
    try:
        splunk_connection = splunk_client.connect(host=host, port=port, username=username, password=password)
    except:
        sys.stderr.write('Could not connect to %s:%d as %s' % (host, port, username))
        return

    search_splunk(splunk_connection, ioc_data)


if __name__ == "__main__":
    main()
