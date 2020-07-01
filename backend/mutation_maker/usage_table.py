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

class UsageTable:
    def __init__(self):
        self.ecoli_usage = {"TTT": 0.58, "TTC": 0.42, "TTA": 0.14, "TTG": 0.13, "TAT": 0.59,
            "TAC": 0.41, "TAA": 0.61, "TAG": 0.09, "CTT": 0.12, "CTC": 0.10,
            "CTA": 0.04, "CTG": 0.47,"CAT": 0.57,"CAC": 0.43,"CAA": 0.34,
            "ATT": 0.49, "ATC": 0.39, "ATA": 0.11, "ATG": 1.00, "AAT": 0.49,
            "AAC": 0.51, "AAA": 0.74, "AAG": 0.26, "TCT": 0.17, "TCC": 0.15,
            "TCA": 0.14, "TCG": 0.14, "TGT": 0.46, "TGC": 0.54, "TGA": 0.30,
            "TGG": 1.00, "CCT": 0.18, "CCC": 0.13, "CCA": 0.20, "CCG": 0.49,
            "CGT": 0.36, "CGC": 0.36, "CGA": 0.07, "CGG": 0.11, "ACT": 0.19,
            "ACC": 0.40, "ACA": 0.17, "ACG": 0.25, "AGT": 0.16, "AGC": 0.25,
            "AGA": 0.07, "AGG": 0.04, "GTT": 0.28, "GTC": 0.20, "GTA": 0.17,
            "GTG": 0.35, "GAT": 0.63, "GAC": 0.37, "GAA": 0.68, "GAG": 0.32,
            "GCT": 0.18, "GCC": 0.26, "GCA": 0.23, "GCG": 0.33, "GGT": 0.35,
            "GGC": 0.37, "GGA": 0.13, "GGG": 0.15, "CAG": 0.66,
        }

        # S. cerevisiae
        self.yeast_usage = {"TTT": 0.59, "TTC": 0.41, "TTA": 0.28, "TTG": 0.29, "TAT": 0.56,
            "TAC": 0.44, "TAA": 0.47, "TAG": 0.23, "CTT": 0.13, "CTC": 0.06,
            "CTA": 0.14, "CTG": 0.11, "CAT": 0.64, "CAC": 0.36, "CAA": 0.69,
            "ATT": 0.46, "ATC": 0.26, "ATA": 0.27, "ATG": 1.00, "AAT": 0.59,
            "AAC": 0.41, "AAA": 0.58, "AAG": 0.42, "TCT": 0.26, "TCC": 0.16,
            "TCA": 0.21, "TCG": 0.10, "TGT": 0.63, "TGC": 0.37, "TGA": 0.30,
            "TGG": 1.00, "CCT": 0.31, "CCC": 0.15, "CCA": 0.42, "CCG": 0.12,
            "CGT": 0.14, "CGC": 0.06, "CGA": 0.07, "CGG": 0.04, "ACT": 0.35,
            "ACC": 0.22, "ACA": 0.30, "ACG": 0.14, "AGT": 0.16, "AGC": 0.11,
            "AGA": 0.47, "AGG": 0.21, "GTT": 0.39, "GTC": 0.21, "GTA": 0.21,
            "GTG": 0.19, "GAT": 0.65, "GAC": 0.35, "GAA": 0.70, "GAG": 0.30,
            "GCT": 0.38, "GCC": 0.22, "GCA": 0.29, "GCG": 0.11, "GGT": 0.47,
            "GGC": 0.19, "GGA": 0.22, "GGG": 0.12, "CAG": 0.31,
            }
        

