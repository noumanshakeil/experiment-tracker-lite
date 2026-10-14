from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import experiments as svc

class ExperimentIn(BaseModel):
    name: str = Field(min_length=2)
    description: str = ""

class RunIn(BaseModel):
    name: str = Field(min_length=1)
    params: dict = Field(default_factory=dict)
    metrics: dict = Field(default_factory=dict)

class CompareIn(BaseModel):
    run_ids: list[str] = Field(min_length=1)

router = APIRouter()

@router.get("/experiments")
async def experiments(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_experiments(db)
    return {"experiments": [{"id": e.id, "name": e.name, "description": e.description[:200]} for e in rows]}

@router.post("/experiments")
async def create_experiment(payload: ExperimentIn, db: AsyncSession = Depends(get_db)):
    e = await svc.create_experiment(db, payload.name, payload.description)
    return {"id": e.id}

@router.post("/experiments/{experiment_id}/runs")
async def create_run(experiment_id: str, payload: RunIn, db: AsyncSession = Depends(get_db)):
    r = await svc.log_run(db, experiment_id, payload.name, payload.params, payload.metrics)
    return {"id": r.id}

@router.get("/experiments/{experiment_id}/runs")
async def list_runs(experiment_id: str, db: AsyncSession = Depends(get_db)):
    rows = await svc.runs(db, experiment_id)
    import json

    return {
        "runs": [
            {
                "id": r.id,
                "name": r.name,
                "params": json.loads(r.params_json or "{}"),
                "metrics": json.loads(r.metrics_json or "{}"),
            }
            for r in rows
        ]
    }

@router.post("/compare")
async def compare(payload: CompareIn, db: AsyncSession = Depends(get_db)):
    return await svc.compare(db, payload.run_ids)
