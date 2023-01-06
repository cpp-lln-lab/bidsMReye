---
title: Is the "prepare" only suitable for the datasets that have eye-tracking info?
alt_titles:
  - If want to only guess the eye position, should I use "generalize"?
---

No the `prepare` action is necessary for all datasets,
whether they have eye-tracking info or not.

This action:

- registers the data to MNI if this is not the case already
- registers the data the the deepmreye template
- extracts data from the eyes mask

In future versions of bidsmreye, this action should also be able to combine
the extracted data with the eye gaze position coming
from preprocessed eyetracking data.
