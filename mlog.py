# coding: utf8
import re
import hashlib

class Log(object):
    """A line of log container"""
    def __init__(self, date, uid, module, version):
        super(Log, self).__init__()
        self.date = date
        self.uid = uid
        self.module = module
        self.version = version

class LogParser(object):
    """A interface between log file and data internal representation"""
    def __init__(self, parsing_format):
        super(LogParser, self).__init__()
        self.parsing_format = parsing_format

    def parse(self, log_lines):
        log_stack = []
        for line in log_lines:
            m = re.match(self.parsing_format, line)
            date = m.group('date')
            uid = hashlib.sha1(m.group('uid').encode('utf8')).hexdigest()
            module = m.group('module')
            version = m.group('version')
            log = Log(date, uid, module, version)
            log_stack.append(log)
        return log_stack
