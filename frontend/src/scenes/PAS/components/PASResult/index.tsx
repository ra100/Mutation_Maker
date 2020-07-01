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

import {Alert, Divider, Row} from 'antd'
import * as React from 'react'
import {compose, withProps} from 'recompose'
import withSelectedAndHighlighted, {
  WithSelectedAndHighlighted,
} from 'shared/components/withSelectedAndHighlighted'
import {
  IndexedPASResultFragment, PASResultData,
  resultRecordsToIndexedResultRecordsPas,
} from 'shared/lib/ResultData'
import {PASFormData} from 'shared/lib/FormData';
import SaveFile from "shared/components/SaveFile";
import PASResultTable from "./components/PASResultTable";
import PASFeatureViewer from './components/PASFeatureViewer'
import PASInputsTable from "./components/PASInputsTable/PASInputsTable";

type PASResultOuterProps = {
  jobId?: string
  resultData: PASResultData,
  formData: Partial<PASFormData>,
}

type WithProcessedResults = {
  geneSequence: string
  geneOffset: number
  resultRecords: IndexedPASResultFragment[]
  resultFound: boolean
}

type PASResultInnerProps =
  PASResultOuterProps
  & WithProcessedResults
  & WithSelectedAndHighlighted

const PASResult: React.SFC<PASResultInnerProps> =
  ({
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
     formData,
     resultFound,
   }) => (
    resultFound ?
      <>
        {jobId && (
          <SaveFile result={resultRecords} type="pas"
                    input={resultData.input_data} formData={formData}/>
        )}
        <Divider className="Result--divider"/>
        <Row className="Result print-only">
            <div className="Result--wrapper Wrapper-Print-Only">
              <PASInputsTable formData={formData}/>
            </div>
        </Row>
        <Row className="Result">
            <div className="Result--wrapper PASResultTableCnt">
              <PASResultTable
                resultRecords={resultRecords}
                selected={selected}
                highlighted={highlighted}
                onClick={onClick}
                onMouseEnter={onMouseEnter}
                onMouseLeave={onMouseLeave}
              />
            </div>
        </Row>
        <Row className="Result">
            <div className="Result--wrapper PASFeatureViewerCnt">
              <PASFeatureViewer
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
        </Row>
      </>
      :
      <Alert
        type="error"
        showIcon
        message="No results"
        description={resultData.message}
      />

  );

export default compose<PASResultInnerProps, PASResultOuterProps>(
  withProps<WithProcessedResults, PASResultOuterProps>(({resultData}) => ({
    geneSequence:
      resultData.input_data.sequences.five_end_flanking_sequence +
      resultData.input_data.sequences.gene_of_interest +
      resultData.input_data.sequences.three_end_flanking_sequence,
    geneOffset: resultData.input_data.sequences.five_end_flanking_sequence.length,
    resultRecords: resultRecordsToIndexedResultRecordsPas(resultData.results),
    inputData: resultData.input_data,
    resultFound: resultData.results.length > 0
  })),
  withSelectedAndHighlighted,
)(PASResult)
