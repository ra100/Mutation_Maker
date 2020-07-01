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

Feature: Primer3 interoperability
  For the SSM workflow we rely on primer3 for generating candidates for mutagenic primers
  therefore we need to support following functionality
  * Create config file for Primer3 from our settings
  * Calling custom binary with Primer3 implementation (custom binary is needed because primer length we want to design)
  * Parsing output from Primer3

  #TODO write tests
  #Scenario: Create config for primer3 to find candidates for pairing

  Scenario: Run one primer3 process at the time
    Given i have some example primer3 config
      And PRIMER3HOME environment variable is set to primer3 path    
    When i run primer3 through primer3 process manager
    Then i get some results
