/*   Copyright (c) 2020 Merck Sharp & Dohme Corp. a subsidiary of Merck & Co., Inc., Kenilworth, NJ, USA.
 *
 *   This file is part of the Mutation Maker, An Open Source Oligo Design Software For Mutagenesis and De Novo Gene Synthesis Experiments.
 *
 *   Mutation Maker is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

import * as R from 'ramda'
import { compose, withHandlers, withStateHandlers } from 'recompose'

import { fetchJobResultData, fetchJobStatus, pollWhilePending, submitRequest } from 'services/api'
import { JobDescription, JobStatus } from 'shared/lib/Api'
import { Workflow } from '../workflow'

export type Job = {
  formData?: any
  responseData?: any
  status?: JobStatus
  polling?: boolean
  error?: any
}

type WithJobState = {
  jobState: {
    [id: string]: Job
  }
}

type WithJobStateUpdaters = {
  setJob(id: string, job: Job): WithJobState
  updateJob(id: string, jobUpdate: Partial<Job>): WithJobState
}

const withJobState = withStateHandlers<WithJobState, WithJobStateUpdaters>(
  { jobState: {} },
  {
    setJob: ({ jobState }) => (id: string, job: Job) => ({
      jobState: {
        ...jobState,
        [id]: job,
      },
    }),
    updateJob: ({ jobState }) => (id: string, job: Job) => ({
      jobState: {
        ...jobState,
        [id]: {
          ...jobState[id],
          ...job,
        },
      },
    }),
  },
)

type WithJobGetter = {
  getJob(id: string): Job | undefined
}

const withJobGetter = withHandlers<WithJobState, WithJobGetter>({
  getJob: ({ jobState }) => (id: string) => jobState[id],
})

type WithJobHandlers = {
  submitRequest(
    workflow: Workflow,
    formDataToRequestData: (formData: any) => any,
    formData: any,
  ): Promise<JobDescription>
  requestJobResult(id: string, pollInterval: number): Promise<void>
}

const withJobHandlers = withHandlers<WithJobGetter & WithJobStateUpdaters, WithJobHandlers>({
  submitRequest: ({ setJob }) => (
    workflow: Workflow,
    formDataToRequestData: (formData: any) => any,
    formData,
  ) => {
    return submitRequest(workflow.toString(), formDataToRequestData(formData)).then(
      jobDescription => {
        setJob(jobDescription.id, { formData })

        return jobDescription
      },
    )
  },
  requestJobResult: ({ getJob, updateJob }) => (id: string, pollInterval: number) => {
    const job = getJob(id)
    const isPolling = job ? job.polling : false

    if (isPolling || hasDataLoaded(job)) {
      return Promise.resolve()
    } else {
      updateJob(id, { polling: true })

      return fetchJobStatus(id)
        .then(status => {
          updateJob(id, { status, polling: true })

          return status === JobStatus.pending
            ? pollWhilePending(id, pollInterval)
            : Promise.resolve(status)
        })
        .then(status =>
          fetchJobResultData(id).then(responseData => {
            if (status === JobStatus.failure) {
              updateJob(id, { status, error: responseData, polling: false })
            } else {
              updateJob(id, { status, responseData, polling: false })
            }
          }),
        )
        .catch(err => {
          updateJob(id, { error: err })
        })
    }
  },
})

export type WithJobStore = WithJobState & WithJobGetter & WithJobHandlers

export default <P>(component: React.ComponentType<P & WithJobStore>) =>
  compose<P & WithJobStore, P>(
    withJobState,
    withJobGetter,
    withJobHandlers,
  )(component)

export const hasDataLoaded = (job: Job | undefined) =>
  !R.isNil(job) &&
  job.status !== JobStatus.pending &&
  (!R.isNil(job.responseData) || !R.isNil(job.error))
