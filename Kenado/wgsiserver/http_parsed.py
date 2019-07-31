from wgsiserver.logging import logger


class BaseRequest(object):
    """
    base request class
    """

    def __init__(self, request):
        self.request = request
        self._parsed_request()

    def _parsed_request(self):
        """
        解析 request
        :param request:
        :return:
        """
        self._parsed_header()
        self._parsed_body()

    def __parse_startline(self, start_line):
        """
        Parse the start line, to get the commond, path, query, http version
        :param start_line:
        :return: (commond, path, query, http version)
        """
        commond, path, version = start_line.split(' ')
        if '?' in path:
            path, query = path.split('?', 1)
        else:
            path, query = path, ''
        return commond, path, query, version

    def _parsed_header(self):
        """
        解析 header
        :param request:
        :return:
        """
        start_line = self.request.split('\r\n\r\n', 1)[0].split('\r\n')[0]
        print(start_line)
        start_line = start_line.replace('\r\n', '\n')
        print(start_line)
        start_line = start_line.replace('\r', '\n')
        print(start_line)
        print("start_line: %s", start_line)
        # Check if read blank string
        if start_line == "":
            raise Exception("Get blank data from client socket")
        self.commond, self.path, self.query, self.version = self.__parse_startline(start_line)
        headers = self.request.split('\r\n\r\n', 1)[0].split('\r\n')[1:3]
        query = {}
        for h in headers:
            k, v = h.split(': ', 1)
            query[k] = v
        self.headers = query
        logger.debug("header: %s", self.headers)
        self.content_length = int(self.headers.get("Content-Length", 0))
        pass

    def _parsed_body(self):
        """
        解析body
        :param request:
        :return:
        """
        self.body = self.request.split('\r\n\r\n', 1)[1]

    def getenv(self):
        """ Get the environ """
        environ = {}
        environ['SERVER_NAME'] = 'neuedu-micro-server'
        environ['GATEWAY_INTERFACE'] = 'CGI/1.1'
        environ['SERVER_PORT'] = '8889'
        environ['REMOTE_HOST'] = ''
        environ['CONTENT_LENGTH'] = ''
        environ['SCRIPT_NAME'] = ''
        environ['HTTPS'] = 'off'
        environ["wsgi.version"] = (1, 0)
        environ["wsgi.input"] = self.body
        environ["wsgi.error"] = None
        environ["wsgi.multithread"] = False
        environ["wsgi.multiprocess"] = False
        environ["wsgi.run_once"] = False

        if environ.get("HTTPS", "off") in ("on", "1"):
            environ["wsgi.url_scheme"] = "https"
        else:
            environ["wsgi.url_scheme"] = "http"

        environ['SERVER_SOFTWARE'] = 'neuedu-wsgi'

        """ Setting the cgi environ """
        # Request http version
        environ['SERVER_PROTOCOL'] = self.version
        environ['REQUEST_METHOD'] = self.commond
        environ['PATH_INFO'] = self.path
        environ['QUERY_STRING'] = self.query

        environ['CONTENT_TYPE'] = self.headers.get('Content-Type', 'text/plain')

        length = self.headers.get('Content-Length')

        if length:
            environ["CONTENT_LENGTH"] = length

        for k, v in self.headers.items():
            k = k.replace('-', '_').upper()
            v = v.strip()

            if k in environ:
                continue
            if 'HTTP_' + k in environ:
                environ['HTTP_' + k] += ',' + v
            else:
                environ['HTTP_' + k] = v
        return environ
