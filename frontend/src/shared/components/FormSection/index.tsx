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

import { Avatar, Col, Collapse, Row, Tooltip} from 'antd'
import * as R from 'ramda'
import * as React from 'react'
import './styles.css'

const Panel = Collapse.Panel;

type FormSectionProps = {
  index?: number
  title?: string
  tooltip?: string
  children: React.ReactNode
  collapse?: boolean
  open?: boolean
}

type FormSectionTitleProps = {
  index?: number
  title?: string
  children?: React.ReactNode
  tooltip?: string
}

const FormSectionTitle: React.SFC<FormSectionTitleProps> =
  ({ index, title, children, tooltip }) =>(
  <Row className="FormSection">
    <Col span={1} className="FormSection-number--col">
      {!R.isNil(index) && <Avatar>{index}</Avatar>}
    </Col>
    <Col span={22}>
    {tooltip ?
      <Tooltip title="Enter primers parameters">
        <React.Fragment/>
        {!R.isNil(title) && <h1>{title}</h1>}
      </Tooltip>
      : (!R.isNil(title) && <h1>{title}</h1>)
    }
      {children}
    </Col>
  </Row>
);

const FormSection: React.SFC<FormSectionProps> = ({ index, title, children, collapse = true, open = true, tooltip }) => (
  <React.Fragment>
    {collapse &&
      <Collapse defaultActiveKey={open ? ['1'] : undefined}>
        <Panel header={<FormSectionTitle index={index} title={title} tooltip={tooltip}/>} key="1" forceRender>
          {children}
        </Panel>
      </Collapse>}
    {!collapse && <div className="FormSectionNotCollapsing">
      <FormSectionTitle index={index} title={title} children={children} tooltip={tooltip}/>
    </div>}
  </React.Fragment>
);

export default FormSection
