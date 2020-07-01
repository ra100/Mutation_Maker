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

import FeatureViewer, { FeatureViewerOptions } from 'feature-viewer'
import * as R from 'ramda'
import * as React from 'react'
import { Boundaries, mutationBoundaries } from 'shared/boundaries'
import FeatureViewerComponent from 'shared/components/FeatureViewerComponent'
import { WithSelectedAndHighlighted } from 'shared/components/withSelectedAndHighlighted'
import { config } from 'shared/config'
import FeatureViewerTheme from 'shared/FeatureViewerTheme'
import { codonToAminoAcid, gcContent, parseMutation, toCodons } from 'shared/genes'
import { notUndefined } from 'shared/helpers'
import { Omit } from 'shared/lib/Omit'
import { SSMResultData } from 'shared/lib/ResultData'

type SSMFeatureViewerProps = {
  resultData: SSMResultData
  scrollOffset?: number
} & Omit<WithSelectedAndHighlighted, 'setSelected' | 'setHighlighted'>

const addSequenceDescription = (sequence: string) => (data: any): any => (
  {
    ...data,
    sequence: sequence.slice(data.x - 1, data.y)
  }
)

const initializeSSMFeatureViewer = (ssmResultData: SSMResultData) => (
  componentId: string,
  options: FeatureViewerOptions | undefined,
): FeatureViewer => {
  const { full_sequence: sequence, results: mutationsData, goi_offset: goiOffset } = ssmResultData
  const featureViewer = new FeatureViewer(sequence, `#${componentId}`, options)

  const aminoacidOffset = goiOffset % 3

  /* Aminoacids */
  featureViewer.addFeature({
    data: toCodons(sequence.slice(aminoacidOffset)).map((codon, index) => {
      const aminoacid = codonToAminoAcid(codon)

      return {
        x: aminoacidOffset + 1 + index * 3,
        y: aminoacidOffset + 3 + index * 3,
        id: codon,
        description: aminoacid ? aminoacid.symbol : codon,
      }
    }),
    name: 'Aminoacids',
    className: 'aminoacids',
    type: 'rect',
  })

  const mutationFeatureData = mutationsData
    .map(
      R.compose(
        parseMutation,
        R.prop('mutation'),
      ),
    )
    .filter(notUndefined)

  /* Mutations */
  featureViewer.addFeature({
    data: mutationFeatureData.map(mutation => {
      const coordinate = goiOffset + mutation.position * 3

      return (
        mutation && {
          x: coordinate - 2,
          y: coordinate,
          description: mutation.identifier,
          className: mutation.identifier,
          mutation: mutation.identifier,
        }
      )
    }),
    name: 'Mutations',
    className: 'mutations',
    type: 'rect',
    color: FeatureViewerTheme.mutation,
    filter: 'mutations',
  })

  mutationsData.forEach((mutationData, index) => {
    if (!mutationData.result_found) {
      return
    }

    const { mutation, forward_primer, reverse_primer } = mutationData
    const data = [
      {
        x: forward_primer.normal_order_start + 1,
        y: forward_primer.normal_order_start + forward_primer.length,
        className: mutation,
        id: `primer${index}-fwd`,
        mutation,
      },
      {
        x: reverse_primer.normal_order_start + 1,
        y: reverse_primer.normal_order_start + reverse_primer.length,
        reverse: true,
        className: mutation,
        id: `primer${index}-rev`,
        mutation,
      },
    ]

    featureViewer.addFeature({
      data: data.map(addSequenceDescription(sequence)),
      name: `Primers for ${mutation}`,
      className: `primers${index + 1}`,
      type: 'arrow',
      color: FeatureViewerTheme.default,
    })
  })

  /* GC Content */
  const gcData = gcContent(config.gcContentWindowSize)(sequence).map((gcc, index) => ({ x: index, y: gcc }))
  const yValues = gcData.map(({y}: any) => y)
  featureViewer.addFeature({
    data: gcData,
    name: 'GC Content',
    className: 'gcContent',
    color: '#008B8D',
    type: 'line',
    height: 5,
    yAxis: {
      min: Math.min(...yValues),
      max: Math.max(...yValues)
    },
  })

  return featureViewer
}

const makeGetBoundaries = (resultData: SSMResultData) => (
  identifier: string,
): Boundaries | undefined => {
  const matchingMutationData = resultData.results.find(result => result.mutation === identifier)

  if (matchingMutationData && matchingMutationData.result_found) {
    const { forward_primer, reverse_primer } = matchingMutationData

    return {
      left: R.min(forward_primer.normal_order_start, reverse_primer.normal_order_start),
      right: R.max(
        forward_primer.normal_order_start + forward_primer.length,
        reverse_primer.normal_order_start + reverse_primer.length,
      ),
    }
  } else {
    const mutation = parseMutation(identifier)

    return mutation ? mutationBoundaries(mutation, resultData.goi_offset) : undefined
  }
}

const SSMFeatureViewer: React.SFC<SSMFeatureViewerProps> = ({
  resultData,
  scrollOffset,
  selected,
  highlighted,
  onClick,
  onMouseEnter,
  onMouseLeave,
}) => (
  <FeatureViewerComponent
    geneSequence={resultData.full_sequence}
    geneOffset={resultData.goi_offset}
    initializeFeatureViewer={initializeSSMFeatureViewer(resultData)}
    getBoundaries={makeGetBoundaries(resultData)}
    selected={selected}
    highlighted={highlighted}
    // tslint:disable-next-line:jsx-no-lambda
    onClick={(dataObject: any) => onClick(dataObject.mutation ? [dataObject.mutation] : [])}
    // tslint:disable-next-line:jsx-no-lambda
    onMouseEnter={(dataObject: any) =>
      onMouseEnter(dataObject.mutation ? [dataObject.mutation] : [])
    }
    // tslint:disable-next-line:jsx-no-lambda
    onMouseLeave={(dataObject: any) =>
      onMouseLeave(dataObject.mutation ? [dataObject.mutation] : [])
    }
    scrollOffset={scrollOffset}
  />
)

export default SSMFeatureViewer
