from dataclasses import dataclass, field
from edcmap import Map

@dataclass
class Maps:
    soi: Map
    selector: Map
    durations: list[Map] = field(default_factory=list)