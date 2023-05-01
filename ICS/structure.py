from dataclasses import InitVar, dataclass, field

alg = None

@dataclass
class Space:
    data: InitVar
    candidates: set = field(default_factory=set)
    gen: object = field(init=False)

    def empty(self):
        return  self.gen==None
    
    def next_CS(self):
        return next(self.gen)
  
@dataclass
class Node:
    data: InitVar
    parent: object = field(default_factory=lambda:None)
    CS: frozenset = field(default_factory=None)
    v: float = 0 
    cumv: float = 0
    level: int = 0
    N: int = 0
    length: int = 0
    expanded: bool = False
    terminal: bool = False
    last = 0
    done: list = field(default_factory=list)
    space: Space = field(init=False)
    frontier: list = field(default_factory=list)

    def __post_init__(self, data):
        self.space = Space(data=data)
    
@dataclass
class Alg:
    A: list = field(default_factory=list)
    H: list = field(default_factory=list)
    Pi: list = field(default_factory=list)
    R: object = field(default_factory=None)
    h: int = 0
    degree: int = 5
    depth: int = 3 
    exp_factor: float = 0.7 # (0,1]
    def __post_init__(self):
        self.h = len(self.H)
