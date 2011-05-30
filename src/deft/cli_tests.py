
import cli
from hamcrest import *
from nose.tools import raises
from deft.tracker import UserError


class FindEditorCommand_Test:
    def test_prefers_deft_editor_if_set(self):
        assert_that(cli.find_editor_command({'DEFT_EDITOR': 'D', 'EDITOR': 'E', 'VISUAL': 'V'}),
                    equal_to('D'))
    
    def test_prefers_visual_if_deft_editor_not_set(self):
        assert_that(cli.find_editor_command({'EDITOR': 'E', 'VISUAL': 'V'}),
                    equal_to('V'))

    def test_will_use_editor_as_last_resort(self):
        assert_that(cli.find_editor_command({'EDITOR': 'E'}),
                    equal_to('E'))
        
    @raises(UserError)
    def test_throws_user_error_if_no_editor_specified(self):
        cli.find_editor_command({})

