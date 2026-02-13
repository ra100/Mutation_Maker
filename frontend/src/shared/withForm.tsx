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
import React from 'react'
import { FormProvider, useForm, UseFormReturn, FieldValues } from 'react-hook-form'

export type WithFormOuterProps<D> = {
  data: Partial<D>
  onSubmit(data: D): void
}

export type WithFormInnerProps<D> = WithFormOuterProps<D> & {
  form: UseFormReturn<D, FieldValues>
}

function withForm<P, D extends FieldValues>(
  Component: React.ComponentType<P & WithFormInnerProps<D>>,
): React.FC<P & WithFormOuterProps<D>> {
  const WrappedComponent: React.FC<P & WithFormOuterProps<D>> = (props) => {
    const form = useForm<D>({
      defaultValues: props.data as D,
    })

    React.useEffect(() => {
      if (props.data) {
        form.reset(props.data as D)
      }
    }, [props.data, form])

    const handleSubmit = form.handleSubmit((values) => {
      props.onSubmit(values)
    })

    return (
      <Form layout="vertical" onFinish={handleSubmit}>
        <FormProvider {...form}>
          <Component {...props} form={form} />
        </FormProvider>
      </Form>
    )
  }

  WrappedComponent.displayName = `withForm(${Component.displayName || Component.name || 'Component'})`

  return WrappedComponent
}

export default withForm
