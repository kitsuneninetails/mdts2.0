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

class HostNotFoundException(Exception):
    def __init__(self, host):
        self.host = host
    def __str__(self):
        return repr(self.host)

class HostAlreadyStartedException(Exception):
    def __init__(self, host):
        self.host = host
    def __str__(self):
        return repr(self.host)

class ObjectNotFoundException(Exception):
    def __init__(self, obj_name):
        self.obj_name = obj_name
    def __str__(self):
        return repr(self.obj_name)

class ObjectAlreadyAddedException(Exception):
    def __init__(self, obj_name):
        self.obj_name = obj_name
    def __str__(self):
        return repr(self.obj_name)

class ArgMismatchException(Exception): 
    def __init__(self, arg):
        self.arg = arg
    def __str__(self):
        return repr(self.arg)

class SubprocessFailedException(Exception):
    def __init__(self, process_name):
        self.process_name = process_name
    def __str__(self):
        return repr(self.process_name)

class ExitCleanException(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return ''

class SocketException(Exception):    
    def __init__(self, info):
        self.info = info
    def __str__(self):
        return repr(self.info)
