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
import { DeleteOutlined } from '@ant-design/icons'
import { Button, Form, message, Radio, Tooltip } from 'antd'
import { Controller, UseFormReturn } from 'react-hook-form'
import FormSection from 'shared/components/FormSection'
import MutationsTable from './MutationsTable'
import FileUploadMutations from './FileUploadMutations'
import { aminoAcidToCodons } from 'shared/genes'

type InputMutationsProps = {
  index: number
  form: UseFormReturn<any>
  inputMutations: any
  isMutationsReset: boolean
  handleResetMutations: () => void
}

const InputMutations: React.FC<InputMutationsProps> = ({
  index,
  form,
  inputMutations,
  isMutationsReset,
  handleResetMutations,
}) => {
  const [mutations, setMutations] = React.useState<any[]>([])

  const { control, setValue, getValues, resetField } = form

  const handleInputMutationsTypeChange = (event: any) => {
    setValue('inputMutationsType', event.target.value)
  }

  const handleInputMutationsUpload = (target: string) => (data: any) => {
    setMutations([...data.mutations])
    setValue(target, data)
  }

  const mutationsValidator = (value: any) => {
    if (!value || !value.mutations || value.mutations.length === 0) {
      return true
    }

    const sequence = getValues('goiSequence')
    const sequenceType = getValues('inputSequenceType')
    const mutationsType = getValues('inputMutationsType')

    for (const [idx, mutation] of value.mutations.entries()) {
      if ('target' in mutation && !mutation.target) {
        return `Please insert Target Residue in row ${idx + 1}`
      }
      if ('target' in mutation && mutation.target && mutation.target.length > 0) {
        const targetValue = mutation.target.charAt(0).toUpperCase()
        const position = parseInt(mutation.target.slice(1))
        if (sequenceType === 'protein') {
          if (!(sequence.charAt(position - 1) === targetValue)) {
            return `Row ${idx + 1}: target ${targetValue} is not present at site ${position}`
          }
        } else {
          if (!aminoAcidToCodons(targetValue).includes(sequence.substr((position - 1) * 3, 3))) {
            return `Row ${idx + 1}: target ${targetValue} is not present at site ${position}`
          }
        }
      }
      if ('mt' in mutation && !mutation.mt) {
        return `Please insert MT in row ${idx + 1}`
      }
      if ('mt' in mutation && mutation.mt && mutation.mt.length > 0) {
        if (mutationsType === 'dna') {
          if (!(mutation.mt || '').match(/^[ACGTacgt, ]+$/)) {
            return `Row ${idx + 1}: the only allowed values for MT are: A, C, T, G`
          }
        } else {
          if (!(mutation.mt || '').match(/^[FLIMVSGTAYHQNKDECWRPflimvsgtayhqnkdecwrp, ]+$/)) {
            return `Row ${idx + 1}: the only allowed values for MT are: F, L, I, M, V, S, G, T, A, Y, H, Q, N, K, D, E, C, W, R, P`
          }
        }
      }
      if ('mtp' in mutation && !mutation.mtp) {
        return `Please insert MT% in row ${idx + 1}`
      }
      if (mutation.mtp < 0 || mutation.mtp > 100) {
        return 'MT% must be between 0 and 100'
      }
    }
    return true
  }

  const resetMutationsTable = () => {
    setMutations([])
    resetField('inputMutations')
    resetField('inputMutationsType')
    setValue('inputMutations', { mutations: [] })
  }

  const handleInputMutationsChange = (newMutations: any) => {
    setMutations([...newMutations.mutations])
  }

  React.useEffect(() => {
    const inputMutationsData = inputMutations?.mutations
    if (inputMutationsData && inputMutationsData.length > 0) {
      setMutations([...inputMutationsData])
      setValue('inputMutations', { mutations: [...inputMutationsData] })
    }
  }, [inputMutations, setValue])

  React.useEffect(() => {
    if (isMutationsReset) {
      resetMutationsTable()
      handleResetMutations()
    }
  }, [isMutationsReset, handleResetMutations])

  return (
    <FormSection index={index} title="Input Mutations">
      <Tooltip placement="rightTop" title="Select the mutations input format.">
        <Form.Item>
          <Controller
            name="inputMutationsType"
            control={control}
            defaultValue="dna"
            render={({ field }) => (
              <Radio.Group {...field} onChange={(e) => { field.onChange(e); handleInputMutationsTypeChange(e) }}>
                <Radio.Button value="dna">DNA</Radio.Button>
                <Radio.Button value="protein">Protein</Radio.Button>
              </Radio.Group>
            )}
          />
        </Form.Item>
      </Tooltip>
      <Form.Item>
        <Tooltip title="Clear Mutations Table" placement="right">
          <Button type="default" htmlType="reset" icon={<DeleteOutlined />} onClick={resetMutationsTable}>
            Reset
          </Button>
        </Tooltip>
      </Form.Item>
      <Tooltip
        placement="topRight"
        title={
          <span>
            Enter or Upload mutations in accordance with the selected input format:
            <br />
            Protein:
            <br />
            Target Residue: [Amino Acid Abbreviation][Location]
            <br />
            MT: [Amino Acid Abbreviation]
            <br />
            MT%: 1-100%
            <br />
            Codons:
            <br />
            Target Residue: [Amino Acid Abbreviation][Location]
            <br />
            MT: [Codon]
            <br />
            MT%: 1-100%
          </span>
        }
      >
        <Form.Item validateStatus={form.formState.errors.inputMutations ? 'error' : undefined} help={form.formState.errors.inputMutations?.message}>
          <FileUploadMutations onChange={handleInputMutationsUpload('inputMutations')} />
          <Controller
            name="inputMutations"
            control={control}
            defaultValue={{ mutations: [] }}
            rules={{
              required: 'Input mutations are required',
              validate: mutationsValidator,
            }}
            render={({ field }) => (
              <MutationsTable
                {...field}
                mutations={mutations}
                onChange={(newMutations: any) => {
                  handleInputMutationsChange(newMutations)
                  field.onChange(newMutations)
                }}
              />
            )}
          />
        </Form.Item>
      </Tooltip>
    </FormSection>
  )
}

export default InputMutations
