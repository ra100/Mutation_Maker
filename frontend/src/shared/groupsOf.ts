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

export const addToLast = <T>(element: T, array: T[][]) =>
  R.over(R.lensIndex(array.length - 1), arraySegment => [...arraySegment, element], array)

export const groupsOf = <T>(count: number, array: T[]): T[][] => {
  const { groups, current } = array.reduce<{ groups: T[][]; current: T[] }>(
    (acc, element) =>
      acc.current.length === count
        ? {
            groups: [...acc.groups, acc.current],
            current: [element],
          }
        : {
            groups: acc.groups,
            current: [...acc.current, element],
          },
    {
      groups: [],
      current: [],
    },
  )

  return [...groups, current]
}
