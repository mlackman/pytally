import unittest
import os

from pytally import tallylog


class TestTallyLog(unittest.TestCase):
    TALLY_FILENAME = 'release.txt'

    def setUp(self):
        if os.path.exists(self.TALLY_FILENAME):
            os.remove(self.TALLY_FILENAME)
        self.t = tallylog.TallyLog(self.TALLY_FILENAME)

    def test_adding(self):
        self.t.add('release 1')
        self.assert_tally_contains(['release 1'])

        t=tallylog.TallyLog(self.TALLY_FILENAME)
        t.add('release 2')
        self.assert_tally_contains(['release 1', 'release 2'])

    def test_getting_lines(self):
        self.t.add('release 1')
        self.t.add('release 2')
        self.assertEquals(self.t.lines, ['release 1', 'release 2'])

    def test_getting_lines_from_non_existing_log(self):
        self.assertEquals(self.t.lines, [])

    def test_tagging(self):
        self.t.add('release 1')
        self.t.add('release 2')
        self.t.tag('release 1', 'current')

        self.assert_tally_contains(['release 1 [current]', 'release 2'])

    def test_tagging_tagged_line_with_same_tag(self):
        self.t.add('release 1')
        self.t.add('release 2')
        self.t.tag('release 2', 'current')
        self.t.tag('release 2', 'current')

    def test_tagging_non_existing_line(self):
        self.t.add('release 1')
        with self.assertRaises(tallylog.NoSuchLineFound):
            self.t.tag('release 2', 'current')

    def test_tagging_non_existing_line_but_tag_defined(self):
        self.t.add('release 1')
        self.t.tag('release 1', 'current')
        with self.assertRaises(tallylog.NoSuchLineFound):
            self.t.tag('release 2', 'current')

    def test_overriding_tag(self):
        self.t.add('release 1')
        self.t.add('release 2')
        self.t.tag('release 2', 'current')
        self.t.tag('release 2', 'previous')
        self.assert_tally_contains(['release 1', 'release 2 [previous]'])

    def test_remove_tag(self):
        self.t.add('release 1')
        self.t.add('release 2')
        self.t.tag('release 1', 'current')
        self.t.tag('release 2', 'current')

        self.t.remove_tag('current')

        self.assert_tally_contains(['release 1', 'release 2'])

    def test_remove_single_tag(self):
        self.t.add('release 1')
        self.t.add('release 2')
        self.t.tag('release 1', 'current')
        self.t.tag('release 2', 'other')

        self.t.remove_tag('current')

        self.assert_tally_contains(['release 1', 'release 2 [other]'])

    def test_removing_non_existing_tag(self):
        self.t.add('release 1')
        self.t.add('release 2')

        self.t.remove_tag('current')

        self.assert_tally_contains(['release 1', 'release 2'])

    def test_move_tag(self):
        self.t.add('release 1')
        self.t.add('release 2')
        self.t.tag('release 1', 'current')

        self.t.move_tag('release 1', 'release 2')

        self.assert_tally_contains(['release 1', 'release 2 [current]'])

    def test_move_tag_from_line_which_does_not_exists(self):
        self.t.add('release 2')
        with self.assertRaises(tallylog.NoSuchLineFound):
            self.t.move_tag('release 1', 'release 2')

    def test_move_tag_to_line_which_does_not_exists(self):
        self.t.add('release 1')
        self.t.tag('release 1', 'current')
        with self.assertRaises(tallylog.NoSuchLineFound):
            self.t.move_tag('release 1', 'release 2')

    def test_move_tag_when_tag_does_not_exists(self):
        self.t.add('release 1')
        self.t.add('release 2')

        with self.assertRaises(tallylog.TagNotFound):
            self.t.move_tag('release 1', 'release 2')

    def test_move_tag_up(self):
        self.t.add('release 1')
        self.t.add('release 2')
        self.t.add('release 3')
        self.t.add('release 4')
        self.t.tag('release 2', 'current')
        self.t.tag('release 4', 'current')

        self.t.move_tag_up('current')
        self.assert_tally_contains(['release 1 [current]', 'release 2', 'release 3 [current]', 'release 4'])

    def test_move_tag_does_not_move_unrelated_tag(self):
        self.t.add('release 1')
        self.t.add('release 2')
        self.t.add('release 3')
        self.t.add('release 4')
        self.t.tag('release 2', 'current')
        self.t.tag('release 3', 'other')

        self.t.move_tag_up('current')
        self.assert_tally_contains(['release 1 [current]', 'release 2', 'release 3 [other]', 'release 4'])

    def test_move_tag_up_when_tag_does_not_exist(self):
        self.t.add('release 1')
        with self.assertRaises(tallylog.TagNotFound):
            self.t.move_tag_up('current')

    def test_move_tag_up_when_no_lines_above(self):
        self.t.add('release 1')
        self.t.tag('release 1', 'current')

        with self.assertRaises(tallylog.CannotMoveTag):
            self.t.move_tag_up('current')

    def test_move_tag_down(self):
        self.t.add('release 1')
        self.t.add('release 2')
        self.t.add('release 3')
        self.t.add('release 4')
        self.t.tag('release 1', 'current')
        self.t.tag('release 3', 'current')

        self.t.move_tag_down('current')
        self.assert_tally_contains(['release 1', 'release 2 [current]', 'release 3', 'release 4 [current]'])

    def test_move_tag_down_when_tag_on_last_line(self):
        self.t.add('release 1')
        self.t.tag('release 1', 'current')

        with self.assertRaises(tallylog.CannotMoveTag):
            self.t.move_tag_down('current')

    def test_move_tag_down_when_tag_does_not_exists(self):
        self.t.add('release 1')
        with self.assertRaises(tallylog.TagNotFound):
            self.t.move_tag_down('current')

    def test_remove_first_line(self):
        self.t.add('release 1')
        self.t.remove_first()
        self.assert_tally_contains([])

    def test_getting_line_with_tag(self):
        self.t.add('release 1')
        self.t.tag('release 1', 'current')

        self.assertEquals(self.t.line('current'), 'release 1')

    def test_getting_line_with_tag_when_tag_does_not_exists(self):
        self.t.add('release 1')
        with self.assertRaises(tallylog.TagNotFound):
            self.t.line('some tag')

    def test_getting_line_tag(self):
        self.t.add('release 1')
        self.t.tag('release 1', 'current')
        self.assertEquals(self.t.line_tag('release 1'), 'current')

    def test_getting_line_tag_when_line_does_not_have_tag(self):
        self.t.add('release 1')
        self.assertEquals(self.t.line_tag('release 1'), None)

    def test_getting_line_tag_when_line_does_not_exists(self):
        self.t.add('release 1')
        with self.assertRaises(tallylog.NoSuchLineFound):
            self.t.line_tag('release 2')

    def assert_tally_contains(self, expected_lines):
        with open(self.TALLY_FILENAME, 'rt') as f:
            lines = f.read().splitlines()
            self.assertEquals(expected_lines, lines)


