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

import {PASFormData} from 'shared/lib/FormData';
import InputsTableRow from 'shared/components/InputsTableRow';
import './styles.css'
import MutationsTable
  from "../../../PASForm/components/InputMutations/MutationsTable";

type PASInputsTableProps = {
  formData: Partial<PASFormData>
}

const PASInputsTable: React.SFC<PASInputsTableProps> = ({ formData}) => (
  <div className="Print-Only">
    <InputsTableRow label="Input Sequence Type"
                    value={formData.inputSequenceType}/>
    <InputsTableRow label="Five Prime Flanking Sequence"
                    value={formData.fivePrimeFlankingSequence}/>
    <InputsTableRow label="Gene of Interest Sequence"
                    value={formData.goiSequence}/>
    <InputsTableRow label="Three Prime Flanking Sequence"
                    value={formData.threePrimeFlankingSequence}/>
    <InputsTableRow label="Input Mutations Type"
                    value={formData.inputMutationsType}/>
    <
      // @ts-ignore
      MutationsTable mutations={formData.inputMutations.mutations}/>
    <InputsTableRow label="Use Degeneracy Codon"
                    value={formData.useDegeneracyCodon ? 'Yes' : 'No'}/>
    <InputsTableRow label="Codon Usage"
                    value={formData.codonUsage === 'custom'
                      ? formData.customCodonUsage + ' ' + formData.taxonomyId
                      : formData.codonUsage}/>
    <InputsTableRow label="Codon Usage Frequency Threshold"
                    value={formData.codonUsageFrequencyThresholdPct}/>
    <InputsTableRow label="Avoid Motifs" value={formData.avoidMotifs}/>
    <InputsTableRow label="Codon Usage Frequency Threshold"
                    value={formData.codonUsageFrequencyThresholdPct}/>
    <InputsTableRow label="Oligo Length"
                    value={`${formData.oligoLengthMin} 
                    - ${formData.oligoLengthMax}`}/>
    <InputsTableRow label="Overlapping Tm"
                    value={`${formData.overlappingTmMin} 
                    - ${formData.overlappingTmOpt} 
                    - ${formData.overlappingTmMax}`}/>
    <InputsTableRow label="Overlapping length"
                    value={`${formData.overlappingLengthMin} 
                    - ${formData.overlappingLengthOpt} 
                    - ${formData.overlappingLengthMax}`}/>
    <InputsTableRow label="GC Content"
                    value={`${formData.gcContentMin} 
                    - ${formData.gcContentMax}`}/>
    <InputsTableRow label="Check for hairpins and primer-dimers"
                    value={formData.computeHairpinHomodimer ? 'Yes' : 'No'}/>
    <InputsTableRow label="Oligo Prefix"
                    value={formData.oligoPrefix
                    !== 'undefined' ? formData.oligoPrefix : ''}/>
    <InputsTableRow label="File name"
                    value={formData.fileName
                    !== 'undefined' ? formData.fileName : ''}/>
  </div>
);

export default PASInputsTable
