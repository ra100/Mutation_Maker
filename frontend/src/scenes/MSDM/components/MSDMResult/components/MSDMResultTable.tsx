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

import { Table } from 'antd'
import { ColumnProps } from 'antd/lib/table'
import * as R from 'ramda'
import * as React from 'react'
import { compose } from 'recompose'
import withRowIndexKey, { WithRowIndexKey } from 'shared/components/withRowIndexKey'
import { WithSelectedAndHighlighted } from 'shared/components/withSelectedAndHighlighted'
import withSelectedAndHighlightedTableHandlers, {
  WithSelectedAndHighlightedTableHandlers,
} from 'shared/components/withSelectedAndHighlightedTableHandlers'
import { Omit } from 'shared/lib/Omit'
import {
  IndexedMSDMFlatResultRecord,
  MSDMFlatResultRecord,
  MSDMResultRecord,
} from 'shared/lib/ResultData'
import { skipUnlessResultFound } from 'shared/table'

type MSDMResultTableOuterProps = {
  resultRecords: IndexedMSDMFlatResultRecord[]
} & Omit<WithSelectedAndHighlighted, 'setSelected' | 'setHighlighted'>

type WithResultDataRecords = {}

type MSDMResultTableInnerProps = MSDMResultTableOuterProps &
  WithResultDataRecords &
  WithRowIndexKey &
  WithSelectedAndHighlightedTableHandlers<MSDMResultRecord>

const columns: Array<ColumnProps<MSDMFlatResultRecord>> = [
  {
    title: 'Mutations',
    key: 'mutations',
    render: (text, record) => record.mutations.map(R.prop('identifier')).join(', '),
  },
  {
    title: 'Ratios',
    key: 'ratios',
    render: (text, record) =>
      record.ratio !== 0 ? `${((record.ratio || 0) * 100).toString().slice(0, 4)}%` : 'N/A',
  },
  {
    title: 'Primer',
    key: 'primer',
    render: (text, record) =>
      record.result_found
        ? record.sequence
        : {
            children: 'Primer Not Found',
            props: { colSpan: 3 },
          },
  },
  {
    title: 'Size',
    key: 'size',
    render: skipUnlessResultFound((text, record) => record.length),
  },
  {
    title: 'Tm',
    key: 'tm',
    render: skipUnlessResultFound((text, record) => record.temperature),
  },
  {
    title: 'GC',
    key: 'gc',
    render: skipUnlessResultFound((text, record) => record.gc_content),
  },
]

const MSDMResultTable: React.SFC<MSDMResultTableInnerProps> = ({
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
)

export default compose<MSDMResultTableInnerProps, MSDMResultTableOuterProps>(
  withRowIndexKey,
  withSelectedAndHighlightedTableHandlers<MSDMResultRecord & { index: number }>(
    (record) => [`primer${record.index.toString()}`, ...record.mutations.map(R.prop('identifier'))],
    (record) => [`primer${record.index.toString()}`],
    (record) => !record.result_found,
  ),
)(MSDMResultTable)
