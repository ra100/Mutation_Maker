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
import { compose, withProps } from 'recompose'
import withSelectedAndHighlighted, {
  WithSelectedAndHighlighted,
} from 'shared/components/withSelectedAndHighlighted'
import {
  IndexedQCLMFlatResultRecord,
  QCLMResultData,
  resultRecordsToFlatResultRecords,
} from 'shared/lib/ResultData'
import SaveFile from 'shared/components/SaveFile'
import QCLMFeatureViewer from './components/QCLMFeatureViewer'
import QCLMResultTable from './components/QCLMResultTable'
import ratioCounter from './components/ratioCounter'
import QCLMInputsTable from './components/QCLMInputsTable/QCLMInputsTable';
import { QCLMFormData } from 'shared/lib/FormData';

type QCLMResultOuterProps = {
  jobId?: string
  resultData: QCLMResultData,
  formData: Partial<QCLMFormData>
}

type WithProcessedResults = {
  geneSequence: string
  geneOffset: number
  resultRecords: IndexedQCLMFlatResultRecord[]
}

type QCLMResultInnerProps = QCLMResultOuterProps & WithProcessedResults & WithSelectedAndHighlighted

const QCLMResult: React.SFC<QCLMResultInnerProps> = ({
  jobId,
  geneSequence,
  geneOffset,
  resultRecords,
  selected,
  highlighted,
  onClick,
  onMouseEnter,
  onMouseLeave,
  resultData,
  formData
}) => (
  <>
    {jobId && (
      <SaveFile result={resultRecords} type="qclm" input={resultData.input_data} formData={formData} />
    )}
    <Divider className="Result--divider" />
    <Row className="Result" gutter={8}>
      <Col className="Result--col print-only" xxl={12}>
        <div className="Result--wrapper Wrapper-Print-Only">
          <QCLMInputsTable formData={formData} />
        </div>
      </Col>
      <Col className="Result--col" xxl={12}>
        <div className="Result--wrapper">
          <QCLMResultTable
            resultRecords={resultRecords}
            selected={selected}
            highlighted={highlighted}
            onClick={onClick}
            onMouseEnter={onMouseEnter}
            onMouseLeave={onMouseLeave}
          />
        </div>
      </Col>
      <Col className="Result--col" xxl={12}>
        <div className="Result--wrapper">
          <QCLMFeatureViewer
            geneSequence={geneSequence}
            geneOffset={geneOffset}
            resultRecords={resultRecords}
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
);

export default compose<QCLMResultInnerProps, QCLMResultOuterProps>(
  withProps<WithProcessedResults, QCLMResultOuterProps>(({ resultData }) => ({
    geneSequence: resultData.full_sequence,
    geneOffset: resultData.goi_offset,
    resultRecords: ratioCounter(
      resultRecordsToFlatResultRecords(resultData.results),
    ),
  })),
  withSelectedAndHighlighted,
)(QCLMResult)
