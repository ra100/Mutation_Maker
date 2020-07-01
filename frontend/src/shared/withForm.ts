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

import { Form } from 'antd'
import { WrappedFormUtils, FormComponentProps } from 'antd/lib/form/Form'

// TODO: fix types, "FormComponentProps<any> &" might not be right
export type WithFormOuterProps<D> = FormComponentProps<any> & {
  data: Partial<D>
  onSubmit(data: D): void
}

export type WithFormInnerProps<D> = WithFormOuterProps<D> & {
  form: WrappedFormUtils
}

function withForm<P, D>(
  component: React.ComponentClass<P & WithFormInnerProps<D>> | React.SFC<P & WithFormInnerProps<D>>,
) {
  return Form.create<P & WithFormOuterProps<D>>({
    mapPropsToFields({ data }: P & WithFormOuterProps<D>) {
      if (data) {
        return Object.keys(data).reduce((acc, key) => {
          return {
            ...acc,
            [key]: Form.createFormField({
              value: data[key],
            }),
          }
        }, {})
      }

      return undefined
    },
  })(component)
}

export default withForm
