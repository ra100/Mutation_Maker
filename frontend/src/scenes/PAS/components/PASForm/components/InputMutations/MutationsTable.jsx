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

import React from 'react'
import {
  Table,
  Input,
  InputNumber,
  Popconfirm,
  Form,
  Button
} from 'antd'
import {
  aminoAcidToCodons,
  codonTableIncludes
} from "shared/genes";

import '../../../styles.css'

const EditableContext = React.createContext();

const EditableRow = ({ form, index, ...props }) => (
  <EditableContext.Provider value={form}>
    <tr {...props} />
  </EditableContext.Provider>
);

const EditableFormRow = Form.create()(EditableRow);

class EditableCell extends React.Component {
  state = {
    editing: true,
  };

  toggleEdit = () => {
    const editing = !this.state.editing;
    this.setState({ editing }, () => {
      if (editing) {
        this.input.focus()
      }
    })
  };

  save = e => {
    e.preventDefault();
    const { record, handleSave } = this.props;
    this.form.validateFields((error, values) => {
      this.toggleEdit();
      handleSave({ ...record, ...values })
    })
  };

  renderCell = form => {
    this.form = form;
    const { children, dataIndex, record, title } = this.props;
    const { editing } = this.state;
    return editing ? (
      <Form.Item style={{ margin: 0 }}>
        {form.getFieldDecorator(dataIndex, {
          rules: [
            {
              required: true,
              message: `Please Input ${title}`,
            },
            {validator: this.validateTarget},
            {validator: this.validateMT},
            {validator: this.validateMTP},
          ],
          initialValue: record[dataIndex],
        })(
          this.props.inputType === 'number' ?
            <InputNumber ref={node => (this.input = node)} onPressEnter={this.save} onBlur={this.save} /> :
            <Input ref={node => (this.input = node)} onPressEnter={this.save} onBlur={this.save} />
          )}
      </Form.Item>
    ) : (
      <div
        className="editable-cell-value-wrap"
        style={{ paddingRight: 24 }}
        onClick={this.toggleEdit}
      >
        {children}
      </div>
    )
  };

  validateTarget = (rule, value, callback) => {
    if (value && value.length > 1 && rule.field === 'target') {
      const sequence = document.getElementById('goiSequence').value;
      const sequenceTypeSelector = document.getElementsByName('sequenceRadioButton')[0];
      let sequenceType = 'dna';
      if (sequenceTypeSelector.value === 'dna') {
        if (sequenceTypeSelector.checked === true) sequenceType = 'dna';
        else sequenceType = 'protein'
      }
      const targetValue = value.charAt(0).toUpperCase();
      const position = parseInt(value.slice(1));
      const errorStr = `Target ${targetValue} is not present at site ${position}.
          Current value is `;
      if(sequenceType === "protein") {
        if (sequence.charAt(position-1) === targetValue) {
          callback()
        } else {
          callback(errorStr)
        }
      } else {
        if (codonTableIncludes(targetValue) && aminoAcidToCodons(targetValue)
          .includes(sequence.substr((position-1)*3, 3))) {
          callback()
        } else {
          callback(errorStr)
        }
      }
    } else {
      callback()
    }
  };

  validateMT = (rule, value, callback) => {
    if (value && rule.field === 'mt') {
      const mutationsTypeSelector = document.getElementsByName('mutationsRadioButton')[0];
      let mutationsType = 'dna';
      if (mutationsTypeSelector.value === 'dna') {
        if (mutationsTypeSelector.checked === true) mutationsType = 'dna';
        else mutationsType = 'protein'
      }
        if (mutationsType === 'dna') {
          if (!(value || '').match(/^[ACGTacgt, ]+$/)) {
            callback('Allowed values are: '
              + 'A, C, T, G')
          } else {
            callback()
          }
        } else {
        if (!(value || '').match(/^[FLIMVSGTAYHQNKDECWRPflimvsgtayhqnkdecwrp, ]+$/)) {
          callback('Allowed values are: '
            + 'F, L, I, M, V, S, G, T, A, Y, H, Q, N, K, D, E, C, W, R, P')
        } else {
          callback()
        }
      }
    } else {
      callback()
    }
  };

  validateMTP = (rule, value, callback) => {
    if (value && rule.field === 'mtp') {
      if (0 < value && value <= 100) callback();
      else callback('MT% must be between 0 and 100')
    } else {
      callback()
    }
  };

  render() {
    const {
      editable,
      dataIndex,
      title,
      record,
      index,
      handleSave,
      children,
      ...restProps
    } = this.props;
    return (
      <td {...restProps}>
        {editable ? (
          <EditableContext.Consumer>{this.renderCell}</EditableContext.Consumer>
        ) : (
          children
        )}
      </td>
    )
  }
}

class EditableTable extends React.Component {
  constructor(props) {
    super(props);
    const mutations = props.mutations;

    this.state = {
      data: mutations,
      editingKey: '',
      count: 0,
    };

    this.columns = [
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
        render: (text, record) =>
          this.state.data.length >= 1 ? (
            <Popconfirm title="Sure to delete?" onConfirm={() => this.handleDelete(record.key)}>
              <Button type="danger" shape="circle" icon="close" />
            </Popconfirm>
          ) : null,
      }
    ]
  }

  static getDerivedStateFromProps(nextProps) {
    // Should be a controlled component.
    if ('value' in nextProps) {
      return {
        ...(nextProps.value || {}),
      }
    }
    return null
  }

  isEditing = record => record.key === this.state.editingKey;

  triggerChange = changedValue => {
    // Should provide an event to pass value to Form.
    const { onChange } = this.props;
    if (onChange) {
      onChange({
        ...changedValue,
      })
    }
  };

  handleSave = row => {
    const newData = [...this.state.data];
    const index = newData.findIndex(item => row.key === item.key);
    const item = newData[index];
    newData.splice(index, 1, {
      ...item,
      ...row,
    });
    this.setState({ data: newData });
    this.triggerChange({mutations: newData})
  };

  handleAdd = () => {
    const {count, data} = this.state;
    const newData = {
      key: count
    };
    this.setState({
      data: [...data, newData],
      count: count + 1,
    })
  };

  handleDelete = key => {
    const dataSource = [...this.state.data];
    const filteredDataSource = dataSource.filter(item => item.key !== key);
    this.setState({
      data: filteredDataSource
    });
    this.triggerChange({mutations: filteredDataSource})
  };

  componentDidUpdate = (prevProps, prevState, snapshot) => {
    // Check if the suplied props is changed
    if (prevProps.mutations !== this.props.mutations) {
      // run the function with the suplied new property
      this.setState({
        data: this.props.mutations,
        count: this.props.mutations.length,
      })
    }
  };

  render() {
    const components = {
      body: {
        row: EditableFormRow,
        cell: EditableCell,
      }
    };

    const columns = this.columns.map(col => {
      if (!col.editable) {
        return col
      }
      return {
        ...col,
        onCell: record => ({
          record,
          inputType: col.dataIndex === 'mtp' ? 'number' : 'text',
          dataIndex: col.dataIndex,
          title: col.title,
          editable: col.editable,
          handleSave: this.handleSave
        }),
      }
    });

    return (
      <div>
        <EditableContext.Provider value={this.props.form}>
          <Table
            components={components}
            bordered
            dataSource={this.state.data}
            columns={columns}
            rowClassName="editable-row"
            pagination={false}
          />
          <Button onClick={this.handleAdd} type="primary"
                  style={{marginBottom: 16}}>
            Add a row
          </Button>
        </EditableContext.Provider>
      </div>
    )
  }
}

const EditableFormTable = Form.create()(EditableTable);
export default EditableFormTable
