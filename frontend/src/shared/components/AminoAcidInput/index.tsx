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

import { Button, Row, Spin } from 'antd'
import * as React from 'react'

export type AminoType = {
  name: string
  state: string
}

type AminoAcidInputProps = {
  value?: AminoType[]
  loading?: boolean
  onChange?(data: object): void
}

class AminoAcidInput extends React.Component<AminoAcidInputProps> {
  static defaultProps: AminoAcidInputProps = {
    value: [],
    onChange: () => ({})
  }

  handleButtonClick = (state: string, acid: string) => () => {
    const newValue = this.props.value!.map(value => {
      if (value.name !== acid) {
        return value
      }

      return {
        ...value,
        state: state === value.state ? '' : state
      }
    })
    this.props.onChange!(newValue)
  }

  render() {
    const {value} = this.props

    const select =
    (<>
      <h3>To include</h3>
      <Row>
        {
          value!.map(({name, state}) =>
            <Button
              className="btn-codons"
              key={name}
              disabled={state === 'avoid'}
              type={state === 'include' ? 'primary' : 'default'}
              onClick={this.handleButtonClick('include', name)}
            >{name}</Button>)
        }
        <p>Select which amino acids you want to include.</p>
      </Row>
      <h3>To avoid</h3>
      <Row>
        {
          value!.map(({name, state}) =>
            <Button
              className="btn-codons"
              key={name}
              disabled={state === 'include'}
              type={state === 'avoid' ? 'primary' : 'default'}
              onClick={this.handleButtonClick('avoid', name)}
            >{name}</Button>)
        }
        <p>Select which amino acids you want to exclude.</p>
      </Row>
    </>)

    return (
      <Row>
        {this.props.loading && <Spin tip="Computing...">{select}</Spin>}
        {!this.props.loading && select}
      </Row>
    )
  }
}

export default AminoAcidInput
