import { ReloadOutlined, SaveOutlined } from '@ant-design/icons'
import { Button, Col, Form, Input, Radio, Row, Select, Switch, Tooltip } from 'antd'
import * as React from 'react'
import { Controller, useWatch } from 'react-hook-form'
import FileUploadInput from 'shared/components/FileUploadInput'
import FormSection from 'shared/components/FormSection'
import MinOptMaxInputs from 'shared/components/MinOptMaxInputs'
import { geneValidationRule } from 'shared/form'
import { PASFormData } from 'shared/lib/FormData'
import withForm, { WithFormInnerProps } from 'shared/withForm'
import CodonUsage from 'shared/components/CodonUsage'
import InputMutations from './components/InputMutations'
import { validateAvoidMotifs, validateSequence } from 'shared/components/FormValidation'

type PASFormOuterProps = {
  disabled: boolean
}

type PASFormInnerProps = PASFormOuterProps & WithFormInnerProps<PASFormData>

const { Option } = Select
const motifsJSON = require('shared/motifs.json')
const motifsOptions: any[] = motifsJSON.map((element: string) => <Option key={element}>{element}</Option>)

const PASForm: React.FC<PASFormInnerProps> = ({ form, disabled, data }) => {
  const [showGoiWarning, setShowGoiWarning] = React.useState(false)
  const [isMutationsReset, setIsMutationsReset] = React.useState(false)

  const {
    control,
    setValue,
    getValues,
    reset,
    formState: { errors },
  } = form

  const inputSequenceType = useWatch({ control, name: 'inputSequenceType', defaultValue: 'dna' })

  const resetForm = (event: React.FormEvent<any>) => {
    event.preventDefault()
    reset()
    setIsMutationsReset(true)
  }

  const resetParameters = (event: React.FormEvent<any>) => {
    event.preventDefault()
    setValue('oligoLengthMin', 40)
    setValue('oligoLengthOpt', 40)
    setValue('oligoLengthMax', 60)
    setValue('overlappingTmMin', 54)
    setValue('overlappingTmOpt', 56)
    setValue('overlappingTmMax', 64)
    setValue('overlappingLengthMin', 18)
    setValue('overlappingLengthOpt', 21)
    setValue('overlappingLengthMax', 30)
    setValue('gcContentMin', 40)
    setValue('gcContentOpt', 40)
    setValue('gcContentMax', 60)
    setValue('computeHairpinHomodimer', true)
  }

  const handleResetMutations = () => {
    setIsMutationsReset(false)
  }

  const onFileUpload = (target: string) => (data: string) => {
    setValue(target as keyof PASFormData, data as any)
  }

  const onGoiChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const inputType = getValues('inputSequenceType')
    if (inputType === 'dna') {
      setShowGoiWarning(!(event.target.value || '').match(/^ATG|atg/))
    } else {
      setShowGoiWarning(!(event.target.value || '').match(/^M|m/))
    }
  }

  const handleInputSequenceTypeChange = (event: any) => {
    setValue('inputSequenceType', event.target.value)
    const goi = getValues('goiSequence')
    setValue('goiSequence', goi)
  }

  const sequenceValidator = (value: string) => {
    const inputType = getValues('inputSequenceType')
    return validateSequence(value, inputType === 'dna')
  }

  React.useEffect(() => {
    const inputMutations = data.inputMutations && data.inputMutations.mutations
    if (inputMutations && inputMutations.length > 0) {
      setValue('inputMutations', { mutations: [...inputMutations] })
    }
  }, [data.inputMutations, setValue])

  return (
    <>
      <FormSection index={1} title="Sequence">
        <Tooltip placement="rightTop" title="Enter 5'-end flanking sequence.">
          <Form.Item label="Five Prime Flanking Sequence" hasFeedback>
            <Controller
              name="fivePrimeFlankingSequence"
              control={control}
              rules={{ validate: (v) => geneValidationRule.validator(null as any, v, () => null) }}
              render={({ field }) => <Input.TextArea {...field} rows={2} />}
            />
          </Form.Item>
        </Tooltip>
        <Tooltip placement="rightTop" title="Select the GOI input sequence format.">
          <Form.Item label="Gene of Interest Sequence">
            <Controller
              name="inputSequenceType"
              control={control}
              defaultValue="dna"
              render={({ field }) => (
                <Radio.Group {...field} onChange={(e) => { field.onChange(e); handleInputSequenceTypeChange(e) }}>
                  <Radio.Button value="dna">DNA</Radio.Button>
                  <Radio.Button value="protein">Protein</Radio.Button>
                </Radio.Group>
              )}
            />
          </Form.Item>
        </Tooltip>
        <Tooltip
          placement="topRight"
          title={'Enter or Upload Gene of Interest sequence. Allowed values: ' + (inputSequenceType === 'dna' ? 'A, C, G and T' : 'F, L, I, M, V, S, G, T, A, Y, H, Q, N, K, D, E, C, W, R, P')}
        >
          <Form.Item className="GeneTextArea" hasFeedback validateStatus={errors.goiSequence ? 'error' : undefined} help={errors.goiSequence?.message?.toString()}>
            <FileUploadInput onChange={onFileUpload('goiSequence')} />
            <Controller
              name="goiSequence"
              control={control}
              rules={{
                required: 'Input Sequence is required',
                validate: sequenceValidator,
              }}
              render={({ field }) => <Input.TextArea {...field} rows={8} onChange={(e) => { field.onChange(e); onGoiChange(e) }} />}
            />
            {showGoiWarning && (
              <div className="has-warning noIcon">
                <div className="ant-form-explain">Gene of Interest should begin with {inputSequenceType === 'dna' ? ' ATG' : ' M'}</div>
              </div>
            )}
          </Form.Item>
        </Tooltip>
        <Tooltip title="Enter 3'-end flanking sequence.">
          <Form.Item label="Three Prime Flanking Sequence" hasFeedback>
            <Controller
              name="threePrimeFlankingSequence"
              control={control}
              rules={{ validate: (v) => geneValidationRule.validator(null as any, v, () => null) }}
              render={({ field }) => <Input.TextArea {...field} rows={2} />}
            />
          </Form.Item>
        </Tooltip>
      </FormSection>

      <InputMutations
        inputMutations={data.inputMutations}
        isMutationsReset={isMutationsReset}
        handleResetMutations={handleResetMutations}
        index={2}
        form={form}
      />

      <FormSection index={3} title="Degenerate Codon" open={false}>
        <Tooltip title="Select usage of degenerate codons">
          <Form.Item label="Use Degeneracy Codon">
            <Controller
              name="useDegeneracyCodon"
              control={control}
              defaultValue={false}
              render={({ field }) => <Switch {...field} checked={field.value} />}
            />
          </Form.Item>
        </Tooltip>
      </FormSection>

      <CodonUsage index={4} form={form} />

      <FormSection index={5} title="Avoid Motifs" open={false}>
        <Form.Item>
          <Tooltip placement="topRight" title="Select from the list or input your own sites to be excluded from oligonucleotide fragments.">
            <Controller
              name="avoidMotifs"
              control={control}
              rules={{ validate: (v) => validateAvoidMotifs(v) }}
              render={({ field }) => (
                <Select {...field} mode="tags" placeholder="None">
                  {motifsOptions}
                </Select>
              )}
            />
          </Tooltip>
        </Form.Item>
      </FormSection>

      <FormSection index={6} title="Parameters" open={false}>
        <Tooltip title="Enter oligo length of an entire primer">
          <Form.Item label="Oligo Length (bp)">
            <MinOptMaxInputs form={form} fieldPrefix="oligoLength" defaults={{ min: 40, opt: 40, max: 60 }} />
          </Form.Item>
        </Tooltip>
        <Tooltip title="Enter overlapping melting temperature of the primer">
          <Form.Item label="Overlapping Tm (°C)">
            <MinOptMaxInputs form={form} fieldPrefix="overlappingTm" defaults={{ min: 54, opt: 56, max: 64 }} optimalPresent />
          </Form.Item>
        </Tooltip>
        <Tooltip title="Enter Overlapping Length of the primer">
          <Form.Item label="Overlapping length (bp)">
            <MinOptMaxInputs form={form} fieldPrefix="overlappingLength" defaults={{ min: 18, opt: 21, max: 30 }} optimalPresent />
          </Form.Item>
        </Tooltip>
        <Tooltip title="Enter the percentage of guanine or cytosine in the primers">
          <Form.Item label="GC Content (%)">
            <MinOptMaxInputs form={form} fieldPrefix="gcContent" defaults={{ min: 40, opt: 40, max: 60 }} />
          </Form.Item>
        </Tooltip>
        <Row gutter={10}>
          <Col>
            <Tooltip title="Toggles whether the fast primer extension algorithm calculates hairpin and primer-dimer temperatures.">
              <Form.Item label="Check for hairpins and primer-dimers">
                <Controller
                  name="computeHairpinHomodimer"
                  control={control}
                  defaultValue={true}
                  render={({ field }) => <Switch {...field} checked={field.value} />}
                />
              </Form.Item>
            </Tooltip>
          </Col>
        </Row>
        <Tooltip title="Reset Parameters to default values">
          <Button type="default" htmlType="reset" icon={<ReloadOutlined />} onClick={resetParameters}>
            Reset
          </Button>
        </Tooltip>
      </FormSection>

      <FormSection index={7} title="File name" open={false}>
        <Tooltip title="Type name of the export report">
          <Form.Item label="Enter file name" hasFeedback>
            <Controller name="fileName" control={control} render={({ field }) => <Input {...field} />} />
          </Form.Item>
        </Tooltip>
      </FormSection>

      <FormSection index={8} title="Oligo prefix" open={false}>
        <Tooltip title="Type oligo prefix to be used in the export report">
          <Form.Item label="Enter oligo prefix" hasFeedback>
            <Controller name="oligoPrefix" control={control} render={({ field }) => <Input {...field} />} />
          </Form.Item>
        </Tooltip>
      </FormSection>

      <FormSection collapse={false}>
        <Form.Item className="DataInputForm-submitRow">
          <Button.Group>
            <Tooltip title="Design primers">
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />} id="submit_pas_btn">
                Submit
              </Button>
            </Tooltip>
            <Tooltip title="Clear the form">
              <Button type="default" htmlType="reset" icon={<ReloadOutlined />} disabled={disabled} onClick={resetForm}>
                Reset
              </Button>
            </Tooltip>
          </Button.Group>
        </Form.Item>
      </FormSection>
    </>
  )
}

export default withForm<PASFormOuterProps, PASFormData>(PASForm)
