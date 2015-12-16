import mlog, random, math, time, datetime
from nvd3 import stackedAreaChart, pieChart, multiBarChart

def test_LogParser_parse():
    test_case = ['2008-09-03 gra45 nc_app3 3.4.5',
                 '2014-12-29 toto4 nc_app2 6.5',
                 '2015-09-14 toto4 nc_app3 6.4.5']
    parser = mlog.Parser(test_case, r'(?P<date>\S+) (?P<uid>\S+) (?P<module>\S+) (?P<version>\S+)')
    logs = parser.parse()

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

    chart = stackedAreaChart(name='stackedAreaChart', height=400, width=1000)
    extra_serie = {"tooltip": {"y_start": "There is ", "y_end": " min"}}
    for cat in (cat for cat in multi_iter1 if cat != 'index') :
        chart.add_serie(name=cat, x=multi_iter1['index'], y=multi_iter1[cat], extra=extra_serie)

    chart.buildhtml()
    write(chart, 'vincent')

def test_nvd3():
    type = 'pieChart'
    chart = pieChart(name=type, color_category='category20c', height=400, width=1050)
    chart.set_containerheader("\n\n<h2>" + type + "</h2>\n\n")

    xdata = ["Orange", "Banana", "Pear", "Kiwi", "Apple", "Strawberry", "Pineapple"]
    ydata = [3, 4, 0, 1, 5, 7, 3]

    extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"}}
    chart.add_serie(y=ydata, x=xdata, extra=extra_serie)
    chart.buildhtml()

    write(chart, 'pie')

def test_nvd3_stacked_area():
    chart = stackedAreaChart(name='stackedAreaChart', height=400, width=1000)

    xdata = [100, 101, 102, 103, 104, 105, 106,]
    ydata = [6, 11, 12, 7, 11, 10, 11]
    ydata2 = [8, 20, 16, 12, 20, 28, 28]

    extra_serie = {"tooltip": {"y_start": "There is ", "y_end": " min"}}
    chart.add_serie(name="Serie 1", y=ydata, x=xdata, extra=extra_serie)
    chart.add_serie(name="Serie 2", y=ydata2, x=xdata, extra=extra_serie)
    chart.buildhtml()

    write(chart, 'stack')

def test_nvd3_date():
    type = "multiBarChart"

    chart = multiBarChart(name=type, height=400, width=1000, x_is_date=True)
    chart.set_containerheader("\n\n<h2>" + type + "</h2>\n\n")

    nb_element = 100
    start_time = int(time.mktime(datetime.datetime(2013, 6, 1).timetuple()) * 1000)
    xdata = range(nb_element)
    xdata = list(map(lambda x: start_time + x * 100000000, xdata))
    ydata = [i + random.randint(1, 10) for i in range(nb_element)]
    ydata2 = map(lambda x: x * 2, ydata)

    tooltip_date = "%d %b %Y %H:%M:%S %p"
    extra_serie = {"tooltip": {"y_start": "There are ", "y_end": " calls"},
                   "date_format": tooltip_date}

    chart.add_serie(name="Count", y=ydata, x=xdata, extra=extra_serie)

    extra_serie = {"tooltip": {"y_start": "There are ", "y_end": " duration"},
                   "date_format": tooltip_date}
    chart.add_serie(name="Duration", y=ydata2, x=xdata, extra=extra_serie)
    chart.buildhtml()

    write(chart, "date")


def datagen(x, ymin, ymax, nsteps, lambdaa=5):
    assert 0 < x < nsteps, 'x must be posive and lower than nsteps'
    for x in range(-x, nsteps-x):
        yield 1/(1+math.exp(x))

def write(chart, filename):
     with open(filename + '.html', 'w') as output_file:
        output_file.write(chart.htmlcontent)

if __name__ == '__main__':
    test_nvd3_stacked_area()
    test_nvd3()
    test_vincent()
    test_nvd3_date()
