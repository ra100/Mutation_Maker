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

import * as React from 'react'
import { dataToQCLMFormData, formDataToQclmRequest } from 'services/api'
import WorkflowScene, { WorkflowSceneExternalProps } from 'shared/components/WorkflowScene'
import { QCLMFormData } from 'shared/lib/FormData'
import { responseToQCLMResultData } from 'shared/lib/ResultData'
import routes from 'shared/routes'
import { Workflow } from 'shared/workflow'
import QCLMForm from './components/QCLMForm'
import QCLMResult from './components/QCLMResult'

const demoData: Partial<QCLMFormData> = {
  fivePrimeFlankingSequence: '',
  goiSequence: '',
  mutations: '',
};

type QCLMOuterProps = WorkflowSceneExternalProps

const QCLM: React.SFC<QCLMOuterProps> = ({
  submitRequest,
  requestJobResult,
  jobId,
  jobData,
  pollInterval,
}) => (
  <WorkflowScene
    jobId={jobId}
    jobData={jobData}
    defaultFormData={demoData}
    getRoute={routes.qclm}
    // tslint:disable-next-line:jsx-no-lambda
    requestJobResult={(id: string) => requestJobResult(id, pollInterval)}
    responseToFormData={dataToQCLMFormData}
    responseToResultData={responseToQCLMResultData}
    // tslint:disable-next-line:jsx-no-lambda
    submitRequest={(formData: QCLMFormData) =>
      submitRequest(Workflow.qclm, formDataToQclmRequest, formData)
    }
    // tslint:disable-next-line:jsx-no-lambda
    InputForm={({ disabled, formData, onSubmit }) => (
      <QCLMForm disabled={disabled} data={formData} onSubmit={onSubmit} />
    )}
    // tslint:disable-next-line:jsx-no-lambda
    ResultsView={({ resultData, formData }) =>
      <QCLMResult
        resultData={resultData}
        jobId={jobId}
        formData={formData}
      />}
  />
);

export default QCLM
