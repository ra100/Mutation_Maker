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

export const validateMutations = (mutations: string, sequence: string): string | true => {
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
        return `Mutations ${wrongMutations.join(', ')} not found in sequence`
      }

      return true
      }
  catch (err) {
      console.log(err)
      return true
    }
};

export const validateSequence = (sequence: any, isSequenceTypeDNA: boolean): string | true => {
  if (sequence && sequence.length > 0) {
    if (isSequenceTypeDNA) {
      if (!(sequence || '').match(/^[ACGTacgt]+$/)) {
        return 'Only A, C, G and T are allowed'
      }
    }
    else {
      if (!(sequence || '').match(
        /^[FLIMVSGTAYHQNKDECWRPflimvsgtayhqnkdecwrp]+$/)) {
        return 'Only the following values are allowed: '
          + 'F, L, I, M, V, S, G, T, A, Y, H, Q, N, K, D, E, C, W, R, P'
      }
    }
  }
  return true
};

export const validateAvoidMotifs = (values: any): string | true => {
  if (!values) {
    return true
  }

  const customMotifsRegex = /^[ABCDGHKMNRSTVWYabcdghkmnrstvwy]+$/;
  const motifsJSON = require('../../motifs.json');
  const customInputs = values.filter((value: any) => !motifsJSON.includes(value));
  const invalidInputs = customInputs.filter((value: any) => !value.match(customMotifsRegex));
  if (invalidInputs.length === 0) {
    return true
  } else {
    return 'Only the following values are allowed: ' +
      'A, B, C, D, G, H, K, M, N, R, S, T, V, W, Y'
  }
};

export default {
  validateMutations,
  validateSequence,
  validateAvoidMotifs
}
