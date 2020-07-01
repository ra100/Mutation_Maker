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

import { Button, Form, Input, message, Radio, Select, Tooltip } from 'antd'
import * as R from 'ramda'
import * as React from 'react'
import AminoAcidInput, { AminoType } from 'shared/components/AminoAcidInput'
import FileUploadInput from 'shared/components/FileUploadInput'
import FormSection from 'shared/components/FormSection'
import { validateMutations } from 'shared/components/FormValidation'
import MutationsInput from 'shared/components/MutationsInput'
import ParametersFormSection from 'shared/components/ParametersFormSection'
import {
  endsWithStopCodonValidationRule,
  geneValidationRule,
} from 'shared/form'
import { getForwardPrimer, getReversePrimer, PrimersType } from 'shared/genes'
import { SSMFormData } from 'shared/lib/FormData'
import withForm, { WithFormInnerProps } from 'shared/withForm'
import {getDegenerateCodons} from './aminoAcidCodons'

type SSMFormOuterProps = {
  disabled: boolean
}

type SSMFormInnerProps = SSMFormOuterProps & WithFormInnerProps<SSMFormData>

const DEFAULT_PRIMERS_TYPE = PrimersType.pETseq1;

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
];

const complementTable = {
  "A": "T",
  "C": "G",
  "G": "C",
  "T": "A",
  "I": "I", // ???
  "R": "Y",
  "Y": "R",
  "M": "K",
  "K": "M",
  "S": "S",
  "W": "W",
  "H": "D",
  "B": "V",
  "V": "B",
  "D": "H",
  "N": "N"
};

const reverseComplement = (sequence: string): string => {
  const reversed = sequence.split("").reverse().join("");

  return reversed.split("").map(x => complementTable[x]).join("")
};


class SSMForm extends React.Component<SSMFormInnerProps> {
  state = {
    generateCodonOrAminoAcidTab: 'Degenerate Codon',
    aminoAcids: [...defaultAminoAcids],
    loading: false,
    showGoiWarning: false
  };

  onSubmit = (event: React.FormEvent<any>) => {
    event.preventDefault();
    const { form, onSubmit } = this.props;

    form.validateFields((error: any, values: SSMFormData) => {
      if (!error) {
        onSubmit(values)
      } else {
        message.error('Validation failed');
        // tslint:disable-next-line no-console
        console.error(error)
      }
    })
  };

  handleTabChange = (event?: any) => {
    this.setState({ generateCodonOrAminoAcidTab: event.target.value })
  };

  handleAminoChange = (aminoAcids: AminoType[]) => {
    this.setState({ aminoAcids, loading: true });
    const { setFieldsValue } = this.props.form;
    getDegenerateCodons(
      aminoAcids.filter((amino: AminoType) => amino.state === 'include').map(R.prop('name')),
      aminoAcids.filter((amino: AminoType) => amino.state === 'avoid').map(R.prop('name')),
    )
      .then(degenerateCodon => {
        setFieldsValue({
          degenerateCodon,
        });
        this.setState({ loading: false })
      })
      .catch(() => {
        console.warn('error in getDegenerateCodons promise');
        this.setState({ loading: false })
      })
  };

  resetForm = (event: React.FormEvent<any>) => {
    event.preventDefault();
    const { form } = this.props;
    this.setState({ aminoAcids: [...defaultAminoAcids] });
    form.resetFields()
  };

  onPrimersTypeChange = (primersType: PrimersType) => {
    const { setFieldsValue } = this.props.form;
    setFieldsValue({
      forwardPrimerValue: getForwardPrimer(primersType),
      reversePrimerValue: getReversePrimer(primersType),
    })
  };

  onInputChange = (target: string) => (data: string) => {
    const { setFieldsValue, validateFields } = this.props.form;
    setFieldsValue({
      [target]: data,
    });
    validateFields()
  };

  onGoiChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const goiStr = (event.target.value || '');
    const hasStartCodon = goiStr.match(/^ATG/);
    const hasStopCodon = goiStr.match(/TAA$/) || goiStr.match(/TAG$/) || goiStr.match(/TGA$/);
    this.setState({showGoiWarning: !hasStartCodon || !hasStopCodon})
  };

  render() {
    const { form, disabled } = this.props;
    const { getFieldDecorator, getFieldValue, resetFields, setFieldsValue } = form;
    const goiIsSubstringOfPlasmid = (
      rule: any,
      value: string,
      callback: (errors: string[]) => void,
    ) =>
      callback(
        getFieldValue('plasmidSequence').indexOf(value) === -1
          ? ['Gene of Interest must be a substring of plasmid.']
          : [],
      );

    const flankingPrimerIsSubstringOfPlasmid = (
      rule: any,
      value: string,
      callback: (errors: string[]) => void,
    ) =>
      callback(
        getFieldValue('plasmidSequence').indexOf(value) === -1
          ? ['Forward flanking primer must be a substring of plasmid.']
          : [],
      );

    const reverseComplementFlankingPrimerIsSubstringOfPlasmid = (
      rule: any,
      value: string,
      callback: (errors: string[]) => void,
    ) =>
      callback(
        getFieldValue('plasmidSequence').indexOf(reverseComplement(value)) === -1
          ? ['Reverse flanking primer must be a substring of plasmid.']
          : [],
      );

    return (
      <Form layout="vertical" onSubmit={this.onSubmit}>
        <FormSection index={1} title="Plasmid">
          <Tooltip title="Enter or Upload Plasmid sequence containing flanking primers and Gene of Interest sequence. Only A, C, G and T are allowed in the sequence.">
            <React.Fragment />
            <Form.Item label="Plasmid Sequence" className="GeneTextArea" hasFeedback>
              <FileUploadInput onChange={this.onInputChange('plasmidSequence')} />
              {getFieldDecorator('plasmidSequence', {
                rules: [
                  {
                    required: true,
                    message: 'Plasmid Sequence is required',
                  },
                  geneValidationRule,
                ],
              })(<Input.TextArea rows={6} />)}
            </Form.Item>
          </Tooltip>
        </FormSection>

        <FormSection index={2} title="Sequence">
          <Tooltip title="Enter or Upload Gene of Interest sequence. Only A, C, G and T are allowed in the sequence. The Gene of Interest must be a substring of the Plasmid.">
            <React.Fragment />
            <Form.Item label="Gene of Interest Sequence" className="GeneTextArea" hasFeedback>
              <FileUploadInput onChange={this.onInputChange('goiSequence')} />
              {getFieldDecorator('goiSequence', {
                rules: [
                  { required: true, message: 'Gene of Interest Sequence is required' },
                  { validator: goiIsSubstringOfPlasmid },
                  geneValidationRule,
                  endsWithStopCodonValidationRule,
                ],
              })(<Input.TextArea rows={8} onChange={this.onGoiChange} />)}
              {this.state.showGoiWarning && <div className="has-warning noIcon"><div className="ant-form-explain">Gene of Interest should begin with ATG and end with TAA, TAG or TGA.</div></div>}
            </Form.Item>
          </Tooltip>
        </FormSection>

        <FormSection index={3} title="Mutations">
          <Tooltip title="Enter mutations in following format [Amino Acid Codon][Location][X] , X represents a degenerate codon">
            <React.Fragment />
            <Form.Item label="Mutations" className="MutationsTextArea" hasFeedback>
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
              })(<MutationsInput cols={11} />)}
            </Form.Item>
          </Tooltip>
        </FormSection>

        <FormSection index={4} title="Flanking primers">
          <Tooltip title="Select forward and reverse flanking primers from a list or enter custom primer sequences. Flanking primers and custom primers have to be searchable in plasmid sequence. Only A, C, G and T are allowed in the custom flanking primer sequence.">
            <React.Fragment />
            <Form.Item label="Primers Type" hasFeedback>
              {getFieldDecorator('primersType', { initialValue: DEFAULT_PRIMERS_TYPE })(
                <Select onChange={this.onPrimersTypeChange}>
                  <Select.Option key={PrimersType.pETseq1}>pET SeqF1 / SeqR1</Select.Option>
                  <Select.Option key={PrimersType.custom}>Custom</Select.Option>
                </Select>,
              )}
            </Form.Item>
            <Form.Item label="Forward Primer" hasFeedback>
              {getFieldDecorator('forwardPrimerValue', {
                rules: [
                  { required: true, message: 'Forward Primer is required' },
                  geneValidationRule,
                  {
                    max: 60
                  },
                  { validator: flankingPrimerIsSubstringOfPlasmid }
                ],
                initialValue: getForwardPrimer(DEFAULT_PRIMERS_TYPE),
              })(<Input disabled={getFieldValue('primersType') !== 'custom'} />)}
            </Form.Item>
            <Form.Item label="Reverse Primer" hasFeedback>
              {getFieldDecorator('reversePrimerValue', {
                rules: [
                  { required: true, message: 'Reverse Primer is required' },
                  geneValidationRule,
                  {
                    max: 60
                  },
                  { validator: reverseComplementFlankingPrimerIsSubstringOfPlasmid }
                ],
                initialValue: getReversePrimer(DEFAULT_PRIMERS_TYPE),
              })(<Input disabled={getFieldValue('primersType') !== 'custom'} />)}
            </Form.Item>
          </Tooltip>
        </FormSection>
        <FormSection index={5} title="Parameters" tooltip="Enter primers parameters" open={false}>
          <ParametersFormSection
            getFieldDecorator={getFieldDecorator}
            getFieldValue={getFieldValue}
            resetFields={resetFields}
            setFieldsValue={setFieldsValue}
          />
        </FormSection>

        <FormSection index={6} title="Degenerate codons or Amino acids" open={false}>
          <Radio.Group defaultValue="Degenerate Codon" onChange={this.handleTabChange}>
            <Radio.Button value="Degenerate Codon">Degenerate Codon</Radio.Button>
            <Radio.Button value="Amino acids">Amino acids</Radio.Button>
            <p className="codon-info">Select what you want to enter</p>
          </Radio.Group>
          <Form.Item
            hasFeedback
            className={
              this.state.generateCodonOrAminoAcidTab !== 'Degenerate Codon' ? 'hidden' : ''
            }>
            <Tooltip title="Type a degenerate codon. It must consist of exactly three letters from A, B, C, D, G, H, K, M, N, R, S, T, V, W, Y.">
              {getFieldDecorator('degenerateCodon', {
                initialValue: 'NNK',
                rules: [
                  {
                    required: true,
                    message: 'Degenerate codon is required',
                  },
                  {
                    pattern: /^[ABCDGHKMNRSTUVWY]{3}(,[ABCDGHKMNRSTUVWY]{3})*$/,
                    message:
                      'Must consist of exactly three letters from A, B, C, D, G, H, K, M, N, R, S, T, U, V, W, Y without spaces',
                  },
                ],
              })(<Input />)}
            </Tooltip>
          </Form.Item>
          <Form.Item
            className={this.state.generateCodonOrAminoAcidTab !== 'Amino acids' ? 'hidden' : ''}>
            <AminoAcidInput
              value={this.state.aminoAcids}
              onChange={this.handleAminoChange}
              loading={this.state.loading}
            />
          </Form.Item>
        </FormSection>

        <FormSection index={7} title="File name" open={false}>
          <Tooltip title="Type name of the export report">
            <React.Fragment />
            <Form.Item label="Enter file name" hasFeedback>
              {getFieldDecorator('fileName')(<Input />)}
            </Form.Item>
          </Tooltip>
        </FormSection>

        <FormSection index={8} title="Oligo prefix" open={false}>
          <Tooltip title="Type oligo prefix to be used in the export report, please use max 19 characters. This name is used for naming tab in report excel file which has hard limit.">
            <React.Fragment />
            <Form.Item label="Enter oligo prefix" hasFeedback>
              {getFieldDecorator('oligoPrefix')(<Input />)}
            </Form.Item>
          </Tooltip>
        </FormSection>

        <FormSection collapse={false}>
          <Form.Item className="DataInputForm-submitRow">
            <Button.Group>
              <Tooltip title="Design primers">
                <Button type="primary" htmlType="submit" icon="save" id="submit_ssm_btn">
                  Submit
                </Button>
              </Tooltip>
              <Tooltip title="Clear the form">
                <Button
                  type="default"
                  id="rest_ssm_btn"
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

export default withForm<SSMFormOuterProps, SSMFormData>(SSMForm)
