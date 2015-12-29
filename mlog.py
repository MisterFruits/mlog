#! /usr/bin/env python
# coding: utf8
import nvd3
import argparse
import dateutil.parser
import re, logging, hashlib
from collections import defaultdict

WRONG_FORMAT_WARNING = "log '{}' does not match provided regex: '{}'"
LOGGER = logging.getLogger(__name__)

def main():
    # maybe add complex command line options such as mlog pie/stack
    parser = argparse.ArgumentParser(description='Output stats on module logs')
    parser.add_argument('logfile', help='input log file')
    parser.add_argument('-f', '--format', help='log format regex', default=r'(?P<module>.*)/(?P<version>.*) ; (?P<date>.*) ; (?P<host>.*) ; (?P<uid>.*) ;.*')
    parser.add_argument('-d', '--date-format', help='hint on date parsing format')
    parser.add_argument('-o', '--output-dir',
                        help='target dir where results will be generated')
    parser.add_argument('-S', '--start-time',
                        help='filter logs, dont consider logs before this date')
    parser.add_argument('-E', '--end-time',
                        help='filter logs, dont consider logs after this date')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='verbose mode')

    args = parser.parse_args()
    LOGGER.setLevel([logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG][args.verbose])

    with open(args.logfile) as loglines:
        p = Parser(loglines, args.format)
        p.modules_filter.add('python')
        # modules, uids = p.extract_infos()
        # print(modules)
        # print(uids)





class Log(object):
    """A line of log container"""
    def __init__(self, module, version, date, uid):
        super(Log, self).__init__()
        self.module = module
        self.version = version
        self.date = date
        self.uid = uid


class Parser(object):
    """An interface between log file and data internal representation"""
    def __init__(self, lines, format):
        super(Parser, self).__init__()
        self.lines = lines
        self.format = re.compile(format)
        self.date_format = None

        # Filtering stuff
        self.modules_filter = set()
        self.uids_filter = set()


    def extract_infos(self):
        modules = defaultdict(set)
        uids = set()
        for log in self.logs:
            uids.add(log.uid)
            modules[log.module].add(log.version)

        return modules, uids

    def _parse_line(self, line):
        """Main  parsing function"""
        m = self.format.match(line)
        if m:
            date =  m.group('date')
            if self.date_format:
                date = dateutil.parser.parse(date)

            return Log(m.group('module'), m.group('version'), date, hashlib.sha1(m.group('uid').encode()).hexdigest()[:5])
        else:
            raise SyntaxError(WRONG_FORMAT_WARNING.format(line, self.format.pattern))

    @property
    def logs(self):
        return self._filter(self.lines)


    def _filter(self, lines):
        for line in lines:
            try:
                log = self._parse_line(line)
                if self._keep(log):
                    yield log
            except SyntaxError as e:
                LOGGER.info(e.msg)

    def _keep(self, log):
        if self.modules_filter and log.module not in self.modules_filter:
            return False
        if self.uids_filter and log.uid not in self.uids_filter:
            return False
        return True

    def key(self, log):
        return self._month_key(log)

    def _month_key(self, log):
        """Provides a key based on the month, this concept of  key must be enforced"""
        key = log.date()
        key.day = 1
        return key

    def _month_label_formater(self):
        return '%d %b %Y'



if __name__ == '__main__':
    main()

