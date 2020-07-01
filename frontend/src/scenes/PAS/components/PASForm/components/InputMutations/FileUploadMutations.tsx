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

import {Icon, message, Upload} from 'antd'
import * as React from 'react'
import {read, utils} from 'xlsx'

const Dragger = Upload.Dragger;

const FILE_EXTENSIONS = '.xlsx';

const getMutationsFromFile = (data: string | ArrayBuffer | null): object => {
  if (!data) {
    return []
  }

  // Read XLSX file
  const wb = read(data, {type: 'binary'});
  const wsname = wb.SheetNames[0];
  const ws = wb.Sheets[wsname];
  const jsonData = utils.sheet_to_json(ws);

  // Convert keys to lower case and string values to upper case
  const formattedJsonData = jsonData.map((obj: object) => {
    const mapped: any = {};
    for (let key in obj) {
      if (typeof obj[key] === 'string') {
        mapped[key.toLowerCase()] = obj[key].toUpperCase()
      } else {
        mapped[key.toLowerCase()] = obj[key]
      }
    }

    return mapped
  });

  // Validate file format
  const header = ['site', 'mt', 'mt%'];
  for (let column of header) {
    if (!formattedJsonData[0].hasOwnProperty(column)) {
      message.error('File has incorrect format. ' +
        'Array must contain collumns: Site, MT and MT%.');
      return {mutations: []}
    }
  }

  // Format result
  const mutations: object[] = [];
  formattedJsonData.forEach((value: object, index) => {
    mutations.push({
      key: index, target: value['site'], mt: value['mt'],
      mtp: value['mt%']
    })
  });

  return {mutations}
};

type FileUploadInputProps = {
  onChange(data: object): void
}

class FileUploadMutations extends React.Component<FileUploadInputProps> {
  state = {
    fileList: []
  };

  fileReader = new FileReader();

  constructor(props: any) {
    super(props);
    this.fileReader.onload = this.onload
  }

  onload = () => {
    this.props.onChange(getMutationsFromFile(this.fileReader.result))
  };

  handleRequest = (option: any) => {

    this.fileReader.readAsBinaryString(option.file);
    this.setState({fileList: []});
    option.onSuccess(true)
  };

  render() {
    return (
      <Dragger
        multiple={false}
        accept={FILE_EXTENSIONS}
        fileList={this.state.fileList}
        customRequest={this.handleRequest}>
        <p className="ant-upload-drag-icon">
          <Icon type="inbox"/>
        </p>
        <p className="ant-upload-text">Click or drag file to this area to upload
          .xlsx file</p>
      </Dragger>
    )
  }
}

export default FileUploadMutations
