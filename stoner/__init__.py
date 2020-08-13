#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 09:49:11 2020

@author: wolf
"""
import os
import json
import logging
import dogma

logger = logging.getLogger(__name__)



def load_config_file(path, file, form='json'):
    if form == 'json':
        parser = json.load
    try:
        fih = open(os.path.join(path, file))

    except FileNotFoundError:
        return None

    logger.info("Reading Config: %s", file)
    config = None
    try:
        config = parser(fih)

    except json.decoder.JSONDecodeError as msg:
        logger.error("json.decoder.JSONDecodeError for %s: %s", file, msg)

    fih.close()
    return config



class Stoner(dogma.Agent):
    config = None
    config_dir = "config"
    config_ext = ".json"
    program_directory = "programs"

    def __init__(self):
        super().__init__()
        self.config = load_config_file(self.config_dir, 'stoner.json')
        if not self.config:
            logger.error("No config file loaded. exiting.")
            exit()

        # initialize logging
        self.config.setdefault("log_level", "INFO")
        self.config.setdefault("log_overrides", {})
        self.config.setdefault("log_format", '[%(levelname)s] %(asctime)s - %(name)s:%(lineno)d - %(message)s')
        self.init_logging()


    def init_logging(self):
        # somewhat borrowed from disco-py
        import warnings

        # Setup warnings module correctly
        warnings.simplefilter('always', DeprecationWarning)
        logging.captureWarnings(True)

        # Pass through our basic configuration
        logging.basicConfig(
            format=self.config["log_format"],
            level=getattr(logging, self.config["log_level"], "INFO"))

        # Override specific loggers
        for olog, olvl in self.config["log_overrides"].items():
            logging.getLogger(olog).setLevel(getattr(logging, olvl, "INFO"))


    def load_config(self, config, unique_id, default_module=None, default_class="Program", default_autoload=False):
        if config is None:
            config = {}

        elif type(config) == str:
            config = load_config_file(self.config_dir, config)

        if config is None:
            logger.error("No config file loaded for %s", unique_id)
            return None

        if default_module is None:
            default_module = "%s.%s" % (self.program_directory, unique_id)

        # apply defaults
        config.setdefault("_module", default_module)
        config.setdefault("_class", default_class)
        config.setdefault("_autoload", default_autoload)

        return config


    def get_autoload_plugins(self, program_id, config):
        plugins = []
        if 'plugins' not in config:
            return plugins

        for plugin_id, plugin_config in config["plugins"].items():
            plugin_config = self.load_config(
                plugin_config, plugin_id, default_module=plugin_id,
                default_class="Plugin", default_autoload=False)

            if not plugin_config.get("_autoload", True):
                logger.info('Program %s skipping plugin %s', program_id, plugin_id)
                continue

            logger.info('Program %s loading plugin %s', program_id, plugin_id)
            plugins.append({
                'module' : plugin_config["_module"],
                'unique_id' : plugin_id,
                'classname' : plugin_config["_class"],
                'config': plugin_config})

        return plugins


    def init(self):
        programs = self.config.get('programs', {})

        for file in programs:
            if not file.endswith(self.config_ext):
                continue

            program_id = os.path.splitext(file)[0]
            config = self.load_config(file, program_id, default_class="Program", default_autoload=False)

            if config is None or not config["_autoload"]:
                continue

            plugins = self.get_autoload_plugins(program_id, config)
            self.program_import(
                module=config["_module"],
                unique_id=program_id,
                classname=config["_class"],
                config=config,
                plugins=plugins
            )

        super().init()
