
from StringIO import StringIO
from deft.formats import LinesFormat, write_table_as_text, write_table_as_csv
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


class WriteTableAsText_Test:
    def test_formats_table_as_aligned_columns(self):
        features = [
            ("pending", 1, "alice"),
            ("pending", 2, "bob"),
            ("active", 8, "carol"),
            ("active", 9, "dave"),
            ("active", 10, "eve")]
        
        output = StringIO()
        
        write_table_as_text(features, output)
        
        formatted_lines = output.getvalue().splitlines()
        
        assert_that(formatted_lines, equal_to([
                    "pending  1 alice",
                    "pending  2 bob  ",
                    "active   8 carol",
                    "active   9 dave ",
                    "active  10 eve  "]))
        
    def test_writes_empty_list_as_empty_string(self):
        output = StringIO()
        
        write_table_as_text([], output)
        
        assert_that(output.getvalue(), equal_to(""))


    

class WriteTableAsCsv_Test:
    def writes_features_in_csv(self):
        features = [
            ("pending", 1, "alice"),
            ("pending", 2, "bob"),
            ("active", 8, "carol"),
            ("active", 9, "dave"),
            ("active", 10, "eve")]
        
        output = StringIO()
        
        write_table_as_csv(features, output, dialect="excel")
        
        csv_lines = output.getvalue().splitlines()
        assert_that(csv_lines, equal_to([
                    "pending,1,alice",
                    "pending,2,bob",
                    "active,8,carol",
                    "active,9,dave",
                    "active,10,eve"]))
    
    def test_formats_empty_list_as_empty_string(self):
        output = StringIO()
        
        write_table_as_csv([], output)
        
        assert_that(output.getvalue(), equal_to(""))
