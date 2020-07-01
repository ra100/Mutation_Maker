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
import sys
import traceback
import binascii

import hug
from celery import Celery
from falcon import HTTP_400


def init_api():
    api = hug.API(sys.modules[__name__])
    celery_broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379'),
    celery_result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')
    celery = Celery('tasks', broker=celery_broker_url, backend=celery_result_backend)
    api.context["celery"] = celery
    return api


@hug.directive()
def celery(api, **kwargs):
    return api.context["celery"]


@hug.post('/ssm', versions=1)
def find_ssm_primers(body, response, hug_celery):
    """
    Return task if type Site Saturation Mutagenesis (SSM)
    """
    return start_celery_task(body, response, hug_celery, 'tasks.ssm', "export_ssm")


@hug.post('/qclm', versions=1)
def find_qclm_primers(body, response, hug_celery):
    """
    Return task if type QuikChange Lightning Multi Site-Directed Mutagenesis (QCLM)
    """
    return start_celery_task(body, response, hug_celery, 'tasks.qclm', "export_qclm")


@hug.post('/pas', versions=1)
def find_pas_primers(body, response, hug_celery):
    """
    Return task if type PCR-based Accurate Synthesis task (PAS)
    """
    return start_celery_task(body, response, hug_celery, 'tasks.pas', "export_pas")


@hug.get('/get_species', versions=1)
def export_species_table(body, response, hug_celery):
    """
    Return list of all species in synchronous get call
    """
    task_name = 'tasks.species_table'

    try:
        start_celery_task(body, response, hug_celery, task_name, "")
        task = hug_celery.send_task(task_name, args=[body])
        final_res = task.wait(timeout=None, propagate=True, interval=0.5)
        return final_res
    except Exception as e:
        response.status = HTTP_400
        return traceback.format_exc()


@hug.post('/species_table', versions=1)
def export_species_table(body, response, hug_celery):
    """
    Return list of all species with asynchronous call
    """
    return start_celery_task(body, response, hug_celery, 'tasks.species_table', "export_species_table")


def start_celery_task(body, response, hug_celery, task_name, export_name):
    try:
        task = hug_celery.send_task(task_name, args=[body])
        return get_urls(task.id, export_name)
    except Exception as e:
        response.status = HTTP_400
        return traceback.format_exc()


def get_urls(task_id, export):
    return {
        "check_url": f"/v1/check/{task_id}",
        "forget_url": f"/v1/forget/{task_id}",
        "cancel_url": f"/v1/cancel/{task_id}",
        "result_url": f"/v1/result/{task_id}",
        "export_url": f"/v1/{export}/{task_id}.xlsx",
    }


@hug.get('/check/{task_id}', versions=1)
def check_task(task_id, hug_celery):
    return hug_celery.AsyncResult(task_id).state


@hug.get('/cancel/{task_id}', versions=1)
def forget_task(task_id, hug_celery):
    hug_celery.AsyncResult(task_id).revoke(terminate=True)


@hug.get('/forget/{task_id}', versions=1)
def forget_task(task_id, hug_celery):
    hug_celery.AsyncResult(task_id).forget()


@hug.get('/result/{task_id}', versions=1)
def check_task(task_id, hug_celery):
    async_result = hug_celery.AsyncResult(task_id)
    if async_result.successful():
        return async_result.result
    if async_result.failed():
        return async_result.traceback


@hug.get('/export_qclm/{task_id}.xlsx', versions=1, output=hug.output_format.file)
def export_task(task_id, hug_celery):
    task = hug_celery.send_task("tasks.export_qclm", args=[task_id])
    result = task.get()
    if result is not None:
        file_like = io.BytesIO(result.encode())
        return file_like


@hug.get('/export_ssm/{task_id}.xlsx', versions=1, output=hug.output_format.file)
def export_task(task_id, hug_celery):
    task = hug_celery.send_task("tasks.export_ssm", args=[task_id])
    result = task.get()
    if result is not None:
        file_like = io.BytesIO(binascii.a2b_base64(result))
        return file_like


@hug.get('/export_species_table/{task_id}.xlsx', versions=1, output=hug.output_format.file)
def export_task(task_id, hug_celery):
    task = hug_celery.send_task("tasks.export_species_table", args=[task_id])
    result = task.get()
    if result is not None:
        file_like = io.BytesIO(binascii.a2b_base64(result))
        return file_like