#!/usr/bin/env python

# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import print_function

import argparse
import os.path
import json
import threading

import logging
import aiy.assistant.auth_helpers
import aiy.voicehat

import google.auth.transport.requests
import google.oauth2.credentials

from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file


DEVICE_API_URL = 'https://embeddedassistant.googleapis.com/v1alpha2'
DEVICE_MODEL_ID = 'akram-raspberrypi3'

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)

class MyAssistant(object):
    def __init__(self):
        self._device_model_id = DEVICE_MODEL_ID
        self._task = threading.Thread(target=self._run_task)
        self._can_start_conversation = False
        self._assistant = None
        self._events = None

    def start(self):
        """Starts the assistant.

        Starts the assistant event loop and begin processing events.
        """
        self._task.start()

    def _run_task(self):
        credpath = os.path.join(os.path.expanduser('~/.config'),'google-oauthlib-tool','credentials.json')
        with open(credpath, 'r') as f:
            credentials = google.oauth2.credentials.Credentials(token=None,
                                                            **json.load(f))

        print(credpath)
        print(credentials)

        with Assistant(credentials, DEVICE_MODEL_ID) as assistant:
            self._assistant = assistant
            events = self._assistant.start()

            print('device_model_id:', self._device_model_id + '\n' +
              'device_id:', self._assistant.device_id + '\n')

            for event in events:
                self._process_event(event,self._assistant.device_id)


    def _process_device_actions(self,event, device_id):
      if 'inputs' in event.args:
        for i in event.args['inputs']:
            if i['intent'] == 'action.devices.EXECUTE':
                for c in i['payload']['commands']:
                    for device in c['devices']:
                        if device['id'] == device_id:
                            if 'execution' in c:
                                for e in c['execution']:
                                    if e['params']:
                                        yield e['command'], e['params']
                                    else:
                                        yield e['command'], None


    def _process_event(self,event, device_id):

      status_ui = aiy.voicehat.get_status_ui()

      if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        status_ui.status('listening')
        print()

      print(event)

      if (event.type == EventType.ON_CONVERSATION_TURN_FINISHED and
            event.args and not event.args['with_follow_on_turn']):
        status_ui.status('ready')
        print()

      if event.type == EventType.ON_DEVICE_ACTION:
        status_ui.status('listening')
        for command, params in self._process_device_actions(event, device_id):
            print('Do command', command, 'with params', str(params))

    def _on_button_pressed(self):
        # Check if we can start a conversation. 'self._can_start_conversation'
        # is False when either:
        # 1. The assistant library is not yet ready; OR
        # 2. The assistant library is already in a conversation.
        if self._can_start_conversation:
            self._assistant.start_conversation()


def main():
    MyAssistant().start()



if __name__ == '__main__':
    main()
