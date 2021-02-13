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

Feature: Mutation class
  Mutation class is encapsulating mutations

  Mutation classes are parsed from list of mutations in format X000Y where:
    * X is old amino acid on position 000
    * 000 is one-based amino acid position of mutation in parent sequence
    * Y is new target amino acid

  Amino acids are from IUPAC one letter amino acid code
  Valid amino acids therefore are: A C D E F G H I K L M N P Q R S T V W Y

  Position is saved as zero-based position with optional offset
  One-based amino position is converted to zero-based base position as b = (a - 1) * 3
  where a is one-based amino position and b is zero-based base position

  For SSM workflow we are using CodonMutation class. It contains only one target
  amino for one position.

  For MSDM workflow we are using MultiAminoTargetMutation which can have multiple
  target amino acids plus it also contains wildcard amino acid what means that
  old amino acid is part of target amino acids

  #TODO check validity of original amino
  Validity of original amino is not checked for now.

  Scenario: Parse valid mutation
    Given input string is A51F
    When i want to create mutation
    Then mutation is created successfully
      And original amino is A
      And position is 150
      And target amino is F

  Scenario: Parse mutation with invalid original amino
    Given input string is X52A
    When i want to create mutation
    Then invalid original amino error is raised

  Scenario: Parse mutation with invalid target amino
    Given input string is A52Z
    When i want to create mutation
    Then invalid target amino error is raised

  Scenario: Parse mutation with invalid position
    Given input string is AFSA
    When i want to create mutation
    Then invalid position error is raised

  Scenario: Parse mutation with negative position
    Given input string is A-52A
    When i want to create mutation
    Then invalid position error is raised

  Scenario: Create multi amino target mutation
    Given input string is A52F A52M
    When i want to create multi amino target mutation
    Then mutation is created successfully
      And original amino is A
      And position is 153
      And target aminos are A,F,M

  Scenario: Create multi amino target mutation with different positions
    Given input string is A52F A99M
    When i want to create multi amino target mutation
    Then inconsistent positions error is raised

  Scenario: Create multi amino target mutation with different original aminos
    Given input string is F52A A52M
    When i want to create multi amino target mutation
    Then inconsistent original aminos error is raised
