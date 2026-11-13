import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from enrollment import pairwise_distances, select_consistent  # noqa: E402


def face(seed, offset=0.0):
	"""A 128-dimensional encoding near a fixed point, like dlib's descriptors"""
	rng = np.random.default_rng(seed)
	base = np.full(128, 0.05) + offset
	return base + rng.normal(0, 0.005, 128)


class PairwiseDistancesTest(unittest.TestCase):
	def test_symmetric_with_zero_diagonal(self):
		d = pairwise_distances([face(1), face(2), face(3)])
		self.assertEqual(d.shape, (3, 3))
		np.testing.assert_allclose(d, d.T)
		np.testing.assert_allclose(np.diag(d), 0)


class SelectConsistentTest(unittest.TestCase):
	def test_keeps_all_when_frames_agree(self):
		encodings = [face(i) for i in range(5)]
		kept, spread = select_consistent(encodings, max_distance=0.35, min_count=3)
		self.assertEqual(len(kept), 5)
		self.assertLess(spread, 0.35)

	def test_drops_a_single_bad_frame(self):
		# One frame far from the rest, e.g. a half-lit IR frame
		encodings = [face(i) for i in range(4)] + [face(9, offset=0.06)]
		kept, _ = select_consistent(encodings, max_distance=0.35, min_count=3)
		self.assertEqual(len(kept), 4)
		self.assertFalse(any(np.allclose(k, encodings[4]) for k in kept))

	def test_rejects_when_too_few_agree(self):
		# Every frame differs from the others: no stable capture
		encodings = [face(i, offset=0.06 * i) for i in range(4)]
		kept, spread = select_consistent(encodings, max_distance=0.35, min_count=3)
		self.assertIsNone(kept)
		self.assertGreater(spread, 0.35)

	def test_single_frame(self):
		kept, spread = select_consistent([face(1)], max_distance=0.35, min_count=1)
		self.assertEqual(len(kept), 1)
		self.assertEqual(spread, 0.0)
		kept, _ = select_consistent([face(1)], max_distance=0.35, min_count=2)
		self.assertIsNone(kept)

	def test_empty(self):
		kept, spread = select_consistent([], max_distance=0.35, min_count=1)
		self.assertIsNone(kept)
		self.assertEqual(spread, 0.0)


if __name__ == "__main__":
	unittest.main()
