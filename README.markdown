Deft: Easy Distributed Feature Tracking
=======================================

Deft is a simple distributed feature tracker (aka issue tracker, task tracker) designed to work with a distributed version control system such as Git.

Goals / Principles
------------------

* store tracked features in VCS, not another tool
* absolute prioritisation of all features (per status)
* store features per-branch
* store the feature database in plain-text files that play well with VCS and diff/merge tools
* don't re-implement functionality that is already in the VCS

Postponed for now 
-----------------

* Integrate Deft with VCS tools themselves
* Scaling (efficient data structure for indexing features by priority to handle large feature databases)

"Make it work. Make it clean. Make it fast." -- Ward Cunningham

