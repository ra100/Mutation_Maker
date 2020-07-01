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

import { Col, Divider, Row } from 'antd'
import * as React from 'react'

import withSelectedAndHighlighted, {
  WithSelectedAndHighlighted,
} from 'shared/components/withSelectedAndHighlighted'
import { SSMResultData } from 'shared/lib/ResultData'

import SaveFile from 'shared/components/SaveFile'
import { SSMFormData } from 'shared/lib/FormData'
import SSMFeatureViewer from './components/SSMFeatureViewer'
import SSMResultTable from './components/SSMResultTable'

import SSMInputsTable from './components/SSMInputsTable/SSMInputsTable';

type SSMResultOuterProps = {
  jobId?: string
  resultData: SSMResultData
  formData: Partial<SSMFormData>
}

type SSMResultInnerProps = SSMResultOuterProps & WithSelectedAndHighlighted

const SSMResult: React.SFC<SSMResultInnerProps> = ({
  jobId,
  resultData,
  formData,
  selected,
  highlighted,
  onClick,
  onMouseEnter,
  onMouseLeave
}) => (
  <>
    {jobId && (
      <SaveFile result={resultData} type="ssm" input={resultData.input_data} formData={formData} />
    )}
    <Divider className="Result--divider" />
    {/* Render Form Data */}
    <Row className="Result" gutter={8}>
      <Col className="Result--col print-only" xxl={12}>
        <div className="Result--wrapper Wrapper-Print-Only">
          <SSMInputsTable formData={formData} />
        </div>
      </Col>
      <Col className="Result--col" xxl={12}>
        <div className="Result--wrapper">
          <SSMResultTable
            resultData={resultData}
            selected={selected}
            highlighted={highlighted}
            onClick={onClick}
            onMouseEnter={onMouseEnter}
            onMouseLeave={onMouseLeave}
            minGcContent={formData.gcContentMin || -Infinity}
            maxGcContent={formData.gcContentMax || Infinity}
          />
        </div>
      </Col>
      <Col className="Result--col" xxl={12}>
        <div className="Result--wrapper">
          <SSMFeatureViewer
            resultData={resultData}
            selected={selected}
            highlighted={highlighted}
            onClick={onClick}
            onMouseEnter={onMouseEnter}
            onMouseLeave={onMouseLeave}
          />
        </div>
      </Col>
    </Row>
  </>
)

export default withSelectedAndHighlighted(SSMResult)
