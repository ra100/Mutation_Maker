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

import * as React from "react";
import {
  Form,
  Input,
  InputNumber,
  Radio,
  Select,
  Tooltip,
} from 'antd';
import FormSection from 'shared/components/FormSection';
import * as _ from "lodash";
import Axios from "axios";

const {Option} = Select;

export default class CodonUsage extends React.Component<any> {

  state = {
    customCodonUsage: '',
    isCodonUsageDisabled: true,
    isCodonUsageLoading: false,
    codonUsageData: [],
  };
  codonUsageDataLoad: any[] = [];
  timeout = 0;

  clearTimeout = () => {
    if (this.timeout) {
      clearTimeout(this.timeout)
    }
  };

  handleCodonUsageSearch = (value: string) => {
    if (value.length === 0) {
      this.setState({
        codonUsageData: this.codonUsageDataLoad.slice(0, 10),
      })
    } else {
      this.setState({isCodonUsageLoading: true,});
      this.clearTimeout();
      this.timeout = window.setTimeout(() => {
        const regex = new RegExp(_.escapeRegExp(value), 'i');
        const isMatch = (result: any) => regex.test(result.name)
          || regex.test(result.id);
        const filteredResults = this.codonUsageDataLoad.filter(isMatch);
        // Display maximum 10 results
        filteredResults.length = Math.min(
          filteredResults.length,
          10
        );

        this.setState({
          isCodonUsageLoading: false,
          codonUsageData: filteredResults,
        })
      }, 500)
    }
  };

  handleCodonUsageChange = (value: string) => {
    const customCodonUsage = this.codonUsageDataLoad.find(
      (element: any) => {
        return element.id === value
      });
    this.props.form.setFieldsValue({customCodonUsage: customCodonUsage.name})
  };

  handleCustomCodonUsageSelect = (event: any) => {
    if (event.target.value === 'custom') {
      this.setState({isCodonUsageDisabled: false})
    } else {
      this.setState({isCodonUsageDisabled: true})
    }
  };

  async componentDidMount() {
    try {
      const response: any = await Axios.get('/v1/get_species');
      if (response && response.data && response.data.length) {
        this.codonUsageDataLoad = [...response.data];
        this.setState({
          codonUsageData: response.data.slice(0, 10),
        })
      } else {
        console.error('Fetching species failed.')
      }
    } catch (error) {
      console.error(error);
      console.error('Fetching species failed because of unexpected exception.')
    }
  }

  render() {
    const {getFieldDecorator} = this.props.form;

    const codonUsageOptions = this.state.codonUsageData.map((data: any) =>
      <Option key={data.id}>{data.name + ' ' + data.id}</Option>);

    return (
      <FormSection index={this.props.index} title='Codon Usage'>
        <Tooltip title='Select species codon usage table'>
          <React.Fragment/>
          <Form.Item label='Codon Usage'>
            {getFieldDecorator('codonUsage', {
              initialValue: 'e-coli',
            })(
              <Radio.Group onChange={this.handleCustomCodonUsageSelect}>
                <Radio.Button value='e-coli'>
                  E.coli
                </Radio.Button>
                <Radio.Button value='yeast'>
                  Yeast
                </Radio.Button>
                <Radio.Button value='custom'>
                  Custom
                </Radio.Button>
              </Radio.Group>,
            )}
          </Form.Item>
          <React.Fragment/>
          <Form.Item>
            {getFieldDecorator('taxonomyId')(
              <Select
                disabled={this.state.isCodonUsageDisabled}
                showSearch
                filterOption={false}
                placeholder='Search Custom Codon Usage'
                onSearch={this.handleCodonUsageSearch}
                onChange={this.handleCodonUsageChange}
              >
                {codonUsageOptions}
              </Select>
            )}
          </Form.Item>
          <React.Fragment/>
          <Form.Item>
            {getFieldDecorator('customCodonUsage')(
              <Input type='hidden'/>)}
          </Form.Item>
        </Tooltip>
        <Tooltip
          title='Enter threshold of frequency percentage. Only codons above
            entered threshold will be used.'>
          <React.Fragment/>
          <Form.Item label='Codon Usage Frequency Threshold Percentage'>
            {getFieldDecorator('codonUsageFrequencyThresholdPct', {
              initialValue: 10,
              rules: [{
                required: true,
                message: 'Frequency Threshold Percentage is required'
              }],
            })(<InputNumber min={0} max={100}/>)}
          </Form.Item>
        </Tooltip>
      </FormSection>
    )

  }
}
