import nvd3
import argparse
import re, logging
from collections import defaultdict

WRONG_FORMAT_WARNING = "log '{}' does not match provided regex: '{}'"

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

    args = parser.parse_args()
    with open(args.logfile) as loglines:
        p = Parser(loglines, args.format)
        print(p.modules)
        print(p.uids)

class Log(object):
    """docstring for Log"""
    def __init__(self, module, version, date, uid):
        super(Log, self).__init__()
        self.module = module
        self.version = version
        self.date = date
        self.uid = uid


class Parser(object):
    """docstring for Parser"""
    def __init__(self, lines, format):
        super(Parser, self).__init__()
        self.lines = lines
        self.format = re.compile(format)
        self.modules, self.uids = self._extract_infos()

    def _extract_infos(self):
        modules = defaultdict(set)
        uids = set()
        for log in self.filter(self.lines):
            uids.add(log.uid)
            modules[log.module].add(log.version)

        return modules, uids

    def _parse_line(self, line):
        m = self.format.match(line)
        if m:
            return Log(m.group('module'), m.group('version'), m.group('date'), m.group('uid'))
        else:
            raise SyntaxError(WRONG_FORMAT_WARNING.format(line, self.format.pattern))

    def filter(self, lines):
        for line in lines:
            try:
                yield self._parse_line(line)
            except SyntaxError as e:
                logging.debug(e.msg)



if __name__ == '__main__':
    main()
