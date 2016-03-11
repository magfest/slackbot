# -*- coding: utf-8 -*-

from __future__ import absolute_import
import logging
import re
import time
import traceback
from six import iteritems
from brain.manager import PluginsManager
from brain.utils import to_utf8, WorkerPool, create_tmp_file, till_end, till_white

logger = logging.getLogger(__name__)

AT_MESSAGE_MATCHER = re.compile(r'^\<@(\w+)\>:? (.*)$')


class MessageDispatcher(object):
    def __init__(self, slackclient, plugins):
        self._client = slackclient
        self._pool = WorkerPool(self.dispatch_msg)
        self._plugins = plugins

    def start(self):
        self._pool.start()

    def dispatch_msg(self, msg):
        category = msg[0]
        msg = msg[1]
        text = msg['text']
        responded = False
        for func, args in self._plugins.get_plugins(category, text):
            if func:
                responded = True
                try:
                    func(Message(self._client, msg, self._plugins), *args)
                except:
                    logger.exception('failed to handle message %s with plugin "%s"', text, func.__name__)
                    reply = '[%s] I have problem when handling "%s"\n' % (func.__name__, text)
                    reply += '```\n%s\n```' % traceback.format_exc()
                    self._client.rtm_send_message(msg['channel'], reply)

        if not responded and category == 'respond_to':
            self._default_reply(msg)

    def _on_new_message(self, msg):
        # ignore edits
        subtype = msg.get('subtype', '')
        if subtype == 'message_changed':
            return

        botname = self._client.login_data['self']['name']
        try:
            msguser = self._client.users.get(msg['user'])
            username = msguser['name']
        except (KeyError, TypeError):
            if 'username' in msg:
                username = msg['username']
            else:
                return

        if username == botname or username == 'slackbot':
            return

        msg_respond_to = self.filter_text(msg)
        if msg_respond_to:
            self._pool.add_task(('respond_to', msg_respond_to))
        else:
            self._pool.add_task(('listen_to', msg))

    def filter_text(self, msg):
        text = msg.get('text', '')
        channel = msg['channel']

        if channel[0] == 'C' or channel[0] == 'G':
            m = AT_MESSAGE_MATCHER.match(text)
            if not m:
                return
            atuser, text = m.groups()
            if atuser != self._client.login_data['self']['id']:
                # a channel message at other user
                return
            logger.debug('got an AT message: %s', text)
            msg['text'] = text
        else:
            m = AT_MESSAGE_MATCHER.match(text)
            if m:
                msg['text'] = m.group(2)
        return msg

    def loop(self):
        while True:
            events = self._client.rtm_read()
            for event in events:
                if event.get('type') != 'message':
                    continue
                self._on_new_message(event)
            time.sleep(1)

    def _default_reply(self, msg):
        try:
            from slackbot.settings import default_reply

            default_reply = to_utf8(default_reply)

        except ImportError:
            default_reply = [
                'Bad command "%s", You can ask me one of the following questions:\n' % msg['text'],
            ]
            default_reply += ['    • `{0}` {1}'.format(p[1]
                                                       , v.__doc__ or "")
                              for p, v in iteritems(self._plugins.commands['respond_to'])]

            default_reply = '\n'.join(to_utf8(default_reply))

        #msg.upload_snippet(default_reply, "Commands")
        self._client.rtm_send_message(msg['channel'], default_reply)


class Message(object):
    def __init__(self, slackclient, body, plugins):
        self._client = slackclient
        self._body = body
        self._plugins = plugins

    def _get_user_id(self):
        if 'user' in self._body:
            return self._body['user']

        return self._client.find_user_by_name(self._body['username'])

    def _gen_at_message(self, text):
        text = '<@{}>: {}'.format(self._get_user_id(), text)
        return text

    def _gen_reply(self, text):
        chan = self._body['channel']
        if chan.startswith('C') or chan.startswith('G'):
            return self._gen_at_message(text)
        else:
            return text

    def reply_webapi(self, text):
        """
            Send a reply to the sender using Web API

            (This function supports formatted message
            when using a bot integration)
        """
        text = self._gen_reply(text)
        self.send_webapi(text)

    def send_webapi(self, text, attachments=None):
        """
            Send a reply using Web API

            (This function supports formatted message
            when using a bot integration)
        """
        self._client.send_message(
            self._body['channel'],
            to_utf8(text),
            attachments=attachments)

    def reply(self, text):
        """
            Send a reply to the sender using RTM API

            (This function doesn't supports formatted message
            when using a bot integration)
        """
        text = self._gen_reply(text)
        self.send(text)

    def send(self, text):
        """
            Send a reply using RTM API

            (This function doesn't supports formatted message
            when using a bot integration)
        """
        self._client.rtm_send_message(
            self._body['channel'], to_utf8(text))

    def react(self, emojiname):
        """
           React to a message using the web api
        """
        self._client.react_to_message(
            emojiname=emojiname,
            channel=self._body['channel'],
            timestamp=self._body['ts'])

    def user_list(self):
        return self._client.webapi.users.list()

    def name_to_id(self, name):
        for x in self._client.users.keys():
            if self._client.users[x]['name'] == name:
                return self._client.users[x]['id']
        return "Not Found"

    def id_to_name(self, id):
        for x in self._client.users.keys():
            if self._client.users[x]['id'] == id:
                return self._client.users[x]['name']
        return "Not Found"

    def sent_by(self):
        for x in self._client.users.keys():
            if self._client.users[x]['id'] == self.body['user']:
                return self._client.users[x]['name']
        return "Not Found"

    def upload_snippet(self, file_text, title="File"):
        with create_tmp_file() as f:
                with open(f, 'w') as tmpf:
                    tmpf.write(file_text)
                    tmpf.flush()
                    tmpf.close()
                self.channel.upload_file(title, f)

    @property
    def channel(self):
        return self._client.get_channel(self._body['channel'])

    @property
    def body(self):
        return self._body

    def docs_reply(self):
        reply = ['    • `{0}` {1}'.format(v.__name__, v.__doc__ or "") for p, v in iteritems(self._plugins.commands['respond_to'])]
        return '\n'.join(to_utf8(reply))
