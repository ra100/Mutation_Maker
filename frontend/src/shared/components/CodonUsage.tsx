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
import { Form, Input, InputNumber, Radio, Select, Tooltip } from 'antd'
import FormSection from 'shared/components/FormSection'
import * as _ from 'lodash'
import Axios from 'axios'
import { Controller, UseFormReturn } from 'react-hook-form'

const { Option } = Select

type CodonUsageProps = {
  index: number
  form: UseFormReturn<any>
}

const CodonUsage: React.FC<CodonUsageProps> = ({ index, form }) => {
  const [codonUsageData, setCodonUsageData] = React.useState<any[]>([])
  const [isCodonUsageDisabled, setIsCodonUsageDisabled] = React.useState(true)
  const [isCodonUsageLoading, setIsCodonUsageLoading] = React.useState(false)
  const codonUsageDataLoad = React.useRef<any[]>([])
  const timeout = React.useRef<number>(0)

  const { control, setValue } = form

  const clearTimeout = () => {
    if (timeout.current) {
      window.clearTimeout(timeout.current)
    }
  }

  const handleCodonUsageSearch = (value: string) => {
    if (value.length === 0) {
      setCodonUsageData(codonUsageDataLoad.current.slice(0, 10))
    } else {
      setIsCodonUsageLoading(true)
      clearTimeout()
      timeout.current = window.setTimeout(() => {
        const regex = new RegExp(_.escapeRegExp(value), 'i')
        const isMatch = (result: any) => regex.test(result.name) || regex.test(result.id)
        let filteredResults = codonUsageDataLoad.current.filter(isMatch)
        filteredResults.length = Math.min(filteredResults.length, 10)
        setIsCodonUsageLoading(false)
        setCodonUsageData(filteredResults)
      }, 500)
    }
  }

  const handleCodonUsageChange = (value: string) => {
    const customCodonUsage = codonUsageDataLoad.current.find((element: any) => element.id === value)
    if (customCodonUsage) {
      setValue('customCodonUsage', customCodonUsage.name)
    }
  }

  const handleCustomCodonUsageSelect = (event: any) => {
    if (event.target.value === 'custom') {
      setIsCodonUsageDisabled(false)
    } else {
      setIsCodonUsageDisabled(true)
    }
  }

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        const response: any = await Axios.get('/v1/get_species')
        if (response && response.data && response.data.length) {
          codonUsageDataLoad.current = [...response.data]
          setCodonUsageData(response.data.slice(0, 10))
        } else {
          console.error('Fetching species failed.')
        }
      } catch (error) {
        console.error(error)
        console.error('Fetching species failed because of unexpected exception.')
      }
    }
    fetchData()
  }, [])

  const codonUsageOptions = codonUsageData.map((data: any) => (
    <Option key={data.id}>{data.name + ' ' + data.id}</Option>
  ))

  return (
    <FormSection index={index} title="Codon Usage">
      <Tooltip title="Select species codon usage table">
        <Form.Item label="Codon Usage">
          <Controller
            name="codonUsage"
            control={control}
            defaultValue="e-coli"
            render={({ field }) => (
              <Radio.Group {...field} onChange={(e) => { field.onChange(e); handleCustomCodonUsageSelect(e) }}>
                <Radio.Button value="e-coli">E.coli</Radio.Button>
                <Radio.Button value="yeast">Yeast</Radio.Button>
                <Radio.Button value="custom">Custom</Radio.Button>
              </Radio.Group>
            )}
          />
        </Form.Item>
        <Form.Item>
          <Controller
            name="taxonomyId"
            control={control}
            render={({ field }) => (
              <Select
                {...field}
                disabled={isCodonUsageDisabled}
                showSearch
                filterOption={false}
                placeholder="Search Custom Codon Usage"
                onSearch={handleCodonUsageSearch}
                onChange={(val) => { field.onChange(val); handleCodonUsageChange(val) }}
                loading={isCodonUsageLoading}
              >
                {codonUsageOptions}
              </Select>
            )}
          />
        </Form.Item>
        <Form.Item>
          <Controller name="customCodonUsage" control={control} render={({ field }) => <Input {...field} type="hidden" />} />
        </Form.Item>
      </Tooltip>
      <Tooltip title="Enter threshold of frequency percentage. Only codons above entered threshold will be used.">
        <Form.Item label="Codon Usage Frequency Threshold Percentage" validateStatus={form.formState.errors.codonUsageFrequencyThresholdPct ? 'error' : undefined} help={form.formState.errors.codonUsageFrequencyThresholdPct?.message?.toString()}>
          <Controller
            name="codonUsageFrequencyThresholdPct"
            control={control}
            defaultValue={10}
            rules={{ required: 'Frequency Threshold Percentage is required' }}
            render={({ field }) => <InputNumber {...field} min={0} max={100} />}
          />
        </Form.Item>
      </Tooltip>
    </FormSection>
  )
}

export default CodonUsage
