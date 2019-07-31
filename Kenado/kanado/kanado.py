import time
import re


def default(environ, start_response):
    status = '404'
    response_headers = [('Content-Type', 'text/html')]
    start_response(status, response_headers)
    return [('==404 Page not found from a simple WSGI application!--->%s\n' % time.ctime()).encode('utf-8')]


class Kanado:
    def __init__(self, import_name):
        self.import_name = import_name
        self.uri_regex_map = {}
        self.uri_map = {
            '404': default,
        }

    def __call__(self, *args):
        environ, start_response = args
        url = environ['PATH_INFO']

        if url in self.uri_map:
            app = self.uri_map.get(url)
            dic = {}
            return app(environ, start_response, **dic)

        for k, v in self.uri_map.items():
            if k in self.uri_regex_map:
                m = self.uri_regex_map[k].match(url)
                if m:
                    app = self.uri_map.get(k)
                    return app(environ, start_response, **m.groupdict())

        else:
            app = self.uri_map.get('404')
            return app(environ, start_response)

    def route(self, path):
        pattern = path
        pattern = pattern.replace('<', '(?P<')
        pattern = pattern.replace('>', '>\w+)')

        def wrapper(func):
            if pattern.find('<') >= 0 and pattern.find('>') >= 0:
                self.uri_regex_map[path] = re.compile(pattern)

            def _wrap(environ, start_response, *args, **kwargs):
                res = func(*args, **kwargs)
                start_response('200 OK', [('Content-Type', 'text/html')])
                return [res.encode('utf-8')]

            self.uri_map.update({
                path: _wrap,
            })
            return _wrap

        return wrapper
