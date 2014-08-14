"""

    dropbytes.stream
    ~~~~~~~~~~~~~~~~

"""
import sys
import socket
import struct


_ENCODING = 'utf8'
_UPLOAD_ADDR = (socket.gethostbyname('upload.dropbytes.net'), 9000)


class StreamError(Exception):
    pass


class Layer(object):
    def __init__(self, impl):
        self._impl = impl
        self._opened = False

    @property
    def opened(self):
        return self._opened

    def send(self, file_):
        if not self.opened:
            raise StreamError('Cannot write to closed stream')
        self._impl.write(callback=self._impl._on_write)

    def open(self):
        self._impl.open()
        self._opened = True

    def finish(self):
        self._impl.close()


class FileMixin(object):
    """This mixin makes file properties to fit into a stream."""
    def to_filename(self, raw_filename):
        filename = raw_filename.encode(_ENCODING) \
            if sys.version_info[0] == 3 else raw_filename
        return filename + b' ' * ((1 << 7) - len(filename))

    def to_filelen(self, raw_chunk):
        return struct.pack('>I', len(raw_chunk))


class Stream(object):
    def __init__(self, filename):
        self._bytes_written = 0
        self._chunk = None
        self._filename = filename
        self._buf_size = 1 << 16
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.initialize()

    def initialize(self):
        """Hook for socket options"""
        pass

    @property
    def ready(self):
        return self._chunk is not None

    def open(self):
        try:
            with open(self._filename, 'rb') as file_:
                self._chunk = file_.read()
        except IOError:
            raise StreamError('File `%s` not exists' % self._filename)

        try:
            self._sock.connect(_UPLOAD_ADDR)
        except socket.error:
            raise StreamError('Upload server is dead')

    def write(self):
        raise NotImplementedError

    def close(self):
        if self._sock is not None:
            self._sock.close()
            self._sock = None
            self._chunk = None

    def _raise_error(self, msg):
        self.close()
        raise StreamError(msg)


class BlockingStream(Stream, FileMixin):
    def write(self, callback=None):
        filename = self.to_filename(self._filename)
        filelen = self.to_filelen(self._chunk)
        try:
            print ('Uploading...: %s' % filename.decode(_ENCODING))

            self._sock.sendall(filename)
            self._sock.sendall(filelen)
            # TODO: Should show progress!
            self._sock.sendall(self._chunk)
        except socket.error:
            self._raise_error(
                'Unexpected Error occured. '
                'Maybe you are trying to send a file larger than 50MB')

        if callback is not None:
            callback()

    def _on_write(self):
        """After uploading is done, this method takes 1 byte from server
        to check whether file is saved successfully or not.

        """
        try:
            state = self._read_all(1, cut=1)
        except socket.error:
            self._raise_error(
                'Unexpected Error occured while reading error bytes')

        if not state:
            self._raise_error(
                'Server closed connection before sending error bytes')
        if state == b's':
            try:
                url = self._read_all(self._buf_size)
                print (
                    'Use this url to retrieve your file: %s'
                    % url.decode(_ENCODING)
                )
            except socket.error:
                self._raise_error(
                    'Unexpected Error occured while reading url')
        else:
            # Use `state` to determine which error has occured.
            self._raise_error(
                'Unexpected error occured. Error byte: %s' %
                state.decode(_ENCODING)
            )

    def _read_all(self, len_, cut=None):
        """Synchronously reads `len_` data from stream"""
        bytes_read = 0
        chunk = b''
        fin = False
        while bytes_read < len_:
            piece = self._sock.recv(cut or self._buf_size)
            if not piece:
                fin = True
                break
            chunk += piece
            bytes_read += len(piece)

        if not fin and len(chunk) != len_:
            self._raise_error('Received bytes length mismatch')
        return chunk


class NonblockingStream(Stream):
    pass
