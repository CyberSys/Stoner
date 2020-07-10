#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 23:42:30 2018

@author: wolf
"""

from gevent import pywsgi
from dogma.program import Plugin

def handler(env, start_response):
    for key, value in env.items():
        print(key, ' = ', value)
    if env['PATH_INFO'] == '/':
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b"<b>hello world</b>"]

    start_response('404 Not Found', [('Content-Type', 'text/html')])
    return [b'<h1>Not Found</h1>']

class WSGI(Plugin):
    def __init__(self, client):
        Plugin.__init__(self, client)
        self.server = None

    def load(self, config=None, state=None):
        Plugin.load(self, config, state)

    def init(self):
        print('Serving on https://:8001')
        self.server = pywsgi.WSGIServer(
                (self.config.get('address', '127.0.0.1'), self.config.get('port', 8001)), 
                handler,
                #keyfile=self.config.get('keyfile'), # 'server.key',
                #certfile=self.config.get('certfile'), # 'server.crt'
                )
        self.server.start()
        print("server started")
