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

def setup_logging(level_overrides, level): # mostly borrowed from disco-py
    import warnings

    # Setup warnings module correctly
    warnings.simplefilter('always', DeprecationWarning)
    logging.captureWarnings(True)

    # Pass through our basic configuration
    logging.basicConfig(
        format='[%(levelname)s] %(asctime)s - %(name)s:%(lineno)d - %(message)s',
        level=level)

    # Override some noisey loggers
    for olog, olvl in level_overrides.items():
        logging.getLogger(olog).setLevel(olvl)



class Stoner(dogma.Agent):
    config_dir = "config"
    config_ext = ".json"
    program_directory = "programs"


    def config_load(self, program_name):
        try:
            fih = open('%s/%s%s' % (self.config_dir, program_name, self.config_ext))

        except FileNotFoundError:
            return None

        logger.info("Reading Config: %s", program_name)
        config = None
        try:
            config = json.load(fih)

        except json.decoder.JSONDecodeError as msg:
            logger.error("json.decoder.JSONDecodeError for %s: %s", program_name, msg)

        fih.close()
        if config is None:
            logger.error("No config file loaded for %s", program_name)
            return None

        config.setdefault("_module", "%s.%s" % (self.program_directory, program_name))
        config.setdefault("_class", "Program")
        config.setdefault("_autoload", False)

        if not "_class" in config:
            config["_class"] = "Program"

        return config


    def init(self):
        for file in os.listdir(self.config_dir):
            if not file.endswith(self.config_ext):
                continue

            program_name = os.path.splitext(file)[0]
            config = self.config_load(program_name)
            if config is None:
                continue

            if not config["_autoload"]:
                continue

            plugins = []
            # messy shit. refactor
            if 'plugins' in config:
                for unique_id, plug_conf in config["plugins"].items():
                    if plug_conf is None:
                        plug_conf = {}
                    
                    if not plug_conf.get("_autoload", True):
                        logger.info('Program %s skipping plugin %s', program_name, unique_id)
                        continue
                    logger.info('Program %s loading plugin %s', program_name, unique_id)
                    plugins.append({
                        'module' : plug_conf.get("_module", unique_id),
                        'unique_id' : unique_id,
                        'classname' : plug_conf.get("_class", "Plugin"),
                        'config': plug_conf})

            self.program_import(
                module=config["_module"],
                unique_id=program_name,
                classname=config["_class"],
                config=config,
                plugins=plugins
            )

        super().init()
