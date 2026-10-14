import pytest

@pytest.mark.asyncio
async def test_compare_runs(client):
    e = await client.post("/api/experiments", json={"name": "resnet-finetune"})
    eid = e.json()["id"]
    r1 = await client.post(f"/api/experiments/{eid}/runs", json={"name": "a", "params": {"lr": 0.01}, "metrics": {"acc": 0.9}})
    r2 = await client.post(f"/api/experiments/{eid}/runs", json={"name": "b", "params": {"lr": 0.02}, "metrics": {"acc": 0.92}})
    cmp = await client.post("/api/compare", json={"run_ids": [r1.json()["id"], r2.json()["id"]]})
    assert len(cmp.json()["runs"]) == 2
