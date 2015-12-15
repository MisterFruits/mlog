import mlog
import random
from nvd3 import stackedAreaChart, pieChart

def test_LogParser_parse():
    parser = mlog.LogParser(r'(?P<date>\S+) (?P<uid>\S+) (?P<module>\S+) (?P<version>\S+)')
    test_case = ['2008-09-03 gra45 nc_app3 3.4.5',
                 '2014-12-29 toto4 nc_app2 6.5',
                 '2015-09-14 toto4 nc_app3 6.4.5']

    logs = parser.parse(test_case)
    assert len(logs) == 3
    assert logs[0].date == '2008-09-03'
    assert logs[1].date == '2014-12-29'
    assert logs[2].date == '2015-09-14'

    assert logs[0].uid != 'gra45'
    assert logs[1].uid != 'toto4'
    assert logs[2].uid != 'toto4'

    assert logs[0].module == 'nc_app3'
    assert logs[1].module == 'nc_app2'
    assert logs[2].module == 'nc_app3'

    assert logs[0].version == '3.4.5'
    assert logs[1].version == '6.5'
    assert logs[2].version == '6.4.5'

def test_vincent():
    cats = ['y1', 'y2', 'y3', 'y4']
    index = range(1, 21, 1)
    multi_iter1 = {'index': index}
    for cat in cats:
        multi_iter1[cat] = [random.randint(10, 100) for x in index]

    chart = stackedAreaChart(name='stackedAreaChart', height=400, width=800)
    extra_serie = {"tooltip": {"y_start": "There is ", "y_end": " min"}}
    for cat in (cat for cat in multi_iter1 if cat != 'index') :
        chart.add_serie(name=cat, x=multi_iter1['index'], y=multi_iter1[cat], extra=extra_serie)

    chart.buildhtml()
    write(chart, 'vincent')

def test_nvd3():
    type = 'pieChart'
    chart = pieChart(name=type, color_category='category20c', height=450, width=450)
    chart.set_containerheader("\n\n<h2>" + type + "</h2>\n\n")

    xdata = ["Orange", "Banana", "Pear", "Kiwi", "Apple", "Strawberry", "Pineapple"]
    ydata = [3, 4, 0, 1, 5, 7, 3]

    extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
    chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
    chart.buildhtml()

    write(chart, 'pie')

def test_nvd3_stacked_area():
    chart = stackedAreaChart(name='stackedAreaChart', height=400, width=400)

    xdata = [100, 101, 102, 103, 104, 105, 106,]
    ydata = [6, 11, 12, 7, 11, 10, 11]
    ydata2 = [8, 20, 16, 12, 20, 28, 28]

    extra_serie = {"tooltip": {"y_start": "There is ", "y_end": " min"}}
    chart.add_serie(name="Serie 1", y=ydata, x=xdata, extra=extra_serie)
    chart.add_serie(name="Serie 2", y=ydata2, x=xdata, extra=extra_serie)
    chart.buildhtml()

    write(chart, 'stack')


def write(chart, filename):
     with open(filename + '.html', 'w') as output_file:
        output_file.write(chart.htmlcontent)

if __name__ == '__main__':
    test_nvd3_stacked_area()
    test_nvd3()
    test_vincent()
