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

from mutation_maker.degenerate_codon import CodonUsage
from mutation_maker.usage_table import UsageTable
from mutation_maker.translation_scoring import TranslationScoring
from mutation_maker.motifs import Motifs
from mutation_maker.pas_exceptions import PASNoSolutionException
from Bio.Data import CodonTable
from typing import List
import numpy as np
import operator
import time

class Translator(object):
    """ Function object for reverse translation of Amino Acid sequence to DNA sequence"""
    threshold_usage: float  # threshold for the codon frequency
    gc_range: List[int]  # desired GC content rage
    epsilon: float  # value of solution imrovment value until "giving up"
    N: int  # value of generated solutions until "giving up" to get solution improvment by epsilon value
    organismus: str # organismus chosen to use as codon frequency reference

    def __init__(self, threshold_usage: float, gc_range: List[int], avoided_motifs, epsilon=0.05, N=600, organism_name='e-coli'):
        self.dna_by_name = CodonTable.unambiguous_dna_by_name["Standard"] #codon usage table initialized
        self.threshold_usage = threshold_usage
        self.gc_range = gc_range
        self.codonUsage = CodonUsage(organism_name)  # codon usage table for e-coli is initialized
        self.usage_table = self.codonUsage.usages  # e-coli organism is chosen
        self.dna_by_name = self.codonUsage.table

        self.scoring = TranslationScoring(self.threshold_usage, self.gc_range, self.codonUsage,
                                          self.usage_table)  # initializing scoring instance

        self.epsilon = epsilon
        self.N = N
        self.get_motifs = Motifs()
        self.avoided_motifs = self.get_motifs(avoided_motifs) #getting list of avoided motifs

    def generate_dna(self, AA: str) -> str:
        """ Function which randomly generates DNA from protein sequence based on codon usage frequency"""
        dna_a = []
        for aa in AA:
            codons = self.codonUsage.get_all_possible_triplets_for_amino(aa, self.threshold_usage) # all possible codons for a given amino acid
            codons_with_frequency = {str(d) : self.usage_table[str(d)] for d in codons} # all possible codons with their usage values
            non_normalized_probabilities = list(codons_with_frequency.values())
            renormalized_probabilities = [freq / sum(non_normalized_probabilities) for freq in
                                          non_normalized_probabilities]
            random_codon =  np.random.choice(list(codons_with_frequency.keys()), 1, replace=True, p=renormalized_probabilities)[0]
            dna_a.append(random_codon)
        dna = ''.join(dna_a)
        return dna

    def perform_calculation(self, AA: str) -> tuple:
        """ Function which implements the main algorithm of generating the solutions and checking their quality"""
        generated_dnas = []
        best_solution_index = 0
        timeout = time.time() + 60*10 # setting up 10 mins timer. After 10 mins it will abort the computation
        while True:
            if time.time() > timeout:
                raise PASNoSolutionException("Impossible to find reverse translation with specified configuration of parameters in a reasonable amount of time. Please try other values.")
            dna = self.generate_dna(AA) #generate the dna from protein
            cai_score, gc_score = self.scoring(dna) # score the solution
            motifs_in_dna = [motif for motif in self.avoided_motifs if motif.search(dna)] #list of avoided motifs which is contained in generated dna sequence
            if(gc_score <= 0.1 and len(motifs_in_dna) == 0):
                generated_dnas.append((dna, cai_score)) # filter out solutions in the desired GC content region
            if(len(generated_dnas) == 1 or not generated_dnas):
                continue
            else:
                if(generated_dnas[-1][1] > generated_dnas[best_solution_index][1]):
                    best_solution_index = len(generated_dnas) - 1 # chosing the best solution and storing the index of best solution
                else:
                    pass
            if((cai_score <= (generated_dnas[best_solution_index][1] + self.epsilon)) and ((len(generated_dnas) - 1) - best_solution_index  ) >= self.N): # checking the "giving up" condition
                return generated_dnas[best_solution_index]

    def threshold_value(self, AA: str) -> float:
        """ Function which calulates dynamic threshold for the solution quality based on the length of protein"""
        length = len(AA)
        return 4.077081048783832/length + 0.7464624052808766



    def __call__(self, AA: str) -> str:
        # score = 0
        # score_threshold = self.threshold_value(AA)
        # while(score < score_threshold):
        #     dna = self.perform_calculation(AA)
        #     score = dna[1]
        # return dna
        if AA:
            return self.perform_calculation(AA)[0]
        return AA