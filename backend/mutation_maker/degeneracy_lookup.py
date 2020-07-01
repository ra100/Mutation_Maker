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

class DegenerateCodon:
    def __init__(self, value, bases):
        self.value = value
        self.bases = frozenset(bases)

    def union(self, other):
        return back_lookup["".join(self.bases.union(other.bases))]

    def __key(self):
        return self.bases

    def __eq__(self, y):
        return self.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.__str__()


A = DegenerateCodon("A", {"A"})
C = DegenerateCodon("C", {"C"})
G = DegenerateCodon("G", {"G"})
T = DegenerateCodon("T", {"T"})
R = DegenerateCodon("R", {"A", "G"})
Y = DegenerateCodon("Y", {"C", "T"})
S = DegenerateCodon("S", {"G", "C"})
W = DegenerateCodon("W", {"A", "T"})
K = DegenerateCodon("K", {"G", "T"})
M = DegenerateCodon("M", {"A", "C"})
B = DegenerateCodon("B", {"C", "G", "T"})
D = DegenerateCodon("D", {"A", "G", "T"})
H = DegenerateCodon("H", {"A", "C", "T"})
V = DegenerateCodon("V", {"A", "C", "G"})
N = DegenerateCodon("N", {"A", "C", "G", "T"})
GAP = DegenerateCodon("_", set())

lookup = {
    "A": A,
    "C": C,
    "G": G,
    "T": T,
    "R": R,
    "Y": Y,
    "S": S,
    "W": W,
    "K": K,
    "M": M,
    "B": B,
    "D": D,
    "H": H,
    "V": V,
    "N": N,
    "_": GAP
}

back_lookup = {
    "A": A,
    "C": C,
    "G": G,
    "T": T,
    "AG": R, "GA": R,
    "CT": Y, "TC": Y,
    "CG": S, "GC": S,
    "AT": W, "TA": W,
    "GT": K, "TG": K,
    "AC": M, "CA": M,
    "CGT": B, "CTG": B, "GCT": B, "GTC": B, "TCG": B, "TGC": B,
    "AGT": D, "ATG": D, "GAT": D, "GTA": D, "TAG": D, "TGA": D,
    "ACT": H, "ATC": H, "CAT": H, "CTA": H, "TAC": H, "TCA": H,
    "ACG": V, "AGC": V, "CAG": V, "CGA": V, "GAC": V, "GCA": V,
    "ACGT": N, "ACTG": N, "AGCT": N, "AGTC": N, "ATGC": N, "ATCG": N,
    "TCGA": N, "TCAG": N, "TGCA": N, "TGAC": N, "TAGC": N, "TACG": N,
    "CTGA": N, "CTAG": N, "CGTA": N, "CGAT": N, "CAGT": N, "CATG": N,
    "GTCA": N, "GTAC": N, "GCTA": N, "GCAT": N, "GACT": N, "GATC": N,
    "_": GAP
}
