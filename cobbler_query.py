#!/usr/bin/env python
"""
 Queries cobbler for information on hosts. Use hostname to iterate over all
 the systems and pull out the info for the hosts you are interested in. No
 Auth required, does not write to cobbler at all.

"""

import optparse
import ConfigParser
import traceback
import xmlrpclib
import sys
import re
import pprint
import logging
import os


""" Set some defaults """

query_config = '/etc/cobbler_query/config'

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
    """

    config = ConfigParser.RawConfigParser()
    config.read(query_config)
    server = config.get('server','host')
    return server

def get_options():
    """ command-line options """
    usage = "usage: %prog [options]"
    optionparser = optparse.OptionParser
    parser = optionparser(usage)

    parser.add_option("-n", "--hostname", action="store", type="string", \
            help="Hostname to query for.")
    parser.add_option("-s", "--server", action="store", type="string", \
            dest="server", help="Cobbler server.")
    parser.add_option("-g", "--glob", action="store", type="string", help="restrict actions to hosts that match regex")
    parser.add_option("-q", "--quiet", action="store_true", help="just tell me what systems match -g or hostname")
# Example, ./cobbler_query.py  -g 'checkout-app0?.*prod.*' For all the
# checkout-app0[] in prod
    parser.add_option("-a", "--all", action="store_true", \
            help="Do for all systems cobbler knows about, use with -q, or get flooded with lots of text")
    parser.add_option("-k", "--koan", action="store_true", help="Return data \
that koan would see, including expanding inheritance. Only works in \
conjunction with the -n flag")
    parser.add_option("-v", "--verbose", action="store_true", help="Extra info about stuff")
    parser.add_option("-d", "--debug", action="store_true", help="Set logging level to debug")
    calling_options, calling_args = parser.parse_args()

    if not calling_options.server:
        calling_options.server = read_config()

    if not calling_options.hostname and not calling_options.glob and not calling_options.all:
        calling_options.hostname = raw_input('hostname: ')

    if calling_options.debug:
        log.setLevel(logging.DEBUG)


    return calling_options, calling_args

def _get_server():
    """ getting the server object """
    url = "http://%s/cobbler_api" % options.server
    try:
        _server = xmlrpclib.Server(url)
        return _server
    except:
        traceback.print_exc()
        return None

if  __name__ == "__main__":

    global_log_level = logging.WARN
    default_log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    default_log_handler = logging.StreamHandler(sys.stderr)
    default_log_handler.setFormatter(default_log_format)

    log = logging.getLogger("cobbler_query")
    log.setLevel(global_log_level)
    log.addHandler(default_log_handler)
    log.debug("Starting logging")


    options, args = get_options()
    server = _get_server()
    if options.hostname:
        # Only doing one system
        hostname = options.hostname
        system = server.get_item('system', hostname)
        try:
            name = system['name']
        except TypeError:
            print "Sorry, hostname %s does not seem to exist in cobbler" % hostname
            sys.exit()

        if options.koan:
            system = server.get_system_for_koan(hostname)

        print "System %s as %s:" % (name, hostname)
        if not options.quiet:
            pprint.pprint(system)

    else:
        for system in server.get_systems():
            name = system['name']
            hostname = system['hostname']
            if hostname not in name and not options.quiet:
                log.warn("hostname <-> name problem with system name %s" % name )
            if options.glob:
                glob = options.glob
                if    re.search(glob, name):
                    print "System %s as %s :" % (name, hostname)
                    if not options.quiet:
                        pprint.pprint(system)
            else:
                print "System %s as %s :" % (name, hostname)
                if not options.quiet:
                    pprint.pprint(system)
