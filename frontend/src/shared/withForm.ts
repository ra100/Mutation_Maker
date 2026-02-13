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

import { Form, FormInstance } from 'antd'
import React from 'react'

export type WithFormOuterProps<D> = {
  data: Partial<D>
  onSubmit(data: D): void
}

export type WithFormInnerProps<D> = WithFormOuterProps<D> & {
  form: FormInstance
}

function withForm<P, D>(
  Component: React.ComponentType<P & WithFormInnerProps<D>>,
): React.FC<P & WithFormOuterProps<D>> {
  const WrappedComponent: React.FC<P & WithFormOuterProps<D>> = (props) => {
    const [form] = Form.useForm()

    React.useEffect(() => {
      if (props.data) {
        form.setFieldsValue(props.data as any)
      }
    }, [props.data, form])

    const handleSubmit = (values: D) => {
      props.onSubmit(values)
    }

    return (
      <Form form={form} layout="vertical" onFinish={handleSubmit}>
        <Component {...props} form={form} />
      </Form>
    )
  }

  WrappedComponent.displayName = `withForm(${Component.displayName || Component.name || 'Component'})`

  return WrappedComponent
}

export default withForm
