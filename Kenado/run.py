from wgsiserver.wgsi_server import WSGIServer
from app import app

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8889
    print('running http://{}:{}'.format(host, port))
    httpd = WSGIServer(host, port, app)
    httpd.serve_forever()
