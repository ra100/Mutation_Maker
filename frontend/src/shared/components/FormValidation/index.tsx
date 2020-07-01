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

import {aminoAcidToCodons} from "../../genes";

// @TODO make it not throw "Uncaught (in promise)"
export const validateMutations = (mutations: string, sequence: string, callback: any) => {
  try {
      const separated = mutations.trim().replace(/\s+/g, ' ').split(' ');
      const wrongMutations: string[] = [];

      for (const mutation of separated) {
        const start = aminoAcidToCodons(mutation.split('')[0]) || '';
        const position = Number(mutation.replace(/[A-Z]*/g,'')) - 1;
        const target = sequence.slice(position  * 3, position * 3 + 3);
        if (!start.includes(target)) {
          wrongMutations.push(mutation)
        }
      }

      if (wrongMutations.length > 0) {
        return callback(`Mutations ${wrongMutations.join(', ')} not found in sequence`)
      }

      return callback()
      }
  catch (err) {
      console.log(err)
      return callback()
    }
};

export const validateSequence = (rule: any, sequence: any, callback: any,
                                 isSequenceTypeDNA: boolean) => {
  // Required
  if (sequence && sequence.length === 0) {
    callback('Input Sequence is required');
    return
  }

  // const sequenceType = this.props.form.getFieldValue('inputSequenceType');
  if (sequence && sequence.length > 0) { // Validate Codons
    if (isSequenceTypeDNA) {
      if (!(sequence || '').match(/^[ACGTacgt]+$/)) {
        callback('Only A, C, G and T are allowed');
        return
      }
    }
    else { // Validate Amino Acids
      if (!(sequence || '').match(
        /^[FLIMVSGTAYHQNKDECWRPflimvsgtayhqnkdecwrp]+$/)) {
        callback('Only the following values are allowed: '
          + 'F, L, I, M, V, S, G, T, A, Y, H, Q, N, K, D, E, C, W, R, P');
        return
      }
    }
  }
  callback()
};

export const validateAvoidMotifs = (rule: any, values: any, callback: any) => {
  // Optional
  if (!values) {
    callback();
    return
  }

  // Allowed custom values
  const customMotifsRegex = /^[ABCDGHKMNRSTVWYabcdghkmnrstvwy]+$/;
  // Exclude motifs selection list
  const motifsJSON = require('../../motifs.json');
  const customInputs = values.filter((value: any) => !motifsJSON.includes(value));
  const invalidInputs = customInputs.filter((value: any) => !value.match(customMotifsRegex));
  if (invalidInputs.length === 0) {
    callback()
  } else {
    callback('Only the following values are allowed: ' +
      'A, B, C, D, G, H, K, M, N, R, S, T, V, W, Y')
  }
};

export default {
  validateMutations,
  validateSequence,
  validateAvoidMotifs
}
