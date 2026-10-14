from __future__ import annotations
import json
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models import Experiment, Run

async def create_experiment(session: AsyncSession, name: str, description: str = "") -> Experiment:
    row = Experiment(id=uuid.uuid4().hex[:10], name=name.strip()[:120], description=description.strip())
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row

async def list_experiments(session: AsyncSession) -> list[Experiment]:
    return list((await session.execute(select(Experiment).order_by(Experiment.created_at.desc()))).scalars())

async def log_run(
    session: AsyncSession,
    experiment_id: str,
    name: str,
    params: dict | None = None,
    metrics: dict | None = None,
) -> Run:
    row = Run(
        id=uuid.uuid4().hex[:12],
        experiment_id=experiment_id,
        name=name.strip()[:120],
        params_json=json.dumps(params or {}),
        metrics_json=json.dumps(metrics or {}),
        status="finished",
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row

async def runs(session: AsyncSession, experiment_id: str) -> list[Run]:
    return list(
        (
            await session.execute(
                select(Run).where(Run.experiment_id == experiment_id).order_by(Run.created_at.desc())
            )
        ).scalars()
    )

async def compare(session: AsyncSession, run_ids: list[str]) -> dict:
    out = []
    for rid in run_ids:
        row = await session.get(Run, rid)
        if not row:
            continue
        out.append(
            {
                "id": row.id,
                "name": row.name,
                "params": json.loads(row.params_json or "{}"),
                "metrics": json.loads(row.metrics_json or "{}"),
            }
        )
    return {"runs": out}
