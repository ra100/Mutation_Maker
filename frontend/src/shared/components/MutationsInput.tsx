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

import {Input} from 'antd'
import * as React from 'react'

import {groupsOf} from 'shared/groupsOf'
import {TextAreaProps} from "antd/lib/input";
import {HTMLTextareaProps} from "antd/lib/input/TextArea";

const transformMutations = (cols: number) => (mutations: string): string => {
  const groups = groupsOf(cols, mutations.split(/\s+/));
  return groups.map(group => group.join('\t').toUpperCase()).join('\n')
};

type MutationsInputProps = TextAreaProps &
  HTMLTextareaProps & {
    cols: number
  }

class MutationsInput extends React.Component<MutationsInputProps> {
  render() {
    const { cols, value, ...props } = this.props;

    return (
      <Input.TextArea
        autoSize={props.autosize || { minRows: 3 }}
        value={value && transformMutations(cols)(value.toString())}
        {...props}
      />
    )
  }
}

export default MutationsInput
