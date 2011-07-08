
from StringIO import StringIO
from deft.warn import PrintWarnings, IgnoreWarnings, WarningRecorder, warnings_recorded_by
from hamcrest import *


class PrintWarnings_Test:
    def test_formats_warnings_and_prints_to_output_stream(self):
        out = StringIO()
        warn = PrintWarnings(out, "PREFIX: ",
                             example_warning="{name} ate {apples} apples")
        
        warn.example_warning(name="bob", apples=20)
        
        assert_that(out.getvalue(), equal_to("PREFIX: bob ate 20 apples\n"))
        
    def test_falls_back_to_generic_format_if_no_format_specified_for_warning(self):
        out = StringIO()
        warn = PrintWarnings(out, "WARNING: ")
        
        warn.example_warning(name="alice", oranges=10, bananas=20)
        
        assert_that(out.getvalue(), equal_to("WARNING: example warning (name: 'alice', oranges: 10, bananas: 20)\n"))


class IgnoreWarnings_Tests:
    def test_ignores_any_warnings_sent_to_it(self):
        warn = IgnoreWarnings()
        warn.a_warning(hello="world")
        warn.another_warning(apples=20)


class WarningRecorderTest_Tests:
    def records_sequence_of_warning_events(self):
        warnings = WarningRecorder()
        
        assert_that(len(warnings), equal_to(0))
        assert_that(list(warnings), equal_to([]))
        
        warnings.a_warning(hello="world")
        
        assert_that(len(warnings), equal_to(1))
        assert_that(list(warnings), equal_to([("a_warning", {"hello": "world"})]))
        assert_that(warnings[0], equal_to(("a_warning", {"hello": "world"})))
        
        warnings.another_warning(apples=20)
        
        assert_that(len(warnings), equal_to(2))
        assert_that(list(warnings), equal_to([("a_warning", {"hello": "world"}),
                                              ("another_warning", {"apples": 20})]))
        assert_that(warnings[0], equal_to(("a_warning", {"hello": "world"})))
        assert_that(warnings[1], equal_to(("another_warning", {"apples": 20})))
