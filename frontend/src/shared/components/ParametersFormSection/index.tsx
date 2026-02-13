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
import { Controller, UseFormReturn, FieldValues, useWatch } from 'react-hook-form'
import MinOptMaxInputs from 'shared/components/MinOptMaxInputs'

type ParametersFormSectionProps = {
  form: UseFormReturn<FieldValues>
}

const stepsZeroSixteen = {
  0: '0',
  1: '1',
  2: '2',
  4: '4',
  8: '8',
  16: '16',
}

const stepsZeroSixtyfour = {
  0: '0',
  4: '4',
  8: '8',
  16: '16',
  32: '32',
  64: '64',
}

const ParametersFormSection: React.FC<ParametersFormSectionProps> = ({ form }) => {
  React.useEffect(() => {
    const el = document.querySelector('#excludeFlankingPrimers')
    if (el !== null) {
      ;(el as any).click()
    }
  }, [])

  const usePrimerGrowingAlgorithm = useWatch({
    control: form.control,
    name: 'usePrimerGrowingAlgorithm',
    defaultValue: true,
  })

  const excludeFlankingPrimers = useWatch({
    control: form.control,
    name: 'excludeFlankingPrimers',
    defaultValue: false,
  })

  const usePrimerGrowingAlgorithmToggle = (checked: boolean) => {
    if (checked) {
      form.setValue('usePrimer3', false)
      form.setValue('computeHairpinHomodimer', false)
    }
  }

  const handlePrimer3Change = (checked: boolean) => {
    if (checked) {
      form.setValue('usePrimerGrowingAlgorithm', false)
      form.setValue('computeHairpinHomodimer', false)
    }
  }

  return (
    <>
      <Form.Item label="Size">
        <Tooltip title="Enter size of an entire primer">
          <MinOptMaxInputs form={form} fieldPrefix="size" defaults={{ min: 33, opt: 33, max: 60 }} />
        </Tooltip>
      </Form.Item>
      <Form.Item label="3' Size">
        <Tooltip title="Enter size of a 3'-end of the primer">
          <MinOptMaxInputs form={form} fieldPrefix="threePrimeSize" defaults={{ min: 15, opt: 15, max: 42 }} />
        </Tooltip>
      </Form.Item>
      <Form.Item label="5' Size">
        <Tooltip title="Enter size of a 5'-end of the primer">
          <MinOptMaxInputs form={form} fieldPrefix="fivePrimeSize" defaults={{ min: 15, opt: 15, max: 42 }} />
        </Tooltip>
      </Form.Item>
      <Form.Item label="Overlap Size">
        <Tooltip title="Enter size of an overlapping complementary sequence">
          <MinOptMaxInputs form={form} fieldPrefix="overlapSize" defaults={{ min: 33, opt: 33, max: 60 }} />
        </Tooltip>
      </Form.Item>
      <Form.Item label="GC Content">
        <Tooltip title="Enter the percentage of guanine or cytosine in the primers">
          <MinOptMaxInputs form={form} fieldPrefix="gcContent" defaults={{ min: 40, opt: 50, max: 60 }} />
        </Tooltip>
      </Form.Item>
      <Tooltip title="Enter temperature of a 3'-end of the primer">
        <Form.Item label="3' Temperature">
          <MinOptMaxInputs
            form={form}
            fieldPrefix="threePrimeTemperature"
            defaults={{ min: 57, opt: 60, max: 62 }}
            disabled={!excludeFlankingPrimers}
          />
        </Form.Item>
      </Tooltip>
      <Form.Item label="Overlap Temperature">
        <Tooltip title="Enter temperature of an overlapping complementary sequence of reverse and forward primers">
          <MinOptMaxInputs form={form} fieldPrefix="overlapTemperature" defaults={{ min: 57, opt: 60, max: 85 }} />
        </Tooltip>
      </Form.Item>
      <Row gutter={10}>
        <Col span={12}>
          <Tooltip title="Specify the importance of the 3'-end temperature, 16 being the most important and 0 the least important">
            <Form.Item label="3' Temperature Weight">
              <Controller
                name="threePrimeTemperatureWeight"
                control={form.control}
                defaultValue={16}
                render={({ field }) => <Slider {...field} marks={stepsZeroSixteen} min={0} max={16} step={null} />}
              />
            </Form.Item>
          </Tooltip>
        </Col>
        <Col span={12}>
          <Tooltip title="Specify the importance of the 3'-end size, 16 being the most important and 0 the least important">
            <Form.Item label="3' Size Weight">
              <Controller
                name="threePrimeSizeWeight"
                control={form.control}
                defaultValue={8}
                render={({ field }) => <Slider {...field} marks={stepsZeroSixteen} min={0} max={16} step={null} />}
              />
            </Form.Item>
          </Tooltip>
        </Col>
      </Row>
      <Row gutter={10}>
        <Col span={12}>
          <Tooltip title="Specify the importance of the overlap temperature, 16 being the most important and 0 the least important">
            <Form.Item label="Overlap Temperature Weight">
              <Controller
                name="overlapTemperatureWeight"
                control={form.control}
                defaultValue={1}
                render={({ field }) => <Slider {...field} marks={stepsZeroSixteen} min={0} max={16} step={null} />}
              />
            </Form.Item>
          </Tooltip>
        </Col>
        <Col span={12}>
          <Tooltip title="Specify the importance of the GC Content, 16 being the most important and 0 the least important">
            <Form.Item label="GC Content Weight">
              <Controller
                name="gcContentWeight"
                control={form.control}
                defaultValue={0}
                render={({ field }) => <Slider {...field} marks={stepsZeroSixteen} min={0} max={16} step={null} />}
              />
            </Form.Item>
          </Tooltip>
        </Col>
      </Row>
      <Row gutter={10}>
        <Col span={12}>
          <Tooltip title="Specify the importance of Hairpin Temperature, 64 being the most important and 0 the least important">
            <Form.Item label="Hairpin Temperature Weight">
              <Controller
                name="hairpinTemperatureWeight"
                control={form.control}
                defaultValue={32}
                render={({ field }) => <Slider {...field} marks={stepsZeroSixtyfour} min={0} max={64} step={null} />}
              />
            </Form.Item>
          </Tooltip>
        </Col>
        <Col span={12}>
          <Tooltip title="Specify the importance of Primer-dimer Temperature, 64 being the most important and 0 the least important">
            <Form.Item label="Primer-dimer Temperature Weight">
              <Controller
                name="primerDimerTemperatureWeight"
                control={form.control}
                defaultValue={32}
                render={({ field }) => <Slider {...field} marks={stepsZeroSixtyfour} min={0} max={64} step={null} />}
              />
            </Form.Item>
          </Tooltip>
        </Col>
      </Row>
      <Tooltip title="Enter maximum temperature difference between 3'-ends of the primers and maximum temperature difference between temperature of an overlapping complementary sequence of reverse and forward primers">
        <Form.Item label="Max Temperature Difference" hasFeedback>
          <Controller
            name="maxTemperatureDifference"
            control={form.control}
            defaultValue={5}
            rules={{ required: 'Max Temperature Difference is required' }}
            render={({ field }) => <Input {...field} type="number" />}
          />
        </Form.Item>
      </Tooltip>
      <Row gutter={10}>
        <Col span={8}>
          <Tooltip title="Calculate 3'-end of reverse and forward primers separately">
            <Form.Item label="Calculate 3' Tm separately">
              <Controller
                name="separateForwardReverseTemperatures"
                control={form.control}
                defaultValue={false}
                render={({ field }) => <Switch {...field} checked={field.value} />}
              />
            </Form.Item>
          </Tooltip>
        </Col>
        <Col span={10}>
          <Tooltip title="Calculate 3'-end Tm of mutagenic primers separately from flanking primers">
            <Form.Item label="Exclude flanking primers from 3' Tm calculation">
              <Controller
                name="excludeFlankingPrimers"
                control={form.control}
                defaultValue={false}
                render={({ field }) => <Switch {...field} checked={field.value} />}
              />
            </Form.Item>
          </Tooltip>
        </Col>
      </Row>
      <Tooltip title="Design mutagenic primers with or without using Primer3 application">
        <Form.Item label="Use primer3">
          <Controller
            name="usePrimer3"
            control={form.control}
            defaultValue={false}
            render={({ field }) => (
              <Switch {...field} checked={field.value} onChange={handlePrimer3Change} disabled={usePrimerGrowingAlgorithm} />
            )}
          />
        </Form.Item>
      </Tooltip>
      <Row gutter={10}>
        <Col span={8}>
          <Tooltip title="Design mutagenic primers with or without the fast primer extension algorithm.">
            <Form.Item label="Use FASTER approximate algorithm">
              <Controller
                name="usePrimerGrowingAlgorithm"
                control={form.control}
                defaultValue={true}
                render={({ field }) => (
                  <Switch {...field} checked={field.value} onChange={usePrimerGrowingAlgorithmToggle} />
                )}
              />
            </Form.Item>
          </Tooltip>
        </Col>
        <Col span={12}>
          <Tooltip title="Toggles whether the fast primer extension algorithm calculates hairpin and primer-dimer temperatures.">
            <Form.Item label="Check for hairpins and primer-dimers">
              <Controller
                name="computeHairpinHomodimer"
                control={form.control}
                defaultValue={false}
                render={({ field }) => <Switch {...field} checked={field.value} />}
              />
            </Form.Item>
          </Tooltip>
        </Col>
      </Row>
    </>
  )
}

export default ParametersFormSection
