"""A Continue button alone must never count as native grading evidence."""
import unittest
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from feedback_checks import assert_native_correct, feedback_terminal


def screen(*texts):
    root = ET.Element('hierarchy')
    for text in texts:
        ET.SubElement(root, 'node', text=text, enabled='true')
    return root


class FeedbackChecksTest(unittest.TestCase):
    def test_observed_positive_banner(self):
        assert_native_correct(screen(' Awesome!', 'CONTINUE'), 'test')
        assert_native_correct(screen(' Correct!', 'CONTINUE'), 'test')
        assert_native_correct(screen(' Excellent!', 'CONTINUE'), 'test')

    def test_historical_native_success_and_skip_screens(self):
        evidence = Path(__file__).parent / 'evidence/2026-11-01'
        def recorded(name):
            entries = json.loads((evidence / name).read_text())
            root = ET.Element('hierarchy')
            for item in entries:
                ET.SubElement(root, 'node', text=item.get('text', ''),
                              enabled=str(item.get('enabled', False)).lower())
            return root
        assert_native_correct(recorded('first-native-correct-answer.json'), 'historical success')
        with self.assertRaises(AssertionError):
            assert_native_correct(recorded('interaction-aerospace-rich-correct-submitted.json'), 'historical technical skip')

    def test_continue_alone_is_not_success(self):
        self.assertFalse(feedback_terminal(screen('CONTINUE')))
        self.assertTrue(feedback_terminal(screen(' Amazing!', 'CONTINUE')))
        self.assertTrue(feedback_terminal(screen('Oops! Something went wrong', 'CONTINUE')))
        with self.assertRaises(AssertionError):
            assert_native_correct(screen('CONTINUE'), 'test')

    def test_incorrect_or_error_cannot_be_overridden_by_positive(self):
        for error in ('GOT IT', 'Incorrect', 'Error', 'Skip', 'Oops! Something went wrong', 'Let’s skip this exercise for now'):
            with self.subTest(error=error), self.assertRaises(AssertionError):
                assert_native_correct(screen(' Correct!', error, 'CONTINUE'), 'test')


if __name__ == '__main__':
    unittest.main()
