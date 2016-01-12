#! /usr/bin/env python
# coding: utf8
import nvd3
import argparse
import dateutil.parser, time
import re, logging, hashlib, os.path
from collections import defaultdict, Counter
from pprint import pprint as pp
from nvd3 import stackedAreaChart, pieChart, multiBarChart
from slugify import slugify


WRONG_FORMAT_WARNING = "log '{}' does not match provided regex: '{}'"
DEFAULT_LOG_FORMAT_REGEX = r'(?P<module>\S*)/(?P<version>\S*)\s*;\s*(?P<date>\d{8} \d{2}:\d{2}:\d{2})\s*;\s*(?P<host>\S*)\s*;\s*(?P<uid>\S*)\s*;\s*$'
LOGGER = logging.getLogger(__name__)

def main():
    # maybe add complex command line options such as mlog pie/stack
    parser = argparse.ArgumentParser(description='Output stats on module logs')
    parser.add_argument('logfile', help='input log file')
    parser.add_argument('-f', '--format', help='log format regex',
                        default=DEFAULT_LOG_FORMAT_REGEX)
    parser.add_argument('-o', '--output-dir', default='.',
                        help='target dir where results will be generated')
    parser.add_argument('-m', '--modules', action='append',
                        help='filter logs, just consider given modules')
    parser.add_argument('-S', '--start-time',
                        help='filter logs, dont consider logs before this date')
    parser.add_argument('-E', '--end-time',
                        help='filter logs, dont consider logs after this date')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='verbose mode')

    config_file_args = []
    with open("mpi.rc") as f:
        config_file_args = f.read().split()
    args = parser.parse_args()
    LOGGER.setLevel([logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG][args.verbose])

    with open(args.logfile) as loglines:
        p = Parser(loglines, args.format)
        p.date_format = True
        p.modules_filter.update(args.modules or config_file_args)
        datas_by_module = defaultdict(lambda: defaultdict(Counter))
        for log in p.logs:
            category = 'Module {}, version {}'.format(log.module, log.version)
            datas_by_module[log.module][category].update([p.key(log)])
        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)
        alll = {}
        for module, datas in datas_by_module.items():
            chart = stacked_chart(module, datas)
            chart.buildhtml()
            alll.update(datas)

            with open(os.path.join(args.output_dir, module + '.html'), 'w') as html_file:
                html_file.write(chart.htmlcontent)

        chart = stacked_chart("All modules", alll)
        chart.buildhtml()
        with open(os.path.join(args.output_dir, 'all.html'), 'w') as html_file:
                html_file.write(chart.htmlcontent)


def stacked_chart(title, datas):
    title = slugify(title)
    dates = set()
    for key in datas:
        dates.update(datas[key].keys())
    xdates = sorted([int(time.mktime(date.timetuple()) * 1000) for date in dates])

    chart = stackedAreaChart(name=title, height=400, width=1000, x_is_date=True)
    chart.set_containerheader("\n\n<h2>" + title + "</h2>\n\n")

    for category, data in datas.items():
        chart.add_serie(name=category, y=[data[date] for date in dates], x=xdates)

    return chart


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

