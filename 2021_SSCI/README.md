# Computing Sequences of Coalition Structures

Here we provide the necessary steps to run our experiments with the algorithms that solve SEQVS instances. 
We evaluated three algorithms:

- **A brute-force algorithm**: it iteratively searches the complete search space.
- **SDP**: based on dynamic programming, it takes advantage of optimal subsequences to avoid computing again a subsequence. 
- **MC-Link**: proposed initially to solve SCFG instances and here extended to cope with valuation structures as well. Furthermore, we modify the first loop in the algorithm to make it feasible the searching on size transitions among levels. 

For more details, we refer to our publication in [SSCI 2021 (forthcoming)]().

## Setup

To setup your environment create a virtual environment (instructions [here](https://docs.python.org/3/tutorial/venv.html)), and inside your new environment run the following:

> pip install -r requirements.txt

## Running
You can run a single algorithm by choosing a file with the prefix *alg_*. To run one of the experiments, choose a file in which its name starts with the prefix *exp_*. The code to generate the charts are placed in folder *results*.   

## Instances

We generate randomly SEQVS instances and store them in tables. We chose this approach because we are experiment with exact algorithms, which run in a tractable time only for small instances. Therefore, storing the value of every coalition in a table is a feasible approach. 

The code that generates the instances is in **. To load a particular instance, use the code in **.
The information contained in each instance are:
- **coalition values**: a value for every coalition
- **pivotal agents**: what agents will play the role of pivotal agents
- **interaction graph**: the social relationship between the agents 

The instances used in our experiment are in folder *instances*.

## Contributors
- [Tabajara Krausburg](https://github.com/TabajaraKrausburg)
- [Jürgen Dix](https://www.in.tu-clausthal.de/index.php?id=cigmember_dix)
- [Rafael H. Bordini](https://inf.pucrs.br/r.bordini/Rafael_Bordini/Welcome.html)

