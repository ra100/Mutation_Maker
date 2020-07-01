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

Feature: Degenerate codon
  #TODO write documentation
  
  Scenario Outline: Get degeneracy code for amino
   Given i have amino <amino>
    When i want to create degeneracy code
    Then i get <result> code
   Examples: 
   |  amino  | result | 
   | A       | GCN    |
   | R       | MGN    |
   | N       | AAY    |
   | D       | GAY    |
   | C       | TGY    |
   | E       | GAR    |
   | Q       | CAR    |
   | G       | GGN    |
   | H       | CAY    |
   | I       | ATH    |
   | L       | YTN    |
   | K       | AAR    |
   | M       | ATG    |
   | F       | TTY    |
   | P       | CCN    |
   | S       | WSN    |
   | T       | ACN    |
   | W       | TGG    |
   | Y       | TAY    |
   | V       | GTN    |

  Scenario Outline: Get minimal triplets
   Given i have triplets <triplets>
    When i want to create minimal triplets
    Then i get <minimal> triplets
   Examples:
   | triplets            | minimal     |
   | TTT,TTA,ATT         | TTW,ATT     |
   | ATG,TAC,TTC         | ATG,TWC     |  
   | GAA,GCA,TGG,TTG,TTT | GMA,TKG,TTT |
   | CTC,GTC,TTC         | BTC         |
   | CTC,GTC,TTC,AGC,GGC | BTC,RGC     |
   