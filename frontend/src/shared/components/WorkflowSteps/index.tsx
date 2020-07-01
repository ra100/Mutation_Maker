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

import {
  Icon,
  Steps
} from 'antd'
import * as React from 'react'
import { WorkflowStep } from '../withCurrentStepState'

type WorkflowStepsProps = {
  loading: boolean
  finished: boolean
  failure: boolean
  currentStep: WorkflowStep | undefined
  makeOnClick(step: WorkflowStep): (() => void) | undefined
}

const WorkflowSteps: React.SFC<WorkflowStepsProps> = ({
  loading,
  finished,
  failure,
  currentStep,
  makeOnClick,
}) => {
  const getIcon = (step: WorkflowStep) => {
    if (finished) {
      return <Icon type="check" />
    }

    return currentStep === step && loading && <Icon type="loading" />
  };

  const stepStyle = {
    marginBottom: 20,
    marginTop: 10,
    paddingLeft: 10,
    paddingRight: 10,
  };

  const clickableStyle = {
    cursor: 'pointer',
  };

  const onInputClick = makeOnClick(WorkflowStep.InputParameters);
  const onResultsClick = makeOnClick(WorkflowStep.Results);

  return (
      <Steps current={currentStep} status={failure ? 'error' : undefined}
             style={stepStyle}
      >
        <Steps.Step
          title="Input Parameters"
          icon={getIcon(WorkflowStep.InputParameters)}
          style={onInputClick && clickableStyle}
          onClick={currentStep !== WorkflowStep.InProgress ? onInputClick : undefined}
        />
        <Steps.Step title="In Progress"
                    icon={getIcon(WorkflowStep.InProgress)}
        />
        <Steps.Step
          title="Results"
          icon={getIcon(WorkflowStep.Results)}
          style={onInputClick && clickableStyle}
          onClick={currentStep !== WorkflowStep.InProgress ? onResultsClick : undefined}
        />
      </Steps>
  )
};

export default WorkflowSteps
