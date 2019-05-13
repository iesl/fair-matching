# fair-matching
In conference peer review, a large number of papers must be matched to a 
large number of reviewers automatically. Typically, each paper must be reviewed 
by _k_ reviewers and each reviewer must review at least _l_ papers and no more 
than _u_ papers. Each reviewer-paper pair has an associated affinity; the higher
the affinity, the better the match. Unfortunately, in most deployed paper 
matching systems, some papers are matched to a group of reviewers all of whom 
have low affinity with the paper.  This is occurs for the sake of maximizing the
global affinity among all papers.

In our recent work, we propose two algorithms, _FairIR_ and _FairFlow_ for more 
fairly assigning reviewers to papers.  In particular, both algorithms attempt to
guarantee that the sum of affinities among the reviewers assigned to all papers 
exceeds a problem specific thresholds. This repository includes our 
implementation of both algorithms, plus some of the data needed to reproduce our
experimental results. More technical details appear in our forthcoming paper.

###Dependencies

Both the algorithms are implemented in the python (3.6) programming language.

Our code is built on top of two libraries. The first is 
[gurobi](http://www.gurobi.com/), a powerful linear programming library. Free 
academic licenses are available.

The second library is [or-tools](https://developers.google.com/optimization/),
another powerful library that includes many optimization algorithms. In 
particular, we make use of the min-cost-flow implementation. For installation
use pip:

`pip install py3-ortools`

###Experiments

To begin, change directory to the top level directory (under fair-matching).
Then, initialize the project with

`source bin/setup.sh`

All experiments are intended to be run from the same top-level directory.  Each
can be run run similarly. To run _FairIR_ on the MIDL data, run

`sh bin/exp/fairir.sh config/midl/fairir.json`

To run the experiment with lower bounds, run

`sh bin/exp/fairir.sh config/midl/fairir-lb.json`

The results of the run are stored in timestamped directory inside of the
`exp_out` directory.  To create boxplots of the paper scores as appear in our
paper, find the timestamped directory and run, e.g.,

`sh bin/plot/boxplot.sh exp_out/midl/fairir/2019-05-13-14-51-51/`