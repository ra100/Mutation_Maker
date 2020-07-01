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

from typing import List
import re

class Motifs(object):

    def degenerate_rules(self, motif: str) -> re.compile:
        motif = motif.replace('R', '[G,A]')
        motif = motif.replace('Y', '[T,C]')
        motif = motif.replace('M', '[A,C]')
        motif = motif.replace('K', '[G,T]')
        motif = motif.replace('S', '[G,C]')
        motif = motif.replace('W', '[A,T]')
        motif = motif.replace('H', '[A,C,T]')
        motif = motif.replace('B', '[G,T,C]')
        motif = motif.replace('V', '[G,C,A]')
        motif = motif.replace('D', '[G,A,T]')
        motif = motif.replace('N', '[G,A,T,C]')
        return re.compile(motif)

    def __init__(self):
        self.motifs = {'AarI': 'CACCTGC', 'AatII': 'GACGTC', 'Acc65I': 'GGTACC', 'AccI': 'GT[A,C][G,T]AC', 'AclI': 'AACGTT', 'AcuI': 'CTGAAG', 'AfeI': 'AGCGCT', 'AflII': 'CTTAAG', 'AflIII': 'AC[G,A][T,C]GT', 'AgeI': 'ACCGGT', 'AhdI': 'GAC[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]GTC', 'AleI': 'CAC[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]GTG', 'AloI': 'GAAC[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]TCC', 'AlwNI': 'CAG[G,A,T,C][G,A,T,C][G,A,T,C]CTG', 'ApaI': 'GGGCCC', 'ApaLI': 'GTGCAC', 'ApoI': '[G,A]AATT[T,C]', 'AscI': 'GGCGCGCC', 'AseI': 'ATTAAT', 'AsiSI': 'GCGATCGC', 'AvrII': 'CCTAGG', 'BaeI': 'AC[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]GTA[T,C]C', 'BamHI': 'GGATCC', 'BanI': 'GG[T,C][G,A]CC', 'BanII': 'G[G,A]GC[T,C]C', 'BbeI': 'GGCGCC', 'BbsI': 'GAAGAC', 'BbvCI': 'CCTCAGC', 'BcgI': 'CGA[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]TGC', 'BciVI': 'GTATCC', 'BclI': 'TGATCA', 'BfrBI': 'ATGCAT', 'BglI': 'GCC[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]GGC', 'BglII': 'AGATCT', 'BlpI': 'GCT[G,A,T,C]AGC', 'Bme1580I': 'G[G,T]GC[A,C]C', 'BmgBI': 'CACGTC', 'BmrI': 'ACTGGG', 'BmtI': 'GCTAGC', 'BplI': 'GAG[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]CTC', 'BpmI': 'CTGGAG', 'Bpu10I': 'CCT[G,A,T,C]AGC', 'BpuEI': 'CTTGAG', 'BsaAI': '[T,C]ACGT[G,A]', 'BsaBI': 'GAT[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]ATC', 'BsaHI': 'G[G,A]CG[T,C]C', 'BsaI': 'GGTCTC', 'BsaWI': '[A,T]CCGG[A,T]', 'BsaXI': 'AC[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]CTCC', 'BseRI': 'GAGGAG', 'BseYI': 'CCCAGC', 'BsgI': 'GTGCAG', 'BsiEI': 'CG[G,A][T,C]CG', 'BsiHKAI': 'G[A,T]GC[A,T]C', 'BsiWI': 'CGTACG', 'BsmBI': 'CGTCTC', 'BsmI': 'GAATGC', 'Bsp1286I': 'G[G,A,T]GC[A,C,T]C', 'BspEI': 'TCCGGA', 'BspHI': 'TCATGA', 'BspMI': 'ACCTGC', 'BsrBI': 'CCGCTC', 'BsrDI': 'GCAATG', 'BsrFI': '[G,A]CCGG[T,C]', 'BsrGI': 'TGTACA', 'BssHII': 'GCGCGC', 'BssSI': 'CACGAG', 'BstAPI': 'GCA[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]TGC', 'BstBI': 'TTCGAA', 'BstEII': 'GGT[G,A,T,C]ACC', 'BstXI': 'CCA[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]TGG', 'BstYI': '[G,A]GATC[T,C]', 'BstZ17I': 'GTATAC', 'Bsu36I': 'CCT[G,A,T,C]AGG', 'BtgI': 'CC[G,A][T,C]GG', 'BtsI': 'GCAGTG', 'ClaI': 'ATCGAT', 'DraI': 'TTTAAA', 'DraIII': 'CAC[G,A,T,C][G,A,T,C][G,A,T,C]GTG', 'DrdI': 'GAC[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]GTC', 'EaeI': '[T,C]GGCC[G,A]', 'EagI': 'CGGCCG', 'EarI': 'CTCTTC', 'EciI': 'GGCGGA', 'Eco57MI': 'CTG[G,A]AG', 'EcoICRI': 'GAGCTC', 'EcoNI': 'CCT[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]AGG', 'EcoO109I': '[G,A]GG[G,A,T,C]CC[T,C]', 'EcoRI': 'GAATTC', 'EcoRV': 'GATATC', 'FalI': 'AAG[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]CTT', 'FseI': 'GGCCGGCC', 'FspAI': '[G,A]TGCGCA[T,C]', 'FspI': 'TGCGCA', 'HaeII': '[G,A]GCGC[T,C]', 'Hin4I': 'GA[T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,C,A]TC', 'HincII': 'GT[T,C][G,A]AC', 'HindIII': 'AAGCTT', 'HpaI': 'GTTAAC', 'KasI': 'GGCGCC', 'KpnI': 'GGTACC', 'MfeI': 'CAATTG', 'MluI': 'ACGCGT', 'MmeI': 'TCC[G,A]AC', 'MscI': 'TGGCCA', 'MslI': 'CA[T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A]TG', 'NaeI': 'GCCGGC', 'NarI': 'GGCGCC', 'NcoI': 'CCATGG', 'NdeI': 'CATATG', 'NgoMIV': 'GCCGGC', 'NheI': 'GCTAGC', 'NotI': 'GCGGCCGC', 'NruI': 'TCGCGA', 'NsiI': 'ATGCAT', 'NspI': '[G,A]CATG[T,C]', 'PacI': 'TTAATTAA', 'PciI': 'ACATGT', 'PflMI': 'CCA[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]TGG', 'PfoI': 'TCC[G,A,T,C]GGA', 'PmeI': 'GTTTAAAC', 'PmlI': 'CACGTG', 'PpiI': 'GAAC[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]CTC', 'PpuMI': '[G,A]GG[A,T]CC[T,C]', 'PshAI': 'GAC[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]GTC', 'PsiI': 'TTATAA', 'PspOMI': 'GGGCCC', 'PsrI': 'GAAC[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]TAC', 'PstI': 'CTGCAG', 'PvuI': 'CGATCG', 'PvuII': 'CAGCTG', 'RsrII': 'CGG[A,T]CCG', 'SacI': 'GAGCTC', 'SacII': 'CCGCGG', 'SalI': 'GTCGAC', 'SanDI': 'GGG[A,T]CCC', 'SapI': 'GCTCTTC', 'SbfI': 'CCTGCAGG', 'ScaI': 'AGTACT', 'SexAI': 'ACC[A,T]GGT', 'SfcI': 'CT[G,A][T,C]AG', 'SfiI': 'GGCC[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]GGCC', 'SfoI': 'GGCGCC', 'SgrAI': 'C[G,A]CCGG[T,C]G', 'SmaI': 'CCCGGG', 'SmlI': 'CT[T,C][G,A]AG', 'SnaBI': 'TACGTA', 'SpeI': 'ACTAGT', 'SphI': 'GCATGC', 'SrfI': 'GCCCGGGC', 'SspI': 'AATATT', 'StuI': 'AGGCCT', 'StyI': 'CC[A,T][A,T]GG', 'SwaI': 'ATTTAAAT', 'TaqII': 'GACCGA', 'Tth111I': 'GAC[G,A,T,C][G,A,T,C][G,A,T,C]GTC', 'XbaI': 'TCTAGA', 'XcmI': 'CCA[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]TGG', 'XhoI': 'CTCGAG', 'XmaI': 'CCCGGG', 'XmnI': 'GAA[G,A,T,C][G,A,T,C][G,A,T,C][G,A,T,C]TTC', 'ZraI': 'GACGTC'}

        self.motif_names = list(self.motifs.keys())



    def __call__(self, list_of_motifs:List) -> List:
        """ Instance of Motifs class takes the input list of motifs and transforms them to list of codons as compiled regular expression objects. """

        output_list = []
        for motif in list_of_motifs:
            if motif in self.motif_names:
                output_list.append(re.compile(self.motifs[motif]))
            else:
                output_list.append(self.degenerate_rules(motif))
        return output_list
