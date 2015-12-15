import nvd3
import argparse

def main():
    # maybe add complex command line options such as mlog pie/stack
    parser = argparse.ArgumentParser(description='Output stats on module logs')
    parser.add_argument('logfile', help='input log file')
    parser.add_argument('-f', '--format' help='log format regex')
    parser.add_argument('-d', '--date-format' help='hint on date parsing format')
    parser.add_argument('-o', '--output-dir',
                        help='target dir where results will be generated')
    parser.add_argument('-S', '--start-time',
                        help='filter logs, dont consider logs before this date')
    parser.add_argument('-E', '--end-time',
                        help='filter logs, dont consider logs after this date')

    args = parser.parse_args()

    with open(args.logfile) as loglines:
        data = Parser(loglines).parse_by_module()
        maj_thumbnails(args.idir, args.odir, args.size, args.force)

if __name__ == '__main__':
    main()
