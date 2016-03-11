# -*- coding: utf-8 -*-
from __future__ import absolute_import
import imp
import importlib
import logging
import re
import time
from glob import glob
from six.moves import _thread
from brain.manager import PluginsManager
from brain.slackclient import SlackClient
from brain.utils import till_end, till_white
from brain.dispatcher import MessageDispatcher

logger = logging.getLogger(__name__)


class Bot(object):
    def __init__(self, settings):
        self._client = SlackClient(
            settings.API_TOKEN,
            bot_icon=settings.BOT_ICON if hasattr(settings, 'BOT_ICON') else None,
            bot_emoji=settings.BOT_EMOJI if hasattr(settings, 'BOT_EMOJI') else None
        )
        self._plugins = PluginsManager(settings)
        self._dispatcher = MessageDispatcher(self._client, self._plugins)

    def run(self):
        self._plugins.init_plugins()
        self._dispatcher.start()
        self._client.rtm_connect()
        _thread.start_new_thread(self._keepactive, tuple())
        logger.info('connected to slack RTM api')
        self._dispatcher.loop()

    def _keepactive(self):
        logger.info('keep active thread started')
        while True:
            time.sleep(30 * 60)
            self._client.ping()
