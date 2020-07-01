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

import * as React from 'react';
import {Button, Form, message, Radio, Tooltip} from "antd";
import FormSection from "shared/components/FormSection";
import MutationsTable from "./MutationsTable";
import FileUploadMutations from "./FileUploadMutations";
import {aminoAcidToCodons} from "shared/genes";

// Input Mutations Form Section with File Upload and Editable Table
export default class InputMutations extends React.Component<any> {
  constructor(props: any) {
    super(props);
    this.handleInputMutationsChange = this.handleInputMutationsChange.bind(this)
  }

  state = {
    mutations: [],
  };

  handleInputMutationsTypeChange = (event: any) => {
    this.props.form.setFieldsValue({
      inputMutations: this.props.form.getFieldValue('inputMutations'),
      inputMutationsType: event.target.value
    });
    this.props.form.validateFields(['inputMutations'],
      () => {
      })
  };

  handleInputMutationsUpload = (target: string) => (data: any) => {
    this.setState({mutations: [...data.mutations]});
    this.props.form.setFieldsValue({
      [target]: data,
    });
    this.props.form.validateFields(['inputMutations'],
      (errors: any) => {
        if (errors) {
          message.warn('Uploaded file contains errors');
          console.warn(errors)
        }
      })
  };

  mutationsValidator = (rule: any, value: any, callback: any) => {
    // Required
    if (value.mutations.length === 0) {
      callback();
      return
    }
    // Validate Target
    const sequence = this.props.form.getFieldValue('goiSequence');
    const sequenceType = this.props.form.getFieldValue('inputSequenceType');
    const mutationsType = this.props.form.getFieldValue('inputMutationsType');
    for (const [index, mutation] of value.mutations.entries()) {
      if ('target' in mutation && !mutation.target) {
        callback(`Please insert Target Residue in row ${index + 1}`);
        return
      }
      if ('target' in mutation && mutation.target && mutation.target.length > 0) {
        const targetValue = mutation.target.charAt(0).toUpperCase();
        const position = parseInt(mutation.target.slice(1));
        if (sequenceType === "protein") {
          if (!(sequence.charAt(position - 1) === targetValue)) {
            callback(`Row ${index + 1}: target ${targetValue} is not present at site ${position}`);
            return
          }
        } else {
          if (!aminoAcidToCodons(targetValue)
            .includes(sequence.substr((position - 1) * 3, 3))) {
            callback(`Row ${index + 1}: target ${targetValue}
            is not present at site ${position}`);
            return
          }
        }
      }
      // Validate MT
      if ('mt' in mutation && !mutation.mt) {
        callback(`Please insert MT in row ${index + 1}`);
        return
      }
      if ('mt' in mutation && mutation.mt && mutation.mt.length > 0) {
        if (mutationsType === 'dna') {
          if (!(mutation.mt || '').match(/^[ACGTacgt, ]+$/)) {
            callback(`Row ${index + 1}: the only allowed values for MT are:
             A, C, T, G`);
            return
          }
        } else {
          if (!(mutation.mt || '').match(/^[FLIMVSGTAYHQNKDECWRPflimvsgtayhqnkdecwrp, ]+$/)) {
            callback(`Row ${index + 1}: the only allowed values for MT are:
              F, L, I, M, V, S, G, T, A, Y, H, Q, N, K, D, E, C, W, R, P`);
            return
          }
        }
      }
      // Validate MT%
      if ('mtp' in mutation && !mutation.mtp) {
        callback(`Please insert MT% in row ${index + 1}`);
        return
      } else {
        if (mutation.mtp < 0 && mutation.mtp > 100) {
          callback('MT% must be between 0 and 100');
          return
        }
      }
      callback()
    }
  };

  resetMutationsTable = () => {
    this.setState({mutations: []});
    this.props.form.resetFields(['inputMutations', 'inputMutationsType']);
    this.props.form.setFieldsValue({
      inputMutations: {mutations: []},
    });
    this.props.form.validateFields(['inputMutations'], () => {
    })
  };

  handleInputMutationsChange(newMutations: any): any {
    this.setState({
      mutations: [...newMutations.mutations]
    })
  }

  async componentDidMount() {
    // Assign data in case of result / reresh page
    const inputMutations = this.props.inputMutations?.mutations;
    if (inputMutations && inputMutations.length > 0) {
      await this.setState({mutations: [...inputMutations]});
      await this.props.form.setFieldsValue({
        'inputMutations': {mutations: [...inputMutations]},
      });
      await this.props.form.validateFields(['inputMutations'],
        () => {
        })
    }
  };

  componentDidUpdate = (prevProps: Readonly<any>): void => {
    // Reset mutations and change isMutationRes
    if (prevProps.isMutationsReset !== this.props.isMutationsReset) {
      if (this.props.isMutationsReset) {
        this.resetMutationsTable();
        this.props.handleResetMutations();
      }
    }
  };

  render() {
    const {form} = this.props;
    const {getFieldDecorator} = form;

    return (
      <FormSection index={this.props.index} title='Input Mutations'>
        <Tooltip
          placement='rightTop'
          title="Select the mutations input format.">
          <React.Fragment/>
          <Form.Item>
            {getFieldDecorator('inputMutationsType', {
              initialValue: 'dna',
            })(
              <Radio.Group name='mutationsRadioButton'
                           onChange={this.handleInputMutationsTypeChange}>
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
        <Form.Item>
          <Tooltip title="Clear Mutations Table" placement='right'>
            <Button
              type="default"
              htmlType="reset"
              icon="delete"
              onClick={this.resetMutationsTable}
            >
              Reset
            </Button>
          </Tooltip>
        </Form.Item>
        <Tooltip placement='topRight'
                 title={<span>Enter or Upload mutations in accordance with the
              selected input format: <br/>
              Protein: <br/>
              Target Residue: [Amino Acid Abbreviation][Location] <br/>
              MT: [Amino Acid Abbreviation] <br/>
              MT%: 1-100% <br/>
              Codons: <br/>
              Target Residue:  [Amino Acid Abbreviation][Location] <br/>
              MT: [Codon] <br/>
              MT%: 1-100% </span>}
        >
          <React.Fragment/>
          <Form.Item>
            <FileUploadMutations
              onChange={this.handleInputMutationsUpload('inputMutations')}/>
            {getFieldDecorator('inputMutations', {
              rules: [
                {validator: this.mutationsValidator},
                {
                  required: true,
                  message: 'Input mutations are required',
                },
              ],
            })(
              <
                // @ts-ignore
                MutationsTable mutations={this.state.mutations}
                               onChange={this.handleInputMutationsChange}/>)}
          </Form.Item>
        </Tooltip>
      </FormSection>
    )
  }
}