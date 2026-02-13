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

import React, { useState, useEffect, useRef, useContext, useCallback } from 'react'
import { CloseOutlined } from '@ant-design/icons'
import { Form, Table, Input, InputNumber, Popconfirm, Button } from 'antd'
import {
  aminoAcidToCodons,
  codonTableIncludes,
} from 'shared/genes'

import '../../../styles.css'

const EditableContext = React.createContext(null)

const EditableRow = ({ index, ...props }) => {
  const [form] = Form.useForm()
  return (
    <Form form={form} component={false}>
      <EditableContext.Provider value={form}>
        <tr {...props} />
      </EditableContext.Provider>
    </Form>
  )
}

const EditableCell = ({
  editable,
  dataIndex,
  title,
  record,
  index,
  handleSave,
  children,
  inputType,
  ...restProps
}) => {
  const [editing, setEditing] = useState(true)
  const inputRef = useRef(null)
  const form = useContext(EditableContext)

  useEffect(() => {
    if (editing && inputRef.current) {
      inputRef.current.focus()
    }
  }, [editing])

  const validateTarget = (_, value) => {
    if (value && value.length > 1 && dataIndex === 'target') {
      const sequence = document.getElementById('goiSequence')?.value || ''
      const sequenceTypeSelector = document.getElementsByName('sequenceRadioButton')[0]
      let sequenceType = 'dna'
      if (sequenceTypeSelector) {
        if (sequenceTypeSelector.value === 'dna' && sequenceTypeSelector.checked) {
          sequenceType = 'dna'
        } else {
          sequenceType = 'protein'
        }
      }
      const targetValue = value.charAt(0).toUpperCase()
      const position = parseInt(value.slice(1))
      const errorStr = `Target ${targetValue} is not present at site ${position}. Current value is `
      if (sequenceType === 'protein') {
        if (sequence.charAt(position - 1) === targetValue) {
          return Promise.resolve()
        }
        return Promise.reject(new Error(errorStr))
      } else {
        if (
          codonTableIncludes(targetValue) &&
          aminoAcidToCodons(targetValue).includes(sequence.substr((position - 1) * 3, 3))
        ) {
          return Promise.resolve()
        }
        return Promise.reject(new Error(errorStr))
      }
    }
    return Promise.resolve()
  }

  const validateMT = (_, value) => {
    if (value && dataIndex === 'mt') {
      const mutationsTypeSelector = document.getElementsByName('mutationsRadioButton')[0]
      let mutationsType = 'dna'
      if (mutationsTypeSelector) {
        if (mutationsTypeSelector.value === 'dna' && mutationsTypeSelector.checked) {
          mutationsType = 'dna'
        } else {
          mutationsType = 'protein'
        }
      }
      if (mutationsType === 'dna') {
        if (!(value || '').match(/^[ACGTacgt, ]+$/)) {
          return Promise.reject(new Error('Allowed values are: A, C, T, G'))
        }
        return Promise.resolve()
      } else {
        if (!(value || '').match(/^[FLIMVSGTAYHQNKDECWRPflimvsgtayhqnkdecwrp, ]+$/)) {
          return Promise.reject(
            new Error('Allowed values are: F, L, I, M, V, S, G, T, A, Y, H, Q, N, K, D, E, C, W, R, P')
          )
        }
        return Promise.resolve()
      }
    }
    return Promise.resolve()
  }

  const validateMTP = (_, value) => {
    if (value !== undefined && dataIndex === 'mtp') {
      if (0 < value && value <= 100) {
        return Promise.resolve()
      }
      return Promise.reject(new Error('MT% must be between 0 and 100'))
    }
    return Promise.resolve()
  }

  const save = async () => {
    try {
      const values = await form.validateFields()
      handleSave({ ...record, ...values })
    } catch {
      // ignore
    }
  }

  const getInputComponent = () => {
    if (inputType === 'number') {
      return (
        <InputNumber
          ref={inputRef}
          onPressEnter={save}
          onBlur={save}
        />
      )
    }
    return (
      <Input
        ref={inputRef}
        onPressEnter={save}
        onBlur={save}
      />
    )
  }

  return (
    <td {...restProps}>
      {editable ? (
        <Form form={form} component={false} initialValues={{ [dataIndex]: record[dataIndex] }}>
          <EditableContext.Provider value={form}>
            {editing ? (
              <Form.Item
                style={{ margin: 0 }}
                name={dataIndex}
                rules={[
                  {
                    required: true,
                    message: `Please Input ${title}`,
                  },
                  { validator: validateTarget },
                  { validator: validateMT },
                  { validator: validateMTP },
                ]}
                initialValue={record[dataIndex]}
              >
                {getInputComponent()}
              </Form.Item>
            ) : (
              <div
                className="editable-cell-value-wrap"
                style={{ paddingRight: 24 }}
                onClick={() => setEditing(true)}
              >
                {children}
              </div>
            )}
          </EditableContext.Provider>
        </Form>
      ) : (
        children
      )}
    </td>
  )
}

const EditableTable = ({ mutations, onChange }) => {
  const [data, setData] = useState(mutations || [])
  const [count, setCount] = useState(mutations?.length || 0)

  useEffect(() => {
    if (mutations) {
      setData(mutations)
      setCount(mutations.length)
    }
  }, [mutations])

  const triggerChange = useCallback(
    (newData) => {
      if (onChange) {
        onChange({ mutations: newData })
      }
    },
    [onChange]
  )

  const handleSave = (row) => {
    const newData = [...data]
    const index = newData.findIndex((item) => row.key === item.key)
    const item = newData[index]
    newData.splice(index, 1, {
      ...item,
      ...row,
    })
    setData(newData)
    triggerChange(newData)
  }

  const handleAdd = () => {
    const newData = {
      key: count,
    }
    const updatedData = [...data, newData]
    setData(updatedData)
    setCount(count + 1)
  }

  const handleDelete = (key) => {
    const filteredDataSource = data.filter((item) => item.key !== key)
    setData(filteredDataSource)
    triggerChange(filteredDataSource)
  }

  const columns = [
    {
      title: 'Target Residue',
      dataIndex: 'target',
      width: '35%',
      editable: true,
    },
    {
      title: 'MT',
      dataIndex: 'mt',
      width: '25%',
      editable: true,
    },
    {
      title: 'MT%',
      dataIndex: 'mtp',
      width: '35%',
      editable: true,
    },
    {
      title: '',
      dataIndex: 'operation',
      width: '5%',
      render: (_, record) =>
        data.length >= 1 ? (
          <Popconfirm title="Sure to delete?" onConfirm={() => handleDelete(record.key)}>
            <Button type="primary" danger shape="circle" icon={<CloseOutlined />} />
          </Popconfirm>
        ) : null,
    },
  ]

  const components = {
    body: {
      row: EditableRow,
      cell: EditableCell,
    },
  }

  const mappedColumns = columns.map((col) => {
    if (!col.editable) {
      return col
    }
    return {
      ...col,
      onCell: (record) => ({
        record,
        inputType: col.dataIndex === 'mtp' ? 'number' : 'text',
        dataIndex: col.dataIndex,
        title: col.title,
        editable: col.editable,
        handleSave,
      }),
    }
  })

  return (
    <div>
      <Table
        components={components}
        bordered
        dataSource={data}
        columns={mappedColumns}
        rowClassName="editable-row"
        pagination={false}
      />
      <Button onClick={handleAdd} type="primary" style={{ marginBottom: 16 }}>
        Add a row
      </Button>
    </div>
  )
}

export default EditableTable
