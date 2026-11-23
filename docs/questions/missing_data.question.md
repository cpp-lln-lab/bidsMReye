---
title: "bidsmreye can not find subject / task"
alt_titles:
  - bidsmreye process only one task in the bids_dir
  - No Subject Found in Layout
---

Check the following things:

- Have you passed the correct path to your BIDS dataset?

  This is one the most common errors,
  that can very easily happen when working with a containerized version of bidsmreye

- Is your dataset a valid preprocessed fMRI BIDS dataset?

  See [How I should structure my input data?](./faq.md#how-i-should-structure-my-input-data)

- Try to rerun your command with the `--reset_database` option to force bidsmreye to reindex your input dataset.

- If you are running several bidsmreye processes in parallel (for example one per participant on a cluster),
  make sure you are using a version of bidsmreye more recent than 0.6.0:
  older versions could fail to find subjects when started at the same time.
  See [How can I run bidsmreye in parallel?](./faq.md#how-can-i-run-bidsmreye-in-parallel)
