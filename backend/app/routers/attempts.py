import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Attempt, User
from ..schemas import AttemptIn, AttemptOut
from ..security import current_user
from ..services.content import get_simulation
from ..services.scoring import evaluate

router = APIRouter(prefix="/api/attempts", tags=["attempts"])


def to_out(attempt: Attempt) -> AttemptOut:
    return AttemptOut(
        id=attempt.id,
        simulation_id=attempt.simulation_id,
        score=attempt.score,
        max_score=attempt.max_score,
        duration_seconds=attempt.duration_seconds,
        errors=attempt.detail_dict().get("errors", []),
        created_at=attempt.created_at,
    )


@router.post("", response_model=AttemptOut, status_code=201)
def submit_attempt(payload: AttemptIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    simulation = get_simulation(payload.simulation_id)
    if simulation is None:
        raise HTTPException(404, "Simulation not found")
    result = evaluate([s.model_dump() for s in simulation.steps], payload.actions)
    attempt = Attempt(
        user_id=user.id,
        simulation_id=simulation.id,
        score=result["score"],
        max_score=result["max_score"],
        duration_seconds=payload.duration_seconds,
        detail=json.dumps({"errors": result["errors"], "actions": payload.actions}),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return to_out(attempt)


@router.get("", response_model=list[AttemptOut])
def list_attempts(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(
        select(Attempt).where(Attempt.user_id == user.id).order_by(Attempt.id.desc()).limit(50)
    ).all()
    return [to_out(a) for a in rows]
