import { ReloadOutlined, SaveOutlined } from '@ant-design/icons'
import { Button, Col, Form, Input, Row, Slider, Switch, Tooltip } from 'antd'
import * as React from 'react'
import { Controller, UseFormReturn } from 'react-hook-form'
import FileUploadInput from 'shared/components/FileUploadInput'
import FormSection from 'shared/components/FormSection'
import { validateMutations } from 'shared/components/FormValidation'
import MinOptMaxInputs from 'shared/components/MinOptMaxInputs'
import MutationsInput from 'shared/components/MutationsInput'
import { endsWithStopCodonValidationRule, geneValidationRule } from 'shared/form'
import { QCLMFormData } from 'shared/lib/FormData'
import withForm, { WithFormInnerProps } from 'shared/withForm'
import CodonUsage from 'shared/components/CodonUsage'

type QCLMFormOuterProps = {
  disabled: boolean
}

type QCLMFormInnerProps = QCLMFormOuterProps & WithFormInnerProps<QCLMFormData>

const stepsZeroSixteen = { 0: '0', 1: '1', 2: '2', 4: '4', 8: '8', 16: '16' }
const stepsZeroSixtyfour = { 0: '0', 4: '4', 8: '8', 16: '16', 32: '32', 64: '64' }
const stepsZeroThreeHundredtwenty = { 0: '0', 80: '80', 160: '160', 240: '240', 320: '320' }

const QCLMForm: React.FC<QCLMFormInnerProps> = ({ form, disabled }) => {
  const [showGoiWarning, setShowGoiWarning] = React.useState(false)

  const {
    control,
    setValue,
    getValues,
    reset,
    formState: { errors },
  } = form as UseFormReturn<QCLMFormData>

  const resetForm = (event: React.FormEvent<any>) => {
    event.preventDefault()
    reset()
  }

  const onInputChange = (target: string) => (data: string) => {
    setValue(target as keyof QCLMFormData, data as any)
  }

  const onGoiChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setShowGoiWarning(!(event.target.value || '').match(/^ATG/))
  }

  const validateMutationField = (value: string) => {
    const goi = getValues('goiSequence')
    const result = validateMutations(value, goi)
    return result.length > 0 ? result[0] : undefined
  }

  return (
    <>
      <FormSection index={1} title="Sequence">
        <Tooltip title="Enter 5'-end flanking sequence.">
          <Form.Item label="Five Prime Flanking Sequence" hasFeedback>
            <Controller
              name="fivePrimeFlankingSequence"
              control={control}
              rules={{ validate: (v) => geneValidationRule.validator?.(null as any, v, () => null) || true }}
              render={({ field }) => <Input.TextArea {...field} rows={2} />}
            />
          </Form.Item>
        </Tooltip>
        <Tooltip title="Enter or Upload Gene of Interest sequence.">
          <Form.Item
            label="Gene of Interest Sequence"
            className="GeneTextArea"
            hasFeedback
            validateStatus={errors.goiSequence ? 'error' : undefined}
            help={errors.goiSequence?.message}
          >
            <FileUploadInput onChange={onInputChange('goiSequence')} />
            <Controller
              name="goiSequence"
              control={control}
              rules={{
                required: 'Gene of Interest Sequence is required',
                validate: {
                  geneValidation: (v) => geneValidationRule.validator?.(null as any, v, () => null) || true,
                  stopCodon: (v) => endsWithStopCodonValidationRule.validator?.(null as any, v, () => null) || true,
                },
              }}
              render={({ field }) => <Input.TextArea {...field} rows={8} onChange={(e) => { field.onChange(e); onGoiChange(e) }} />}
            />
            {showGoiWarning && (
              <div className="has-warning noIcon">
                <div className="ant-form-explain">Gene of Interest should begin with ATG</div>
              </div>
            )}
          </Form.Item>
        </Tooltip>
        <Tooltip title="Enter 3'-end flanking sequence.">
          <Form.Item label="Three Prime Flanking Sequence" hasFeedback>
            <Controller
              name="threePrimeFlankingSequence"
              control={control}
              rules={{ validate: (v) => geneValidationRule.validator?.(null as any, v, () => null) || true }}
              render={({ field }) => <Input.TextArea {...field} rows={2} />}
            />
          </Form.Item>
        </Tooltip>
      </FormSection>

      <FormSection index={2} title="Mutations">
        <Tooltip title="Enter mutations in following format [Amino Acid Codon][Location][Amino Acid Codon]">
          <Form.Item
            label="Mutations"
            className="MutationsTextArea"
            hasFeedback
            validateStatus={errors.mutations ? 'error' : undefined}
            help={errors.mutations?.message}
          >
            <Controller
              name="mutations"
              control={control}
              rules={{
                required: 'Mutations are required',
                pattern: { value: /^\s*([A-Z][0-9]*[A-Z])(\s+[A-Z][0-9]*[A-Z]\s*)*$/i, message: 'Invalid format' },
                validate: validateMutationField,
              }}
              render={({ field }) => <MutationsInput {...field} cols={11} />}
            />
          </Form.Item>
        </Tooltip>
      </FormSection>

      <CodonUsage index={3} form={form} />

      <FormSection index={4} title="Parameters" open={false}>
        <Tooltip title="Enter size of an entire primer">
          <Form.Item label="Size">
            <MinOptMaxInputs form={form} fieldPrefix="size" defaults={{ min: 33, opt: 33, max: 60 }} />
          </Form.Item>
        </Tooltip>
        <Tooltip title="Enter size of a 3'-end of the primer">
          <Form.Item label="3' Size">
            <MinOptMaxInputs form={form} fieldPrefix="threePrimeSize" defaults={{ min: 15, opt: 15, max: 40 }} />
          </Form.Item>
        </Tooltip>
        <Tooltip title="Enter size of a 5'-end of the primer">
          <Form.Item label="5' Size">
            <MinOptMaxInputs form={form} fieldPrefix="fivePrimeSize" defaults={{ min: 15, opt: 15, max: 40 }} />
          </Form.Item>
        </Tooltip>
        <Tooltip title="Enter the percentage of guanine or cytosine in the primers">
          <Form.Item label="GC Content">
            <MinOptMaxInputs form={form} fieldPrefix="gcContent" defaults={{ min: 40, opt: 50, max: 60 }} />
          </Form.Item>
        </Tooltip>
        <Tooltip title="Enter temperature of entire primers">
          <Form.Item label="Temperature">
            <MinOptMaxInputs form={form} fieldPrefix="temperature" defaults={{ min: 75, opt: 78, max: 90 }} />
          </Form.Item>
        </Tooltip>

        <Row gutter={10}>
          <Col span={12}>
            <Tooltip title="Specify the importance of entire primer temperature">
              <Form.Item label="Temperature Weight">
                <Controller
                  name="temperatureWeight"
                  control={control}
                  defaultValue={16}
                  render={({ field }) => <Slider {...field} marks={stepsZeroSixteen} min={0} max={16} step={null} />}
                />
              </Form.Item>
            </Tooltip>
          </Col>
          <Col span={12}>
            <Tooltip title="Specify the importance of entire primer size">
              <Form.Item label="Total Primer Size Weight">
                <Controller
                  name="totalSizeWeight"
                  control={control}
                  defaultValue={4}
                  render={({ field }) => <Slider {...field} marks={stepsZeroSixteen} min={0} max={16} step={null} />}
                />
              </Form.Item>
            </Tooltip>
          </Col>
        </Row>

        <Row gutter={10}>
          <Col span={12}>
            <Tooltip title="Specify the importance of the 3'-end size">
              <Form.Item label="3' Size Weight">
                <Controller
                  name="threePrimeSizeWeight"
                  control={control}
                  defaultValue={8}
                  render={({ field }) => <Slider {...field} marks={stepsZeroSixteen} min={0} max={16} step={null} />}
                />
              </Form.Item>
            </Tooltip>
          </Col>
          <Col span={12}>
            <Tooltip title="Specify the importance of 5' Size">
              <Form.Item label="5' Size Weight">
                <Controller
                  name="fivePrimeSizeWeight"
                  control={control}
                  defaultValue={1}
                  render={({ field }) => <Slider {...field} marks={stepsZeroSixteen} min={0} max={16} step={null} />}
                />
              </Form.Item>
            </Tooltip>
          </Col>
        </Row>

        <Row gutter={10}>
          <Col span={12}>
            <Tooltip title="Specify the importance of the GC Content">
              <Form.Item label="GC Content Weight">
                <Controller
                  name="gcContentWeight"
                  control={control}
                  defaultValue={0}
                  render={({ field }) => <Slider {...field} marks={stepsZeroSixteen} min={0} max={16} step={null} />}
                />
              </Form.Item>
            </Tooltip>
          </Col>
          <Col span={12}>
            <Tooltip title="Specify the importance of Hairpin Temperature">
              <Form.Item label="Hairpin Temperature Weight">
                <Controller
                  name="hairpinTemperatureWeight"
                  control={control}
                  defaultValue={32}
                  render={({ field }) => <Slider {...field} marks={stepsZeroSixtyfour} min={0} max={64} step={null} />}
                />
              </Form.Item>
            </Tooltip>
          </Col>
        </Row>

        <Row gutter={10}>
          <Col span={12}>
            <Tooltip title="Specify the importance of Primer-dimer Temperature">
              <Form.Item label="Primer-dimer Temperature Weight">
                <Controller
                  name="primerDimerTemperatureWeight"
                  control={control}
                  defaultValue={32}
                  render={({ field }) => <Slider {...field} marks={stepsZeroSixtyfour} min={0} max={64} step={null} />}
                />
              </Form.Item>
            </Tooltip>
          </Col>
          <Col span={12}>
            <Tooltip title="Specify the importance of Mutation coverage">
              <Form.Item label="Mutation Coverage Weight">
                <Controller
                  name="mutationCoverageWeight"
                  control={control}
                  defaultValue={160}
                  render={({ field }) => <Slider {...field} marks={stepsZeroThreeHundredtwenty} min={0} max={320} step={null} />}
                />
              </Form.Item>
            </Tooltip>
          </Col>
        </Row>

        <Row gutter={10}>
          <Tooltip title="Enter maximum temperature difference between entire primers">
            <Form.Item label="Max Temperature Difference" hasFeedback validateStatus={errors.maxTemperatureDifference ? 'error' : undefined} help={errors.maxTemperatureDifference?.message}>
              <Controller
                name="maxTemperatureDifference"
                control={control}
                defaultValue={5}
                rules={{ required: 'Max Temperature Difference is required' }}
                render={({ field }) => <Input {...field} type="number" />}
              />
            </Form.Item>
          </Tooltip>
        </Row>
        <Row gutter={10}>
          <Col span={12}>
            <Tooltip title="Toggles whether the fast primer extension algorithm calculates hairpin and primer-dimer temperatures.">
              <Form.Item label="Check for hairpins and primer-dimers">
                <Controller
                  name="usePrimer3"
                  control={control}
                  defaultValue={false}
                  render={({ field }) => <Switch {...field} checked={field.value} />}
                />
              </Form.Item>
            </Tooltip>
          </Col>
          <Col span={12}>
            <Tooltip title="Search only for solutions with no overlaps between primers">
              <Form.Item label="Non-overlapping primers only">
                <Controller
                  name="nonOverlappingPrimers"
                  control={control}
                  defaultValue={false}
                  render={({ field }) => <Switch {...field} checked={field.value} />}
                />
              </Form.Item>
            </Tooltip>
          </Col>
        </Row>
      </FormSection>

      <FormSection index={5} title="Degenerate Codon" open={false}>
        <Tooltip title="Select usage of degenerate codons">
          <Form.Item label="Use Degeneracy Codon">
            <Controller
              name="useDegeneracyCodon"
              control={control}
              defaultValue={true}
              render={({ field }) => <Switch {...field} checked={field.value} />}
            />
          </Form.Item>
        </Tooltip>
      </FormSection>

      <FormSection index={6} title="File name" open={false}>
        <Tooltip title="Type name of the export report">
          <Form.Item label="Enter file name" hasFeedback>
            <Controller name="fileName" control={control} render={({ field }) => <Input {...field} />} />
          </Form.Item>
        </Tooltip>
      </FormSection>

      <FormSection index={7} title="Oligo prefix" open={false}>
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
              <Button type="primary" htmlType="submit" icon={<SaveOutlined />} id="submit_qclm_btn">
                Submit
              </Button>
            </Tooltip>
            <Tooltip title="Clear the form">
              <Button type="default" id="reset_qclm_btn" htmlType="reset" icon={<ReloadOutlined />} disabled={disabled} onClick={resetForm}>
                Reset
              </Button>
            </Tooltip>
          </Button.Group>
        </Form.Item>
      </FormSection>
    </>
  )
}

export default withForm<QCLMFormOuterProps, QCLMFormData>(QCLMForm)
