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

- Try to rerun your command with the `--reset-database` option for force bidsmreye to reindex your input dataset.
