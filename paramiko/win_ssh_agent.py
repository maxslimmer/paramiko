"""
Functions for communicating with ssh-agent, the OpenSsh windows ssh agent service.
"""

from win32.win32file import CreateFile, WriteFile, ReadFile
from win32 import win32file

import pywintypes

PIPE_NAME = "open-ssh-agent"

def _get_agent_pipe_object():
    try:
        handle = CreateFile(
            r'\\.\pipe\openssh-ssh-agent',
            win32file.GENERIC_READ | win32file.GENERIC_WRITE,
            0,
            None,
            win32file.OPEN_EXISTING,
            0,
            None
        )

        if handle:
            return handle
        else:
            return

    except pywintypes.error as e:
        if e.args[0] == 2:
            # no pipe
            pass
        elif e.args[0] == 109:
            # broken pipe
            pass
    return None


def can_talk_to_agent():
    """
    Check to see if there is a agent we can talk to.

    """
    return True # TODO: maybe check if the ssh-agent service is running?


def _query_agent(msg):
    """
    Communication with the agent process is done through a named pipe
    """
    handle = _get_agent_pipe_object()
    if not handle:
        # Raise a failure to connect exception, agent isn't running anymore!
        return None

    ret = WriteFile(handle, msg)
    # TODO: Check write return value

    response = ReadFile(handle, 64*1024)
    if response[0] == 0:
        return response[1]


class SSHAgentConnection(object):
    """
    Mock "connection" to an agent which roughly approximates the behavior of
    a unix local-domain socket (as used by Agent).  Requests are sent to the
    ssh-agent daemon via Windows named pipe, and responses are buffered back
    for subsequent reads.
    """

    def __init__(self):
        self._response = None

    def send(self, data):
        self._response = _query_agent(data)

    def recv(self, n):
        if self._response is None:
            return ""
        ret = self._response[:n]
        self._response = self._response[n:]
        if self._response == "":
            self._response = None
        return ret

    def close(self):
        pass
