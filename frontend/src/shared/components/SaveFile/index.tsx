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

import {Button} from 'antd'
import * as R from 'ramda'
import * as React from 'react'
import * as XLSX from 'xlsx'
import * as Excel from 'exceljs'
import * as FileSaver from 'file-saver'

import {
  IndexedPASResultFragment,
  IndexedQCLMFlatResultRecord,
  SSMResultData
} from 'shared/lib/ResultData'
import {PASFormData, QCLMFormData, SSMFormData} from 'shared/lib/FormData';

const PLATE_SIZE = 96;
const CHAR_LOWER_A = 97;
const CHAR_UPPER_A = 65;

type AnyFormData =
  Partial<SSMFormData>
  | Partial<QCLMFormData>
  | Partial<PASFormData>

type SaveFileProps = {
  result: SSMResultData | IndexedQCLMFlatResultRecord[] | IndexedPASResultFragment[],
  type: 'ssm' | 'qclm' | 'pas',
  input: any,
  formData: AnyFormData
}

const getPosition = (pos: number) => `${String.fromCharCode(CHAR_UPPER_A + Math.floor(pos / 12))}${`0${(pos % 12 + 1).toString()}`.slice(-2)}`;

const tableHeaders = {
  ssm: ['Well Position', 'Name', 'Sequence', 'Notes'],
  qclm: ['Name', 'Primer Sequence', 'Scale', 'Purification', 'Mutation Syntax', 'Overlap'],
  pas: ['Name', 'Fragment Sequence', 'Mutation Syntax', 'Mix ratio', 'Target and MT%']
};

const complementTable = {
  "A": "T",
  "C": "G",
  "G": "C",
  "T": "A",
  "I": "I", // ???
  "R": "Y",
  "Y": "R",
  "M": "K",
  "K": "M",
  "S": "S",
  "W": "W",
  "H": "D",
  "B": "V",
  "V": "B",
  "D": "H",
  "N": "N"
};

const replaceAt = (str: string, index: number, target: string): string => {
  return str.substr(0, index) + target + str.substr(index + target.length)
};

const reverseComplement = (sequence: string): string => {
  const reversed = sequence.split("").reverse().join("");

  return reversed.split("").map(x => complementTable[x]).join("")
};

const createSSMTable = (result: any, oligoPrefix: string, input: any): any => {
  const table = {};
  const type = 'ssm';
  const codons = input.degenerate_codon.split(',');
  let forward = 'Forward';
  let reverse = 'Reverse';

  const fileName = result.input_data.config.file_name;

  codons.forEach((codon: string) => {
    table[`${fileName} ${codon} ${forward}`] = [tableHeaders[type]];
    table[`${fileName} ${codon} ${reverse}`] = [tableHeaders[type]]
  });
  result.results.forEach((data: any, index: number) => {
    if (index === PLATE_SIZE) {
      forward = 'Forward Second';
      reverse = 'Reverse Second';
      codons.forEach((codon: string) => {
        table[`${fileName} ${codon} ${forward}`] = [tableHeaders[type]];
        table[`${fileName} ${codon} ${reverse}`] = [tableHeaders[type]]
      })
    }
    codons.forEach((codon: string) => {
      const mutationOffset = parseInt(data.mutation.substr(1, data.mutation.length - 2), 10);
      const mutationNormalOffset = (mutationOffset - 1) * 3 + result.goi_offset;

      const fwRelativePrimerOffset = mutationNormalOffset - data.forward_primer.normal_order_start;
      const rwRelativePrimerOffset = mutationNormalOffset - data.reverse_primer.normal_order_start;

      const fwMutagenicSequence = replaceAt(data.forward_primer.normal_order_sequence, fwRelativePrimerOffset, codon);
      const rwNormalOrderMutagenicSequence = replaceAt(data.reverse_primer.normal_order_sequence, rwRelativePrimerOffset, codon);

      const rwMutagenicSequence = reverseComplement(rwNormalOrderMutagenicSequence);

      table[`${fileName} ${codon} ${forward}`].push([
        getPosition(index % PLATE_SIZE),
        `${oligoPrefix}-${Math.floor(index / PLATE_SIZE) + 1}F-${getPosition(index % PLATE_SIZE)}`,
        fwMutagenicSequence,
        ''
      ]);
      table[`${fileName} ${codon} ${reverse}`].push([
        getPosition(index % PLATE_SIZE),
        `${oligoPrefix}-${Math.floor(index / PLATE_SIZE) + 1}R-${getPosition(index % PLATE_SIZE)}`,
        rwMutagenicSequence,
        ''
      ])
    })
  });

  return table
};

const createQCLMTable = (result: any, oligoPrefix: string, formData: Partial<QCLMFormData>): any => {
  const table = {};
  const type = 'qclm';
  // Create array of sites
  const sites = result.reduce((acc: any, mutation: any) => {
    // Create site ID based on source and position of all mutations
    const siteIds: string[] = [];
    mutation.mutations.forEach((element: any) => {
      siteIds.push(`${element.source}${element.position}`)
    });

    const siteId = siteIds.join('-');
    // Add new site or append to existing one.
    acc[siteId] ? acc[siteId].push(mutation) : acc[siteId] = [mutation];

    return acc
  }, {});

  const sheetName = formData.fileName ? `${formData.fileName} qclm` : 'qclm';
  table[sheetName] = [tableHeaders[type]];

  // Create table
  Object.keys(sites).forEach((siteId: string, siteIndex: number) => {
    const site = sites[siteId];
    // For each mutation of each site, add new row to table
    site.forEach((m: any, index: number) => table[sheetName].push([
        `${oligoPrefix}-${siteIndex + 1}${site.length > 1 ? String.fromCharCode(CHAR_LOWER_A + index) : ''}`,
        m.sequence,
        '25nm',
        'STD',
        `${m.mutations.map(R.prop('identifier')).join(',')} (${m.degenerate_codons.join(',')})`,
        m.overlap_with_following ? 'Yes' : 'No',
      ])
    )
  });

  return table
};

const createPASTable = (result: IndexedPASResultFragment[], oligoPrefix: string, formData: Partial<PASFormData>): any => {
  const table = {};
  const type = 'pas';

  // Create sheet and add header
  const sheetName = formData.fileName ? `${formData.fileName} pas` : 'pas';
  table[sheetName] = [tableHeaders[type]];

  result.forEach((result, index) => {
    // Create array for separate Target and MT% column
    const targetAndMtp = result.mutations.length > 0 ? result.mutations
      .filter(mutation => !mutation.wild_type)
      .map(mutation =>
        mutation.wild_type_amino
        + mutation.position
        + mutation.mutated_amino
        + ': ' + mutation.frequency * 100) : '-';

    // Create table of Oligo fragments
    result.oligos.forEach((oligo, oIndex) => {
      const mutations = oligo.mutations.map(mIndex => result.mutations[mIndex]);

      const dictMC: any[] = [];
      const uniqueMC: any[] = [];
      mutations
        .forEach(mutation => {
          if(dictMC[mutation.position]) {
            dictMC[mutation.position.toString()].push(mutation.mutated_codon)
          } else {dictMC[mutation.position.toString()] = [mutation.mutated_codon]}
        });

      dictMC.forEach((key) => {
        uniqueMC.push(...new Set(key))
      });

      const oligoMutationSyntax = mutations.length > 0 ? mutations
          .map(mutation =>
            mutation.wild_type_amino
            + mutation.position
            + mutation.mutated_amino)
          .join(', ')
        + ' ('
        + uniqueMC.join(', ')
        + ')' : '-';

      // colour letters
      const colors: any[] = [];
      oligo.reds.forEach((value: number) => {
        colors.push({color: 'red', position: value})
      });
      oligo.blues.forEach((value: number) => {
        colors.push({color: 'blue', position: value})
      });

      colors.sort((a, b) => a.position - b.position);
      const sequence: any = {'richText': []};
      if (colors.length > 0) {
        sequence.richText.push({'text': oligo.sequence.slice(0, colors[0].position)});
        colors.forEach((color: any, cIndex: number, cArray: any[]) => {
          if (cIndex !== 0 && (cArray[cIndex - 1].position + 3 !== color.position)) {
            sequence.richText.push({
              'font': {'color': {'argb': '000000'}},
              'text': oligo.sequence.slice(cArray[cIndex - 1].position + 3, color.position)
            })
          }
          if (color.color === 'red') {
            sequence.richText.push({
              'font': {'color': {'argb': 'ff0000'}},
              'text': oligo.sequence.slice(color.position, color.position + 3)
            })
          } else {
            sequence.richText.push({
              'font': {'color': {'argb': '0000ff'}},
              'text': oligo.sequence.slice(color.position, color.position + 3)
            })
          }
        });
        sequence.richText.push(
          {
            'font': {'color': {'argb': '000000'}},
            'text': oligo.sequence.slice(colors[colors.length - 1].position + 3,
              oligo.sequence.length - 1)
          })
      } else {
        sequence.richText.push({'text': oligo.sequence})
      }

      // Push oligos
      table[sheetName].push([
        `${oligoPrefix}-Fr${index + 1}-${oIndex + 1}`,
        sequence,
        oligoMutationSyntax,
        oligo.mix_ratio || '-',
        targetAndMtp[oIndex]
      ])
    })
  });

  return table
};

const resultsToTable = (result: any, type: string, input: any, formData: AnyFormData): any => {
  const oligoPrefix = input.config.oligo_prefix || 'prefix';
  if (type === 'ssm') {
    return createSSMTable(result, oligoPrefix, input)
  }
  if (type === 'qclm') {
    return createQCLMTable(result, oligoPrefix, formData as Partial<QCLMFormData>)
  }
  if (type === 'pas') {
    return createPASTable(result, oligoPrefix, formData as Partial<PASFormData>)
  }
};

class SaveFile extends React.Component<SaveFileProps> {
  handleClick = () => {
    const {result, type, input, formData} = this.props;
    const fileName = input.config.file_name;
    const table = resultsToTable(result, type, input, formData);

    if (type === 'pas') {
      //ExcelJS
      const workbook = new Excel.Workbook();
      Object.keys(table).forEach(name => {
        const sheet = workbook.addWorksheet(name.toUpperCase());
        sheet.addRows(table[name]);
        workbook.xlsx.writeBuffer()
          .then(buffer => FileSaver.saveAs(new Blob([buffer]), `${fileName}.xlsx`))
          .catch(err => console.error('Error writing excel export', err))
      })
    } else {
      //SheetJS
      const workbook = XLSX.utils.book_new();
      Object.keys(table).forEach(name => {
        XLSX.utils.book_append_sheet(workbook, XLSX.utils.aoa_to_sheet(table[name]), name)
      });
      XLSX.writeFile(workbook, `${fileName}.xlsx`)
    }
  };

  render() {
    return (
      <Button className="no-print" type="primary" icon="download" onClick={this.handleClick}>
        Download as XLSX
      </Button>
    )
  }
}

export default SaveFile
