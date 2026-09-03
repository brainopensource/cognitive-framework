import unittest
from src.intervals import merge_intervals
from src.scheduler import Scheduler


class TestIntervals(unittest.TestCase):
    def test_merges_overlapping(self):
        self.assertEqual(merge_intervals([(0, 5), (3, 8)]), [(0, 8)])

    def test_merges_touching_intervals(self):
        # A meeting ending at 5 and one starting at 5 is a conflict.
        self.assertEqual(merge_intervals([(0, 5), (5, 8)]), [(0, 8)])

    def test_leaves_disjoint_intervals_separate(self):
        self.assertEqual(merge_intervals([(0, 5), (6, 8)]), [(0, 5), (6, 8)])


class TestScheduler(unittest.TestCase):
    def test_back_to_back_booking_is_a_conflict(self):
        sched = Scheduler()
        self.assertTrue(sched.book(0, 5))
        self.assertFalse(sched.book(5, 8))

    def test_disjoint_booking_succeeds(self):
        sched = Scheduler()
        self.assertTrue(sched.book(0, 5))
        self.assertTrue(sched.book(6, 8))


if __name__ == "__main__":
    unittest.main()
