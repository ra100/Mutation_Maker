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
import * as React from 'react'
import FeatureViewer, { FeatureViewerOptions } from 'feature-viewer'
import { Boundaries, combinedBoundaries, mutationBoundaries } from 'shared/boundaries'
import FeatureViewerComponent from 'shared/components/FeatureViewerComponent'
import { WithSelectedAndHighlighted } from 'shared/components/withSelectedAndHighlighted'
import { config } from 'shared/config'
import FeatureViewerTheme from 'shared/FeatureViewerTheme'
import { codonToAminoAcid, gcContent, Mutation, toCodons } from 'shared/genes'
import { notUndefined } from 'shared/helpers'
import { Omit } from 'shared/lib/Omit'
import { IndexedMSDMFlatResultRecord } from 'shared/lib/ResultData'

type MSDMFeatureViewerProps = {
  geneSequence: string
  geneOffset: number
  resultRecords: IndexedMSDMFlatResultRecord[]
  scrollOffset?: number
} & Omit<WithSelectedAndHighlighted, 'setSelected' | 'setHighlighted'>

const addSequenceDescription = (sequence: string) => (data: any): any => (
  {
    ...data,
    sequence: sequence.slice(data.x - 1, data.y)
  }
);

const initializeMSDMFeatureViewer = (
  geneSequence: string,
  geneOffset: number,
  resultRecords: IndexedMSDMFlatResultRecord[],
) => (componentId: string, options: FeatureViewerOptions | undefined): FeatureViewer => {
  const featureViewer = new FeatureViewer(geneSequence, `#${componentId}`, options);

  const aminoacidOffset = geneOffset % 3;

  /* Aminoacids */
  featureViewer.addFeature({
    data: toCodons(geneSequence.slice(aminoacidOffset)).map((codon, index) => {
      const aminoacid = codonToAminoAcid(codon);

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
  });

  /* Mutations */
  const allMutations = R.uniqBy<Mutation, string>(
    R.prop('identifier'),
    resultRecords.map(R.prop('mutations')).reduce((acc, mutations) => [...acc, ...mutations], []),
  );

  featureViewer.addFeature({
    data: allMutations.map(mutation => {
      const coordinate = geneOffset + mutation.position * 3;

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
  });

  const allPrimersData = resultRecords
    .map((flatResultRecord, index) => {
      const primerIdentifier = `primer${index}`;
      const mutationsIdentifiers = flatResultRecord.mutations.map(R.prop('identifier'));

      return flatResultRecord.result_found
        ? {
            x: flatResultRecord.start! + 1,
            y: flatResultRecord.start! + flatResultRecord.length!,
            //   description: flatResultRecord.sequence,
            className: primerIdentifier,
            id: `primer${index}-fwd`,
            identifiers: [primerIdentifier, ...mutationsIdentifiers],
          }
        : undefined
    })
    .filter(notUndefined);

  featureViewer.addFeature({
    data: allPrimersData.map(addSequenceDescription(geneSequence)),
    name: 'Primers',
    className: 'primers',
    type: 'arrow',
    color: FeatureViewerTheme.default,
  });

  /* GC Content */
  const gcData = gcContent(config.gcContentWindowSize)(geneSequence).map((gcc, index) => ({ x: index, y: gcc }));
  const yValues = gcData.map(({y}: any) => y);
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
  });

  return featureViewer
};

const makeGetBoundaries = (resultRecords: IndexedMSDMFlatResultRecord[]) => (
  identifier: string,
): Boundaries | undefined => {
  const matchingResultRecords = resultRecords.filter(result =>
    R.any(mutation => mutation.identifier === identifier, result.mutations),
  );

  const allBoundaries = matchingResultRecords
    .map(result => {
      if (result.result_found) {
        return {
          left: result.start!,
          right: result.start! + result.length!,
        }
      } else {
        return combinedBoundaries(result.mutations.map(mutationBoundaries).filter(notUndefined))
      }
    })
    .filter(notUndefined);

  return combinedBoundaries(allBoundaries)
};

const MSDMFeatureViewer: React.SFC<MSDMFeatureViewerProps> = ({
  geneSequence,
  geneOffset,
  resultRecords,
  scrollOffset,
  selected,
  highlighted,
  onClick,
  onMouseEnter,
  onMouseLeave,
}) => (
  <FeatureViewerComponent
    geneSequence={geneSequence}
    geneOffset={geneOffset}
    initializeFeatureViewer={initializeMSDMFeatureViewer(geneSequence, geneOffset, resultRecords)}
    getBoundaries={makeGetBoundaries(resultRecords)}
    selected={selected}
    scrollOffset={scrollOffset}
    highlighted={highlighted}
    // tslint:disable-next-line:jsx-no-lambda
    onClick={(dataObject: any) => onClick(dataObject.identifiers || [])}
    // tslint:disable-next-line:jsx-no-lambda
    onMouseEnter={(dataObject: any) => onMouseEnter(dataObject.identifiers || [])}
    // tslint:disable-next-line:jsx-no-lambda
    onMouseLeave={(dataObject: any) => onMouseLeave(dataObject.identifiers || [])}
  />
);

export default MSDMFeatureViewer
