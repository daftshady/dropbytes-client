"""

    dropbytes.option
    ~~~~~~~~~~~~~~~~

"""


class ParseError(Exception):
    pass


class OptionParser(object):
    """Command-line option parser.
    Available options are not implemented yet.

    """
    def __init__(self):
        self._FILENAME_LIMIT = 128
        self._available = []

    @property
    def raw(self):
        return self._options

    def parse(self, args):
        if len(args) == 1:
            raise ParseError('Error: Filename must be provided')

        global global_option
        if len(args[-1]) > self._FILENAME_LIMIT:
            raise ParseError('Filename cannot exceed 128 character')
        if '/' in len(args[-1]):
            raise ParseError('DO NOT USE path indentifier / to filename. ')
        global_option.filename = args[-1]

        for i in range(1, len(args) - 1):
            if not args[i].startswith('-'):
                raise ParseError('Error: Invalid options')
            global_option.args.append(args[i])


class Option(object):
    def __init__(self):
        self._filename = None
        self._args = None

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, v):
        self._filename = v

    @property
    def args(self):
        return self._args

    @args.setter
    def args(self, v):
        self._args = v

    def process(self):
        pass

global_option = Option()
