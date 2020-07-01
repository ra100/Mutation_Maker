#    Copyright (c) 2020 Merck Sharp & Dohme Corp. a subsidiary of Merck & Co., Inc., Kenilworth, NJ, USA.
#
#    This file is part of the Mutation Maker, An Open Source Oligo Design Software For Mutagenesis and De Novo Gene Synthesis Experiments.
#
#    Mutation Maker is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Feature: Calculate possible positions of mutagenic primer in gene of interest
  For every mutation we need to calculate possible positions of mutagenic primers.
  
  This position is used as an input for primer3
  
  We count with an option that gene sequence is inside a plasmid therefore we can return 
  negative positions for area start and positions outsize gene for area end

  Mutation have to be in gene sequence 

  Scenario Outline: Calculate search area
    Given gene sequence is <sequence>
      And mutation starts at <mutation start> base
      And max primer size is <max primer size>
      And length of three end needs to be between <min three end size> and <max three end size>
      And primer direction is <primer direction>
    When i calculate mutagenic primer search area
    Then i get area from <area from> to <area to>

  Examples: Valid examples
    | sequence                        | mutation start | max primer size | min three end size | max three end size | primer direction | area from | area to |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 0              | 15              | 3                  | 6                  | forward          | -9        | 9       |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 21             | 15              | 3                  | 6                  | forward          | 12        | 30      |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 3              | 15              | 3                  | 6                  | forward          | -6        | 12      |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 9              | 15              | 3                  | 6                  | forward          | 0         | 18      |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 9              | 18              | 3                  | 6                  | forward          | -3        | 18      |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 9              | 12              | 3                  | 6                  | forward          | 3         | 18      |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 9              | 15              | 3                  | 3                  | forward          | 0         | 15      |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 9              | 15              | 3                  | 9                  | forward          | 0         | 21      |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 9              | 15              | 2                  | 6                  | forward          | -1        | 18      |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 9              | 15              | 4                  | 6                  | forward          | 1         | 18      |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 0              | 15              | 3                  | 6                  | reverse          | -6        | 12      |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 21             | 15              | 3                  | 6                  | reverse          | 15        | 33      |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 3              | 15              | 3                  | 6                  | reverse          | -3        | 15      |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 9              | 15              | 3                  | 6                  | reverse          | 3         | 21      |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 9              | 18              | 3                  | 6                  | reverse          | 3         | 24      |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 9              | 12              | 3                  | 6                  | reverse          | 3         | 18      |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 9              | 15              | 3                  | 3                  | reverse          | 6         | 21      |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 9              | 15              | 3                  | 9                  | reverse          | 0         | 21      |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 9              | 15              | 2                  | 6                  | reverse          | 3         | 22      |
    | AAT GTC AAA CCC TTT GCC ACT AGG | 9              | 15              | 4                  | 6                  | reverse          | 3         | 20      |
