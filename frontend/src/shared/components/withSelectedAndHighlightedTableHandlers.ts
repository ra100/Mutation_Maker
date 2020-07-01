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

import * as R from 'ramda'
import * as React from 'react'
import { withHandlers } from 'recompose'

import { notUndefined } from 'shared/helpers'
import { Omit } from 'shared/lib/Omit'

import { WithSelectedAndHighlighted } from './withSelectedAndHighlighted'

export type WithSelectedAndHighlightedTableHandlers<T> = {
  onRow(record: T): any
  rowClassName(record: T): string
}

const withSelectedAndHighlightedTableHandlers = <T>(
  setIdentifiers: (record: T) => string[],
  getIdentifiers: (record: T) => string[],
  isNotFound: (record: T) => boolean,
) => <P extends Omit<WithSelectedAndHighlighted, 'setSelected' | 'setHighlighted'>>(
  component: React.ComponentType<P & WithSelectedAndHighlightedTableHandlers<T>>,
) =>
  withHandlers<P, WithSelectedAndHighlightedTableHandlers<T>>({
    onRow: ({ onClick, onMouseEnter, onMouseLeave }) => (record: T) => {
      const identifiers = setIdentifiers(record)

      return {
        onClick: () => onClick(identifiers),
        onMouseEnter: () => onMouseEnter(identifiers),
        onMouseLeave: () => onMouseLeave(identifiers),
      }
    },
    rowClassName: ({ highlighted, selected }) => (record: T): string => {
      const identifiers = getIdentifiers(record)

      const highlightedClassName =
        !R.isEmpty(R.intersection(identifiers, highlighted)) && 'highlighted'
      const selectedClassName = !R.isEmpty(R.intersection(identifiers, selected)) && 'selected'
      const resultNotFoundClassName = isNotFound(record) && 'resultNotFound'

      return [highlightedClassName, selectedClassName, resultNotFoundClassName]
        .filter(notUndefined)
        .join(' ')
    },
  })(component)

export default withSelectedAndHighlightedTableHandlers
