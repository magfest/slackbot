from brain.utils import till_end, till_white
import re
from brain.manager import PluginsManager
import logging

logger = logging.getLogger(__name__)

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
