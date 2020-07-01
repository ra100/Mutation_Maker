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

import sys
sys.path.append('../')
from test_support import generate_pas_input


def parse_input(input):
    threshold_usage = input.config.codon_usage_frequency_threshold
    gc_range = [input.config.min_gc_content, input.config.max_gc_content]
    dna = input.sequences.gene_of_interest #should be fragment, not gene of interest!!!
    mutations_input = input.mutations
    mutations = []
    for mutation in mutations_input:
        print(mutation.mutations, mutation.position)
        for mut in mutation.mutations:
            temp = (mutation.position, str(mut)[0], float(str(mut)[1:]))
            mutations.append(temp)
    print(input.config.avoided_motifs)

parse_input(generate_pas_input(1))
