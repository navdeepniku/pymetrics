'''
This module has custome exceptions
'''


class FailedSSHClient(Exception):
    def __init__(self, hostname, e):
        super(FailedSSHClient, self).__init__(
            ("Paramiko failed to create SSH session for " + hostname + " due to " + str(e)))
