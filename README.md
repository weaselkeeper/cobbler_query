Pretty basic, query cobbler server over xmlrpc.  If you want to query a cobbler
server from somewhere else, this will let you do that.  If you are querying
from the cobbler server, it's probably better to just use the cobber <object>
report|list|edit etc method.


usage: cobbler_query.py [-h] [-n HOSTNAME] [-s SERVER] [-g GLOB] [-q] [-k]
                        [-v] [-d] [-c CONFIG] [-l] [-z] [-u USER] [-p PASSWD]
                        [--param PARAM] [--value PARAMVAL]

Pass cli options to script

optional arguments:
  -h, --help            show this help message and exit
  -n HOSTNAME, --hostname HOSTNAME
                        Hostname to query for.
  -s SERVER, --server SERVER
                        Cobbler server.
  -g GLOB, --glob GLOB  restrict actions to hosts that match regex Example,
                        ./cobbler_query.py -g 'checkout-app0?.*prod.*' For all
                        the checkout-app0[] in prod
  -q, --quiet           just tell me what systems match -g or hostname
  -k, --koan            Return data that koan would see, including expanding
                        inheritance. Only works in conjunction with the n flag
  -v, --verbose         Extra info about stuff
  -d, --debug           Set logging level to debug
  -c CONFIG, --config CONFIG
                        config file
  -l, --list_all        List all hosts
  -z, --auth            ask for authentication data
  -u USER, --user USER  username
  -p PASSWD, --pass PASSWD
                        password
  --param PARAM         pick a parameter, requires --value also
  --value PARAMVAL      value of param to query for, requires --param

