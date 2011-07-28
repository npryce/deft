
from StringIO import StringIO
from datetime import date
from argparse import Namespace
from deft.history.cfd import write_table_as_chart, cumulative_flow
from deft.storage.git import GitStorageHistory
from deft.history import History
from deft.warn import IgnoreWarnings
from hamcrest import *
from nose.plugins.attrib import attr


    

@attr("fileio")
def test_can_analyse_history_as_cumulative_flow():
    warning_listener = IgnoreWarnings()
    history = History(GitStorageHistory("."), warning_listener)
    
    revision_2011_06_07 = "d163370c11dede181f119e40ad315079177af3ec"
    buckets = [["new"], ["blocked"], ["in-progress"], ["implemented"], ["released"]]
    
    flow = cumulative_flow(history, revision_2011_06_07, buckets, warning_listener)
    
    assert_that(flow[0], equal_to(["date", "released", "implemented", "in-progress", "blocked", "new"]))
    
    assert_that(flow[1:], equal_to(
            [[date(2011,6,4),0,1,1,1,7],
             [date(2011,6,5),0,3,3,3,11],
             [date(2011,6,6),0,3,3,3,13],
             [date(2011,6,7),0,3,3,3,14]]))

    
def test_can_write_as_graphical_chart():
    table = [['date', 'released', 'implemented', 'in-progress, blocked', 'new'], 
             [date(2011, 6, 4), 0, 1, 1, 7], 
             [date(2011, 6, 5), 0, 3, 3, 11], 
             [date(2011, 6, 6), 0, 3, 3, 13], 
             [date(2011, 6, 7), 0, 3, 3, 14]]
    
    args = Namespace()
    args.format = "ps"
    
    output = StringIO()
    write_table_as_chart(table, args, output)
    
    chart_file = output.getvalue()
    
    for col_header in table[0][1:]:
        assert_that(chart_file, contains_string(col_header))

