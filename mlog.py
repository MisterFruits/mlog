#! /usr/bin/env python
# coding: utf8
import nvd3
import argparse
import dateutil.parser, time
import re, logging, hashlib
from collections import defaultdict, Counter
from pprint import pprint as pp
from nvd3 import stackedAreaChart, pieChart, multiBarChart


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
        p.date_format = True
        p.modules_filter.add('intel')
        data = defaultdict(Counter)
        for log in p.logs:
            category = 'Module {}, version {}'.format(log.module, log.version)
            data[category].update([p.key(log)])
        stacked_chart(data)

def stacked_chart(datas):
    pp(datas)
    x_values = set()
    for key in datas:
        x_values.update(datas[key].keys())
    pp(x_values)
    xx_values = [int(time.mktime(date.timetuple()) * 1000) for date in x_values]

    type = "stackedAreaChart"

    chart = stackedAreaChart(name=type, height=400, width=1000, x_is_date=True)
    chart.set_containerheader("\n\n<h2>" + type + "</h2>\n\n")


    tooltip_date = "%b %Y"

    for category, data in datas.items():
        extra_serie = {"tooltip": {"y_start": "There were ", "y_end": " {} moduel loaded".format(category)},
                       "date_format": tooltip_date}
        chart.add_serie(name=category, y=[data[key] for key in x_values], x=xx_values, extra=extra_serie)

    chart.buildhtml()

    write(chart, "date_from_log")

def write(chart, filename):
     with open(filename + '.html', 'w') as output_file:
        output_file.write(chart.htmlcontent)

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
                LOGGER.warning(e.msg)

    def _keep(self, log):
        if self.modules_filter and log.module not in self.modules_filter:
            return False
        if self.uids_filter and log.uid not in self.uids_filter:
            return False
        return True

    def key(self, log):
        return self._month_key(log)

    def _month_key(self, log):
        """Provides a key based on the month, this concept of key must be enforced"""
        date_key = log.date.date()
        return date_key.replace(day=1)

    def _month_label_formater(self):
        return '%d %b %Y'



if __name__ == '__main__':
    main()

