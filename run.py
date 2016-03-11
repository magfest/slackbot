#!/usr/bin/env python

import sys
import logging
import logging.config
from magbot import settings
from magbot.bot import Bot as magbot
from leinad.bot import Bot as leinad


def main():
    kw = {
        'format': '[%(asctime)s] %(message)s',
        'datefmt': '%m/%d/%Y %H:%M:%S',
        'level': logging.DEBUG if settings.DEBUG else logging.INFO,
        'stream': sys.stdout,
    }
    logging.basicConfig(**kw)
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.WARNING)
    bot = magbot()
    bot2 = leinad()
    #CANT HANDLE TWO LIKE THIS. SEPARATE THREADS (actually makes this easier)
    bot.run()
    #bot2.run()

if __name__ == '__main__':
    main()
