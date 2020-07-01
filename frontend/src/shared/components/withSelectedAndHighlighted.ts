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
import { compose, withHandlers, withState } from 'recompose'

export type WithSelectedState<T> = {
  selected: T
  setSelected(selected: T): T
}

export const withSelectedState = <T>(initialValue: T) => <P>(
  component: React.ComponentType<P & WithSelectedState<T>>,
) => withState<P, T, 'selected', 'setSelected'>('selected', 'setSelected', initialValue)(component)

export type WithHighlightedState<T> = {
  highlighted: T
  setHighlighted(identifier: T): T
}

export const withHighlightedState = <T>(initialValue: T) => <P>(
  component: React.ComponentType<P & WithHighlightedState<T>>,
) =>
  withState<P, T, 'highlighted', 'setHighlighted'>('highlighted', 'setHighlighted', initialValue)(
    component,
  )

type WithMouseHandlers = {
  onClick(identifiers: string[]): void
  onMouseEnter(identifiers: string[]): void
  onMouseLeave(identifiers: string[]): void
}

export type WithSelectedAndHighlighted = WithHighlightedState<string[]> &
  WithSelectedState<string[]> &
  WithMouseHandlers

const withSelectedAndHighlighted = <P>(
  component: React.ComponentType<P & WithSelectedAndHighlighted>,
) =>
  compose<P & WithSelectedAndHighlighted, P>(
    withSelectedState<string[]>([]),
    withHighlightedState<string[]>([]),
    withHandlers<WithSelectedState<string[]> & WithHighlightedState<string[]>, WithMouseHandlers>({
      onClick: ({ selected, setSelected }) => (identifiers: string[]) => {
        setSelected(
          R.isEmpty(R.intersection(identifiers, selected))
            ? identifiers
            : R.difference(selected, identifiers),
        )
      },
      onMouseEnter: ({ setHighlighted }) => (identifiers: string[]) => {
        setHighlighted(identifiers)
      },
      onMouseLeave: ({ setHighlighted }) => (identifiers: string[]) => {
        setHighlighted([])
      },
    }),
  )(component)

export default withSelectedAndHighlighted
