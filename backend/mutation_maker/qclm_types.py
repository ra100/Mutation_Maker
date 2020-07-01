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

from typing import List, Tuple
from jsonobject import JsonObject, IntegerProperty, FloatProperty, \
    BooleanProperty, StringProperty, ObjectProperty, ListProperty

from mutation_maker.mutation import parse_codon_mutation, create_multi_amino_mutations
from mutation_maker.temperature_calculator import (
    TemperatureConfig, create_default_qclm_temperature_config)
from mutation_maker.mutation import MutationSite, QCLMMutationSiteSequence


class QCLMConfig(JsonObject):
    min_primer_size = IntegerProperty(default=23)
    opt_primer_size = IntegerProperty(default=23)
    max_primer_size = IntegerProperty(default=60)

    min_gc_content = FloatProperty(default=40)
    opt_gc_content = FloatProperty(default=50)
    max_gc_content = FloatProperty(default=60)

    min_three_end_size = IntegerProperty(default=10)
    opt_three_end_size = IntegerProperty(default=10)
    max_three_end_size = IntegerProperty(default=40)

    min_five_end_size = IntegerProperty(default=10)
    opt_five_end_size = IntegerProperty(default=10)
    max_five_end_size = IntegerProperty(default=40)

    min_temperature = FloatProperty(default=75)
    max_temperature = FloatProperty(default=90)

    gc_clamp = IntegerProperty(default=1)
    use_degeneracy_codon = BooleanProperty(default=True)
    codon_usage_frequency_threshold = FloatProperty(default=0.1)

    # Search only for solutions with non-overlapping primers?
    non_overlapping_primers = BooleanProperty(default=False)

    # Should we use the primer3 to check generated primers?
    use_primer3 = BooleanProperty(default=True)

    # The allowed range for primer melting temperatures, in deg C
    temp_range_size = FloatProperty(default=5)

    # Temperature calculator configuration
    temperature_config = ObjectProperty(TemperatureConfig,
                                        default=create_default_qclm_temperature_config())

    # Weights used for non_optimality calculation.
    temp_weight = FloatProperty(default=16)         # for 1 deg C difference from the reaction temperature
    primer_size_weight = FloatProperty(default=4)   # for 1 base difference from the optimal primer size
    three_end_size_weight = FloatProperty(default=8)
    five_end_size_weight = FloatProperty(default=1)
    gc_content_weight = FloatProperty(default=0)
    mutation_coverage_weight = FloatProperty(default=160)  # multiplies (1- <total mutation coverage>)
    # For primers which break the hairpin/primer-dimer temperature constraints
    hairpin_temperature_weight = FloatProperty(default=32)         # for each deg C higher
    primer_dimer_temperature_weight = FloatProperty(default=32)    #   formation temperature

    # Step for iteration over possible melting temperature thresholds, in deg C
    temp_threshold_step = FloatProperty(default=1)

    organism=StringProperty(default="e-coli")


class QCLMSequences(JsonObject):
    gene_of_interest = StringProperty(required=True)
    five_end_flanking_sequence = StringProperty(default="")
    three_end_flanking_sequence = StringProperty(default="")

    def get_full_sequence_with_offset(self) -> Tuple[str, int]:
        full_sequence = \
            self.five_end_flanking_sequence + \
            self.gene_of_interest + \
            self.three_end_flanking_sequence
        offset = len(self.five_end_flanking_sequence)
        return full_sequence, offset


class QCLMInput(JsonObject):
    sequences = ObjectProperty(QCLMSequences, required=True)
    config = ObjectProperty(QCLMConfig, required=True)
    mutations = ListProperty(str, required=True)

    def parse_mutations(self, goi_offset: int) -> List[MutationSite]:
        """
        Parses the user input in the format "E32W E32L E49K" and produces multi-amino
        mutations in the format of "E32WL E49K"
        """
        codon_muts = [parse_codon_mutation(mutation, goi_offset) for mutation in self.mutations]
        return create_multi_amino_mutations(codon_muts)


class PrimerOutput(JsonObject):
    sequence = StringProperty(required=True)
    start = IntegerProperty(required=True)
    length = IntegerProperty(required=True)
    temperature = FloatProperty(required=True)
    gc_content = FloatProperty(required=True)
    degenerate_codons = ListProperty(str, required=True)
    overlap_with_following = BooleanProperty(default=False, required=False)

class QCLMMutationOutput(JsonObject):
    # List of mutations in the format "E42L"
    mutations = ListProperty(str, required=True)
    result_found = BooleanProperty(required=True)
    # List of primers for the given mutations, however
    # this is *ALWAYS only a single primer*!!!
    # We keep it as a list because frontend depends on it.
    primers = ListProperty(PrimerOutput)


class QCLMOutput(JsonObject):
    input_data = ObjectProperty(QCLMInput, required=True)
    full_sequence = StringProperty(required=True)
    goi_offset = IntegerProperty(required=True)
    results = ListProperty(QCLMMutationOutput, required=True)


class SetOfMutationSiteSequences:
    def __init__(self, mutation_options_for_site_combos: List[QCLMMutationSiteSequence]) -> None:
        self.mutations = frozenset(mutation_options_for_site_combos)
        self.total_aminos = sum(map(lambda x: x.aminos_count, self.mutations))

    def get_mutation_site_combo_count(self) -> int:
        return sum([len(x) for x in self.mutations])

    def __iter__(self):
        return self.mutations.__iter__()

    def __key(self):
        return self.mutations

    def __eq__(x, y) -> bool:
        return x.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    def __repr__(self):
        return " ".join([str(x) for x in self.mutations])
