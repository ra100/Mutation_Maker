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

from typing import Tuple

from Bio.Seq import reverse_complement
from jsonobject import JsonObject, IntegerProperty, FloatProperty, \
    BooleanProperty, StringProperty, ObjectProperty, ListProperty

from mutation_maker.reverse_translation import Translator
from mutation_maker.temperature_calculator import (
    TemperatureConfig, create_default_pas_temperature_config)


class PASConfig(JsonObject):

    min_oligo_size = IntegerProperty(default=40)
    max_oligo_size = IntegerProperty(default=90)
    opt_oligo_size = IntegerProperty(default=56)

    min_overlap_tm = FloatProperty(default=50)
    max_overlap_tm = FloatProperty(default=65)
    opt_overlap_tm = IntegerProperty(default=56)  # this optimal temperature is for NEB like temperature calculator

    min_overlap_length = IntegerProperty(default=15)
    max_overlap_length = IntegerProperty(default=25)
    opt_overlap_length = IntegerProperty(default=21)

    min_gc_content = FloatProperty(default=40)
    max_gc_content = FloatProperty(default=60)

    use_degeneracy_codon = BooleanProperty(default=False)

    organism = StringProperty(default="e-coli")
    avoided_motifs = ListProperty(str)
    codon_usage_frequency_threshold = FloatProperty(default=0.1)

    # The allowed range for melting temperatures of fragment overlaps, in deg C
    temp_range_size = FloatProperty(default=5)

    # Temperature calculator configuration
    temperature_config = ObjectProperty(TemperatureConfig,
                                        default=create_default_pas_temperature_config())

    # Weights used for non_optimality calculation.
    temp_weight = FloatProperty(default=1)
    gc_content_weight = FloatProperty(default=1)
    length_weight = FloatProperty(default=1)
    hairpin_homodimer_weight = FloatProperty(default=2)

    # "Safe" temperature difference between a hairpin or homodimer formation and the reaction temperature
    safe_temp_difference = FloatProperty(default=10)

    # Step for iteration over possible melting temperature thresholds, in deg C
    temp_threshold_step = FloatProperty(default=1)


class PASSequences(JsonObject):
    gene_of_interest = StringProperty(required=True)
    five_end_flanking_sequence = StringProperty(default="")
    three_end_flanking_sequence = StringProperty(default="")

    def get_full_sequence_with_offset(self) -> Tuple[str, int]:
        return self.get_full_sequence(), self.get_goi_offset()

    def translate_goi_sequences(self, translator: Translator):
        if self.five_end_flanking_sequence is None:
            self.five_end_flanking_sequence = ""
        if self.three_end_flanking_sequence is None:
            self.three_end_flanking_sequence = ""

        self.gene_of_interest = translator(self.gene_of_interest)

    def get_goi_offset(self):
        if self.five_end_flanking_sequence is None:
            self.five_end_flanking_sequence = ""
        return len(self.five_end_flanking_sequence)

    def get_full_sequence(self):
        if self.five_end_flanking_sequence is None:
            self.five_end_flanking_sequence = ""
        if self.three_end_flanking_sequence is None:
            self.three_end_flanking_sequence = ""
        full_sequence = \
            self.five_end_flanking_sequence + \
            self.gene_of_interest + \
            self.three_end_flanking_sequence
        return full_sequence


class PASMutation(JsonObject):
    mutation = StringProperty(required=True)
    frequency = FloatProperty(required=True)

    def __repr__(self):
        return self.mutation+str(self.frequency)

    def __str__(self):
        return self.mutation + str(self.frequency)


class PASMutationSite(JsonObject):
    """ List of mutations at a given amino acid position """
    position = IntegerProperty(required=True)
    # List of mutation. Each mutation is a amino acid IUPAC code, or a DNA codon.
    mutations = ListProperty(PASMutation, required=True)
    # frequency = FloatProperty(required=True)

    def __gt__(self, other):
        if type(other) == int:
            return self.position > other
        return self.position > other.position

    def __lt__(self, other):
        if type(other) == int:
            return self.position < other
        return self.position < other.position

    def __eq__(self, other):
        if type(other) == int:
            return self.position == other
        return self.position == other.position

    # def __hash__(self):
    #     return hash(str(self.position))

    def get_mutations_str_list(self):
        return [mut.mutation for mut in self.mutations]


class PASOligo(JsonObject):
    sequence = StringProperty(required=True)
    # Mixing ratio for the oligo. A missing value means N/A.
    ratio = FloatProperty(required=False)


class PASMutationFormattedInput(JsonObject):
    mutants = ListProperty(required=True)
    position = IntegerProperty(required=True)
    # TODO this should be also list if we have list of mutants
    frequency = FloatProperty(required=True)


class PASMutationFormatted(JsonObject):
    position = IntegerProperty(required=True)
    mutated_amino = StringProperty(required=True)
    wild_type_amino = StringProperty(required=False)
    wild_type_codon = StringProperty(required=False)
    mutated_codon = StringProperty(required=True)
    frequency = FloatProperty(required=True)
    wild_type = BooleanProperty(required=True)


class PASOligoOutput(JsonObject):
    sequence = StringProperty(required=True)
    mix_ratio = FloatProperty(required=True)
    mutations = ListProperty(required=False)
    reds = ListProperty(required=False)
    blues = ListProperty(required=False)

    def make_reverse_complement(self):
        # TODO test this
        self.sequence = reverse_complement(self.sequence)
        # -3 because when we do reverse complement we reverse the order of indexes
        #    -> what was start of codon will be end of codon in the reverse complement
        # thus we are moving from the end to start of codon in reversed sequence by subtracting 3
        def reindexer(ind): return abs(len(self.sequence) - ind - 3)
        self.reds = sorted(list(map(reindexer, self.reds)))
        self.blues = sorted(list(map(reindexer, self.blues)))


class PASResult(JsonObject):
    fragment = StringProperty(required=True)
    start = IntegerProperty(required=True)
    end = IntegerProperty(required=True)
    length = IntegerProperty(required=True)
    overlap = StringProperty(required=False)
    overlap_Tm = FloatProperty(required=False)
    overlap_GC = FloatProperty(required=False)
    overlap_length = IntegerProperty(required=False)
    mutations = ListProperty(PASMutationFormatted, required=False)
    oligos = ListProperty(PASOligoOutput, required=True)


class PASInput(JsonObject):
    # Sequences for the synthesized gene.
    # Expressed as ATGC or amino acid sequence.
    sequences = ObjectProperty(PASSequences, required=True)
    # Is the gene sequence a DNA (ATGC) sequence?
    is_dna_sequence = BooleanProperty(required=True)
    # Input parameters
    config = ObjectProperty(PASConfig, required=True)
    # List of mutations by position in the gene
    mutations = ListProperty(PASMutationFormattedInput, required=False)
    # Are mutations given as codons?
    is_mutations_as_codons = BooleanProperty(required=True)


class PASOutput(JsonObject):
    input_data = ObjectProperty(PASInput, required=True)
    results = ListProperty(PASResult, required=False)
    message = StringProperty()
