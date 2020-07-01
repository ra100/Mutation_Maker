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

import { Alert, Col, Row } from 'antd'
import * as R from 'ramda'
import * as React from 'react'
import { RouteComponentProps, withRouter } from 'react-router'
import { compose } from 'recompose'
import withCurrentStepState, {
  WithCurrentStepState,
  WorkflowStep,
} from 'shared/components/withCurrentStepState'
import WorkflowSteps from 'shared/components/WorkflowSteps'
import { JobDescription, JobStatus } from 'shared/lib/Api'
import withErrorStatusState, { WithErrorStatusState } from './withErrorStatusState'
import { hasDataLoaded, Job, WithJobStore } from './withJobStore'

export type WorkflowSceneExternalProps = {
  jobId?: string
  jobData?: Job
  pollInterval: number
} & Pick<WithJobStore, 'submitRequest' | 'requestJobResult'>

type WorkflowSceneOuterProps<FormData, ResultData> = Pick<
  WorkflowSceneExternalProps,
  'jobId' | 'jobData'
> & {
  defaultFormData: Partial<FormData>
  getRoute(jobId?: string): string

  requestJobResult(id: string): Promise<void>

  responseToFormData(data: any): FormData
  responseToResultData(data: any): ResultData

  submitRequest(formData: FormData): Promise<JobDescription>

  InputForm(props: {
    disabled: boolean
    formData: Partial<FormData>
    onSubmit(formData: Partial<FormData>): void
  }): JSX.Element
  ResultsView(props: { resultData: ResultData; formData: Partial<FormData> }): JSX.Element
}

type WorkflowSceneInnerProps<FormData, ResultData> = WorkflowSceneOuterProps<FormData, ResultData> &
  RouteComponentProps<any> &
  WithCurrentStepState &
  WithErrorStatusState

class WorkflowScene<FormData, ResultData> extends React.PureComponent<
  WorkflowSceneInnerProps<FormData, ResultData>
> {
  setCurrentStepOnProps = () => {
    const { currentStep, setCurrentStep, jobId, jobData } = this.props;

    if (R.isNil(currentStep)) {
      if (!R.isNil(jobId)) {
        if (jobData && jobData.status === JobStatus.pending) {
          setCurrentStep(WorkflowStep.InProgress)
        } else {
          setCurrentStep(WorkflowStep.Results)
        }
      } else {
        setCurrentStep(WorkflowStep.InputParameters)
      }
    }
  };

  requestJobResultWithErrorHandler = (jobId: string) => {
    const { requestJobResult, setError } = this.props;

    return requestJobResult(jobId).catch(err => {
      setError('Error occured while requesting job result. Please contact support.');
      // tslint:disable-next-line:no-console
      console.error(err)
    })
  };

  componentDidMount() {
    const { jobId, jobData } = this.props;

    this.setCurrentStepOnProps();

    if (!R.isNil(jobId) && !hasDataLoaded(jobData)) {
      // tslint:disable-next-line:no-floating-promises
      this.requestJobResultWithErrorHandler(jobId)
    }
  }

  componentDidUpdate(prevProps: WorkflowSceneInnerProps<FormData, ResultData>) {
    const { jobId, jobData } = this.props;

    this.setCurrentStepOnProps();

    if (prevProps.jobId !== jobId && !R.isNil(jobId) && !hasDataLoaded(jobData)) {
      // tslint:disable-next-line:no-floating-promises
      this.requestJobResultWithErrorHandler(jobId)
    }
  }

  onSubmit = (formData: FormData) => {
    const { setError, history, getRoute, submitRequest } = this.props;
    window.scrollTo(0, 0);

    return submitRequest(formData)
      .then(jobDescription => {
        history.push(getRoute(jobDescription.id))
      })
      .catch(err => {
        setError('Error occured during WorkflowScene workflow. Please contact support.');
        // tslint:disable-next-line:no-console
        console.error(err, `Response from server: ${err.response && err.response.data}`)
      })
  };

  getFormData = () => {
    const { responseToFormData, jobData } = this.props;
    const formData = jobData ? jobData.formData : undefined;
    const responseData = jobData ? jobData.responseData : undefined;

    if (formData) {
      return formData
    } else if (responseData) {
      return responseToFormData(responseData)
    }

    return undefined
  };

  getResultData = () => {
    const { responseToResultData, jobData } = this.props;
    const responseData = jobData ? jobData.responseData : undefined;

    return responseData ? responseToResultData(responseData) : undefined
  };

  render() {
    const {
      defaultFormData,
      jobId,
      jobData,
      currentStep,
      setCurrentStep,
      error,
      InputForm,
      ResultsView,
    } = this.props;

    const jobStatus = jobData ? jobData.status : undefined;
    const jobError = jobData ? jobData.error : undefined;

    const formData = jobStatus !== JobStatus.failure ? this.getFormData() : undefined;
    const resultData = jobStatus !== JobStatus.failure ? this.getResultData() : undefined;

    const hasId = !R.isNil(jobId);
    const loading = hasId && !hasDataLoaded(jobData);
    const finished = hasId && !R.isNil(resultData);
    const failure = error || jobError;

    const displayedFormData = hasId ? (formData as Partial<FormData>) : defaultFormData;

    const makeOnWorkflowStepsClick = (step: WorkflowStep) =>
      hasId ? () => setCurrentStep(step) : undefined;

    return (
      <>
        <WorkflowSteps
          loading={loading}
          finished={finished}
          currentStep={currentStep}
          failure={failure}
          makeOnClick={makeOnWorkflowStepsClick}
        />
        {error && (
          <Alert
            type="error"
            showIcon
            message="Submit Error"
            description={`Error occurred while submitting job: \n${error}`}
          />
        )}
        {jobError && (
          <Alert
            type="error"
            showIcon
            message="Job Error"
            description={`Error occurred while processing job: \n${jobError}`}
          />
        )}
        {currentStep === WorkflowStep.InputParameters &&
          displayedFormData && (
            <Row>
              <Col
                xs={{ span: 18, offset: 3 }}
                lg={{ span: 16, offset: 4 }}
                xxl={{ span: 12, offset: 6 }}>
                <InputForm onSubmit={this.onSubmit} disabled={hasId} formData={displayedFormData} />
              </Col>
            </Row>
          )}
        {currentStep === WorkflowStep.InProgress && (
          <div className="InProgress">Computation is in progress. Please wait.</div>
        )}
        {currentStep === WorkflowStep.Results &&
          resultData && <ResultsView resultData={resultData} formData={displayedFormData} />}
      </>
    )
  }
}

export default <FormData, ResultData>(props: WorkflowSceneOuterProps<FormData, ResultData>) => {
  const EnhancedWorkflowScene = compose<
    WorkflowSceneInnerProps<FormData, ResultData>,
    WorkflowSceneOuterProps<FormData, ResultData>
  >(
    withRouter,
    withErrorStatusState,
    withCurrentStepState,
  )(WorkflowScene);

  return <EnhancedWorkflowScene {...props} />
}
