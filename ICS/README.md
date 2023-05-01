# Modelling the Roaring River Flood Scenario

We model and experiment with the [Roaring River Flood (RRF) Scenario](https://www.usda.gov/sites/default/files/documents/ICS200.pdf), where the ICS framework is used to model the response to a complex disaster incident.
Our goal is to generate a hierarchy of resources that follows the determined span of control (relationship between supervisor and subordinate units) using a coalition formation technique.

Detailed information is available in our paper [Modelling a Chain of Command in the Incident
Command System using Sequential CFGs](https://emas.in.tu-clausthal.de/2022/papers/paper14.pdf).

## Setup

To setup your environment create a virtual environment (instructions [here](https://docs.python.org/3/tutorial/venv.html)), and inside your new environment run the following:

> pip install -r requirements.txt

## RRF Instances

We follow the specification of the RRF problem to generate instances. 
That is, the abstract hierarchy of units to which the personnel are allocated.
We generate randomly RRF instances and store them in YAML files.

To create a new instance, specify the instance in the file `rrf_create_instance.py`, and run: 

> python rrf_create_instance.py

The instances are stored in folder *instances*.

## Experiments

We consider two RRF instances containing 100 and 140 resources. In both instances we follow the hierarchy specified in the ICS training course for the RRF problem.

To compute a solution for the problem, we use a variation of the [UCT-Seq algorithm](https://link.springer.com/chapter/10.1007/978-3-031-21203-1_24) that considers coalition sizes in the [SEQVS framework](https://ieeexplore.ieee.org/document/9660127).


### Running an Experiment

You can run an experiment by configuring it in file `rrf_experiment.py` and run it with: 

> python rrf_experiment.py

An experiment records all FCSSs found and stores them in folder *FCSSs*.
To generate a chart, move the FCSSs found to the folder *results* (compute any aditional information you need), and execute the _chart\_[name]_ file.

Alternatevely, you can run a set of experiments and analyse them altogether using the file _rrf_set_of_experiments.py_.

> python rrf_set_of_experiments.py

**Note:** by generating new instances or running all experiments, you overwrite the results/instances in the respective folders.

## Contributors
- [Tabajara Krausburg](https://github.com/TabajaraKrausburg)
- [Jürgen Dix](https://www.in.tu-clausthal.de/index.php?id=cigmember_dix)
- [Rafael H. Bordini](https://inf.pucrs.br/r.bordini/Rafael_Bordini/Welcome.html)
