#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 23:42:30 2018

@author: wolf
"""

from gevent import pywsgi, sleep
from dogma.program import PlugableProgram
from chameleon import PageTemplateLoader
import lupa

class WSGI(PlugableProgram):
    def __init__(self, agent):
        PlugableProgram.__init__(self, agent)
        self.server = None
        self.templates = None
        self.lua = lupa.LuaRuntime(unpack_returned_tuples=True)


    def load(self, config=None, state=None):
        """
        """
        PlugableProgram.load(self, config, state)
        self.templates = PageTemplateLoader(self.config.get("templates"))
        #print len(self.templates), "loaded"


    def init(self):
        """
        """
        print'Serving on https://:8001'
        self.server = pywsgi.WSGIServer(
                (self.config.get('address', '127.0.0.1'), self.config.get('port', 8001)), 
                self.connect_handler,
                #keyfile=self.config.get('keyfile'), # 'server.key', 
                #certfile=self.config.get('certfile'), # 'server.crt'
                )
        
        PlugableProgram.init(self)


    def run(self):
        """
        """
        self.server.start()
        print "server started"
        while True:
            sleep(0.01)


    def connect_handler(self, env, start_response):
        """
        """
        for key, value in env.items():
            print key, ' = ', value

        response = {
            'code' : None,
            'headers' : [('Content-Type', 'text/html')],
            'data': None,
        }

        for plugin in self.plugins.values():
            if not hasattr(plugin, 'connect_handler'):
                continue
            if plugin.input_callback(env, response) is False:
                return # explicitly returned false, drop this connection

        self.url_handler(env, response)

        if response['data'] is None:
            self.set_http_code(404, env, response)

        if response['code'] is None and not response['data'] is None:
            response['code'] = '200 OK'
        
        start_response(response['code'], response['headers'])

        if isinstance(response['data'], dict):
            response['data'] = self.build_page(env, response)
        if not isinstance(response['data'], (list, tuple)):
            response['data'] = [response['data']]
        return response['data']


    def url_handler(self, env, response):
        """
        """
        for plugin in self.plugins.values():
            if hasattr(plugin, 'url_handler'):
                plugin.url_handler(env, response)


    def set_http_code(self, code, env, response):
        """
        """
        data = response.get('data')
        if code == 403:
            if data is None:
                data = {}
            response['code'] = '403 Forbidden'
            data['head'] = self.templates['head_default.pt']
            data['head_args'] = {'title':'4 oh 4'}
            data['body'] = self.templates['404.pt']
            data['body_args'] = {'name':'bob'}
            response['data'] = data
            return

        if code == 404:
            if data is None:
                data = {}
            response['code'] = '404 Not Found'
            data['head'] = self.templates['head_default.pt']
            data['head_args'] = {'title':'4 oh 4'}
            data['body'] = self.templates['404.pt']
            data['body_args'] = {'name':'bob'}
            response['data'] = data
            return
        
        raise ValueError

    def build_page(self, env, response):
        """
        """
        data = response['data']
        return [b' <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n',
                b'<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">',
                (data.get('head') and data['head'](**data.get('head_args', {})) or b''),
                (data.get('body') and data['body'](**data.get('body_args', {})) or b''),
                '</html>']





#return response['data'] or [b'<h1>Not Found</h1>']
#if env['PATH_INFO'] == '/':
#    start_response('200 OK', [('Content-Type', 'text/html')])
#    return [b"<b>hello world</b>"]

#start_response('404 Not Found', [('Content-Type', 'text/html')])
#return [b'<h1>Not Found</h1>']
