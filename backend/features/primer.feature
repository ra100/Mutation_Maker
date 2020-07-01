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

Feature: Primer class
  Primer class is encapsulating primers.

  Scenario Outline: Create valid primer
    Given parent sequence is specified as <parent sequence>
      And direction is <direction>
      And start of the primer is <primer start>
      And length of the primer is <primer length>
    When i want to create the primer
    Then primer is created successfully

    Examples: Valid example sequences
      | direction | primer start | primer length | parent sequence |
      | forward   | 0            | 1             | ACGT            |
      | forward   | 0            | 4             | ACGT            |
      | forward   | 1            | 2             | ACGT            |
      | reverse   | 3            | 1             | ACGT            |
      | reverse   | 3            | 4             | ACGT            |
      | reverse   | 2            | 2             | ACGT            |

  Scenario: Create primer without parent sequence
    Given parent sequence is not specified    
    When i want to create the primer
    Then parent sequence missing error is raised

  Scenario: Create primer with invalid direction
    Given parent sequence is specified as ACGT
      But direction is invalid
    When i want to create the primer
    Then invalid direction error is raised

  Scenario: Create primer without direction
    Given parent sequence is specified as ACGT
      But direction is not specified
    When i want to create the primer
    Then direction missing error is raised

  Scenario Outline: Create primer without start
    Given parent sequence is specified as ACGT
      And direction is <primer direction>
      But start is not specified
    When i want to create the primer
    Then start missing error is raised
    
    Examples: All directions
      | primer direction |
      | forward          |
      | reverse          |

  Scenario Outline: Create primer before the sequence
    Given parent sequence is specified as ACGT
      And direction is <primer direction>
      And start of the primer is -1
    When i want to create the primer
    Then invalid start position error is raised
    
    Examples: All directions
      | primer direction |
      | forward          |
      | reverse          |
    
  Scenario Outline: Create primer without length
    Given parent sequence is specified as ACGT
      And direction is <primer direction>
      And start of the primer is 2
      But length of the primer is not specified
    When i want to create the primer
    Then start missing length is raised
    
    Examples: All directions
      | primer direction |
      | forward          |
      | reverse          |
  
  Scenario Outline: Create primer after the sequence
    Given parent sequence is specified as ACGT
      And direction is <primer direction>
      And start of the primer is 4
    When i want to create the primer
    Then invalid start position error is raised

    Examples: All directions
      | primer direction |
      | forward          |
      | reverse          |

  Scenario Outline: Create reverse primer partly before the sequence
    Given parent sequence is specified as ACGT
      And direction is reverse
      And start of the primer is <primer start>
      And length of the primer is <primer length>
    When i want to create the primer
    Then invalid end position error is raised

    Examples: Invalid example lengths
      | primer start | primer length |
      | 0            | 2             |
      | 0            | 3             |
      | 1            | 3             |
      | 1            | 4             |
      | 1            | 5             |
      | 2            | 10            |

  Scenario Outline: Create forward primer partly after the sequence
    Given parent sequence is specified as ACGT
      And direction is forward
      And start of the primer is <primer start>
      And length of the primer is <primer length>
    When i want to create the primer
    Then invalid end position error is raised

    Examples: Invalid example lengths
      | primer start | primer length |
      | 3            | 2             |
      | 3            | 3             |
      | 2            | 3             |
      | 2            | 4             |
      | 2            | 5             |
      | 0            | 10            |

  Scenario Outline: Create primer with zero length
    Given parent sequence is specified as ACGT
      And direction is <primer direction>
      And start of the primer is 2
      But length of the primer is 0
    When i want to create the primer
    Then primer length error is raised

    Examples: All directions
      | primer direction |
      | forward          |
      | reverse          |

  Scenario Outline: Calculate primer start in normal order
    Given parent sequence is specified as <parent sequence>
      And direction is <direction>
      And start of the primer is <primer start>
      And length of the primer is <primer length>
      And i create primer with these settings
    When i want to calculate primer start in normal order 
    Then start of the primer in normal order is <normal_order_start>

    Examples: valid examples
      | direction | primer start | primer length | parent sequence | normal_order_start |
      | forward   | 0            | 1             | ACGT            | 0                  |
      | forward   | 0            | 4             | ACGT            | 0                  |
      | forward   | 1            | 2             | ACGT            | 1                  |
      | reverse   | 3            | 1             | ACGT            | 3                  |
      | reverse   | 3            | 4             | ACGT            | 0                  |
      | reverse   | 2            | 2             | ACGT            | 1                  |

  Scenario Outline: Calculate primer end in normal order
    Given parent sequence is specified as <parent sequence>
      And direction is <direction>
      And start of the primer is <primer start>
      And length of the primer is <primer length>
      And i create primer with these settings
    When i want to calculate primer end in normal order 
    Then end of the primer in normal order is <normal_order_end>

    Examples: valid examples
      | direction | primer start | primer length | parent sequence | normal_order_end |
      | forward   | 0            | 1             | ACGT            | 1                |
      | forward   | 0            | 4             | ACGT            | 4                |
      | forward   | 1            | 2             | ACGT            | 3                |
      | reverse   | 3            | 1             | ACGT            | 4                |
      | reverse   | 3            | 4             | ACGT            | 4                |
      | reverse   | 2            | 2             | ACGT            | 3                |

  Scenario Outline: Calculate three end size from mutation
    Given parent sequence is specified as <parent sequence>
      And start of the primer is <primer start>
      And length of the primer is <primer length>
      And direction is <direction>
      And i create primer with these settings
    When i want to calculate three end size from codon mutation starting at <mutation start>
    Then i get following three end size <size>

    Examples: valid examples
      | direction | primer start | primer length | parent sequence | mutation start | size |
      | forward   | 0            | 5             | ACGTACGTA       | 1              | 1    |
      | forward   | 0            | 6             | ACGTACGTA       | 1              | 2    |
      | forward   | 1            | 6             | ACGTACGTA       | 2              | 2    |
      | reverse   | 7            | 5             | ACGTACGTA       | 4              | 1    |
      | reverse   | 7            | 6             | ACGTACGTA       | 4              | 2    |
      | reverse   | 6            | 6             | ACGTACGTA       | 3              | 2    |
      | reverse   | 8            | 9             | AAAAAAAAA       | 4              | 4    |

  Scenario Outline: Calculate five end size from mutation
    Given parent sequence is specified as <parent sequence>
      And start of the primer is <primer start>
      And length of the primer is <primer length>
      And direction is <direction>
      And i create primer with these settings
    When i want to calculate five end size from codon mutation starting at <mutation start>
    Then i get following five end size <size>

    Examples: valid examples
      | direction | primer start | primer length | parent sequence | mutation start | size |
      | forward   | 0            | 5             | ACGTACGTA       | 1              | 1    |
      | forward   | 0            | 6             | ACGTACGTA       | 1              | 1    |
      | forward   | 1            | 6             | ACGTACGTA       | 2              | 1    |
      | forward   | 1            | 7             | ACGTACGTA       | 3              | 2    |
      | reverse   | 7            | 5             | ACGTACGTA       | 4              | 1    |
      | reverse   | 7            | 6             | ACGTACGTA       | 4              | 1    |
      | reverse   | 6            | 6             | ACGTACGTA       | 3              | 1    |
      | reverse   | 7            | 6             | ACGTACGTA       | 3              | 2    |

  Scenario Outline: Calculate GC content
    Given primer sequence is <primer sequence>
      And direction is <direction>
    When i want to calculate gc content
    Then i get following gc content <gc content>

    Examples: valid examples
      | direction | primer sequence | gc content |
      | forward   | GCGCGCGCG       | 100        |
      | reverse   | ATATATATA       | 0          |
      | forward   | CGCGAAAA        | 50         |
      | reverse   | CCCCCCAA        | 75         |


  Scenario Outline: Get 3' end sequence
    Given primer sequence is <primer sequence>
      And direction is <direction>
      And codon mutation starts at base <mutation start>
    When i want to get three end sequence
    Then i get following sequence <three end sequence>

    Examples: valid examples
      | direction | primer sequence | mutation start | three end sequence |
      | forward   | GCGCGCGCG       | 0              | CGCGCG             |
      | reverse   | ATATATATA       | 4              | ATAT               |
      | forward   | CGCGAAAA        | 2              | AAA                |
      | reverse   | CCCCCCAA        | 7              | CCCCCCA            |
    
  Scenario Outline: Get gc clamp
    Given primer sequence is <primer sequence>
      And direction is <direction>
    When i want to get gc_clamp
    Then i get following gc_clamp <gc_clamp>

    Examples: valid examples
      | direction | primer sequence | gc_clamp |
      | forward   | GCGCGCGCG       | 9        |
      | reverse   | GCGCGCGCG       | 9        |
      | forward   | ATATATATA       | 0        |
      | reverse   | ATATATATA       | 0        |
      | forward   | ATAC            | 1        |
      | forward   | GTAC            | 1        |
      | reverse   | CTAA            | 1        |
      | reverse   | GTAC            | 1        |
      | reverse   | CCACCCAA        | 2        |
      | forward   | CGCGAACC        | 2        |

  Scenario Outline: Get mutated sequence
    Given primer sequence is <primer sequence>
      And direction is <direction>
      And codon mutation starts at base <mutation start>
    When i want to get mutated sequence with mutation triplet <triplet>
    Then i get following sequence <mutated sequence>

    Examples: valid examples
      | direction | primer sequence | mutation start | triplet | mutated sequence |
      | forward   | AAAAAAAAA       | 0              | GGT     | GGTAAAAAA        |
      | reverse   | AAAAAAAAA       | 4              | GTT     | AAAAGTTAA        |
      | forward   | AAAAAAAA        | 2              | GGT     | AAGGTAAA         |
      | reverse   | AAAAAAAA        | 5              | GTT     | AAAAAGTT         |

    #TODO get overlap test
