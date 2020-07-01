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
import { withState } from 'recompose'

export enum WorkflowStep {
  InputParameters,
  InProgress,
  Results,
}

export type WithCurrentStepState = {
  currentStep: WorkflowStep | undefined
  setCurrentStep(value: WorkflowStep | undefined): WorkflowStep | undefined
}

export default <P>(component: React.ComponentType<P & WithCurrentStepState>) =>
  withState<P, WorkflowStep | undefined, 'currentStep', 'setCurrentStep'>(
    'currentStep',
    'setCurrentStep',
    undefined,
  )(component)
