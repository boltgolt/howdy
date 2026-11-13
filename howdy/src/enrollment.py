# Helpers for building a face model from several captured frames
#
# A model built from a single frame is only as good as that frame: a frame
# caught mid-blink, half lit by a strobing IR emitter, or with the head turned
# produces an encoding that later fails to match the user. Enrolling several
# frames and discarding the ones that disagree with the rest avoids that.

import numpy as np


def pairwise_distances(encodings):
	"""Euclidean distance between every pair of encodings, as a square matrix"""
	data = np.asarray(encodings, dtype=float)
	diff = data[:, None, :] - data[None, :, :]
	return np.linalg.norm(diff, axis=2)


def select_consistent(encodings, max_distance, min_count):
	"""
	Keep the encodings that agree with the rest of the capture.

	An encoding is kept when its median distance to the other encodings is at
	most max_distance. Returns (kept, spread), where spread is the largest
	distance between two kept encodings, or (None, spread_of_all) when fewer
	than min_count encodings agree.
	"""
	if len(encodings) == 0:
		return None, 0.0

	if len(encodings) == 1:
		return (list(encodings), 0.0) if min_count <= 1 else (None, 0.0)

	distances = pairwise_distances(encodings)
	count = len(encodings)

	kept = []
	for i in range(count):
		others = np.delete(distances[i], i)
		if np.median(others) <= max_distance:
			kept.append(i)

	if len(kept) < min_count:
		return None, float(distances.max())

	spread = float(distances[np.ix_(kept, kept)].max()) if len(kept) > 1 else 0.0
	return [encodings[i] for i in kept], spread
