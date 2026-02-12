#!/usr/bin/env python3
#    Copyright (c) 2020 Merck Sharp & Dohme Corp. a subsidiary of Merck & Co., Inc., Kenilworth, NJ, USA.
#
#    This file is part of the Mutation Maker, An Open Source Oligo Design Software For Mutagenesis and De Novo Gene Synthesis Experiments.
#
#    Mutation Maker is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import io
import os
import traceback
import binascii
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from celery import Celery

celery_broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery_result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379"
)
CELERY = Celery("tasks", broker=celery_broker_url, backend=celery_result_backend)

app = FastAPI(title="Mutation Maker API", version="1.0.0")


class TaskBody(BaseModel):
    data: Any = {}


def get_urls(task_id: str, export: str) -> Dict[str, str]:
    return {
        "check_url": f"/v1/check/{task_id}",
        "forget_url": f"/v1/forget/{task_id}",
        "cancel_url": f"/v1/cancel/{task_id}",
        "result_url": f"/v1/result/{task_id}",
        "export_url": f"/v1/{export}/{task_id}.xlsx",
    }


@app.post("/v1/ssm")
def find_ssm_primers(body: TaskBody) -> Dict[str, Any]:
    return start_celery_task(body.data, CELERY, "tasks.ssm", "export_ssm")


@app.post("/v1/qclm")
def find_qclm_primers(body: TaskBody) -> Dict[str, Any]:
    return start_celery_task(body.data, CELERY, "tasks.qclm", "export_qclm")


@app.post("/v1/pas")
def find_pas_primers(body: TaskBody) -> Dict[str, Any]:
    return start_celery_task(body.data, CELERY, "tasks.pas", "export_pas")


@app.get("/v1/get_species")
def export_species_table_get() -> Any:
    task_name = "tasks.species_table"
    try:
        task = CELERY.send_task(task_name, args=[{}])
        final_res = task.wait(timeout=None, propagate=True, interval=0.5)
        return final_res
    except Exception as e:
        raise HTTPException(status_code=400, detail=traceback.format_exc())


@app.post("/v1/species_table")
def export_species_table_post(body: TaskBody) -> Dict[str, Any]:
    return start_celery_task(
        body.data, CELERY, "tasks.species_table", "export_species_table"
    )


def start_celery_task(
    body: Any, celery_app: Celery, task_name: str, export_name: str
) -> Dict[str, Any]:
    try:
        task = celery_app.send_task(task_name, args=[body])
        return get_urls(task.id, export_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=traceback.format_exc())


@app.get("/v1/check/{task_id}")
def check_task(task_id: str) -> str:
    return CELERY.AsyncResult(task_id).state


@app.get("/v1/cancel/{task_id}")
def cancel_task(task_id: str) -> None:
    CELERY.AsyncResult(task_id).revoke(terminate=True)


@app.get("/v1/forget/{task_id}")
def forget_task(task_id: str) -> None:
    CELERY.AsyncResult(task_id).forget()


@app.get("/v1/result/{task_id}")
def check_task_result(task_id: str) -> Any:
    async_result = CELERY.AsyncResult(task_id)
    if async_result.successful():
        return async_result.result
    if async_result.failed():
        return async_result.traceback


@app.get("/v1/export_qclm/{task_id}.xlsx")
def export_qclm(task_id: str) -> StreamingResponse:
    task = CELERY.send_task("tasks.export_qclm", args=[task_id])
    result = task.get()
    if result is not None:
        file_like = io.BytesIO(result.encode())
        return StreamingResponse(
            file_like,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={task_id}.xlsx"},
        )
    raise HTTPException(status_code=404, detail="Result not found")


@app.get("/v1/export_ssm/{task_id}.xlsx")
def export_ssm(task_id: str) -> StreamingResponse:
    task = CELERY.send_task("tasks.export_ssm", args=[task_id])
    result = task.get()
    if result is not None:
        file_like = io.BytesIO(binascii.a2b_base64(result))
        return StreamingResponse(
            file_like,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={task_id}.xlsx"},
        )
    raise HTTPException(status_code=404, detail="Result not found")


@app.get("/v1/export_species_table/{task_id}.xlsx")
def export_species_table(task_id: str) -> StreamingResponse:
    task = CELERY.send_task("tasks.export_species_table", args=[task_id])
    result = task.get()
    if result is not None:
        file_like = io.BytesIO(binascii.a2b_base64(result))
        return StreamingResponse(
            file_like,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={task_id}.xlsx"},
        )
    raise HTTPException(status_code=404, detail="Result not found")


if __name__ == "__main__":
    import uvicorn

    print("Mutation Maker version: 1.0.0")
    uvicorn.run(app, host="0.0.0.0", port=8000)
