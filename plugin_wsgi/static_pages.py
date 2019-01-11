#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 17:20:12 2018

@author: wolf
"""
import os.path
import mimetypes
from dogma.program import Plugin

class StaticPage(Plugin):
    def __init__(self, parent):
        Plugin.__init__(self, parent)
        

    def load(self, config=None, state=None):
        Plugin.load(self, config=config, state=state)

    def unload(self, state=None):
        Plugin.unload(self, state=state)

    def init(self):
        Plugin.init(self)

    def url_handler(self, env, response):
        url = self.config.get('directory', 'static_pages') + env['PATH_INFO']
        filename = url
        if '\\' in url:
            self.parent.set_http_code(403, env, response)
            return
        elif '/./' in url or '/../' in url:
            self.parent.set_http_code(403, env, response)
            return

        if os.path.isdir(url):
            if url[-1] == '/':
                filename = url + (url[-1] == '/' and 'index.html' or '/index.html')
        
        # TODO: there should be specific checks here to see if such things are allowed.
        if os.path.isfile(filename):
            fi = open(filename, 'rb')
            data = fi.read()
            fi.close()
            
            mime = mimetypes.guess_type(filename)
            response['headers'] = [('Content-Type', mime[0])]

            response['data'] = [data]
