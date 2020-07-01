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

import { Col, Form, Input, Row, Slider, Switch, Tooltip } from 'antd'
import * as React from 'react'
import MinOptMaxInputs from 'shared/components/MinOptMaxInputs'
import {WrappedFormUtils} from "antd/lib/form/Form";

type ParametersFormSectionProps = Pick<
  WrappedFormUtils,
  'getFieldDecorator' | 'getFieldValue' | 'resetFields' | 'setFieldsValue'
>

class ParametersFormSection extends React.Component<ParametersFormSectionProps> {
  stepsZeroSixteen = {
    0: '0',
    1: '1',
    2: '2',
    4: '4',
    8: '8',
    16: '16',
  }

  stepsZeroSixtyfour = {
    0: '0',
    4: '4',
    8: '8',
    16: '16',
    32: '32',
    64: '64',
  }

  stepsZeroHundredsixty = {
    0: '0',
    20: '20',
    40: '40',
    80: '80',
    160: '160',
  }

  componentDidMount() {
    const el = document.querySelector("#excludeFlankingPrimers")
    if (el !== null) {
      (el as any).click();
    }
  }

  usePrimerGrowingAlgorithmToggle = (checked: boolean) => {
    const { setFieldsValue } = this.props
    if (checked) {
      setFieldsValue({
        usePrimer3: false,
        computeHairpinHomodimer: false
      })
    }
  }

  handlePrimer3Change = (checked: boolean) => {
    const { setFieldsValue } = this.props
    if (checked) {
      setFieldsValue({
        // Here we just turn off some settings
        usePrimerGrowingAlgorithm: false,
        computeHairpinHomodimer: false
      })
    }
  }

  render() {
    const { getFieldDecorator, getFieldValue, resetFields } = this.props

    return (
      <>
        <Form.Item label="Size">
          <Tooltip title="Enter size of an entire primer">
            <React.Fragment />
            <MinOptMaxInputs
              getFieldDecorator={getFieldDecorator}
              getFieldValue={getFieldValue}
              resetFields={resetFields}
              fieldPrefix="size"
              defaults={{ min: 33, opt: 33, max: 60 }}
            />
          </Tooltip>
        </Form.Item>
        <Form.Item label="3' Size">
          <Tooltip title="Enter size of a 3'-end of the primer">
            <React.Fragment />
            <MinOptMaxInputs
              getFieldDecorator={getFieldDecorator}
              getFieldValue={getFieldValue}
              resetFields={resetFields}
              fieldPrefix="threePrimeSize"
              defaults={{ min: 15, opt: 15, max: 42 }}
            />
          </Tooltip>
        </Form.Item>
        <Form.Item label="5' Size">
          <Tooltip title="Enter size of a 5'-end of the primer">
            <React.Fragment />
            <MinOptMaxInputs
              getFieldDecorator={getFieldDecorator}
              getFieldValue={getFieldValue}
              resetFields={resetFields}
              fieldPrefix="fivePrimeSize"
              defaults={{ min: 15, opt: 15, max: 42 }}
            />
          </Tooltip>
        </Form.Item>
        <Form.Item label="Overlap Size">
          <Tooltip title="Enter size of an overlapping complementary sequence">
            <React.Fragment />
            <MinOptMaxInputs
              getFieldDecorator={getFieldDecorator}
              getFieldValue={getFieldValue}
              resetFields={resetFields}
              fieldPrefix="overlapSize"
              defaults={{ min: 33, opt: 33, max: 60 }}
            />
          </Tooltip>
        </Form.Item>
        <Form.Item label="GC Content">
          <Tooltip title="Enter the percentage of guanine or cytosine in the primers">
            <React.Fragment />
            <MinOptMaxInputs
              getFieldDecorator={getFieldDecorator}
              getFieldValue={getFieldValue}
              resetFields={resetFields}
              fieldPrefix="gcContent"
              defaults={{ min: 40, opt: 50, max: 60 }}
            />
          </Tooltip>
        </Form.Item>
        <Tooltip title="Enter temperature of a 3'-end of the primer">
          <React.Fragment />
          <Form.Item label="3' Temperature">
            <MinOptMaxInputs
              getFieldDecorator={getFieldDecorator}
              getFieldValue={getFieldValue}
              resetFields={resetFields}
              fieldPrefix="threePrimeTemperature"
              defaults={{ min: 57, opt: 60, max: 62 }}
              disabled={!getFieldValue('excludeFlankingPrimers')}
            />
          </Form.Item>
        </Tooltip>
        <Form.Item label="Overlap Temperature">
          <Tooltip title="Enter temperature of an overlapping complementary sequence of reverse and forward primers">
            <React.Fragment />
            <MinOptMaxInputs
              getFieldDecorator={getFieldDecorator}
              getFieldValue={getFieldValue}
              resetFields={resetFields}
              fieldPrefix="overlapTemperature"
              defaults={{ min: 57, opt: 60, max: 85 }}
            />
          </Tooltip>
        </Form.Item>
        <Row gutter={10}>
          <Col span={12}>
            <Tooltip title="Specify the importance of the 3'-end temperature,  16 being the most important and 0 the least important">
              <React.Fragment />
              <Form.Item label="3' Temperature Weight">
                {getFieldDecorator('threePrimeTemperatureWeight', {
                  initialValue: 16,
                  valuePropName: 'value',
                })(<Slider marks={this.stepsZeroSixteen} min={0} max={16} step={null} />)}
              </Form.Item>
            </Tooltip>
          </Col>
          <Col span={12}>
            <Tooltip title="Specify the importance of the 3'-end size, 16  being the most important and 0 the least important">
              <React.Fragment />
              <Form.Item label="3' Size Weight">
                {getFieldDecorator('threePrimeSizeWeight', {
                  initialValue: 8,
                  valuePropName: 'value',
                })(<Slider marks={this.stepsZeroSixteen} min={0} max={16} step={null} />)}
              </Form.Item>
            </Tooltip>
          </Col>
        </Row>
        <Row gutter={10}>
          <Col span={12}>
            <Tooltip title="Specify the importance of the overlap temperature, 16  being the most important and 0 the least important">
              <React.Fragment />
              <Form.Item label="Overlap Temperature Weight">
                {getFieldDecorator('overlapTemperatureWeight', {
                  initialValue: 1,
                  valuePropName: 'value',
                })(<Slider marks={this.stepsZeroSixteen} min={0} max={16} step={null} />)}
              </Form.Item>
            </Tooltip>
          </Col>
          <Col span={12}>
            <Tooltip title="Specify the importance of the GC Content, 16  being the most important and 0 the least important">
              <React.Fragment />
              <Form.Item label="GC Content Weight">
                {getFieldDecorator('gcContentWeight', {
                  initialValue: 0,
                  valuePropName: 'value',
                })(<Slider marks={this.stepsZeroSixteen} min={0} max={16} step={null} />)}
              </Form.Item>
            </Tooltip>
          </Col>
        </Row>

        <Row gutter={10}>
          <Col span={12}>
            <Tooltip title="Specify the importance of Hairpin Temperature, 64 being the most important and 0 the least important. Hairpins with temperatures close to the melting temperature of the primer are penalized mores than those with hairpin temperatures far from the melting temperature.">
              <React.Fragment />
              <Form.Item label="Hairpin Temperature Weight">
                {getFieldDecorator('hairpinTemperatureWeight', {
                  initialValue: 32,
                  valuePropName: 'value',
                })(<Slider marks={this.stepsZeroSixtyfour} min={0} max={64} step={null} />)}
              </Form.Item>
            </Tooltip>
          </Col>

          <Col span={12}>
            <Tooltip title="Specify the importance of Primer-dimer Temperature, 64 being the most important and 0 the least important. Primer-dimer with temperatures close to the melting temperature of the primer are penalized mores than those with primer-dimer temperatures far from the melting temperature.">
              <React.Fragment />
              <Form.Item label="Primer-dimer Temperature Weight">
                {getFieldDecorator('primerDimerTemperatureWeight', {
                initialValue: 32,
                  valuePropName: 'value',
                })(<Slider marks={this.stepsZeroSixtyfour} min={0} max={64} step={null} />)}
              </Form.Item>
            </Tooltip>
          </Col>
        </Row>

        <Tooltip title="Enter maximum temperature difference between 3'-ends of the primers and maximum temperature difference between temperature of an overlapping complementary sequence of reverse and forward primers">
          <React.Fragment />
          <Form.Item label="Max Temperature Difference" hasFeedback>
            {getFieldDecorator('maxTemperatureDifference', {
              rules: [{ required: true, message: 'Max Temperature Difference is required' }],
              initialValue: 5,
            })(<Input type="number" />)}
          </Form.Item>
        </Tooltip>

        <Row gutter={10}>
          <Col span={8}>
            <Tooltip title="Calculate 3'-end of reverse and forward primers separately">
              <React.Fragment />
              <Form.Item label="Calculate 3' Tm separately">
                {getFieldDecorator('separateForwardReverseTemperatures', {
                  initialValue: false,
                  valuePropName: 'checked',
                })(<Switch />)}
              </Form.Item>
            </Tooltip>
          </Col>

          <Col span={10}>
            <Tooltip title="Calculate 3'-end Tm of mutagenic primers separately from flanking primers">
              <React.Fragment />
              <Form.Item label="Exclude flanking primers from 3' Tm calculation">
                {getFieldDecorator('excludeFlankingPrimers', {
                  initialValue: false,
                  valuePropName: 'checked',
                })(<Switch />)}
              </Form.Item>
            </Tooltip>
          </Col>
        </Row>

        <Tooltip title="Design mutagenic primers with or without using Primer3 application">
          <React.Fragment />
          <Form.Item label="Use primer3">
            {getFieldDecorator('usePrimer3', {
              initialValue: false,
              valuePropName: 'checked',
            })(<Switch onChange={this.handlePrimer3Change} disabled={getFieldValue('usePrimerGrowingAlgorithm')}/>)}
          </Form.Item>
        </Tooltip>

        <Row gutter={10}>
          <Col span={8}>
            <Tooltip title="Design mutagenic primers with or without the fast primer extension algorithm. The results are achieved much faster, but at the cost of possibly missing a better solution.">
              <React.Fragment />
              <Form.Item label="Use FASTER approximate algorithm">
                {getFieldDecorator('usePrimerGrowingAlgorithm', {
                  initialValue: true,
                  valuePropName: 'checked',
                })(<Switch onChange={this.usePrimerGrowingAlgorithmToggle} />)}
              </Form.Item>
            </Tooltip>
          </Col>
          <Col span={12}>
            <Tooltip title="Toggles whether the fast primer extension algorithm calculates hairpin and primer-dimer temperatures. Solutions which form hairpins and primer-dimers are penalized and solutions without them are picked instead (unless they break other constraints more).">
              <React.Fragment />
              <Form.Item label="Check for hairpins and primer-dimers">
                {getFieldDecorator('computeHairpinHomodimer', {
                  initialValue: false,
                  valuePropName: 'checked',
                })(<Switch />)}
              </Form.Item>
            </Tooltip>
          </Col>
        </Row>
      </>
    )
  }
}

export default ParametersFormSection
