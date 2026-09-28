from fastapi import APIRouter, Depends, HTTPException

from ..models import User
from ..schemas import ActionOut, SimulationOut, SimulationSummary, StepOut
from ..security import current_user
from ..services.content import get_simulation, load_simulations

router = APIRouter(prefix="/api/simulations", tags=["simulations"])


@router.get("", response_model=list[SimulationSummary])
def list_simulations(_: User = Depends(current_user)):
    return [
        SimulationSummary(
            id=s.id,
            title=s.title,
            area=s.area,
            description=s.description,
            step_count=len(s.steps),
        )
        for s in load_simulations().values()
    ]


@router.get("/{simulation_id}", response_model=SimulationOut)
def read_simulation(simulation_id: str, _: User = Depends(current_user)):
    simulation = get_simulation(simulation_id)
    if simulation is None:
        raise HTTPException(404, "Simulation not found")
    return SimulationOut(
        id=simulation.id,
        title=simulation.title,
        area=simulation.area,
        description=simulation.description,
        actions=[ActionOut(id=a.id, label=a.label) for a in simulation.actions],
        steps=[
            StepOut(id=s.id, instruction=s.instruction, hint=s.hint, points=s.points)
            for s in simulation.steps
        ],
    )
