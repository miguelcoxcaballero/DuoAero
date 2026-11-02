"""A Continue button alone must never count as native grading evidence."""
import unittest
from xml.etree import ElementTree as ET
from feedback_checks import assert_native_correct


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

    def test_continue_alone_is_not_success(self):
        with self.assertRaises(AssertionError):
            assert_native_correct(screen('CONTINUE'), 'test')

    def test_incorrect_or_error_cannot_be_overridden_by_positive(self):
        for error in ('GOT IT', 'Incorrect', 'Error', 'Skip', 'Something went wrong'):
            with self.subTest(error=error), self.assertRaises(AssertionError):
                assert_native_correct(screen(' Correct!', error, 'CONTINUE'), 'test')


if __name__ == '__main__':
    unittest.main()
