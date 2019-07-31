import selectors
import socket
import time
from wgsiserver.http_parsed import BaseRequest
# Weekday and month names for HTTP date/time formatting; always English!
_weekdayname = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
_monthname = [None, # Dummy so we can use 1-based month numbers
              "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
def format_date_time(timestamp):
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
    return "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
        _weekdayname[wd], day, _monthname[month], year, hh, mm, ss
    )
class WSGIServer(object):

    def __init__(self, host, port,application):
        self.selector = selectors.DefaultSelector()
        self.sock = socket.socket()
        self.address = (host, port)
        self.app = application
        self.request_queue_size = 5
        self.open_socket()

    def accept(self, sock, mask):
        sel = self.selector
        conn, addr = sock.accept()  # Should be ready
        conn.setblocking(False)
        sel.register(conn, selectors.EVENT_READ, self.read)

    def start_response(self, status, headers_list):
        """
        :return:
        """
        r = 'HTTP/1.1 {}\r\n'.format(status)
        for h in headers_list:
            k = h[0]
            v = h[1]
            r += '{}: {}\r\n'.format(k, v)
        r += "Date: %s\r\n" % format_date_time(time.time())
        r += "Server: neuedu-wsgi\r\n"
        r += '\r\n'
        self.response = r.encode()

    def write(self, sock, mask):
        sel = self.selector
        body = self.app(self.req.getenv(), self.start_response)
        for data in body:
            self.response += data
        resp = self.response
        sock.send(resp)
        sel.unregister(sock)
        sock.close()

    def read(self, conn, mask):
        sel = self.selector
        data = conn.recv(1000)  # Should be ready
        if data:
            conn.setblocking(False)
            sel.unregister(conn)
            s = data.decode('utf-8')
            self.req = BaseRequest(s)
            sel.register(conn, selectors.EVENT_WRITE, self.write)
        else:
            sel.unregister(conn)
            conn.close()

    def server_close(self):
        self.sock.close()
        self.selector.close()

    def server_bind(self):
        """
        绑定
        """
        sock = self.sock
        sock.bind(self.address)
        self.server_address = sock.getsockname()

    def server_listen(self):
        """
        监听
        """
        self.sock.listen(self.request_queue_size)

    def open_socket(self):
        sock = self.sock
        self.server_bind()
        self.server_listen()
        sock.setblocking(False)

    def serve_forever(self):
        sock = self.sock
        sel = self.selector
        sel.register(sock, selectors.EVENT_READ, self.accept)
        try:
            while True:
                events = sel.select()
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj, mask)
        finally:
            print('close')
            self.server_close()
