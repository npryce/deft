Deft: Easy Distributed Feature Tracking
=======================================

Deft is a simple distributed feature tracker (aka issue tracker, task tracker) designed to work with a distributed version control system such as Git.

Goals / Principles
------------------

* store tracked features in VCS, not another tool
* all features have status (e.g. new, in-development, ready-for-testing, ready-for-deployment)
* absolute prioritisation of features that have the same status
* store feature database alongside the code
* store the feature database in plain-text files that play well with VCS and diff/merge tools
* don't re-implement functionality that is already in the VCS

Future Plans
------------

When the tool does what I want for small projects, I plan to add the following features: 

* Integrate Deft with specific VCS tools more seamlessly
* Visualisation of history, such as Cumulative Flow Diagrams
* Analysis of history, such as velocity estimation
* Scaling (efficient data structure for indexing features by priority to handle large feature databases)


