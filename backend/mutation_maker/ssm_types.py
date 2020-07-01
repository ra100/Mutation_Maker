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

import collections
import numpy as np
from typing import List, NamedTuple, Tuple

from Bio import Seq
from jsonobject import (BooleanProperty, FloatProperty,
                        IntegerProperty, JsonObject, ListProperty,
                        ObjectProperty, StringProperty)

from mutation_maker.mutation import parse_codon_mutation, AminoMutation
from mutation_maker.primer import Primer
from mutation_maker.temperature_calculator import TemperatureConfig


MinOptMax = collections.namedtuple("MinOptMax", "min opt max")


class Plasmid(JsonObject):
    gene_start_in_plasmid = IntegerProperty(default=None)
    gene_end_in_plasmid = IntegerProperty(default=None)
    plasmid_sequence = StringProperty(required=True)

    def get_five_end(self, gene_of_interest, forward_primer):
        self.check_sequence_occurrences(forward_primer, "Forward primer")

        if self.gene_start_in_plasmid is None:
            self.check_sequence_occurrences(
                gene_of_interest, "Gene of interest")
            gene_start = self.plasmid_sequence.find(gene_of_interest)
        else:
            gene_start = self.gene_start_in_plasmid

        forward_position = self.plasmid_sequence.find(forward_primer)

        if forward_position <= gene_start:
            return self.plasmid_sequence[forward_position:gene_start]
        else:
            return self.plasmid_sequence[forward_position:] + self.plasmid_sequence[:gene_start]

    def get_three_end(self, gene_of_interest, reverse_primer):
        reverse_complement = Seq.reverse_complement(reverse_primer)
        self.check_sequence_occurrences(reverse_complement, "Reverse primer")

        if self.gene_end_in_plasmid is None:
            self.check_sequence_occurrences(
                gene_of_interest, "Gene of interest")
            gene_end = self.plasmid_sequence.find(
                gene_of_interest) + len(gene_of_interest)
        else:
            gene_end = self.gene_end_in_plasmid
        reverse_position = self.plasmid_sequence.find(reverse_complement)
        reverse_primer_end = reverse_position + len(reverse_primer)

        if reverse_primer_end > gene_end:
            return self.plasmid_sequence[gene_end:reverse_primer_end]
        else:
            return self.plasmid_sequence[gene_end:] + \
                   self.plasmid_sequence[:reverse_primer_end]

    def check_sequence_occurrences(self, sequence, name):
        occurrences = self.plasmid_sequence.count(sequence)

        if occurrences != 1:
            if occurrences == 0:
                raise ValueError("{} was not found in plasmid".format(name))
            else:
                raise ValueError("{} position is ambiguous".format(name))


class SSMFlankingSequences:
    forward_flank: str
    reverse_flank: str

    def __init__(self, fw: str, rv: str):
        self.forward_flank = fw
        self.reverse_flank = rv


class SSMSequences(JsonObject):
    forward_primer = StringProperty(required=True)
    reverse_primer = StringProperty(required=True)
    gene_of_interest = StringProperty(required=True)
    five_end_flanking_sequence = StringProperty(default=None)
    three_end_flanking_sequence = StringProperty(default=None)
    plasmid = ObjectProperty(Plasmid, default=None)

    def get_full_sequence_with_offset(self) -> Tuple[str, Tuple[int, int]]:
        if self.plasmid is None:

            # TODO finish implementation of this option and write tests

            if self.five_end_flanking_sequence is None or self.three_end_flanking_sequence is None:
                raise ValueError("""If plasmid is not specified - \
five end flanking sequence and three end flanking sequence must be specified""")
            five_end = self.get_five_end(
                self.five_end_flanking_sequence, self.forward_primer)
            three_end = self.get_three_end(
                self.three_end_flanking_sequence, self.reverse_primer)
        else:
            if self.five_end_flanking_sequence is not None or \
                    self.three_end_flanking_sequence is not None:
                raise ValueError(
                    "If plasmid is specified - flanking sequences must be empty")
            five_end = self.plasmid.get_five_end(
                self.gene_of_interest, self.forward_primer)
            three_end = self.plasmid.get_three_end(
                self.gene_of_interest, self.reverse_primer)

        full_sequence = five_end + self.gene_of_interest + three_end
        offset = len(five_end)

        return full_sequence, (offset, offset + len(self.gene_of_interest))


class SSMConfig(JsonObject):
    min_primer_size = IntegerProperty(default=33)
    opt_primer_size = IntegerProperty(default=33)
    max_primer_size = IntegerProperty(default=60)

    min_gc_content = FloatProperty(default=40)
    opt_gc_content = FloatProperty(default=50)
    max_gc_content = FloatProperty(default=60)

    min_three_end_size = IntegerProperty(default=15)
    opt_three_end_size = IntegerProperty(default=15)
    max_three_end_size = IntegerProperty(default=42)

    min_overlap_size = IntegerProperty(default=33)
    opt_overlap_size = IntegerProperty(default=33)
    max_overlap_size = IntegerProperty(default=60)

    # These are only used in case `exclude_flanking_primers` is set to `True`.
    min_three_end_temperature = FloatProperty(default=57)
    opt_three_end_temperature = FloatProperty(default=60)
    max_three_end_temperature = FloatProperty(default=85)

    min_overlap_temperature = FloatProperty(default=57)
    opt_overlap_temperature = FloatProperty(default=60)
    max_overlap_temperature = FloatProperty(default=85)

    gc_clamp = IntegerProperty(default=1)

    min_five_end_size = IntegerProperty(default=3)
    max_five_end_size = IntegerProperty(default=60)

    # TODO: unify this naming with FE, we don't need them separately
    three_end_temp_range = FloatProperty(default=5)
    overlap_temp_range = FloatProperty(default=5)

    # Weights used for non_optimality calculation.
    three_end_temp_weight = FloatProperty(default=16)
    three_end_size_weight = FloatProperty(default=8)
    overlap_temp_weight = FloatProperty(default=1)
    gc_content_weight = FloatProperty(default=0)
    hairpin_temperature_weight = FloatProperty(default=32)
    primer_dimer_temperature_weight = FloatProperty(default=32)

    compute_hairpin_homodimer = BooleanProperty(default=False)

    # This is essentially the same as the original precision in the temp calculator.
    # Right now this isn't used by frontend, so we use the default value of 2.
    three_end_temp_range_step = FloatProperty(default=2)
    overlap_temp_range_step = FloatProperty(default=3)

    # This option determines if we allow different temperature for all
    # forward and reverse primers. If set to `False`, all primers are going
    # to fall in the same 5 degree temp range (controlled by `three_end_temp_range`).
    separate_forward_reverse_temperatures = BooleanProperty(default=True)

    # When set to false we use `NullGenerator` in place of primer3 to enforce
    # the secondary algorithm always being used.
    use_primer3 = BooleanProperty(default=True)

    # When set to true we use the fast approximation approach for growing primers.
    # (ref. https://github.com/matteoferla/mutational_scanning)
    use_fast_approximation_algorithm = BooleanProperty(default=True)

    # This option determins if we use flanking primers for computing 3' Tm,
    # or if we use the user specified 3' Tm range.
    exclude_flanking_primers = BooleanProperty(default=False)

    file_name = StringProperty(default="xxx")
    oligo_prefix = StringProperty(default="ssm")

    max_combinations_considered = IntegerProperty(default=10000)
    temperature_config = ObjectProperty(
        TemperatureConfig, default=TemperatureConfig())
    calculation_method = StringProperty(
        default="MaxMutationsCovered",
        choices=["All", "Random3End", "MaxMutationsCovered"])
    max_number_of_three_end_ranges = IntegerProperty(default=10)


class SSMInput(JsonObject):
    sequences = ObjectProperty(SSMSequences, required=True)
    config = ObjectProperty(SSMConfig, required=True)
    mutations = ListProperty(str, required=True)
    degenerate_codon = StringProperty(required=True, default="NNS")

    def parse_mutations(self, goi_offset):
        return [parse_codon_mutation(mutation, goi_offset) for mutation in self.mutations]


class OverlapOutput(JsonObject):
    length = IntegerProperty(required=True)
    temperature = FloatProperty(required=True)


class PrimerOutput(JsonObject):
    direction = StringProperty(required=True)
    normal_order_sequence = StringProperty(required=True)
    normal_order_start = IntegerProperty(required=True)
    three_end_temperature = FloatProperty(required=True)
    gc_content = FloatProperty(required=True)
    parameters_in_range = BooleanProperty(required=True)


class SSMMutationOutput(JsonObject):
    mutation = StringProperty(required=True)
    non_optimality = FloatProperty(required=True)
    parameters_in_range = BooleanProperty(required=True)
    # This is no longer used by the backend because we have second best.
    # The frontend however still requires it, which is why we're keeping it.
    result_found = BooleanProperty(required=True)

    forward_primer = ObjectProperty(PrimerOutput)
    reverse_primer = ObjectProperty(PrimerOutput)
    overlap = ObjectProperty(OverlapOutput)


class SSMOutput(JsonObject):
    input_data = ObjectProperty(SSMInput, required=True)
    results = ListProperty(SSMMutationOutput, required=True)
    full_sequence = StringProperty(required=True)
    goi_offset = IntegerProperty(required=True)
    new_sequence_start = IntegerProperty(required=True)

    forward_flanking_primer_temperature = FloatProperty(required=True)
    reverse_flanking_primer_temperature = FloatProperty(required=True)
    min_three_end_temperature = FloatProperty()
    max_three_end_temperature = FloatProperty()
    min_overlap_temperature = FloatProperty()
    max_overlap_temperature = FloatProperty()


# TODO: get rid of this
class SSMMutagenicPrimer:
    def __init__(self, primer: Primer, three_end_size: int,
                 three_end_temperature: float) -> None:
        self.primer = primer
        self.three_end_size = three_end_size
        self.three_end_temperature = three_end_temperature

    def __repr__(self):
        return f"{self.primer} " + \
               f"[{self.three_end_size},{self.three_end_temperature}]"

    def check_in_range(self, config: SSMConfig, result) -> bool:
        gc_content = self.primer.get_gc_content()
        gc_content_in_range = config.min_gc_content <= gc_content <= config.max_gc_content

        # Based on the primer's direction we check its temperature against
        # the picked temperatures.
        if self.primer.direction == Primer.FORWARD:
            temp_range = result.forward_temp_range
        else:
            temp_range = result.reverse_temp_range

        temp_in_range = temp_range.min <= self.three_end_temperature <= temp_range.max

        return bool(gc_content_in_range and temp_in_range)


class SSMPrimerPair:
    def __init__(self, mutation: AminoMutation,
                 fw_primer: Primer, fw_size: int, fw_temp: float,
                 rw_primer: Primer, rw_size: int, rw_temp: float,
                 overlap_len: int, overlap_temp: float, non_optimality: float) -> None:
        self.mutation = mutation

        self.fw_primer = fw_primer
        self.fw_size = fw_size
        self.fw_temp = fw_temp

        self.rw_primer = rw_primer
        self.rw_size = rw_size
        self.rw_temp = rw_temp

        self.overlap_size = overlap_len
        self.overlap_temp = overlap_temp

        self.non_optimality = non_optimality

    def __repr__(self):
        return f"{self.fw_primer} {self.rw_primer} [{self.overlap_size}, {self.overlap_temp}]"


class SSMPrimerPossibilities:
    def __init__(self, mutation,
                 forward_primers: List[Primer], fw_sizes: np.ndarray, fw_temps: np.ndarray, fw_gc_contents: np.ndarray,
                 reverse_primers: List[Primer], rw_sizes: np.ndarray, rw_temps: np.ndarray, rw_gc_contents: np.ndarray,) \
                 -> None:
        self.mutation = mutation

        self.fw_primers = forward_primers
        self.fw_sizes = fw_sizes
        self.fw_temps = fw_temps
        self.fw_gc_contents = fw_gc_contents

        self.rw_primers = reverse_primers
        self.rw_temps = rw_temps
        self.rw_sizes = rw_sizes
        self.rw_gc_contents = rw_gc_contents

    def __repr__(self):
        return f"Primer possibilities for mutation {self.mutation} " + \
               f"[{len(self.fw_primers)}/{len(self.rw_primers)}]"


class SSMPrimerPairPossibilities:
    def __init__(self, options: SSMPrimerPossibilities, pair_indexes: np.ndarray,
                 overlap_temps: np.ndarray, is_main=True) -> None:
        self.mutation = options.mutation
        self.options = options
        self.pair_indexes = pair_indexes
        self.overlap_temps = overlap_temps
        self.is_main = is_main

    def __repr__(self):
        return f"{self.mutation.original_string} {len(self.pair_indexes)} possibilities " + \
               f"\t(is_main={self.is_main})"


class SSMSolution:
    def __init__(self, forward_temp_opt: float, reverse_temp_opt: float,
                 overlap_temp: float, result: List[SSMPrimerPair],
                 temp_range: float) -> None:
        self.forward_temp = forward_temp_opt
        self.reverse_temp = reverse_temp_opt
        self.overlap_temp = overlap_temp
        self.result = result

        half_temp_range = temp_range / 2

        self.forward_temp_range = MinOptMax(forward_temp_opt - half_temp_range,
                                            forward_temp_opt,
                                            forward_temp_opt + half_temp_range)

        self.reverse_temp_range = MinOptMax(reverse_temp_opt - half_temp_range,
                                            reverse_temp_opt,
                                            reverse_temp_opt + half_temp_range)

        self.overlap_temp_range = MinOptMax(overlap_temp - half_temp_range,
                                            overlap_temp,
                                            overlap_temp + half_temp_range)

    def primer_non_optimalities(self) -> List[float]:
        return [pair.non_optimality for pair in self.result]

    def sum_of_non_optimality(self):
        return sum(self.primer_non_optimalities())


class SSMPrimerSpec(NamedTuple):
    offset: int
    length: int
    three_end_size: int
    three_end_temp: float


class SSMGrownSolution:
    overlaps: List[SSMPrimerSpec]
    fw_primers: List[SSMPrimerSpec]
    rw_primers: List[SSMPrimerSpec]
    fw_temp: float
    rw_temp: float
    overlap_temp: float

    def __init__(self,
                 overlaps: List[SSMPrimerSpec],
                 fw_primers: List[SSMPrimerSpec],
                 rw_primers: List[SSMPrimerSpec]):
        self.overlaps = overlaps
        self.fw_primers = fw_primers
        self.rw_primers = rw_primers

        half_temp_range = 2.5

        fw_temp, rw_temp, overlap_temp = self.compute_optimal_reaction_temps()

        self.fw_temp = fw_temp
        self.rw_temp = rw_temp
        self.overlap_temp = overlap_temp

        self.forward_temp_range = MinOptMax(fw_temp - half_temp_range,
                                            fw_temp,
                                            fw_temp + half_temp_range)

        self.reverse_temp_range = MinOptMax(rw_temp - half_temp_range,
                                            rw_temp,
                                            rw_temp + half_temp_range)

        self.overlap_temp_range = MinOptMax(overlap_temp - half_temp_range,
                                            overlap_temp,
                                            overlap_temp + half_temp_range)

    def compute_optimal_reaction_temps(self) -> Tuple[float, float, float]:
        """
        Computes the temperatures for SSM reactions based on the actual primer
        temperatures. This is used in the output instead of the temperature picked
        by the primer growth, because by construction we know all of the primers will
        be above the threshold, from which it directly follows that the threshold
        is not an optimal reaction temperature.
        """
        fw_temps = np.array([primer.three_end_temp for primer in self.fw_primers])
        rw_temps = np.array([primer.three_end_temp for primer in self.rw_primers])
        overlap_temps = np.array([overlap.three_end_temp for overlap in self.overlaps])

        result = (
            temp_with_most_in_range(fw_temps),
            temp_with_most_in_range(rw_temps),
            temp_with_most_in_range(overlap_temps)
        )

        return result


def temp_with_most_in_range(temps) -> float:
    checked_temps = np.arange(min(temps), max(temps) + 0.11, 0.1)

    counts = [len(temps[abs(temps - temp) < 2.5]) for temp in checked_temps]

    return checked_temps[np.argmax(counts)].item()


def create_output_sequence(full_sequence, goi_range, primers):
    if len(primers) == 0:
        return full_sequence[goi_range[0]:goi_range[1]], 0

    min_primer_start = min([primer.primer.get_normal_start() for primer in primers])
    max_primer_end = max([primer.primer.get_normal_end() for primer in primers])
    start = min(min_primer_start, goi_range[0])
    end = max(max_primer_end, goi_range[1])
    new_goi_offset = goi_range[0] - start

    return full_sequence[start:end], new_goi_offset
