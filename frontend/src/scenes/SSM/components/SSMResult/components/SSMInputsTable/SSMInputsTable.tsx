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
import { SSMFormData } from 'shared/lib/FormData';
import InputsTableRow from 'shared/components/InputsTableRow';
import './styles.css'

type SSMInputsTableProps = {
 formData: Partial<SSMFormData>
}

const SSMInputsTable: React.SFC<SSMInputsTableProps> = ({
  formData
}) => (
  <div className="Print-Only">
    <InputsTableRow label="Plasmid Sequence" value={formData.plasmidSequence} />
    <InputsTableRow label="Sequence" value={formData.goiSequence} />
    <InputsTableRow label="Mutations" value={formData.mutations} />
    <InputsTableRow label="Forward Primer" value={formData.forwardPrimerValue} />
    <InputsTableRow label="Reverse Primer" value={formData.reversePrimerValue} />
    <InputsTableRow label="Size" value={`${formData.sizeMin} - ${formData.sizeMax}`} />
    <InputsTableRow label="3' Size" value={`${formData.threePrimeSizeMin} - ${formData.threePrimeSizeMax}`} />
    <InputsTableRow label="5' Size" value={`${formData.fivePrimeSizeMin} - ${formData.fivePrimeSizeMax}`} />
    <InputsTableRow label="Overlap Size" value={`${formData.overlapSizeMin} - ${formData.overlapSizeMax}`} />
    <InputsTableRow label="GC Content" value={`${formData.gcContentMin} - ${formData.gcContentMax}`} />
    <InputsTableRow label="3' Temperature" value={`${formData.threePrimeTemperatureMin} - ${formData.threePrimeTemperatureMax}`} />
    <InputsTableRow label="Overlap Temperature" value={`${formData.overlapTemperatureMin} - ${formData.overlapTemperatureMax}`} />
    <InputsTableRow label="3' Temperature Weight" value={formData.threePrimeTemperatureWeight} />
    <InputsTableRow label="3' Size Weight" value={formData.threePrimeSizeWeight} />
    <InputsTableRow label="Overal Temperature Weight" value={formData.overlapTemperatureWeight} />
    <InputsTableRow label="GC Content Weight" value={formData.gcContentWeight} />
    <InputsTableRow label="Hairpin Temperature Weight" value={formData.hairpinTemperatureWeight} />
    <InputsTableRow label="Primer-dimer Temperature Weight" value={formData.primerDimerTemperatureWeight} />
    <InputsTableRow label="Max Temperature Difference" value={formData.maxTemperatureDifference} />
    <InputsTableRow label="Calculate 3' Tm separately" value={formData.separateForwardReverseTemperatures ? 'Yes' : 'No'} />
    <InputsTableRow label="Exclude flanking primers from 3' Tm calculation" value={formData.excludeFlankingPrimers ? 'Yes' : 'No'} />
    <InputsTableRow label="Use primer3" value={formData.usePrimer3 ? 'Yes' : 'No'} />
    <InputsTableRow label="Use FASTER approximate algorithm" value={formData.usePrimerGrowingAlgorithm ? 'Yes' : 'No'} />
    <InputsTableRow label="Check for hairpins and primer-dimers" value={formData.computeHairpinHomodimer ? 'Yes' : 'No'} />
    <InputsTableRow label="Degenerate Codon" value={formData.degenerateCodon} />
    <InputsTableRow label="File Name" value={formData.fileName !== 'undefined' ? formData.fileName : ''} />
    <InputsTableRow label="Oligo Prefix" value={formData.oligoPrefix !== 'undefined' ? formData.oligoPrefix : ''} />
  </div>
)

export default SSMInputsTable
