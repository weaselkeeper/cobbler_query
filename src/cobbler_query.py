#!/usr/bin/env python
"""
 Queries cobbler for information on hosts. Use hostname to iterate over all
 the systems and pull out the info for the hosts you are interested in. No
 Auth required, does not write to cobbler at all.

"""

import argparse
from ConfigParser import SafeConfigParser
import traceback
import xmlrpclib
import sys
import re
import pprint
import logging


""" Set some defaults """

CONFIGFILE = '/etc/cobbler_query/config'


def read_config():
    """ if a config file exists, read and parse it.
    Override with the get_options function, and any relevant environment
    variables.
    Config file is in ConfigParser format

    Basically:

    [sectionname]
    key=value
    [othersection]
    key=value

    Currently, only has one key=value pair, the default cobbler host to direct
    the query to.
    """

    config = SafeConfigParser()
    config.read(CONFIGFILE)
    server = config.get('server', 'host')
    return server


def get_options():
    """ command-line options """
    parser = argparse.ArgumentParser(description='Pass cli options to script')

    parser.add_argument("-n", "--hostname", action="store",
                        help="Hostname to query for.")
    parser.add_argument("-s", "--server", action="store",
                        dest="server", help="Cobbler server.")
    parser.add_argument("-g", "--glob", action="store",
                        help="""restrict actions to hosts that match regex
Example, ./cobbler_query.py  -g 'checkout-app0?.*prod.*'
For all the checkout-app0[] in prod""")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="just tell me what systems match -g or hostname")
    parser.add_argument("-a", "--all", action="store_true",
                        help="Do for all systems cobbler knows about, use with \
-q, or get flooded with lots of text")
    parser.add_argument("-k", "--koan", action="store_true", help="Return data \
that koan would see, including expanding inheritance. \
Only works in conjunction with the n flag")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Extra info about stuff")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Set logging level to debug")

    args = parser.parse_args()

    if not args.server:
        args.server = read_config()

    if not args.hostname and not args.glob \
            and not args.all:
        args.hostname = raw_input('hostname: ')

    if args.debug:
        log.setLevel(logging.DEBUG)

    args.usage = "usage: %prog [options]"

    return args


def _get_server():
    """ getting the server object """
    url = "http://%s/cobbler_api" % args.server
    try:
        _server = xmlrpclib.Server(url)
        return _server
    except:
        traceback.print_exc()
        return None

if __name__ == "__main__":

    global_log_level = logging.WARN
    default_log_format = logging.Formatter("%(asctime)s - %(levelname)s - \
                                           %(message)s")
    default_log_handler = logging.StreamHandler(sys.stderr)
    default_log_handler.setFormatter(default_log_format)

    log = logging.getLogger("cobbler_query")
    log.setLevel(global_log_level)
    log.addHandler(default_log_handler)
    log.debug("Starting logging")
    args = get_options()
    server = _get_server()
    if args.hostname:
        # Only doing one system
        hostname = args.hostname
        system = server.get_item('system', hostname)
        try:
            name = system['name']
        except TypeError:
            log.warn("Sorry, hostname %s does not seem to exist in cobbler" %
                     hostname)
            sys.exit()

        if args.koan:
            system = server.get_system_for_koan(hostname)

        print "System %s as %s:" % (name, hostname)
        if not args.quiet:
            pprint.pprint(system)

    else:
        for system in server.get_systems():
            name = system['name']
            hostname = system['hostname']
            if hostname not in name and not args.quiet:
                log.warn("hostname <-> name problem with system name %s"
                         % name)
            if args.glob:
                glob = args.glob
                if re.search(glob, name):
                    print "System %s as %s :" % (name, hostname)
                    if not args.quiet:
                        pprint.pprint(system)
            else:
                print "System %s as %s :" % (name, hostname)
                if not args.quiet:
                    pprint.pprint(system)
