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

import { Icon, Upload } from 'antd'
import * as React from 'react'

const Dragger = Upload.Dragger;

const FILE_EXTENSIONS = '.fa, .fasta, .gb';

const getSequenceFromFile = (data: string | ArrayBuffer | null): string => {
  if (!data) {
    return ''
  }
  const text = data.toString();
  if (text[0] === '>') {
    return text.split('\n').slice(1).join('')
  }
  if (text.indexOf('ORIGIN') > -1) {
    return text.split('ORIGIN')[1].split('')
      .filter(letter => /[ATCGatcgFLIMVSYHQNKDEWRPflimvsyhqnkdewrp]/.test(letter))
      .join('').toUpperCase()
  }

  return ''
};

type FileUploadInputProps = {
  onChange(data: string): void
}

class FileUploadInput extends React.Component<FileUploadInputProps> {
  state = {
    fileList: []
  };

  fileReader = new FileReader();

  constructor(props: any) {
    super(props);
    this.fileReader.onload = this.onload
  }

  onload = () => {
    this.props.onChange(getSequenceFromFile(this.fileReader.result))
  };

  handleRequest = (option: any) => {
    this.fileReader.readAsText(option.file);
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
          <Icon type="inbox" />
        </p>
        <p className="ant-upload-text">Click or drag file to this area to upload .fa, .fasta or .gb files</p>
      </Dragger>
    )
  }
}

export default FileUploadInput
