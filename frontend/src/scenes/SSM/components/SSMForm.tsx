import { ReloadOutlined, SaveOutlined } from '@ant-design/icons'
import { Button, Form, Input, Radio, Select, Tooltip } from 'antd'
import * as R from 'ramda'
import * as React from 'react'
import { Controller, useWatch } from 'react-hook-form'
import AminoAcidInput, { AminoType } from 'shared/components/AminoAcidInput'
import FileUploadInput from 'shared/components/FileUploadInput'
import FormSection from 'shared/components/FormSection'
import { validateMutations } from 'shared/components/FormValidation'
import MutationsInput from 'shared/components/MutationsInput'
import ParametersFormSection from 'shared/components/ParametersFormSection'
import { endsWithStopCodonValidationRule, geneValidationRule } from 'shared/form'
import { getForwardPrimer, getReversePrimer, PrimersType } from 'shared/genes'
import { SSMFormData } from 'shared/lib/FormData'
import withForm, { WithFormInnerProps } from 'shared/withForm'
import { getDegenerateCodons } from './aminoAcidCodons'

type SSMFormOuterProps = {
  disabled: boolean
}

type SSMFormInnerProps = SSMFormOuterProps & WithFormInnerProps<SSMFormData>

const DEFAULT_PRIMERS_TYPE = PrimersType.pETseq1

const defaultAminoAcids = [
  { name: 'F', state: '' },
  { name: 'L', state: '' },
  { name: 'I', state: '' },
  { name: 'V', state: '' },
  { name: 'S', state: '' },
  { name: 'P', state: '' },
  { name: 'T', state: '' },
  { name: 'A', state: '' },
  { name: 'Y', state: '' },
  { name: 'H', state: '' },
  { name: 'Q', state: '' },
  { name: 'M', state: '' },
  { name: 'N', state: '' },
  { name: 'K', state: '' },
  { name: 'D', state: '' },
  { name: 'E', state: '' },
  { name: 'C', state: '' },
  { name: 'W', state: '' },
  { name: 'R', state: '' },
  { name: 'G', state: '' },
]

const complementTable: { [key: string]: string } = {
  A: 'T',
  C: 'G',
  G: 'C',
  T: 'A',
  I: 'I',
  R: 'Y',
  Y: 'R',
  M: 'K',
  K: 'M',
  S: 'S',
  W: 'W',
  H: 'D',
  B: 'V',
  V: 'B',
  D: 'H',
  N: 'N',
}

const reverseComplement = (sequence: string): string => {
  const reversed = sequence.split('').reverse().join('')
  return reversed
    .split('')
    .map((x) => complementTable[x])
    .join('')
}

const SSMForm: React.FC<SSMFormInnerProps> = ({ form, disabled }) => {
  const [generateCodonOrAminoAcidTab, setGenerateCodonOrAminoAcidTab] = React.useState('Degenerate Codon')
  const [aminoAcids, setAminoAcids] = React.useState([...defaultAminoAcids])
  const [loading, setLoading] = React.useState(false)
  const [showGoiWarning, setShowGoiWarning] = React.useState(false)

  const {
    control,
    setValue,
    getValues,
    reset,
    formState: { errors },
  } = form

  const primersType = useWatch({ control, name: 'primersType' }) as PrimersType | undefined
  const degenerateCodon = useWatch({ control, name: 'degenerateCodon' }) as string | undefined

  const handleTabChange = (event?: any) => {
    setGenerateCodonOrAminoAcidTab(event.target.value)
  }

  const handleAminoChange = (newAminoAcids: AminoType[]) => {
    setAminoAcids(newAminoAcids)
    setLoading(true)
    getDegenerateCodons(
      newAminoAcids.filter((amino: AminoType) => amino.state === 'include').map(R.prop('name')),
      newAminoAcids.filter((amino: AminoType) => amino.state === 'avoid').map(R.prop('name')),
    )
      .then((degenerateCodon) => {
        setValue('degenerateCodon', degenerateCodon)
        setLoading(false)
      })
      .catch(() => {
        console.warn('error in getDegenerateCodons promise')
        setLoading(false)
      })
  }

  const resetForm = (event: React.FormEvent<any>) => {
    event.preventDefault()
    setAminoAcids([...defaultAminoAcids])
    reset()
  }

  const onPrimersTypeChange = (newPrimersType: PrimersType) => {
    setValue('forwardPrimerValue', getForwardPrimer(newPrimersType))
    setValue('reversePrimerValue', getReversePrimer(newPrimersType))
  }

  const onInputChange = (target: string) => (data: string) => {
    setValue(target as keyof SSMFormData, data as any)
  }

  const onGoiChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const goiStr = event.target.value || ''
    const hasStartCodon = goiStr.match(/^ATG/)
    const hasStopCodon = goiStr.match(/TAA$/) || goiStr.match(/TAG$/) || goiStr.match(/TGA$/)
    setShowGoiWarning(!hasStartCodon || !hasStopCodon)
  }

  const goiIsSubstringOfPlasmid = (value: string) => {
    const plasmid = getValues('plasmidSequence')
    return plasmid.indexOf(value) === -1 ? 'Gene of Interest must be a substring of plasmid.' : undefined
  }

  const flankingPrimerIsSubstringOfPlasmid = (value: string) => {
    const plasmid = getValues('plasmidSequence')
    return plasmid.indexOf(value) === -1 ? 'Forward flanking primer must be a substring of plasmid.' : undefined
  }

  const reverseComplementFlankingPrimerIsSubstringOfPlasmid = (value: string) => {
    const plasmid = getValues('plasmidSequence')
    return plasmid.indexOf(reverseComplement(value)) === -1
      ? 'Reverse flanking primer must be a substring of plasmid.'
      : undefined
  }

  const validateMutationField = (value: string) => {
    const goi = getValues('goiSequence')
    return validateMutations(value, goi)
  }

  return (
    <>
      <FormSection index={1} title="Plasmid">
        <Tooltip title="Enter or Upload Plasmid sequence containing flanking primers and Gene of Interest sequence.">
          <Form.Item
            label="Plasmid Sequence"
            className="GeneTextArea"
            hasFeedback
            validateStatus={errors.plasmidSequence ? 'error' : undefined}
            help={errors.plasmidSequence?.message?.toString()}
          >
            <FileUploadInput onChange={onInputChange('plasmidSequence')} />
            <Controller
              name="plasmidSequence"
              control={control}
              rules={{
                required: 'Plasmid Sequence is required',
                validate: { geneValidation: (v) => geneValidationRule.validator(null as any, v, () => null) },
              }}
              render={({ field }) => <Input.TextArea {...field} rows={6} />}
            />
          </Form.Item>
        </Tooltip>
      </FormSection>

      <FormSection index={2} title="Sequence">
        <Tooltip title="Enter or Upload Gene of Interest sequence.">
          <Form.Item
            label="Gene of Interest Sequence"
            className="GeneTextArea"
            hasFeedback
            validateStatus={errors.goiSequence ? 'error' : undefined}
            help={errors.goiSequence?.message?.toString()}
          >
            <FileUploadInput onChange={onInputChange('goiSequence')} />
            <Controller
              name="goiSequence"
              control={control}
              rules={{
                required: 'Gene of Interest Sequence is required',
                validate: {
                  substring: goiIsSubstringOfPlasmid,
                  geneValidation: (v) => geneValidationRule.validator(null as any, v, () => null),
                  stopCodon: (v) => endsWithStopCodonValidationRule.validator(null as any, v, () => null),
                },
              }}
              render={({ field }) => <Input.TextArea {...field} rows={8} onChange={(e) => { field.onChange(e); onGoiChange(e) }} />}
            />
            {showGoiWarning && (
              <div className="has-warning noIcon">
                <div className="ant-form-explain">
                  Gene of Interest should begin with ATG and end with TAA, TAG or TGA.
                </div>
              </div>
            )}
          </Form.Item>
        </Tooltip>
      </FormSection>

      <FormSection index={3} title="Mutations">
        <Tooltip title="Enter mutations in following format [Amino Acid Codon][Location][X]">
          <Form.Item
            label="Mutations"
            className="MutationsTextArea"
            hasFeedback
            validateStatus={errors.mutations ? 'error' : undefined}
            help={errors.mutations?.message?.toString()}
          >
            <Controller
              name="mutations"
              control={control}
              rules={{
                required: 'Mutations are required',
                pattern: { value: /^\s*([A-Z][0-9]*[A-Z])(\s+[A-Z][0-9]*[A-Z]\s*)*$/i, message: 'Invalid mutation format' },
                validate: validateMutationField,
              }}
              render={({ field }) => <MutationsInput {...field} cols={11} />}
            />
          </Form.Item>
        </Tooltip>
      </FormSection>

      <FormSection index={4} title="Flanking primers">
        <Tooltip title="Select forward and reverse flanking primers from a list or enter custom primer sequences.">
          <Form.Item label="Primers Type" hasFeedback>
            <Controller
              name="primersType"
              control={control}
              defaultValue={DEFAULT_PRIMERS_TYPE}
              render={({ field }) => (
                <Select {...field} onChange={(val) => { field.onChange(val); onPrimersTypeChange(val as PrimersType) }}>
                  <Select.Option key={PrimersType.pETseq1}>pET SeqF1 / SeqR1</Select.Option>
                  <Select.Option key={PrimersType.custom}>Custom</Select.Option>
                </Select>
              )}
            />
          </Form.Item>
          <Form.Item
            label="Forward Primer"
            hasFeedback
            validateStatus={errors.forwardPrimerValue ? 'error' : undefined}
            help={errors.forwardPrimerValue?.message?.toString()}
          >
            <Controller
              name="forwardPrimerValue"
              control={control}
              defaultValue={getForwardPrimer(DEFAULT_PRIMERS_TYPE)}
              rules={{
                required: 'Forward Primer is required',
                max: { value: 60, message: 'Max 60 characters' },
                validate: {
                  geneValidation: (v) => geneValidationRule.validator(null as any, v, () => null),
                  substring: flankingPrimerIsSubstringOfPlasmid,
                },
              }}
              render={({ field }) => <Input {...field} disabled={primersType !== PrimersType.custom} />}
            />
          </Form.Item>
          <Form.Item
            label="Reverse Primer"
            hasFeedback
            validateStatus={errors.reversePrimerValue ? 'error' : undefined}
            help={errors.reversePrimerValue?.message?.toString()}
          >
            <Controller
              name="reversePrimerValue"
              control={control}
              defaultValue={getReversePrimer(DEFAULT_PRIMERS_TYPE)}
              rules={{
                required: 'Reverse Primer is required',
                max: { value: 60, message: 'Max 60 characters' },
                validate: {
                  geneValidation: (v) => geneValidationRule.validator(null as any, v, () => null),
                  substring: reverseComplementFlankingPrimerIsSubstringOfPlasmid,
                },
              }}
              render={({ field }) => <Input {...field} disabled={primersType !== PrimersType.custom} />}
            />
          </Form.Item>
        </Tooltip>
      </FormSection>

      <FormSection index={5} title="Parameters" tooltip="Enter primers parameters" open={false}>
        <ParametersFormSection form={form} />
      </FormSection>

      <FormSection index={6} title="Degenerate codons or Amino acids" open={false}>
        <Radio.Group defaultValue="Degenerate Codon" onChange={handleTabChange}>
          <Radio.Button value="Degenerate Codon">Degenerate Codon</Radio.Button>
          <Radio.Button value="Amino acids">Amino acids</Radio.Button>
          <p className="codon-info">Select what you want to enter</p>
        </Radio.Group>
        <Form.Item
          hasFeedback
          className={generateCodonOrAminoAcidTab !== 'Degenerate Codon' ? 'hidden' : ''}
          validateStatus={errors.degenerateCodon ? 'error' : undefined}
          help={errors.degenerateCodon?.message?.toString()}
        >
          <Tooltip title="Type a degenerate codon.">
            <Controller
              name="degenerateCodon"
              control={control}
              defaultValue="NNK"
              rules={{
                required: 'Degenerate codon is required',
                pattern: {
                  value: /^[ABCDGHKMNRSTUVWY]{3}(,[ABCDGHKMNRSTUVWY]{3})*$/,
                  message: 'Must consist of exactly three letters from A, B, C, D, G, H, K, M, N, R, S, T, U, V, W, Y',
                },
              }}
              render={({ field }) => <Input {...field} />}
            />
          </Tooltip>
        </Form.Item>
        <Form.Item className={generateCodonOrAminoAcidTab !== 'Amino acids' ? 'hidden' : ''}>
          <div>
            <b>Degenerate Codon:</b> {degenerateCodon}
          </div>
          <AminoAcidInput value={aminoAcids} onChange={handleAminoChange} loading={loading} />
        </Form.Item>
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
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />} id="submit_ssm_btn">
                Submit
              </Button>
            </Tooltip>
            <Tooltip title="Clear the form">
              <Button
                type="default"
                id="rest_ssm_btn"
                htmlType="reset"
                icon={<ReloadOutlined />}
                disabled={disabled}
                onClick={resetForm}
              >
                Reset
              </Button>
            </Tooltip>
          </Button.Group>
        </Form.Item>
      </FormSection>
    </>
  )
}

export default withForm<SSMFormOuterProps, SSMFormData>(SSMForm)
