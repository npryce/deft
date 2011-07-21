
import datetime
from StringIO import StringIO
from argparse import Namespace
from deft.history.cfd import write_table_as_chart
from hamcrest import *

table = [['date', 'released', 'implemented', 'in-progress, blocked', 'new'], [datetime.date(2011, 6, 4), 0, 1, 1, 7], [datetime.date(2011, 6, 5), 0, 3, 3, 11], [datetime.date(2011, 6, 6), 0, 3, 3, 13], [datetime.date(2011, 6, 7), 0, 3, 3, 14], [datetime.date(2011, 6, 8), 0, 3, 3, 14], [datetime.date(2011, 6, 9), 0, 4, 4, 17], [datetime.date(2011, 6, 10), 0, 4, 5, 18], [datetime.date(2011, 6, 12), 0, 4, 5, 18], [datetime.date(2011, 6, 13), 0, 4, 5, 18], [datetime.date(2011, 6, 14), 0, 5, 6, 18], [datetime.date(2011, 6, 15), 0, 5, 7, 18], [datetime.date(2011, 6, 16), 0, 5, 7, 18], [datetime.date(2011, 6, 17), 0, 5, 7, 18], [datetime.date(2011, 6, 18), 0, 5, 7, 18], [datetime.date(2011, 6, 19), 0, 5, 7, 18], [datetime.date(2011, 6, 20), 0, 6, 7, 18], [datetime.date(2011, 6, 21), 0, 6, 7, 20], [datetime.date(2011, 6, 22), 0, 7, 8, 22], [datetime.date(2011, 6, 23), 0, 7, 9, 22], [datetime.date(2011, 6, 24), 0, 7, 9, 22], [datetime.date(2011, 6, 25), 0, 8, 9, 22], [datetime.date(2011, 6, 26), 0, 8, 9, 22], [datetime.date(2011, 6, 27), 0, 8, 9, 22], [datetime.date(2011, 6, 28), 0, 9, 9, 22], [datetime.date(2011, 6, 29), 0, 9, 9, 22], [datetime.date(2011, 7, 1), 9, 9, 9, 22], [datetime.date(2011, 7, 3), 9, 9, 9, 22], [datetime.date(2011, 7, 4), 9, 9, 9, 22], [datetime.date(2011, 7, 5), 9, 9, 10, 22]]

def test_can_write_as_graphical_chart():
    args = Namespace()
    args.format = "ps"
    
    output = StringIO()
    write_table_as_chart(table, args, output)
    
    chart_file = output.getvalue()
    
    for col_header in table[0][1:]:
        assert_that(chart_file, contains_string(col_header))
