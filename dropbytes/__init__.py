#!/usr/bin/env python

#      _                 _           _
#   __| |_ __ ___  _ __ | |__  _   _| |_ ___  ___
#  / _` | '__/ _ \| '_ \| '_ \| | | | __/ _ \/ __|
# | (_| | | | (_) | |_) | |_) | |_| | ||  __/\__ \
#  \__,_|_|  \___/| .__/|_.__/ \__, |\__\___||___/
#                 |_|          |___/

__title__ = 'dropbytes'
__version__ = '0.1'
__author__ = 'Park Ilsu'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014 Park Ilsu'


"""
Minimal implementation for `dropbytes` command-line client.
In this client, you can send small file (smaller than 50MB) with super-simple
command.

Example usage:

    dropbytes daftshady.py

    Uploading...: daftshady.py
    Use this url to retrieve your file: http://dropbytes.net/8fca35eddf

Type anywhere `dropbytes something` to upload file to dropbytes server.
We can get rid of dizzy FTP command-line tools or heavy file-sync services.

"""

import sys
from dropbytes.stream import Layer, StreamError, BlockingStream
from dropbytes.option import global_parser, global_option, ParseError


def main():
    try:
        global_parser.parse(sys.argv)
    except ParseError as e:
        on_error(e.args[0], helper=True)

    try:
        layer = Layer(impl=BlockingStream(global_option.filename))
        layer.open()
        layer.send(global_option.filename)
    except StreamError as e:
        layer.finish()
        on_error(e.args[0])
    except KeyboardInterrupt as e:
        print ('File transfer has aborted by user')
        sys.exit(-1)


def on_error(message, helper=False):
    print ('Error occured: %s' % message)
    if helper:
        print ('Example usage: dropbytes daftshady.py')
    sys.exit(-1)
