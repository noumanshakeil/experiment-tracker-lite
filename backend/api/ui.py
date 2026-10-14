from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
import json
from backend.db import get_db
from backend.services import experiments as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, experiment_id: str | None = None, db: AsyncSession = Depends(get_db)):
    exps = await svc.list_experiments(db)
    eid = experiment_id or (exps[0].id if exps else None)
    runs = await svc.runs(db, eid) if eid else []
    compare = None
    if len(runs) >= 2:
        compare = await svc.compare(db, [runs[0].id, runs[1].id])
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Experiment Tracker Lite",
            "experiments": exps,
            "experiment_id": eid,
            "runs": runs,
            "compare": compare,
        },
    )

@router.post("/ui/experiments")
async def ui_exp(name: str = Form(...), description: str = Form(""), db: AsyncSession = Depends(get_db)):
    e = await svc.create_experiment(db, name, description)
    return RedirectResponse(f"/?experiment_id={e.id}", status_code=303)

@router.post("/ui/runs")
async def ui_run(
    experiment_id: str = Form(...),
    name: str = Form(...),
    lr: float = Form(0.01),
    acc: float = Form(0.9),
    db: AsyncSession = Depends(get_db),
):
    await svc.log_run(db, experiment_id, name, {"lr": lr}, {"accuracy": acc})
    return RedirectResponse(f"/?experiment_id={experiment_id}", status_code=303)
