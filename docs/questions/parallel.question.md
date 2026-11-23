---
title: "How can I run bidsmreye in parallel?"
alt_titles:
  - parallelize
  - run on a cluster / HPC
  - one job per participant
---

You can run one bidsmreye process per participant
(for example one job per participant on a cluster)
by passing a single label to `--participant_label` in each job.

bidsmreye indexes the input dataset with pybids
and saves this index in a database in its working directory,
so later runs do not need to reindex the dataset.

Use the same output directory (or the same `--work_dir`) for all jobs
so they all share the same database.
By default the working directory is `<output_dir>/work`.

The database is saved in a way that is safe for processes started at the same time:
if several jobs start before the database exists,
each of them indexes the dataset
and only one copy of the database is kept.

Do not use `--reset_database` in jobs that run in parallel
as it would make each job reindex the input dataset.
If you need to reindex the input dataset,
run bidsmreye once with `--reset_database` before starting the parallel jobs.
