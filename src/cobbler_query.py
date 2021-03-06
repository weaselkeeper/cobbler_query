#!/usr/bin/env python
###
# Copyright (c) 2012, Jim Richardson <weaselkeeper@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

"""
 Queries cobbler for information on hosts. Use hostname to iterate over all
 the systems and pull out the info for the hosts you are interested in. No
 Auth required, does not write to cobbler at all.

"""

import argparse
import ConfigParser
import xmlrpclib
import sys
import pprint
import logging
import getpass


# Set some sane defaults

CONFIGFILE = '/etc/cobbler_query/cobbler_query.conf'


global_log_level = logging.WARN
default_log_format = logging.Formatter("%(asctime)s - %(levelname)s - \
                                       %(message)s")
default_log_handler = logging.StreamHandler(sys.stderr)
default_log_handler.setFormatter(default_log_format)

log = logging.getLogger("cobbler_query")
log.setLevel(global_log_level)
log.addHandler(default_log_handler)
log.debug("Starting logging")



def run():
    """ Main loop, called via .run method, or via __main__ section """
    log.debug('entring run()')
    args = get_options()
    conn = _get_server(args)

    if args.hostname:
        # Only doing one system
        hostname = args.hostname
        try:
            system = conn.get_item('system', hostname)
            name = system['name']
        except TypeError as error:
            log.warn('Couldn\'t fetch %s due to "%s"', hostname, error)
            sys.exit()

        if args.koan:
            system = conn.get_system_for_koan(hostname)

        print "System %s as %s:" % (name, hostname)
        if not args.quiet:
            pprint.pprint(system)

    else:
        get_query(conn, args)
    log.debug('leaving run()')


def get_query(conn, args):
    """ Query cobbler for various results, profiles, etc """
    if args.param and args.paramval:
        query_for = args.param
        query_val = args.paramval
        if query_val == 'list':
            query = conn.get_item_names(query_for)
        else:
            query = conn.get_item(query_for, query_val)
        if not args.quiet:
            print 'Cobbler knows about the following %ss \n' % query_for
        for line in query:
            print line
        return

    else:
        if not args.hostname and not args.list_all and not args.all:
            args.hostname = raw_input('hostname: ')

        for system in conn.get_systems():
            name = system['name']
            hostname = system['hostname']
            if hostname not in name and not args.quiet:
                log.warn("hostname <-> name problem with system name %s", name)
            else:
                print "System %s as %s :" % (name, hostname)
                if not args.quiet:
                    pprint.pprint(system)


def read_config(args):
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
    log.debug('entering read_config()')
    try:
        config = ConfigParser.SafeConfigParser()
        config.read(args.config)
        server = config.get('server', 'host')
    except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as error:
        log.warn('Something went wrong, python says "%s"', error)
        sys.exit(1)
    log.debug('leaving read_config()')
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
    parser.add_argument("-k", "--koan", action="store_true", help="Return data \
that koan would see, including expanding inheritance. \
Only works in conjunction with the n flag")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Extra info about stuff")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Set logging level to debug")
    parser.add_argument("-c", "--config", action="store", help="config file")

    parser.add_argument('-l', '--list_all', action='store_true',
                        help='List all hosts')

    parser.add_argument('-z', '--auth', action='store_true',
                        help='ask for authentication data')

    parser.add_argument('-u', '--user', action='store', help='username')

    parser.add_argument('-p', '--pass', dest='passwd', action='store',
                        help='password')
    parser.add_argument('--param', dest='param', action='store',
                        help='pick a parameter, requires --value also')

    parser.add_argument('--value', dest='paramval', action='store',
                        help='value of param to query for, requires --param')

    args = parser.parse_args()

    # Adding username/pass args because we will be using these in the future
    # for making changes rather than just reading data. But not needed yet.
    if args.auth:
        if not args.user:
            args.user = getpass.getuser()
        if not args.passwd:
            # Remember, passwd will be stored in memory, in cleartxt.
            args.passwd = getpass.getpass()

    if not args.config:
        args.config = CONFIGFILE

    if not args.server:
        args.server = read_config(args)

    if args.debug:
        log.setLevel(logging.DEBUG)

    args.usage = "usage: %prog [options]"

    return args


def _get_server(args):
    """ get the server object """
    log.debug('entering _get_server()')
    url = "http://%s/cobbler_api" % args.server
    conn = xmlrpclib.Server(url, allow_none=True)
    log.debug('leaving _get_server()')
    return conn

if __name__ == "__main__":
    sys.exit(run())
