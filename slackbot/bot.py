# -*- coding: utf-8 -*-
from __future__ import absolute_import
import imp
import importlib
import logging
import re
import time
from glob import glob
from six.moves import _thread
from slackbot.manager import PluginsManager
import slackbot.globals as globs
from slackbot.slackclient import SlackClient
from slackbot.utils import till_end, till_white
from slackbot.dispatcher import MessageDispatcher

logger = logging.getLogger(__name__)


class Bot(object):
    def __init__(self, settings):
        self._client = SlackClient(
            settings.API_TOKEN,
            bot_icon=settings.BOT_ICON if hasattr(settings, 'BOT_ICON') else None,
            bot_emoji=settings.BOT_EMOJI if hasattr(settings, 'BOT_EMOJI') else None
        )
        if hasattr(settings, 'ATTRIBUTES'):
            for x in settings.ATTRIBUTES.keys():
                globs.set_atr(x, settings.ATTRIBUTES[x])
        globs.set_atr('bot_name', self._client.login_data['self']['name'])
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

def respond_to(matchstr, flags=0, halp=""):
    if halp == "":
        halp = matchstr.replace("\\b", "").replace(till_white, "(until whitespace)").replace(till_end, "(until end of line)")
    def wrapper(func):
        PluginsManager.commands['respond_to'][tuple((re.compile(matchstr, flags), halp))] = func
        logger.info('registered respond_to plugin "%s" to "%s"', func.__name__, matchstr)
        return func
    return wrapper


def listen_to(matchstr,flags=0, halp=""):
    if halp == "":
        halp = matchstr.replace("\\b", "").replace(till_white, "(until whitespace)").replace(till_end, "(until end of line)")
    def wrapper(func):
        PluginsManager.commands['listen_to'][tuple((re.compile(matchstr, flags), halp))] = func
        logger.info('registered listen_to plugin "%s" to "%s"', func.__name__, matchstr)
        return func
    return wrapper
