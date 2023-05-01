# Sequential Characteristic-Function Games

In this repository, we maintain the main work related to the Sequential Characteristic-Function Games (SCFG). In this setting, we investigate the interdependence of Characteristic-Function Games (CFG), which are received as input in a total ordered sequence. The solution for such a game is an ordered sequence, according to the input, of coalition structures. 

## Related Papers
- **2023** The Incident Command System: we investigate how to model the Incident Command System (ICS) framework using the coalition formation techniques we proposed. Look the [*ICS folder*](https://github.com/smart-pucrs/SCFG/tree/main/ICS) for additional detail.
- **2021** [Computing Sequences of Coalition Structures](https://ieeexplore.ieee.org/document/9660127): we investigate constraints applied to individual games in a SCFG. We propose the integration of SCFG and [Valuation Structures](https://www.sciencedirect.com/science/article/pii/S0004370217300516) (VS), resulting in a framework called **Sequential CFGs induced by VSs** (SEQVS). In addition, we propose an **exact** algorithm based on dynamic programming that solves both SEQVS and SCFG instances (given the proper modifications). This algorithm is named SDP. For the experiments, we adapt [MC-Link](https://dl.acm.org/doi/10.5555/3463952.3464039) to cope with VSs. All the experiments are available in folder [*2021_SSCI*](https://github.com/smart-pucrs/SCFG/tree/main/2021_SSCI).
- **2021** [Feasible Coalition Sequences](https://dl.acm.org/doi/10.5555/3463952.3464039): We formally propose the framework for sequential games. We theoretically investigate how this setting relates to other coalition formation problems. Further, we propose a heuristic based algorithm (inspired by [C-Link](https://www.sciencedirect.com/science/article/pii/S0952197616302536)) and experiment with it (watch our presentation [here](https://slideslive.com/38954936/feasible-coalition-sequences)). All the experiments are available in folder [*2021_AAMAS*](https://github.com/smart-pucrs/SCFG/tree/main/2021_AAMAS).
- **2020** [Hierarchical Coalition Formation in Multi-agent Systems](https://link.springer.com/chapter/10.1007%2F978-3-030-53829-3_23): In this paper we propose our first idea to apply coalition formation in disaster response operations.

## Main Contributors
- [Tabajara Krausburg](https://github.com/TabajaraKrausburg)
- [Jürgen Dix](https://www.in.tu-clausthal.de/index.php?id=cigmember_dix)
- [Rafael H. Bordini](https://inf.pucrs.br/r.bordini/Rafael_Bordini/Welcome.html)
