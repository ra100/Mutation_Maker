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

import {Table} from 'antd'
import {ColumnProps} from 'antd/lib/table'
import * as R from 'ramda'
import * as React from 'react'
import {compose} from 'recompose'

import withRowIndexKey, {WithRowIndexKey} from 'shared/components/withRowIndexKey'
import {WithSelectedAndHighlighted} from 'shared/components/withSelectedAndHighlighted'
import withSelectedAndHighlightedTableHandlers, {WithSelectedAndHighlightedTableHandlers} from 'shared/components/withSelectedAndHighlightedTableHandlers'
import {Omit} from 'shared/lib/Omit'
import {IndexedPASResultFragment,} from 'shared/lib/ResultData'
import {PASResultFragment} from 'shared/lib/Api'

type PASResultTableOuterProps = {
  resultRecords: IndexedPASResultFragment[]
} & Omit<WithSelectedAndHighlighted, 'setSelected' | 'setHighlighted'>

type WithResultDataRecords = {}

type PASResultTableInnerProps = PASResultTableOuterProps &
  WithResultDataRecords &
  WithRowIndexKey &
  WithSelectedAndHighlightedTableHandlers<PASResultFragment>

const columns: Array<ColumnProps<IndexedPASResultFragment>> = [
  {
    title: 'Name',
    width: '5%',
    key: 'name',
    align: 'center',
    render: (text, record) =>
      `Fr${record.index + 1}`
  },
  {
    title: 'Fragment sequence (WT fragment)',
    key: 'fragment',
    width: '25%',
    align: 'left',
    className: 'PASFragmentSeqCol',
    render: (text, record) =>
      record.fragment
  },
  {
    title: 'Length (bp)',
    key: 'length',
    width: '5%',
    align: 'center',
    render: (text, record) =>
      record.length
  },
  {
    title: 'Overlap to next fragment (bp)',
    key: 'overlap_length',
    width: '10%',
    align: 'center',
    render: (text, record) =>
      record.overlap_length
  },
  {
    title: 'Overlap GC (%)',
    key: 'overlap_gc',
    width: '5%',
    align: 'center',
    render: (text, record) => {
      if (record.overlap_GC) {
        return record.overlap_GC.toFixed(2)
      } else {
        return '-'
      }
    }
  },
  {
    title: `Overlap Tm (${'\u00b0'}C)`,
    key: 'overlap_tm',
    width: '10%',
    align: 'center',
    render: (text, record) => {
      if (record.overlap_Tm) {
        return record.overlap_Tm.toFixed(1)
      } else {
        return '-'
      }
    }
  },
  {
    title: 'Mutations',
    key: 'mutations',
    width: '10%',
    align: 'center',
    render: (text, record) => {
      return record.mutations
        .filter(mutation => !mutation.wild_type)
        .map(mutation =>
          mutation.wild_type_amino
          + mutation.position
          + mutation.mutated_amino)
        .join(', ')
    }
  },
  {
    title: 'WT codon',
    key: 'wt_codon',
    width: '10%',
    align: 'center',
    render: (text, record) => {
      const dictWTC: any[] = [];
      const uniqueWTC: any[] = [];

      record.mutations
        .filter(mutation => !mutation.wild_type)
        .forEach(mutation => {
          if (dictWTC[mutation.position]) {
            dictWTC[mutation.position.toString()].push(mutation.wild_type_codon)
          } else {
            dictWTC[mutation.position.toString()] = [mutation.wild_type_codon]
          }
        });

      dictWTC.forEach((key) => {
        uniqueWTC.push(...new Set(key))
      });

      return uniqueWTC.join(', ')
    }
  },
  {
    title: 'Library Codons',
    key: 'library_codons',
    width: '10%',
    align: 'center',
    render: (text, record) => {
      const dictLC: any[] = [];
      const uniqueLC: any[] = [];
      record.mutations
        .filter(mutation => !mutation.wild_type)
        .forEach(mutation => {
          const libraryCodon = mutation.wild_type_codon + '/'
            + mutation.mutated_codon;
          if (dictLC[mutation.position]) {
            dictLC[mutation.position.toString()].push(libraryCodon)
          } else {
            dictLC[mutation.position.toString()] = [libraryCodon]
          }
        });

      dictLC.forEach((key) => {
        uniqueLC.push(...new Set(key))
      });

      return uniqueLC.join(', ')
    }
  },
  {
    title: '#Oligonucleotides',
    key: 'num_of_oligos',
    width: '10%',
    align: 'center',
    render: (text, record) =>
      record.oligos.length
  },
];

const PASResultTable: React.SFC<PASResultTableInnerProps> =
  ({
     resultRecords,
     rowKey,
     onRow,
     rowClassName,
   }) => (
    <Table
      className="ResultTable"
      bordered
      size="small"
      rowKey={rowKey}
      columns={columns}
      dataSource={resultRecords}
      pagination={false}
      onRow={onRow}
      rowClassName={rowClassName}
    />
  );

export default compose<PASResultTableInnerProps, PASResultTableOuterProps>(
  withRowIndexKey,
  withSelectedAndHighlightedTableHandlers<PASResultFragment & { index: number }>(
    record => [`primer${record.index.toString()}`
      , ...record.mutations.map(R.prop('identifier'))],
    record => [`primer${record.index.toString()}`],
    record => !record.mutations.length,
  ),
)(PASResultTable)
