__author__ = 'micucci'
# Copyright 2015 Midokura SARL
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

import VTM.VirtualTopologyConfig
import json

class Network(object):
    def __init__(self, vtc):
        self.vtc = vtc
        self.ports = {}
        """ :type: VirtualTopologyConfig """

    def get_port(self, port_id):
        if port_id in self.ports:
            return self.ports[port_id]
        return None

    def create_port(self):
        port = None
        port_id = ''
        self.ports[port_id] = port
        return port_id

    def to_json(self):
        return json.dumps(self)
