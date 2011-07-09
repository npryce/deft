
from StringIO import StringIO
from deft.warn import PrintWarnings, IgnoreWarnings, WarningRecorder, WarningRaiser, fallback_format
from hamcrest import *


class FallbackFormat_Test:
    def test_turns_warning_name_into_words(self):
        assert_that(fallback_format("example_warning_name", {}),
                    equal_to("example warning name"))
        
    def test_appends_warning_parameters_in_parentheses(self):
        assert_that(fallback_format("another_warning", {"foo": "bar", "boz": 10}),
                    equal_to("another warning (boz: 10, foo: 'bar')"))


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
        
        assert_that(out.getvalue(), equal_to(
                "WARNING: example warning (bananas: 20, name: 'alice', oranges: 10)\n"))


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


class WarningRaiser_Tests:
    def test_raises_warnings_as_exceptions(self):
        warnings = WarningRaiser()
        
        try:
            warnings.example_warning(who="carol", bananas=10)
        except UserWarning as e:
            assert_that(str(e), contains_string("example warning (bananas: 10, who: 'carol')"))
    
    def test_can_specify_the_type_of_exception_raised(self):
        class ExampleException(Exception):
            pass
        
        warnings = WarningRaiser(ExampleException)
        
        try:
            warnings.point_blank()
        except ExampleException as e:
            assert_that(str(e), contains_string("point blank"))
