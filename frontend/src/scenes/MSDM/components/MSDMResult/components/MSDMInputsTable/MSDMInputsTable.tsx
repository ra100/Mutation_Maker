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
import { MSDMFormData } from 'shared/lib/FormData';
import InputsTableRow from 'shared/components/InputsTableRow';
import './styles.css'

type MSDMInputsTableProps = {
 formData: Partial<MSDMFormData>
}

const MSDMInputsTable: React.SFC<MSDMInputsTableProps> = ({
  formData
}) => (
  <div className="Print-Only">
    <InputsTableRow label="Five Prime Flanking Sequence" value={formData.fivePrimeFlankingSequence} />
    <InputsTableRow label="Gene of Interest Sequence" value={formData.goiSequence} />
    <InputsTableRow label="Three Prime Flanking Sequence" value={formData.threePrimeFlankingSequence} />
    <InputsTableRow label="Mutations" value={formData.mutations} />
    <InputsTableRow label="Codon Usage" value={formData.codonUsage === 'custom' ? formData.customCodonUsage + ' ' + formData.taxonomyId : formData.codonUsage} />
    <InputsTableRow label="Codon Usage Frequency Threshold" value={formData.codonUsageFrequencyThresholdPct} />
    <InputsTableRow label="Size" value={`${formData.sizeMax} - ${formData.sizeMax}`} />
    <InputsTableRow label="3' Size" value={`${formData.threePrimeSizeMin} - ${formData.threePrimeSizeMax}`} />
    <InputsTableRow label="5' Size" value={`${formData.fivePrimeSizeMin} - ${formData.fivePrimeSizeMax}`} />
    <InputsTableRow label="GC Content" value={`${formData.gcContentMin} - ${formData.gcContentMax}`} />
    <InputsTableRow label="Temperature" value={`${formData.temperatureMin} - ${formData.temperatureMax}`} />
    <InputsTableRow label="Temperature Weight" value={formData.temperatureWeight} />
    <InputsTableRow label="Size Weight" value={formData.totalSizeWeight} />
    <InputsTableRow label="3' Size Weight" value={formData.threePrimeSizeWeight} />
    <InputsTableRow label="5' Size Weight" value={formData.fivePrimeSizeWeight} />
    <InputsTableRow label="GC Content Weight" value={formData.gcContentWeight} />
    <InputsTableRow label="Hairpin Temperature Weight" value={formData.hairpinTemperatureWeight} />
    <InputsTableRow label="Primer-dimer Temperature Weight" value={formData.primerDimerTemperatureWeight} />
    <InputsTableRow label="Max Temperature Difference" value={formData.maxTemperatureDifference} />
    <InputsTableRow label="User primer3" value={formData.usePrimer3 ? 'Yes' : 'No'} />
    <InputsTableRow label="Use Degeneracy Codon"  value={formData.useDegeneracyCodon ? 'Yes' : 'No'} />
    <InputsTableRow label="Non-overlapping primers only" value={formData.nonOverlappingPrimers ? 'Yes' : 'No'} />
    <InputsTableRow label="Oligo Prefix" value={formData.oligoPrefix !== 'undefined' ? formData.oligoPrefix : ''} />
  </div>
);

export default MSDMInputsTable
