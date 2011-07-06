
from StringIO import StringIO
from deft.formats import LinesFormat
from hamcrest import *


def saved(format, sequence):
    output = StringIO()
    format.save(sequence, output)
    return output.getvalue()


class LinesFormat_Tests:
    def test_reads_lines_and_constructs_an_object_from_the_sequence(self):
        text = "alice\nbob\ncarol\n"
        
        assert_that(LinesFormat(list).load(StringIO(text)), equal_to(["alice", "bob", "carol"]))
        assert_that(LinesFormat(tuple).load(StringIO(text)), equal_to(("alice", "bob", "carol")))
        assert_that(LinesFormat(set).load(StringIO(text)), equal_to(set(["alice", "bob", "carol"])))

    def test_copes_with_missing_newline_at_end_of_file(self):
        text = "alice\nbob\ncarol"
        
        assert_that(LinesFormat(list).load(StringIO(text)), equal_to(["alice", "bob", "carol"]))

    def test_writes_each_element_of_iterable_on_a_line(self):
        assert_that(saved(LinesFormat(list), ["alice", "bob", "carol"]), equal_to("alice\nbob\ncarol\n"))
        assert_that(saved(LinesFormat(tuple), ("alice", "bob", "carol")), equal_to("alice\nbob\ncarol\n"))
