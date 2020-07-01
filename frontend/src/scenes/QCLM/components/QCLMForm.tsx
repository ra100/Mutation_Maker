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

import {
  Button,
  Col,
  Form,
  Input,
  message,
  Row,
  Slider,
  Switch,
  Tooltip,
} from 'antd'
import * as React from 'react'
import FileUploadInput from 'shared/components/FileUploadInput'
import FormSection from 'shared/components/FormSection'
import {validateMutations} from 'shared/components/FormValidation'
import MinOptMaxInputs from 'shared/components/MinOptMaxInputs'
import MutationsInput from 'shared/components/MutationsInput'
import {endsWithStopCodonValidationRule, geneValidationRule} from 'shared/form'
import {QCLMFormData} from 'shared/lib/FormData'
import withForm, {WithFormInnerProps} from 'shared/withForm'
import CodonUsage from "shared/components/CodonUsage";

type QCLMFormOuterProps = {
  disabled: boolean
}

type QCLMFormInnerProps = QCLMFormOuterProps & WithFormInnerProps<QCLMFormData>

class QCLMForm extends React.Component<QCLMFormInnerProps> {
  state = {
    showGoiWarning: false,
    customCodonUsage: '',
    isCodonUsageDisabled: true,
    isCodonUsageLoading: false,
    codonUsageData: [],
  };
  timeout: number = 0;

  stepsZeroSixteen = {
    0: '0',
    1: '1',
    2: '2',
    4: '4',
    8: '8',
    16: '16',
  };

  stepsZeroSixtyfour = {
    0: '0',
    4: '4',
    8: '8',
    16: '16',
    32: '32',
    64: '64',
  };

  stepsZeroThreeHundredtwenty = {
    0: '0',
    80: '80',
    160: '160',
    240: '240',
    320: '320'
  };

  onSubmit = (event: React.FormEvent<any>) => {
    event.preventDefault();
    const {form, onSubmit} = this.props;

    form.validateFields((error: any, values: QCLMFormData) => {
      if (!error) {
        onSubmit(values)
      } else {
        message.error('Validation failed');
        // tslint:disable-next-line no-console
        console.error(error)
      }
    })
  };

  resetForm = (event: React.FormEvent<any>) => {
    event.preventDefault();
    const {form} = this.props;
    form.resetFields()
  };

  onInputChange = (target: string) => (data: string) => {
    const {setFieldsValue, validateFields} = this.props.form;
    setFieldsValue({
      [target]: data,
    });
    validateFields()
  };

  onGoiChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    this.setState({showGoiWarning: !(event.target.value || '').match(/^ATG/)})
  };

  clearTimeout = () => {
    if (this.timeout) {
      clearTimeout(this.timeout)
    }
  };

  render() {
    const {form, disabled} = this.props;
    const {getFieldDecorator, getFieldValue, resetFields} = form;

    return (
      <Form layout="vertical" onSubmit={this.onSubmit}>
        <FormSection index={1} title="Sequence">
          <Tooltip
            title="Enter 5'-end flanking sequence. Only A, C, G and T are allowed in the sequence.">
            <React.Fragment/>
            <Form.Item label="Five Prime Flanking Sequence" hasFeedback>
              {getFieldDecorator('fivePrimeFlankingSequence', {
                rules: [geneValidationRule],
              })(<Input.TextArea rows={2}/>)}
            </Form.Item>
          </Tooltip>
          <Tooltip
            title="Enter or Upload Gene of Interest sequence. Only A, C, G and T are allowed in the sequence.">
            <React.Fragment/>
            <Form.Item label="Gene of Interest Sequence"
                       className="GeneTextArea" hasFeedback>
              <FileUploadInput onChange={this.onInputChange('goiSequence')}/>
              {getFieldDecorator('goiSequence', {
                rules: [
                  {
                    required: true,
                    message: 'Gene of Interest Sequence is required',
                  },
                  geneValidationRule,
                  endsWithStopCodonValidationRule,
                ],
              })(<Input.TextArea rows={8} onChange={this.onGoiChange}/>)}
              {this.state.showGoiWarning && <div className="has-warning noIcon">
                <div className="ant-form-explain">Gene of Interest should begin
                  with ATG
                </div>
              </div>}
            </Form.Item>
          </Tooltip>
          <Tooltip
            title="Enter 3'-end flanking sequence. Only A, C, G and T are allowed is the sequence.">
            <React.Fragment/>
            <Form.Item label="Three Prime Flanking Sequence" hasFeedback>
              {getFieldDecorator('threePrimeFlankingSequence', {
                rules: [geneValidationRule],
              })(<Input.TextArea rows={2}/>)}
            </Form.Item>
          </Tooltip>
        </FormSection>

        <FormSection index={2} title="Mutations">
          <Tooltip
            title="Enter mutations in following format [Amino Acid Codon][Location][Amino Acid Codon]">
            <React.Fragment/>
            <Form.Item label="Mutations" className="MutationsTextArea"
                       hasFeedback>
              {getFieldDecorator('mutations', {
                rules: [
                  {
                    required: true,
                    message: 'Mutations are required',
                  },
                  {
                    type: 'string',
                    pattern: /^\s*([A-Z][0-9]*[A-Z])(\s+[A-Z][0-9]*[A-Z]\s*)*$/i,
                  },
                  {
                    validator: (rule, value, callback) =>
                      validateMutations(
                        value,
                        this.props.form.getFieldValue('goiSequence'),
                        callback,
                      ),
                  },
                ],
              })(<MutationsInput cols={11}/>)}
            </Form.Item>
          </Tooltip>
        </FormSection>

        <CodonUsage index={3} form={form}/>

        <FormSection index={4} title="Parameters" open={false}>
          <Tooltip title="Enter size of an entire primer">
            <React.Fragment/>
            <Form.Item label="Size">
              <MinOptMaxInputs
                getFieldDecorator={getFieldDecorator}
                getFieldValue={getFieldValue}
                resetFields={resetFields}
                fieldPrefix="size"
                defaults={{min: 33, opt: 33, max: 60}}
              />
            </Form.Item>
          </Tooltip>
          <Tooltip title="Enter size of a 3'-end of the primer">
            <React.Fragment/>
            <Form.Item label="3' Size">
              <MinOptMaxInputs
                getFieldDecorator={getFieldDecorator}
                getFieldValue={getFieldValue}
                resetFields={resetFields}
                fieldPrefix="threePrimeSize"
                defaults={{min: 15, opt: 15, max: 40}}
              />
            </Form.Item>
          </Tooltip>
          <Tooltip title="Enter size of a 5'-end of the primer">
            <React.Fragment/>
            <Form.Item label="5' Size">
              <MinOptMaxInputs
                getFieldDecorator={getFieldDecorator}
                getFieldValue={getFieldValue}
                resetFields={resetFields}
                fieldPrefix="fivePrimeSize"
                defaults={{min: 15, opt: 15, max: 40}}
              />
            </Form.Item>
          </Tooltip>
          <Tooltip
            title="Enter the percentage of guanine or cytosine in the primers">
            <React.Fragment/>
            <Form.Item label="GC Content">
              <MinOptMaxInputs
                getFieldDecorator={getFieldDecorator}
                getFieldValue={getFieldValue}
                resetFields={resetFields}
                fieldPrefix="gcContent"
                defaults={{min: 40, opt: 50, max: 60}}
              />
            </Form.Item>
          </Tooltip>
          <Tooltip title="Enter temperature of entire primers">
            <React.Fragment/>
            <Form.Item label="Temperature">
              <MinOptMaxInputs
                getFieldDecorator={getFieldDecorator}
                getFieldValue={getFieldValue}
                resetFields={resetFields}
                fieldPrefix="temperature"
                defaults={{min: 75, opt: 78, max: 90}}
              />
            </Form.Item>
          </Tooltip>

          <Row gutter={10}>
            <Col span={12}>
              <Tooltip
                title="Specify the importance of entire primer temperature, 16 being the most important and 0 the least important">
                <React.Fragment/>
                <Form.Item label="Temperature Weight">
                  {getFieldDecorator('temperatureWeight', {
                    initialValue: 16,
                    valuePropName: 'value',
                  })(<Slider marks={this.stepsZeroSixteen} min={0} max={16}
                             step={null}/>)}
                </Form.Item>
              </Tooltip>
            </Col>
            <Col span={12}>
              <Tooltip
                title="Specify the importance of entire primer size, 16 being the most important and 0 the least important">
                <React.Fragment/>
                <Form.Item label="Total Primer Size Weight">
                  {getFieldDecorator('totalSizeWeight', {
                    initialValue: 4,
                    valuePropName: 'value',
                  })(<Slider marks={this.stepsZeroSixteen} min={0} max={16}
                             step={null}/>)}
                </Form.Item>
              </Tooltip>
            </Col>
          </Row>

          <Row gutter={10}>
            <Col span={12}>
              <Tooltip
                title="Specify the importance of the 3'-end size, 16 being the most important and 0 the least important">
                <React.Fragment/>
                <Form.Item label="3' Size Weight">
                  {getFieldDecorator('threePrimeSizeWeight', {
                    initialValue: 8,
                    valuePropName: 'value',
                  })(<Slider marks={this.stepsZeroSixteen} min={0} max={16}
                             step={null}/>)}
                </Form.Item>
              </Tooltip>
            </Col>
            <Col span={12}>
              <Tooltip
                title="Specify the importance of 5' Size, 16 being the most important and 0 the least important">
                <React.Fragment/>
                <Form.Item label="5' Size Weight">
                  {getFieldDecorator('fivePrimeSizeWeight', {
                    initialValue: 1,
                    valuePropName: 'value',
                  })(<Slider marks={this.stepsZeroSixteen} min={0} max={16}
                             step={null}/>)}
                </Form.Item>
              </Tooltip>
            </Col>
          </Row>

          <Row gutter={10}>
            <Col span={12}>
              <Tooltip
                title="Specify the importance of the GC Content, 16 being the most important and 0 the least important">
                <React.Fragment/>
                <Form.Item label="GC Content Weight">
                  {getFieldDecorator('gcContentWeight', {
                    initialValue: 0,
                    valuePropName: 'value',
                  })(<Slider marks={this.stepsZeroSixteen} min={0} max={16}
                             step={null}/>)}
                </Form.Item>
              </Tooltip>
            </Col>
            <Col span={12}>
              <Tooltip
                title="Specify the importance of Hairpin Temperature, 64 being the most important and 0 the least important. Hairpins with temperatures close to the melting temperature of the primer are penalized mores than those with hairpin temperatures far from the melting temperature.">
                <React.Fragment/>
                <Form.Item label="Hairpin Temperature Weight">
                  {getFieldDecorator('hairpinTemperatureWeight', {
                    initialValue: 32,
                    valuePropName: 'value',
                  })(<Slider marks={this.stepsZeroSixtyfour} min={0} max={64}
                             step={null}/>)}
                </Form.Item>
              </Tooltip>
            </Col>
          </Row>

          <Row gutter={10}>
            <Col span={12}>
              <Tooltip
                title="Specify the importance of Primer-dimer Temperature, 64 being the most important and 0 the least important. Primer-dimer with temperatures close to the melting temperature of the primer are penalized mores than those with primer-dimer temperatures far from the melting temperature.">
                <React.Fragment/>
                <Form.Item label="Primer-dimer Temperature Weight">
                  {getFieldDecorator('primerDimerTemperatureWeight', {
                    initialValue: 32,
                    valuePropName: 'value',
                  })(<Slider marks={this.stepsZeroSixtyfour} min={0} max={64}
                             step={null}/>)}
                </Form.Item>
              </Tooltip>
            </Col>
            <Col span={12}>
              <Tooltip
                title="Specify the importance of Mutation coverage, 320 being the most important and 0 the least important. Higher number means we prefer coverage of mutation sites over quality of primers.">
                <React.Fragment/>
                <Form.Item label="Mutation Coverage Weight">
                  {getFieldDecorator('mutationCoverageWeight', {
                    initialValue: 160,
                    valuePropName: 'value',
                  })(<Slider marks={this.stepsZeroThreeHundredtwenty} min={0}
                             max={320} step={null}/>)}
                </Form.Item>
              </Tooltip>
            </Col>
          </Row>
          <Row gutter={10}>
            <Tooltip
              title="Enter maximum temperature difference between entire primers">
              <React.Fragment/>
              <Form.Item label="Max Temperature Difference" hasFeedback>
                {getFieldDecorator('maxTemperatureDifference', {
                  rules: [{
                    required: true,
                    message: 'Max Temperature Difference is required'
                  }],
                  initialValue: 5,
                })(<Input type="number"/>)}
              </Form.Item>
            </Tooltip>
          </Row>
          <Row gutter={10}>
            <Col span={12}>
              <Tooltip
                title="Toggles whether the fast primer extension algorithm calculates hairpin and primer-dimer temperatures. Solutions which form hairpins and primer-dimers are penalized and solutions without them are picked instead (unless they break other constraints more).">
                <React.Fragment/>
                <Form.Item label="Check for hairpins and primer-dimers">
                  {getFieldDecorator('usePrimer3', {
                    initialValue: false,
                    valuePropName: 'checked',
                  })(<Switch/>)}
                </Form.Item>
              </Tooltip>
            </Col>
            <Col span={12}>
              <Tooltip
                title="Search only for solutions with no overlaps between primers">
                <React.Fragment/>
                <Form.Item label="Non-overlapping primers only">
                  {getFieldDecorator('nonOverlappingPrimers', {
                    initialValue: false,
                    valuePropName: 'checked',
                  })(<Switch/>)}
                </Form.Item>
              </Tooltip>
            </Col>
          </Row>
        </FormSection>

        <FormSection index={5} title="Degenerate Codon" open={false}>
          <Tooltip title="Select usage of degenerate codons">
            <React.Fragment/>
            <Form.Item label="Use Degeneracy Codon">
              {getFieldDecorator('useDegeneracyCodon', {
                initialValue: true,
                valuePropName: 'checked',
              })(<Switch/>)}
            </Form.Item>
          </Tooltip>
        </FormSection>

        <FormSection index={6} title="File name" open={false}>
          <Tooltip title="Type name of the export report">
            <React.Fragment/>
            <Form.Item label="Enter file name" hasFeedback>
              {getFieldDecorator('fileName')(<Input/>)}
            </Form.Item>
          </Tooltip>
        </FormSection>

        <FormSection index={7} title="Oligo prefix" open={false}>
          <Tooltip title="Type oligo prefix to be used in the export report, please use max 19 characters. This name is used for naming tab in report excel file which has hard limit.">
            <React.Fragment/>
            <Form.Item label="Enter oligo prefix" hasFeedback>
              {getFieldDecorator('oligoPrefix')(<Input/>)}
            </Form.Item>
          </Tooltip>
        </FormSection>

        <FormSection collapse={false}>
          <Form.Item className="DataInputForm-submitRow">
            <Button.Group>
              <Tooltip title="Design primers">
                <Button type="primary" htmlType="submit" icon="save"
                        id="submit_qclm_btn">
                  Submit
                </Button>
              </Tooltip>
              <Tooltip title="Clear the form">
                <Button
                  type="default"
                  id="reset_qclm_btn"
                  htmlType="reset"
                  icon="reload"
                  disabled={disabled}
                  onClick={this.resetForm}>
                  Reset
                </Button>
              </Tooltip>
            </Button.Group>
          </Form.Item>
        </FormSection>
      </Form>
    )
  }
}

export default withForm<QCLMFormOuterProps, QCLMFormData>(QCLMForm)
