import json
from functools import lru_cache

from pydantic import BaseModel

from ..config import CONTENT_DIR


class Action(BaseModel):
    id: str
    label: str


class Step(BaseModel):
    id: str
    instruction: str
    action: str
    points: int = 10
    hint: str = ""


class Simulation(BaseModel):
    id: str
    title: str
    area: str
    description: str = ""
    actions: list[Action]
    steps: list[Step]

    def validate_references(self):
        known = {a.id for a in self.actions}
        for step in self.steps:
            if step.action not in known:
                raise ValueError(f"{self.id}: step {step.id} uses unknown action {step.action}")


@lru_cache
def load_simulations() -> dict[str, Simulation]:
    simulations = {}
    for path in sorted(CONTENT_DIR.glob("*.json")):
        simulation = Simulation.model_validate(json.loads(path.read_text(encoding="utf-8")))
        simulation.validate_references()
        simulations[simulation.id] = simulation
    return simulations


def get_simulation(simulation_id: str) -> Simulation | None:
    return load_simulations().get(simulation_id)
