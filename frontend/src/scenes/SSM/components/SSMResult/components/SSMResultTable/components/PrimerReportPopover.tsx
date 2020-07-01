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

import { Icon, Popover, Table } from 'antd'
import { ColumnProps } from 'antd/lib/table'
import * as React from 'react'
import { withProps } from 'recompose'

import { SSMMutationPairingReport, SSMMutationPrimerSelectionReport } from 'shared/lib/Api'

type ReportRecord = {
  key: string
  value: React.ReactNode
}

type PrimerReportPopoverInnerProps = {
  records: ReportRecord[]
}

const popoverContentColumns: Array<ColumnProps<ReportRecord>> = [
  {
    key: 'key',
    dataIndex: 'key',
  },
  {
    key: 'value',
    dataIndex: 'value',
  },
]

const PrimerReportPopover: React.SFC<PrimerReportPopoverInnerProps> = ({ records }) => {
  const popoverContent = (
    <Table
      rowKey="key"
      columns={popoverContentColumns}
      dataSource={records}
      pagination={false}
      showHeader={false}
    />
  )

  return (
    <Popover title="Report" content={popoverContent}>
      <Icon type="info-circle-o" />
    </Popover>
  )
}

type PrimerReportPopoverOuterProps = {
  ssmMutationPrimerSelectionReport: SSMMutationPrimerSelectionReport
  ssmMutationPairingReport: SSMMutationPairingReport
  forward_flanking_primer_temperature: number
  reverse_flanking_primer_temperature: number
  min_three_end_temperature: number
  max_three_end_temperature: number
  min_overlap_temperature: number
  max_overlap_temperature: number
}

export default withProps<PrimerReportPopoverInnerProps, PrimerReportPopoverOuterProps>(
  ({
    ssmMutationPrimerSelectionReport,
    ssmMutationPairingReport,
    forward_flanking_primer_temperature,
    reverse_flanking_primer_temperature,
    min_three_end_temperature,
    max_three_end_temperature,
    min_overlap_temperature,
    max_overlap_temperature,
  }) => ({
    records: [
      {
        key: 'Forward flanking primer temperature',
        value: forward_flanking_primer_temperature,
      },
      {
        key: 'Reverse flanking primer temperature',
        value: reverse_flanking_primer_temperature,
      },
      {
        key: '3 end temperature range',
        value: `${min_three_end_temperature} - ${max_three_end_temperature}`,
      },
      {
        key: 'Overlap temperature range',
        value: `${min_overlap_temperature} - ${max_overlap_temperature}`,
      },
      {
        key: 'Primers considered from Primer3',
        value: ssmMutationPrimerSelectionReport.primers_considered_from_primer3,
      },
      {
        key: 'After 3 end filtering',
        value: ssmMutationPrimerSelectionReport.after_three_end_filtering,
      },
      {
        key: 'All pairs count',
        value: ssmMutationPairingReport.all_pairs_count,
      },
      {
        key: 'After overlap length filtering',
        value: ssmMutationPairingReport.after_overlap_length_filtering,
      },
    ],
  }),
)(PrimerReportPopover)
