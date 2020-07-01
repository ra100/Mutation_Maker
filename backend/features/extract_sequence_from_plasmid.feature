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

Feature: Extract sequence from plasmid
  We need to get full sequence for primer calculation

  Full sequence is concatenated
    either: 
      * 5` end of plasmid from forward primer to gene start in plasmid
      * gene of interest
      * 3` end of plasmid from gene end in plasmid to reverse primer   
    or:
      * 5` end flanking sequence
      * gene of interest
      * 3` end flanking sequence

  If gene boundaries are not specified we need to find exact match of gene of interest in plasmid and set gene boundaries by that

  Scenario Outline: Create full sequence from plasmid and gene of interest
    Given plasmid is <plasmid sequence>
      And forward primer is <forward primer>
      And reverse primer is <reverse primer>
      And gene of interest is <goi>
    When i want to extract full sequence
    Then i get following sequence <full sequence>
      And gene is offset by <offset> bases
  # TODO: Much more testing is needed regarding invalid cases and when primers are not in the expected order
  # TODO: Currently we do not solve problem when primers are on the edge of plasmid (partly at the end partly at the start)
  Examples: Valid example sequences
    | plasmid sequence                | forward primer | reverse primer | goi | full sequence           | offset |
    | AAT GTC AAA CCC TTT GCC         | AAT            | GGC            | AAA | AAT GTC AAA CCC TTT GCC | 6      |
    | AAA AAT GTC AAA CCC TTT GCC AAA | AAT            | GGC            | CCC | AAT GTC AAA CCC TTT GCC | 9      |

  Scenario: When gene of interest is not found in plasmid we report an error    
    Given plasmid is AAT GTC AAA CCC TTT GCC
      And gene of interest is GGG
      And forward primer is AAT
      And reverse primer is GGC
    When i want to extract full sequence
    Then gene of interest not found error is raised

  Scenario: When forward primer is not found in plasmid we report an error    
    Given plasmid is AAT GTC AAA CCC TTT GCC
      And gene of interest is AAA
      And forward primer is GGG
      And reverse primer is GGC
    When i want to extract full sequence
    Then forward primer not found error is raised

  Scenario: When reverse complement of reverse primer is not found in plasmid we report an error    
    Given plasmid is AAT GTC AAA CCC TTT GCC
      And gene of interest is AAA
      And forward primer is AAT
      And reverse primer is CCC
    When i want to extract full sequence
    Then reverse primer not found error is raised

  Scenario: When gene of interest is not found in plasmid multiple times    
    Given plasmid is AAT GTC AAA AAA CCC TTT GCC
      And gene of interest is AAA
      And forward primer is AAT
      And reverse primer is GGC
    When i want to extract full sequence
    Then gene of interest position ambiguous error is raised

  Scenario Outline: Create full sequence from plasmid gene of interest and gene location in plasmid
    Given plasmid is <plasmid sequence>
      And forward primer is <forward primer>
      And reverse primer is <reverse primer>
      And gene of interest is <goi>
      And gene is located from <gene start> to <gene end>
    When i want to extract full sequence
    Then i get following sequence <full sequence>
      And gene is offset by <offset> bases

  Examples: Valid example sequences
    | plasmid sequence                | forward primer | reverse primer | goi | gene start | gene end | full sequence       | offset |
    | AAT GTC AAA CCC TTT GCC         | AAT            | GGC            | AAT | 6          | 12       | AAT GTC AAT TTT GCC | 6      |
    | AAA AAT GTC AAA CCC TTT GCC AAA | AAT            | GGC            | AAT | 9          | 15       | AAT GTC AAT TTT GCC | 6      |

  # TODO more test cases when flanking sequence are provided and plasmid is not 
