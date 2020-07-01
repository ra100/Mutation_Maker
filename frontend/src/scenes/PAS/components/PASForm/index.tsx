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
  Radio,
  Row,
  Select,
  Switch,
  Tooltip,
} from 'antd';
import * as React from 'react';
import FileUploadInput from 'shared/components/FileUploadInput';
import FormSection from 'shared/components/FormSection';
import MinOptMaxInputs from 'shared/components/MinOptMaxInputs';
import {geneValidationRule,} from 'shared/form';
import {PASFormData} from 'shared/lib/FormData';
import withForm, {WithFormInnerProps} from 'shared/withForm';
import CodonUsage from "shared/components/CodonUsage";
import InputMutations from "./components/InputMutations";
import {
  validateAvoidMotifs, validateSequence
} from "shared/components/FormValidation";


type PASFormOuterProps = {
  disabled: boolean
}

type PASFormInnerProps = PASFormOuterProps & WithFormInnerProps<PASFormData>
const {Option} = Select;
const motifsJSON = require('shared/motifs.json');
const motifsOptions: any[] = [];

class PASForm extends React.Component<PASFormInnerProps> {
  state = {
    showGoiWarning: false,
    isMutationsReset: false, // Trigger InputMutation reset
  };
  index = 0; // Form Section No.

  submitForm = (event: React.FormEvent<any>) => {
    event.preventDefault();
    const {form, onSubmit} = this.props;

    form.validateFields((error: any, values: PASFormData) => {
      if (!error) {
        onSubmit(values)
      } else {
        message.error('Validation failed');
        // tslint:disable-next-line no-console
        console.warn(error)
      }
    })
  };

  preventSubmitForm = (event: any) => {
    event.preventDefault();
  };

  resetForm = (event: React.FormEvent<any>) => {
    event.preventDefault();
    this.props.form.resetFields();
    this.setState({isMutationsReset: true})
  };

  resetParameters = (event: React.FormEvent<any>) => {
    event.preventDefault();
    const {form} = this.props;
    form.resetFields([
      'oligoLengthMin', 'oligoLengthOpt', 'oligoLengthMax',
      'overlappingTmMin', 'overlappingTmOpt', 'overlappingTmMax',
      'overlappingLengthMin', 'overlappingLengthOpt', 'overlappingLengthMax',
      'gcContentMin', 'gcContentOpt', 'gcContentMax', 'computeHairpinHomodimer'
    ])
  };

  handleResetMutations = () => {
    this.setState({isMutationsReset: false})
  };


  onFileUpload = (target: string) => (data: string) => {
    const {setFieldsValue, validateFields} = this.props.form;
    setFieldsValue({
      [target]: data,
    });
    validateFields([target], () => {
    })
  };

  // Additional validation for Gene of Interest
  onGoiChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (this.props.form.getFieldValue('inputSequenceType') === 'dna') {
      this.setState({
        showGoiWarning: !(event.target.value || '')
          .match(/^ATG|atg/)
      })
    } else {
      this.setState({
        showGoiWarning: !(event.target.value || '')
          .match(/^M|m/)
      })
    }
    this.props.form.validateFields(['inputMutations'],
      () => {
      })
  };

  // Set Sequence Type and trigger validation
  handleInputSequenceTypeChange = (event: any) => {
      this.props.form.setFieldsValue({
        inputSequenceType: event.target.value,
        goiSequence: this.props.form.getFieldValue('goiSequence'),
      });
      this.props.form.validateFields(['goiSequence', 'inputMutations'],
        () => {
        })
  };

  sequenceValidator = (rule: any, sequence: any, callback: any) => {
    validateSequence(rule, sequence, callback,
      this.props.form
        .getFieldValue('inputSequenceType') === 'dna')
  };

  async componentDidMount() {
    // Load Avoid Motifs Data
    motifsJSON.forEach((element: string) => {
      motifsOptions.push(<Option key={element}>{element}</Option>)
    });

    // Assign data in case of result / reresh page
    const inputMutations = this.props.data.inputMutations
      && this.props.data.inputMutations.mutations;
    if (inputMutations && inputMutations.length > 0) {
      await this.props.form.setFieldsValue({
        'inputMutations': {mutations: [...inputMutations]},
      });
      await this.props.form.validateFields(['inputMutations'],
        () => {
        })
    }
  }

  render() {
    this.index = 1;
    const {form, disabled} = this.props;
    const {getFieldDecorator, getFieldValue, resetFields} = form;

    return (
      <Form layout='vertical' onSubmit={this.preventSubmitForm}>
        <FormSection index={this.index++} title='Sequence'>

          <Tooltip
            placement='rightTop'
            title="Enter 5'-end flanking sequence. Allowed values: A, C, G and T">
            <React.Fragment/>
            <Form.Item label='Five Prime Flanking Sequence' hasFeedback>
              {getFieldDecorator('fivePrimeFlankingSequence', {
                rules: [geneValidationRule],
              })(<Input.TextArea rows={2}/>)}
            </Form.Item>
          </Tooltip>
          <React.Fragment/>
          <Tooltip
            placement='rightTop'
            title="Select the GOI input sequence format.">
            <React.Fragment/>
            <Form.Item
              label='Gene of Interest Sequence'>
              {getFieldDecorator('inputSequenceType', {
                initialValue: 'dna',
              })(
                <Radio.Group name='sequenceRadioButton'
                             onChange={this.handleInputSequenceTypeChange}>
                  <Radio.Button value='dna'>
                    DNA
                  </Radio.Button>
                  <Radio.Button value='protein'>
                    Protein
                  </Radio.Button>
                </Radio.Group>,
              )}
            </Form.Item>
          </Tooltip>
          <Tooltip placement="topRight"
                   title={'Enter or Upload Gene of Interest sequence. Allowed values: '
                   + (getFieldValue('inputSequenceType') === 'dna'
                     ? 'A, C, G and T'
                     : 'F, L, I, M, V, S, G, T, A, Y, H, Q, N, K, D, E, C, W, R, P')}>
            <React.Fragment/>
            <Form.Item
              className='GeneTextArea' hasFeedback>
              <FileUploadInput onChange={this.onFileUpload('goiSequence')}/>
              {getFieldDecorator('goiSequence', {
                rules: [
                  {validator: this.sequenceValidator},
                  {
                    required: true,
                    message: 'Input Sequence is required',
                  },
                ],
              })(<Input.TextArea rows={8} onChange={this.onGoiChange}/>)}
              {this.state.showGoiWarning && <div className='has-warning noIcon'>
                <div className='ant-form-explain'>
                  Gene of Interest should begin with
                  {getFieldValue('inputSequenceType') === 'dna' ? ' ATG' : ' M'}
                </div>
              </div>}
            </Form.Item>
          </Tooltip>
          <Tooltip
            title={"Enter 3'-end flanking sequence. Allowed values: A, C, G and T"}>
            <React.Fragment/>
            <Form.Item label='Three Prime Flanking Sequence' hasFeedback>
              {getFieldDecorator('threePrimeFlankingSequence', {
                rules: [geneValidationRule],
              })(<Input.TextArea rows={2}/>)}
            </Form.Item>
          </Tooltip>
        </FormSection>

        <InputMutations inputMutations={this.props.data.inputMutations}
                        isMutationsReset={this.state.isMutationsReset}
                        handleResetMutations={this.handleResetMutations}
                        index={this.index++}
                        form={form} />

        <FormSection index={this.index++} title='Degenerate Codon' open={false}>
          <Tooltip title='Select usage of degenerate codons'>
            <React.Fragment/>
            <Form.Item label='Use Degeneracy Codon'>
              {getFieldDecorator('useDegeneracyCodon', {
                initialValue: false,
                valuePropName: 'checked',
              })(<Switch/>)}
            </Form.Item>
          </Tooltip>
        </FormSection>

        <CodonUsage index={this.index++} form={form}/>

        <FormSection index={this.index++} title='Avoid Motifs' open={false}>
            <React.Fragment/>
            <Form.Item>
              <Tooltip placement='topRight'
                       title="Select from the list or input your own sites to be
          excluded from oligonucleotide fragments.">
              {getFieldDecorator('avoidMotifs', {
                rules: [{
                  validator: validateAvoidMotifs
                }],
              })(<Select
                  mode='tags'
                  placeholder='None'>
                  {motifsOptions}
                </Select>)}
              </Tooltip>
            </Form.Item>
        </FormSection>

        <FormSection index={this.index++} title='Parameters' open={false}>
          <Tooltip title='Enter oligo length of an entire primer'>
            <React.Fragment/>
            <Form.Item label='Oligo Length (bp)'>
              <MinOptMaxInputs
                getFieldDecorator={getFieldDecorator}
                getFieldValue={getFieldValue}
                resetFields={resetFields}
                fieldPrefix='oligoLength'
                defaults={{min: 40, opt: 40, max: 60}}
              />
            </Form.Item>
          </Tooltip>
          <Tooltip title='Enter overlapping melting temperature of the primer'>
            <React.Fragment/>
            <Form.Item label='Overlapping Tm (&deg;C)'>
              <MinOptMaxInputs
                getFieldDecorator={getFieldDecorator}
                getFieldValue={getFieldValue}
                resetFields={resetFields}
                fieldPrefix='overlappingTm'
                defaults={{min: 54, opt: 56, max: 64}}
                optimalPresent={true}
              />
            </Form.Item>
          </Tooltip>
          <Tooltip title='Enter Overlapping Length of the primer'>
            <React.Fragment/>
            <Form.Item label='Overlapping length (bp)'>
              <MinOptMaxInputs
                getFieldDecorator={getFieldDecorator}
                getFieldValue={getFieldValue}
                resetFields={resetFields}
                fieldPrefix='overlappingLength'
                defaults={{min: 18, opt: 21, max: 30}}
                optimalPresent={true}
              />
            </Form.Item>
          </Tooltip>
          <Tooltip
            title='Enter the percentage of guanine or cytosine in the primers'>
            <React.Fragment/>
            <Form.Item label='GC Content (%)'>
              <MinOptMaxInputs
                getFieldDecorator={getFieldDecorator}
                getFieldValue={getFieldValue}
                resetFields={resetFields}
                fieldPrefix='gcContent'
                defaults={{min: 40, opt: 40, max: 60}}
              />
            </Form.Item>
          </Tooltip>
          <Row gutter={10}>
            <Col>
              <Tooltip title="Toggles whether the fast primer extension
                algorithm calculates hairpin and primer-dimer temperatures.
                Solutions which form hairpins and primer-dimers are penalized
                and solutions without them are picked instead (unless they
                break other constraints more).">
                <React.Fragment/>
                <Form.Item label="Check for hairpins and primer-dimers">
                  {getFieldDecorator('computeHairpinHomodimer', {
                    initialValue: true,
                    valuePropName: 'checked',
                  })(<Switch/>)}
                </Form.Item>
              </Tooltip>
            </Col>
          </Row>

          <Tooltip title='Reset Parameters to default values'>
            <React.Fragment/>
            <Button
              type='default'
              htmlType='reset'
              icon='reload'
              onClick={this.resetParameters}>
              Reset
            </Button>
          </Tooltip>
        </FormSection>

        <FormSection index={this.index++} title='File name' open={false}>
          <Tooltip title='Type name of the export report'>
            <React.Fragment/>
            <Form.Item label='Enter file name' hasFeedback>
              {getFieldDecorator('fileName')(<Input/>)}
            </Form.Item>
          </Tooltip>
        </FormSection>

        <FormSection index={this.index++} title='Oligo prefix'
                     open={false}>
          <Tooltip title="Type oligo prefix to be used in the export report, please use max 19 characters. This name is used for naming tab in report excel file which has hard limit.">
            <React.Fragment/>
            <Form.Item label='Enter oligo prefix' hasFeedback>
              {getFieldDecorator('oligoPrefix')(<Input/>)}
            </Form.Item>
          </Tooltip>
        </FormSection>

        <FormSection collapse={false}>
          <Form.Item className='DataInputForm-submitRow'>
            <Button.Group>
              <Tooltip title='Design primers'>
                <Button type='primary' htmlType='button' icon='save'
                        id='submit_pas_btn' onClick={this.submitForm}>
                  Submit
                </Button>
              </Tooltip>
              <Tooltip title='Clear the form'>
                <Button
                  type='default'
                  htmlType='reset'
                  icon='reload'
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

export default withForm<PASFormOuterProps, PASFormData>(PASForm)
