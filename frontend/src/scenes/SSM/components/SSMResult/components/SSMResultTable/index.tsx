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

import { CheckOutlined, CloseOutlined } from '@ant-design/icons'
import { Table } from 'antd'
import * as React from 'react'
import withRowIndexKey, { WithRowIndexKey } from 'shared/components/withRowIndexKey'
import { SSMMutationData, SSMPrimerData } from 'shared/lib/Api'
import { Omit } from 'shared/lib/Omit'
import { SSMResultData } from 'shared/lib/ResultData'
import { WithSelectedAndHighlighted } from 'shared/components/withSelectedAndHighlighted'
import withSelectedAndHighlightedTableHandlers, {
  WithSelectedAndHighlightedTableHandlers,
} from 'shared/components/withSelectedAndHighlightedTableHandlers'
import InRangeNumber from './components/InRangeNumber'
import {ColumnProps} from "antd/lib/table";

type PrimerTableOuterProps = {
  resultData: SSMResultData
  minGcContent: number
  maxGcContent: number
} & Omit<WithSelectedAndHighlighted, 'setSelected' | 'setHighlighted'>

type PrimerTableInnerProps = PrimerTableOuterProps &
  WithSelectedAndHighlightedTableHandlers<SSMMutationData> &
  WithRowIndexKey

const primerMetadataSubTable = (
  keyPrefix: string,
  getPrimerMetadata: (result: SSMMutationData) => SSMPrimerData,
  metadata: {
    minGcContent: number
    maxGcContent: number
    minThreeEndTemperature: number
    maxThreeEndTemperature: number
  },
): Array<ColumnProps<SSMMutationData>> => [
  {
    title: 'Size',
    key: `${keyPrefix}Size`,
    width: '4em',
    render: (text: any, record: SSMMutationData) => 
      record.result_found ? getPrimerMetadata(record).length : { props: { colSpan: 0 } },
  },
  {
    title: 'GC',
    key: `${keyPrefix}Gc`,
    width: '4em',
    render: (text: any, record: SSMMutationData) =>
      record.result_found ? (
        <InRangeNumber
          min={metadata.minGcContent}
          max={metadata.maxGcContent}
          value={getPrimerMetadata(record).gc_content}
        />
      ) : { props: { colSpan: 0 } },
  },
  {
    title: '3End Tm',
    key: `${keyPrefix}ThreeEndTm`,
    width: '4em',
    render: (text: any, record: SSMMutationData) =>
      record.result_found ? (
        <InRangeNumber
          min={metadata.minThreeEndTemperature}
          max={metadata.maxThreeEndTemperature}
          value={getPrimerMetadata(record).three_end_temperature}
        />
      ) : { props: { colSpan: 0 } },
  },
]

const primerTableColumns = (
  ssmResultData: SSMResultData,
  metadata: {
    minGcContent: number
    maxGcContent: number
  },
): Array<ColumnProps<SSMMutationData>> => {
  const fwdColumns: ColumnProps<SSMMutationData>[] = [
    {
      title: 'Sequence',
      key: 'fwdSequence',
      className: 'sequence',
      render: (text: any, record: SSMMutationData) =>
        record.result_found
          ? record.forward_primer.sequence
          : {
              children: 'Primer Not Found',
              props: { colSpan: 4 },
            },
    },
    ...primerMetadataSubTable('fwd', result => result.forward_primer, {
      ...metadata,
      minThreeEndTemperature: ssmResultData.min_forward_temperature,
      maxThreeEndTemperature: ssmResultData.max_forward_temperature,
    }),
  ]

  const revColumns: ColumnProps<SSMMutationData>[] = [
    {
      title: 'Sequence',
      key: 'revSequence',
      className: 'sequence',
      render: (text: any, record: SSMMutationData) =>
        record.result_found
          ? record.reverse_primer.sequence
          : {
              children: 'Primer Not Found',
              props: { colSpan: 4 },
            },
    },
    ...primerMetadataSubTable('rev', result => result.reverse_primer, {
      ...metadata,
      minThreeEndTemperature: ssmResultData.min_reverse_temperature,
      maxThreeEndTemperature: ssmResultData.max_reverse_temperature,
    }),
  ]

  const overlapColumns: ColumnProps<SSMMutationData>[] = [
    {
      title: 'Size',
      key: 'overlapSize',
      width: '4em',
      render: (text: any, record: SSMMutationData) =>
        record.result_found ? record.overlap.length : { children: '', props: { colSpan: 2 } },
    },
    {
      title: 'Tm',
      key: 'overlapTemperature',
      width: '4em',
      render: (text: any, record: SSMMutationData) => {
        if (!record.result_found) return { props: { colSpan: 0 } }
        return (
          <InRangeNumber
            min={ssmResultData.min_overlap_temperature}
            max={ssmResultData.max_overlap_temperature}
            value={record.overlap?.temperature}
          />
        )
      },
    },
  ]

  return [
    {
      title: 'Mutation',
      key: 'mutation',
      dataIndex: 'mutation',
      width: '6em',
    },
    {
      title: 'Fwd Primer',
      key: 'fwdPrimer',
      children: fwdColumns as any,
    },
    {
      title: 'Rev Primer',
      key: 'revPrimer',
      children: revColumns as any,
    },
    {
      title: 'Overlap',
      key: 'overlap',
      children: overlapColumns as any,
    },
    {
      title: 'In range',
      key: 'parameters_in_range',
      width: '5em',
      render: (text: any, record: SSMMutationData) =>
        record.result_found ? (
          record.parameters_in_range ? (
            <CheckOutlined style={{ color: 'green' }} />
          ) : (
            <CloseOutlined style={{ color: 'red' }} />
          )
        ) : null,
    },
    {
      title: 'Score (lower is better)',
      key: 'non_optimality',
      width: '6em',
      render: (text: any, record: SSMMutationData) => record.non_optimality
    },
  ]
}

const SSMResultTable: React.FC<PrimerTableInnerProps> = ({
  resultData,
  minGcContent,
  maxGcContent,
  selected,
  highlighted,
  onRow,
  rowKey,
  rowClassName,
}) => (
  <Table
    className="ResultTable"
    bordered
    size="small"
    rowKey={(record, index) => rowKey(record, index ?? 0)}
    columns={primerTableColumns(resultData, { minGcContent, maxGcContent })}
    dataSource={resultData.results}
    pagination={false}
    onRow={onRow}
    rowClassName={rowClassName}
  />
)

export default withRowIndexKey(
  withSelectedAndHighlightedTableHandlers<SSMMutationData>(
    record => [record.mutation],
    record => [record.mutation],
    record => !record.result_found,
  )(SSMResultTable),
)
