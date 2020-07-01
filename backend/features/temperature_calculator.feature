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

Feature: Temperature calculator
  #TODO write documentation
  
  Scenario Outline: Create all possible temperature ranges including some temperatures
   Given i have temperature calculator with precision <precision>
    And i work with temperature range of <range> degrees
    When i want to create all possible ranges from <min> to <max>
    Then i get <interval count> intervals
    And first interval is <first interval> 
    And last interval is <last interval>

   Examples: valid examples
   | precision | range | min | max | interval count | first interval | last interval |
   | 0         | 5     | 64  | 72  | 4              | 64-69          | 67-72         |
   | 1         | 5     | 64  | 72  | 31             | 64-69          | 67-72         |
   | 2         | 5     | 64  | 72  | 301            | 64-69          | 67-72         |
   | 0         | 5     | 64  | 71  | 3              | 64-69          | 66-71         |
   | 0         | 5     | 64  | 69  | 1              | 64-69          | 64-69         |
