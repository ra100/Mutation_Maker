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

import { Col, Input, Row } from 'antd'
import { WrappedFormUtils } from 'antd/lib/form/Form'
import * as R from 'ramda'
import * as React from 'react'

type MinOptMaxInputsProps = Pick<
  WrappedFormUtils,
  'getFieldDecorator' | 'getFieldValue' | 'resetFields'
> & {
  fieldPrefix: string
  defaults?: {
    min?: number
    opt?: number
    max?: number
  },
  disabled?: boolean
  optimalPresent?: boolean
}

const MinOptMaxInputs = ({
  getFieldDecorator,
  getFieldValue,
  resetFields,
  fieldPrefix,
  defaults = {},
  disabled = false,
  optimalPresent = false,
}: MinOptMaxInputsProps) => {
  const onBlurReset = (fieldName: string) => () => {
    if (R.isEmpty(getFieldValue(fieldName))) {
      resetFields([fieldName])
    }
  }

  return (
    <Row className="MinOptMaxInputs" gutter={10}>
      <Col span={optimalPresent ? 8 : 12}>
        {getFieldDecorator(`${fieldPrefix}Min`, { initialValue: defaults.min })(
          <Input type="number" addonBefore="MIN" onBlur={onBlurReset(`${fieldPrefix}Min`)} disabled={disabled} />,
        )}
      </Col>
      {optimalPresent &&
        <Col span={8}>
          {getFieldDecorator(`${fieldPrefix}Opt`, { initialValue: defaults.opt })(
            <Input type="number" addonBefore="OPT" onBlur={onBlurReset(`${fieldPrefix}Opt`)} disabled={disabled} />,
          )}
        </Col>
      }
      <Col span={optimalPresent ? 8 : 12}>
        {getFieldDecorator(`${fieldPrefix}Max`, { initialValue: defaults.max })(
          <Input type="number" addonBefore="MAX" onBlur={onBlurReset(`${fieldPrefix}Max`)} disabled={disabled} />,
        )}
      </Col>
    </Row>
  )
}

export default MinOptMaxInputs
