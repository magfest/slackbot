# -*- coding: utf-8 -*-

import os
import logging
from glob import glob
from six import PY2
from importlib import import_module
from magbot import settings
from brain.utils import to_utf8

logger = logging.getLogger(__name__)


class PluginsManager(object):
    def __init__(self, settings):
        self.settings = settings

    commands = {
        'respond_to': {},
        'listen_to': {}
    }

    def init_plugins(self):
        if hasattr(self.settings, 'PLUGINS'):
            plugins = self.settings.PLUGINS
        else:
            plugins = 'slackbot.plugins'

        if hasattr(self.settings, 'answer_key'):
            self.answer_key = self.settings.answer_key
        else:
            self.answer_key = "$"

        if hasattr(self.settings, 'db'):
            self.db = self.settings.db
        else:
            self.db = None

        for plugin in plugins:
            self._load_plugins(plugin)

    def _load_plugins(self, plugin):
        logger.info('loading plugin "%s"', plugin)
        path_name = None

        if PY2:
            import imp

            for mod in plugin.split('.'):
                if path_name is not None:
                    path_name = [path_name]
                _, path_name, _ = imp.find_module(mod, path_name)
        else:
            from importlib.util import find_spec as importlib_find

            path_name = importlib_find(plugin).submodule_search_locations[0]

        for pyfile in glob('{}/[!_]*.py'.format(path_name)):
            module = '.'.join((plugin, os.path.split(pyfile)[-1][:-3]))
            try:
                import_module(module)
            except:
                # TODO Better exception handling
                logger.exception('Failed to import %s', module)

    def get_plugins(self, category, text):
        has_matching_plugin = False
        has_answer_key = True
        if category == "listen_to":
            has_answer_key = False
            if text[0] == self.answer_key:
                has_answer_key = True
        for matcher in self.commands[category]:
            m = matcher[0].search(text)
            if m and has_answer_key:
                has_matching_plugin = True
                yield self.commands[category][matcher], to_utf8(m.groups())

        if not has_matching_plugin:
            yield None, None
