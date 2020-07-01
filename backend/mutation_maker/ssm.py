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

import math
from pprint import pprint
from typing import List, Tuple

import numpy as np
import primer3
from Bio import Seq

from mutation_maker.ssm_fast_approximation import pick_best_grown_solution, grow_primers, find_best_overlaps, \
    compute_grown_solution_score, calc_GC_content
from mutation_maker.ssm_types import SSMConfig, SSMSequences, MinOptMax, SSMInput, SSMGrownSolution, \
    SSMSolution, SSMPrimerPossibilities, SSMPrimerPairPossibilities, SSMPrimerPair, \
    SSMMutagenicPrimer, SSMMutationOutput, SSMOutput, create_output_sequence, PrimerOutput, OverlapOutput, \
    SSMPrimerSpec, SSMFlankingSequences
from mutation_maker.temperature_calculator import PrimerDimerCalculator
from .section_timer import SectionTimer
from .mutation import AminoMutation
from .primer import Primer
from .primer3_interoperability import Primer3Config, PrimerGenerator


def calculate_mutagenic_primer_search_area(mutation, ssm_config, primer_direction):
    max_five_end_size = ssm_config.max_primer_size - \
                        mutation.length - ssm_config.min_three_end_size
    search_area_length = max_five_end_size + \
                         mutation.length + ssm_config.max_three_end_size

    if primer_direction == Primer.FORWARD:
        min_start = mutation.position - max_five_end_size
    elif primer_direction == Primer.REVERSE:
        min_start = mutation.position - ssm_config.max_three_end_size
    else:
        raise NotImplemented()

    return min_start, search_area_length


def ssm_solve(workflow_input: SSMInput, main_primer_generator, secondary_primer_generator):
    solver = SSMSolver(workflow_input.sequences, workflow_input.config,
                       main_primer_generator, secondary_primer_generator)

    flanks = SSMFlankingSequences(workflow_input.sequences.forward_primer,
                                  workflow_input.sequences.reverse_primer)
    mutations = workflow_input.parse_mutations(solver.goi_range[0])

    if workflow_input.config.use_fast_approximation_algorithm:
        result = solver.solve_for_mutations_faster(mutations)
        output = format_fast_output(mutations, solver, workflow_input, result, workflow_input.degenerate_codon)
    else:
        result = solver.solve_for_mutations(mutations,flanks)
        output = format_output(solver, workflow_input, result, workflow_input.degenerate_codon)

    return output.to_json()


def pick_best_solution(solutions: List[SSMSolution]) -> SSMSolution:
    sums = np.fromiter((solution.sum_of_non_optimality() for solution in solutions), dtype=np.float32)
    min_idx: int = np.argmin(sums).item()

    best_solution: SSMSolution = solutions[min_idx]

    return best_solution


def compute_heterodimer_err(this_primer_pair: SSMPrimerPair, config: SSMConfig,
                            flanks: SSMFlankingSequences):
    """
    Computes error of heterodimer temperature for forward and reverse primers.
    The error is computed as sum of all hetero-dimers combinations. e.g. we have primer A as this primer pair.
    Other_primer_pairs contains primers A,B,C,D,E. We compute error for A-B, A-C, A-D, A-E. We skip A-A combination
    because it does not make sens to compute heterodimer error with its-self.
    :return: square root ( sum of (weighted heterodimers error pairs) )
    """
    if flanks.reverse_flank is None or flanks.forward_flank is None:
        return 0
    return primer3.calcHeterodimerTm(this_primer_pair.fw_primer.normal_order_sequence,
                                     flanks.reverse_flank,
                                     config.temperature_config.k,
                                     config.temperature_config.mg,
                                     config.temperature_config.dntp) + \
           primer3.calcHeterodimerTm(this_primer_pair.rw_primer.normal_order_sequence,
                                     flanks.forward_flank,
                                     config.temperature_config.k,
                                     config.temperature_config.mg,
                                     config.temperature_config.dntp)



def penalize_solution(best_solution: SSMSolution, config: SSMConfig, fw_opt_temp, rv_opt_temp,
                      flanks: SSMFlankingSequences):
    """
    Computes primer dimer penalty. The penalty consists of following penalties:
        - hairpin penalty
        - homo dimer penalty
        - hetero dimer penalty (this is applied for each combinations of primer pairs with the rest)
    Each component is computed with help of primer3 library. It is weighted squared error by corresponding weights
    from config. Than all errors are added together and we return square error of this errors.
    :param best_solution:
    :param config:
    :param fw_opt_temp:
    :param rv_opt_temp:
    :return:
    """
    for pair in best_solution.result:
        fw_sequence = pair.fw_primer.normal_order_sequence
        rw_sequence = pair.rw_primer.normal_order_sequence
        temp_cfg = config.temperature_config
        fw_hairpin_tm = primer3.calcHairpinTm(fw_sequence, temp_cfg.k, temp_cfg.mg, temp_cfg.dntp)
        rw_hairpin_tm = primer3.calcHairpinTm(rw_sequence, temp_cfg.k, temp_cfg.mg, temp_cfg.dntp)

        fw_homodimer_tm = primer3.calcHomodimerTm(fw_sequence, temp_cfg.k, temp_cfg.mg, temp_cfg.dntp)
        rw_homodimer_tm = primer3.calcHomodimerTm(rw_sequence, temp_cfg.k, temp_cfg.mg, temp_cfg.dntp)

        fw_hairpin_err = (best_solution.forward_temp - fw_hairpin_tm) ** 2
        rw_hairpin_err = (best_solution.reverse_temp - rw_hairpin_tm) ** 2

        fw_homodimer_err = (fw_opt_temp - fw_homodimer_tm) ** 2
        rw_homodimer_err = (rv_opt_temp - rw_homodimer_tm) ** 2

        heterodimer_err = compute_heterodimer_err(pair, config, flanks)

        penalty = math.sqrt(
                    config.hairpin_temperature_weight * fw_hairpin_err +
                    config.hairpin_temperature_weight * rw_hairpin_err +
                    config.primer_dimer_temperature_weight * fw_homodimer_err +
                    config.primer_dimer_temperature_weight * rw_homodimer_err +
                    config.primer_dimer_temperature_weight * heterodimer_err)

        pair.non_optimality += penalty


class SSMSolver:
    def __init__(self, ssm_sequences: SSMSequences, ssm_config: SSMConfig,
                 main_primer_generator: PrimerGenerator, secondary_primer_generator: PrimerGenerator) -> None:
        self.main_primer_generator = main_primer_generator
        self.secondary_primer_generator = secondary_primer_generator
        self.config = ssm_config
        self.temp_calculator = ssm_config.temperature_config.create_calculator()

        if self.temp_calculator.precision > 1:
            raise ValueError("""Temperature calculation for SSM with precision of more than one decimal place \
is not needed and have severe negative impact on performance""")

        self.gc_settings = MinOptMax(self.config.min_gc_content,
                                     self.config.opt_gc_content,
                                     self.config.max_gc_content)

        self.forward_primer = ssm_sequences.forward_primer
        self.reverse_primer = ssm_sequences.reverse_primer
        self.forward_primer_temp = self.temp_calculator(self.forward_primer)
        self.reverse_primer_temp = self.temp_calculator(self.reverse_primer)
        self.three_end_pivot_temps = [
            self.forward_primer_temp,
            self.reverse_primer_temp
        ]
        self.sequence, self.goi_range = ssm_sequences.get_full_sequence_with_offset()
        self.flanks = SSMFlankingSequences(ssm_sequences.forward_primer, ssm_sequences.reverse_primer)

    def generate_fw_rw_primers(self, mutations: List[AminoMutation], primer_generator):
        fw_configs = [
            self.config_for_mutation(mutation, Primer.FORWARD)
            for mutation in mutations
        ]
        rw_configs = [
            self.config_for_mutation(mutation, Primer.REVERSE)
            for mutation in mutations
        ]

        all_configs = fw_configs + rw_configs
        results = primer_generator.design_primers_for_all_mutations(all_configs)

        fw_count = len(fw_configs)
        fw_lists = results[:fw_count]
        rw_lists = results[fw_count:]

        assert len(fw_lists) == len(fw_configs)
        assert len(rw_lists) == len(rw_configs)

        return fw_lists, rw_lists

    def generate_primers(self, mutations: List[AminoMutation], primer_generator, generator_name) \
            -> Tuple[List[SSMPrimerPossibilities], List[SSMPrimerPairPossibilities]]:
        with SectionTimer(f"generate primers {generator_name}") as timer:
            with timer.child("primer options"):
                fw_lists, rw_lists = self.generate_fw_rw_primers(mutations, primer_generator)

                combos = zip(mutations, fw_lists, rw_lists)
                primer_options = []

                for mutation, fw_primers_list, rw_primers_list in combos:
                    fw_primers, fw_sizes, fw_gc_contents = self.filter_by_three_end_size(mutation, fw_primers_list)
                    rw_primers, rw_sizes, rw_gc_contents = self.filter_by_three_end_size(mutation, rw_primers_list)

                    fw_temps = np.fromiter((
                        primer.get_three_end_temperature_with_size(size, self.temp_calculator)
                        for primer, size in zip(fw_primers, fw_sizes)
                    ), dtype=np.float32)

                    rw_temps = np.fromiter((
                        primer.get_three_end_temperature_with_size(size, self.temp_calculator)
                        for primer, size in zip(rw_primers, rw_sizes)
                    ), dtype=np.float32)

                    primer_options.append(SSMPrimerPossibilities(mutation,
                                                                 fw_primers, fw_sizes, fw_temps, fw_gc_contents,
                                                                 rw_primers, rw_sizes, rw_temps, rw_gc_contents))

            with timer.child("pairs"):
                possible_pairs = self.get_all_valid_pairs_for_all_options(primer_options, generator_name == "main")

        return primer_options, possible_pairs

    def solve_for_mutations_faster(self, mutations: List[AminoMutation]) -> SSMGrownSolution:
        temps: List[Tuple[float, float, float]] = self.get_temp_combinations()

        solutions: List[SSMGrownSolution] = []

        overlap_temps = self.get_overlap_temps()
        overlaps_with_temps: List[Tuple[float, List[SSMPrimerSpec]]] = []

        for overlap_temp in overlap_temps:
            overlaps = find_best_overlaps(self.sequence,
                                          self.config.min_five_end_size,
                                          self.config.min_overlap_size,
                                          self.config.max_overlap_size,
                                          mutations,
                                          overlap_temp,
                                          self.temp_calculator,
                                          self.config.overlap_temp_range / 2)

            overlaps_with_temps.append((overlap_temp, overlaps))

        for fw_temp, rw_temp, overlap_temp in temps:
            pair_temps = np.array([pair[0] for pair in overlaps_with_temps])
            overlaps = overlaps_with_temps[np.argmin(abs(pair_temps - overlap_temp)).item()][1]

            fw_primers, rw_primers = grow_primers(self.config.max_primer_size,
                                                  self.config.min_three_end_size,
                                                  self.sequence,
                                                  mutations,
                                                  overlaps,
                                                  fw_temp,
                                                  rw_temp,
                                                  self.temp_calculator)

            solutions.append(SSMGrownSolution(overlaps, fw_primers, rw_primers))

        best_solution = pick_best_grown_solution(self.config, self.sequence, solutions, self.flanks)

        return best_solution

    def solve_for_mutations(self, mutations: List[AminoMutation], flanks: SSMFlankingSequences) -> SSMSolution:
        with SectionTimer("solve_for_mutations") as timer:
            with timer.child("main primers"):
                main_primer_options, main_possible_pairs = \
                    self.generate_primers(mutations, self.main_primer_generator, "main")

            with timer.child("secondary primers"):
                secondary_mutations = [pair.mutation for pair in main_possible_pairs
                                       if len(pair.pair_indexes) == 0]

                secondary_primer_options, secondary_pairs = \
                    self.generate_primers(secondary_mutations,
                                          self.secondary_primer_generator, "secondary")

                main_valid_pairs = [pair for pair in main_possible_pairs if len(pair.pair_indexes) > 0]
                possible_pairs = main_valid_pairs + secondary_pairs

            # Here we generate all combinations for 3' FW, RW and overlap temperature.
            temp_combinations = self.get_temp_combinations()

            with timer.child("generate possible solutions"):
                # Now we generate a separate solution for each temperature combination.
                solutions = [self.get_best_primers_for_temp_ranges(possible_pairs,
                                                                   forward_temp,
                                                                   reverse_temp,
                                                                   overlap_temp,
                                                                   self.config,
                                                                   flanks)
                             for forward_temp, reverse_temp, overlap_temp in temp_combinations]

            with timer.child("pick_best_solution"):
                # And finally pick the 3' forward, reverse & overlap temperatures
                # which have the best solution.
                final_result = pick_best_solution(solutions)

            pprint(possible_pairs)

            return final_result

    def get_temp_combinations(self) -> List[Tuple[float, float, float]]:
        combinations = []

        overlap_temps = self.get_overlap_temps()

        if self.config.separate_forward_reverse_temperatures:
            forward_temps, reverse_temps = self.get_separate_three_end_temps()

            # Here we consider all combinations of 3' forward, 3' reverse and overlap temperatures.
            for fw in forward_temps:
                for rw in reverse_temps:
                    for overlap in overlap_temps:
                        combinations.append((fw, rw, overlap))
        else:
            three_end_temps = self.get_single_three_end_temps()

            for three_end_temp in three_end_temps:
                for overlap in overlap_temps:
                    # Here we specify the same forward/reverse Tm since the rest of the algorithm
                    # does not distinguish on the `config.separate_forward_reverse_temperatures` flag.
                    combinations.append((three_end_temp, three_end_temp, overlap))

        return combinations

    def get_single_three_end_temps(self) -> List[float]:
        assert not self.config.separate_forward_reverse_temperatures

        three_end_temp_range = self.config.three_end_temp_range
        three_end_temp_range_step = self.config.three_end_temp_range_step

        if self.config.exclude_flanking_primers:
            return self.get_three_end_temps_from_explicit_input()
        else:
            min_three_end = max(self.forward_primer_temp, self.reverse_primer_temp) - three_end_temp_range
            max_three_end = min(self.forward_primer_temp, self.reverse_primer_temp) + three_end_temp_range

            three_temps = np.arange(min_three_end,
                                    max_three_end,
                                    step=three_end_temp_range_step).tolist()

            # This is here only for the type checker, since `.tolist()` doesn't have the right annotation.
            assert isinstance(three_temps, List)

            # In case the flanking primers are further than 10 Tm degrees apart
            # we simply set 3' Tm to their mean temperature.
            if len(three_temps) == 0:
                three_temps = [min(self.forward_primer_temp, self.reverse_primer_temp) - 1]

            return three_temps

    def get_separate_three_end_temps(self) -> Tuple[List[float], List[float]]:
        assert self.config.separate_forward_reverse_temperatures

        three_end_temp_range = self.config.three_end_temp_range
        three_end_temp_range_step = self.config.three_end_temp_range_step

        if self.config.exclude_flanking_primers:
            three_end_temps = self.get_three_end_temps_from_explicit_input()

            return three_end_temps, three_end_temps
        else:
            min_forward = self.forward_primer_temp - three_end_temp_range
            max_forward = self.forward_primer_temp + three_end_temp_range

            min_reverse = self.reverse_primer_temp - three_end_temp_range
            max_reverse = self.reverse_primer_temp + three_end_temp_range

            forward_temps: List[float] = np.arange(min_forward, max_forward, step=three_end_temp_range_step).tolist()
            reverse_temps: List[float] = np.arange(min_reverse, max_reverse, step=three_end_temp_range_step).tolist()

            return forward_temps, reverse_temps

    def get_three_end_temps_from_explicit_input(self) -> List[float]:
        """Returns 3' Tm temperatures based on the input field,
        only valid if flanking primers are excluded."""
        assert self.config.exclude_flanking_primers

        three_temps: List[float] = np.arange(self.config.min_three_end_temperature,
                                             self.config.max_three_end_temperature,
                                             step=self.config.three_end_temp_range).tolist()

        return three_temps

    def get_overlap_temps(self) -> List[float]:
        # Since overlap temperature is not related to flanking primers, we calculate
        # it directly from the user input.
        min_overlap = self.config.min_overlap_temperature
        max_overlap = self.config.max_overlap_temperature

        overlap_temps: List[float] = np.arange(min_overlap,
                                               max_overlap,
                                               step=self.config.overlap_temp_range_step).tolist()

        return overlap_temps

    def get_all_valid_pairs_for_all_options(self, all_primer_options: List[SSMPrimerPossibilities], is_main) \
            -> List[SSMPrimerPairPossibilities]:
        """
        Returns a list of possible primer combinations for a given set of
        possible forward and reverse primers.
        """
        list_of_pairs = []

        min_overlap_size = self.config.min_overlap_size
        max_overlap_size = self.config.max_overlap_size

        for primer_options in all_primer_options:
            fw_count = len(primer_options.fw_primers)
            rw_count = len(primer_options.rw_primers)

            filtered_indexes = []
            overlap_temps = []

            for i in range(fw_count):
                for j in range(rw_count):
                    fw = primer_options.fw_primers[i]
                    rw = primer_options.rw_primers[j]

                    start = max(fw.normal_start, rw.normal_start)
                    end = min(fw.normal_end, rw.normal_end)

                    overlap_len = end - start

                    if min_overlap_size <= overlap_len <= max_overlap_size:
                        filtered_indexes.append((i, j))

                        start_offset = start - fw.normal_start
                        end_offset = end - fw.normal_start

                        overlap = fw.normal_order_sequence[start_offset:end_offset]
                        overlap_temp = self.temp_calculator(overlap)

                        overlap_temps.append(overlap_temp)

            possibilities = SSMPrimerPairPossibilities(
                primer_options,
                np.array(filtered_indexes),
                np.array(overlap_temps),
                is_main)

            list_of_pairs.append(possibilities)

        return list_of_pairs

    def filter_by_three_end_size(self, mutation: AminoMutation, primers: List[Primer]) \
                                 -> Tuple[List[Primer], np.ndarray, np.ndarray]:
        """
        Filters givne primers by minimum three and five and size.
        """
        min_three_size = self.config.min_three_end_size
        max_three_size = self.config.max_three_end_size

        min_five_size = self.config.min_five_end_size
        max_five_size = self.config.max_five_end_size

        filtered_primers = []
        three_end_sizes = []
        gc_contents = []

        for primer in primers:
            three_end_size = primer.get_three_end_size_from_mutation(mutation)
            five_end_size = primer.get_five_end_size_from_mutation(mutation)

            three_in_range = min_three_size <= three_end_size <= max_three_size
            five_in_range = min_five_size <= five_end_size <= max_five_size

            if three_in_range and five_in_range:
                filtered_primers.append(primer)
                three_end_sizes.append(three_end_size)
                gc_contents.append(calc_GC_content(primer.normal_order_sequence))
                # gc_contents.append(0)

        return filtered_primers, np.array(three_end_sizes), np.array(gc_contents)

    def get_best_primers_for_temp_ranges(self,
                                         possible_pairs: List[SSMPrimerPairPossibilities],
                                         forward_temp_opt: float,
                                         reverse_temp_opt: float,
                                         overlap_temp: float,
                                         config: SSMConfig,
                                         flanks: SSMFlankingSequences) -> SSMSolution:
        half_temp_interval = config.three_end_temp_range / 2
        min_three_end_size = config.min_three_end_size

        best = []

        for pairs in possible_pairs:
            idx_arry = pairs.pair_indexes

            fw_sizes = pairs.options.fw_sizes[idx_arry[:, 0]]
            fw_gc_contetns = pairs.options.fw_gc_contents[idx_arry[:, 0]]
            rw_sizes = pairs.options.rw_sizes[idx_arry[:, 1]]
            rw_gc_contetns = pairs.options.rw_gc_contents[idx_arry[:, 1]]


            fw_temps = pairs.options.fw_temps[idx_arry[:, 0]]
            rw_temps = pairs.options.rw_temps[idx_arry[:, 1]]
            overlap_temps = pairs.overlap_temps

            overlap_diff = np.abs(overlap_temps - overlap_temp)
            overlap_diff[overlap_diff < half_temp_interval] = 0

            fw_temp_diff = np.abs(fw_temps - forward_temp_opt)
            fw_temp_diff[fw_temp_diff < half_temp_interval] = 0

            rw_temp_diff = np.abs(rw_temps - reverse_temp_opt)
            rw_temp_diff[rw_temp_diff < half_temp_interval] = 0

            # compute overflow of GC content which are below min to negative values
            # 1st param -> array of constants, 2nd param -> what we want to substract, 3rd param -> where to store output
            # 4th param condition where to do operation
            np.subtract(config.min_gc_content,fw_gc_contetns, out=fw_gc_contetns, where=config.min_gc_content > fw_gc_contetns)
            np.subtract(config.min_gc_content,rw_gc_contetns, out=rw_gc_contetns, where=config.min_gc_content > rw_gc_contetns)


            # subtract those above max
            np.subtract(fw_gc_contetns, config.max_gc_content, out=fw_gc_contetns, where=config.max_gc_content < fw_gc_contetns)
            np.subtract(rw_gc_contetns, config.max_gc_content, out=rw_gc_contetns, where=config.max_gc_content < rw_gc_contetns)

            # set to zero those which are inside interval, () are necessary
            fw_gc_contetns[(config.min_gc_content <= fw_gc_contetns) & (fw_gc_contetns <= config.max_gc_content)] = 0
            rw_gc_contetns[(config.min_gc_content <= rw_gc_contetns) & (rw_gc_contetns <= config.max_gc_content)] = 0

            fw_extra_sizes = fw_sizes - min_three_end_size
            rw_extra_sizes = rw_sizes - min_three_end_size

            scores = np.sqrt(
                config.three_end_temp_weight * (fw_temp_diff ** 2) +
                config.three_end_temp_weight * (rw_temp_diff ** 2) +
                config.overlap_temp_weight * (overlap_diff ** 2) +
                config.three_end_size_weight * (fw_extra_sizes ** 2) +
                config.three_end_size_weight * (rw_extra_sizes ** 2) +
                config.gc_content_weight * (fw_gc_contetns ** 2) +
                config.gc_content_weight * (rw_gc_contetns ** 2)
            )

            minimal_pair_idx = np.argmin(scores).item()
            minimal_pair_idx_tup = idx_arry[minimal_pair_idx]

            min_fw_idx, min_rw_idx = minimal_pair_idx_tup

            options = pairs.options

            fw_primer = options.fw_primers[min_fw_idx]
            rw_primer = options.rw_primers[min_rw_idx]

            _, overlap_len = fw_primer.get_overlap(rw_primer)

            minimal_pair = SSMPrimerPair(
                pairs.mutation,
                fw_primer,
                options.fw_sizes[min_fw_idx].item(),
                options.fw_temps[min_fw_idx].item(),

                rw_primer,
                options.rw_sizes[min_rw_idx].item(),
                options.rw_temps[min_rw_idx].item(),

                overlap_len,
                pairs.overlap_temps[minimal_pair_idx].item(),
                scores[minimal_pair_idx].item()
            )

            best.append(minimal_pair)
        best_solution = SSMSolution(forward_temp_opt, reverse_temp_opt, overlap_temp, best, config.three_end_temp_range)
        # Due to high number of possible combinations and given that primer-dimer penalty would be very costly regarding
        # computing for all combinations, we just introduce ad-hoc penalty
        # for the best solution for given reaction temperature
        if config.compute_hairpin_homodimer:
            penalize_solution(best_solution, config,forward_temp_opt, reverse_temp_opt, flanks)
        return best_solution

    def config_for_mutation(self, mutation, primer_direction) -> Primer3Config:
        start, length = calculate_mutagenic_primer_search_area(
            mutation, self.config, primer_direction)

        return self.create_config_for_primer3(start, length, primer_direction)

    def create_config_for_primer3(self, area_start, area_len, mutagenic_primer_direction):
        primer3_config = Primer3Config()

        if mutagenic_primer_direction == Primer.REVERSE:
            primer3_config.force_forward_primer(self.forward_primer)
            primer3_config.search_region(reverse_from=area_start, reverse_len=area_len)
        elif mutagenic_primer_direction == Primer.FORWARD:
            primer3_config.force_reverse_primer(self.reverse_primer)
            primer3_config.search_region(forward_from=area_start, forward_len=area_len)

        primer3_config.template_sequence(self.sequence)
        primer3_config.size_range(minimum=self.config.min_primer_size,
                                  optimum=self.config.opt_primer_size,
                                  maximum=self.config.max_primer_size)

        primer3_config.gc_content_range(minimum=0, maximum=100)
        primer3_config.temperature_range(minimum=0, maximum=100)
        primer3_config.gc_clamp(0)

        return primer3_config


def format_fast_output(mutations: List[AminoMutation], solver, input_data: SSMInput,
                       solution: SSMGrownSolution, degenerate_codon: str):
    all_primers = []

    parent_sequence = solver.sequence
    primer_pairs: List[SSMPrimerPair] = []
    flanks = SSMFlankingSequences(input_data.sequences.forward_primer,
                                  input_data.sequences.reverse_primer)
    pdCalc = PrimerDimerCalculator(input_data.config.temperature_config.k,
                                   input_data.config.temperature_config.mg,
                                   input_data.config.temperature_config.dntp,
                                   cached=True)

    non_optimalities = compute_grown_solution_score(input_data.config, parent_sequence, solution, flanks, pdCalc)

    for mutation, overlap, fw_primer_spec, rw_primer_spec, score in \
            zip(mutations, solution.overlaps, solution.fw_primers, solution.rw_primers, non_optimalities):
        # Wrap primer specs in the standard Primer structure
        fw_primer = Primer(parent_sequence, Primer.FORWARD, fw_primer_spec.offset, fw_primer_spec.length)
        rw_primer = Primer(parent_sequence, Primer.REVERSE, rw_primer_spec.offset + rw_primer_spec.length - 1,
                           rw_primer_spec.length)

        # A simple check that we're converting between primer representations correctly
        assert rw_primer.normal_order_sequence == parent_sequence[
                                                  rw_primer_spec.offset:rw_primer_spec.offset + rw_primer_spec.length]
        assert fw_primer.normal_order_sequence == parent_sequence[
                                                  fw_primer_spec.offset:fw_primer_spec.offset + fw_primer_spec.length]

        all_primers.append(
            SSMMutagenicPrimer(fw_primer, fw_primer_spec.three_end_size, fw_primer_spec.three_end_temp))
        all_primers.append(
            SSMMutagenicPrimer(rw_primer, rw_primer_spec.three_end_size, rw_primer_spec.three_end_temp))

        primer_pairs.append(
            SSMPrimerPair(mutation,
                          fw_primer, fw_primer_spec.three_end_size, fw_primer_spec.three_end_temp,
                          rw_primer, rw_primer_spec.three_end_size, rw_primer_spec.three_end_temp,
                          overlap.length, overlap.three_end_temp, score))

    sequence, offset = create_output_sequence(solver.sequence,
                                              solver.goi_range,
                                              all_primers)

    new_sequence_start = solver.goi_range[0] - offset

    mutation_outputs = [create_mutation_output(input_data.config,
                                               primer_pair,
                                               non_optimality,
                                               degenerate_codon,
                                               new_sequence_start,
                                               solution)
                        for primer_pair, non_optimality in zip(primer_pairs, non_optimalities)]

    # Here we use the solution to figure out the optimal temperatures of the reaction.
    opt_forward_temp, opt_reverse_temp, opt_overlap_temp = \
        solution.compute_optimal_reaction_temps()

    # We re-construct the original temperature range by adding half of the temp
    # interval on both sides of the reaction temperatures.
    half_temp_range = input_data.config.three_end_temp_range / 2

    return SSMOutput(
        input_data=input_data,
        results=mutation_outputs,
        full_sequence=sequence,
        goi_offset=offset,
        new_sequence_start=new_sequence_start,
        forward_flanking_primer_temperature=solver.forward_primer_temp,
        reverse_flanking_primer_temperature=solver.reverse_primer_temp,

        min_forward_temperature=(opt_forward_temp - half_temp_range),
        opt_forward_temperature=opt_forward_temp,
        max_forward_temperature=(opt_forward_temp + half_temp_range),

        min_reverse_temperature=(opt_reverse_temp - half_temp_range),
        opt_reverse_temperature=opt_reverse_temp,
        max_reverse_temperature=(opt_reverse_temp + half_temp_range),

        min_overlap_temperature=(opt_overlap_temp - half_temp_range),
        opt_overlap_temperature=opt_overlap_temp,
        max_overlap_temperature=(opt_overlap_temp + half_temp_range)
    )


def format_output(solver, input_data: SSMInput, result: SSMSolution, degenerate_codon: str):
    all_primers = []

    for mutation_result in result.result:
        all_primers.append(SSMMutagenicPrimer(mutation_result.fw_primer,
                                              mutation_result.fw_size,
                                              mutation_result.fw_temp))

        all_primers.append(SSMMutagenicPrimer(mutation_result.rw_primer,
                                              mutation_result.rw_size,
                                              mutation_result.rw_temp))

    sequence, offset = create_output_sequence(solver.sequence,
                                              solver.goi_range,
                                              all_primers)

    new_sequence_start = solver.goi_range[0] - offset
    non_optimalities = result.primer_non_optimalities()

    mutation_outputs = [create_mutation_output(input_data.config,
                                               primer_pair,
                                               non_optimality,
                                               degenerate_codon,
                                               new_sequence_start,
                                               result)
                        for primer_pair, non_optimality in zip(result.result, non_optimalities)]

    return SSMOutput(
        input_data=input_data,
        results=mutation_outputs,
        full_sequence=sequence,
        goi_offset=offset,
        new_sequence_start=new_sequence_start,
        forward_flanking_primer_temperature=solver.forward_primer_temp,
        reverse_flanking_primer_temperature=solver.reverse_primer_temp,

        min_forward_temperature=result.forward_temp_range.min,
        opt_forward_temperature=result.forward_temp_range.opt,
        max_forward_temperature=result.forward_temp_range.max,

        min_reverse_temperature=result.reverse_temp_range.min,
        opt_reverse_temperature=result.reverse_temp_range.opt,
        max_reverse_temperature=result.reverse_temp_range.max,

        min_overlap_temperature=result.overlap_temp_range.min,
        opt_overlap_temperature=result.overlap_temp_range.opt,
        max_overlap_temperature=result.overlap_temp_range.max
    )


def create_mutation_output(config: SSMConfig, primer_pair: SSMPrimerPair, non_optimality: float,
                           degenerate_codon: str, new_sequence_start, result):
    fw_primer = SSMMutagenicPrimer(primer_pair.fw_primer, primer_pair.fw_size, primer_pair.fw_temp)
    rw_primer = SSMMutagenicPrimer(primer_pair.rw_primer, primer_pair.rw_size, primer_pair.rw_temp)

    fw_in_range = fw_primer.check_in_range(config, result)
    rw_in_range = rw_primer.check_in_range(config, result)

    overlap_in_range = bool(result.overlap_temp_range.min <= primer_pair.overlap_temp <= result.overlap_temp_range.max)

    pair_in_range = fw_in_range and rw_in_range and overlap_in_range

    return SSMMutationOutput(
        mutation=primer_pair.mutation.original_string,
        result_found=True,
        parameters_in_range=pair_in_range,
        non_optimality=round(non_optimality),

        forward_primer=create_primer_output(config,
                                            fw_primer,
                                            primer_pair.mutation,
                                            degenerate_codon,
                                            new_sequence_start,
                                            fw_in_range),
        reverse_primer=create_primer_output(config,
                                            rw_primer,
                                            primer_pair.mutation,
                                            degenerate_codon,
                                            new_sequence_start,
                                            rw_in_range),
        overlap=create_overlap_output(primer_pair))


def create_primer_output(config: SSMConfig, mutagenic_primer, mutation,
                         degenerate_codon: str, new_sequence_start,
                         parameters_in_range: bool):
    # The actual degenerate outputs for the export are created on the frontend. This is simply for the resulting
    # table, which can only show one primer at a time.
    first_degenerate_codon = degenerate_codon.split(",")[0]

    mutated = mutagenic_primer.primer.get_mutated_sequence(mutation.position, first_degenerate_codon)
    direction = mutagenic_primer.primer.direction
    primer = mutagenic_primer.primer

    if mutagenic_primer.primer.direction == Primer.FORWARD:
        sequence = mutated
    elif mutagenic_primer.primer.direction == Primer.REVERSE:
        sequence = Seq.reverse_complement(mutated)
    else:
        raise NotImplemented()

    return PrimerOutput(
        direction=direction,
        sequence=sequence,
        normal_order_sequence=mutated,
        normal_order_start=primer.get_normal_start() - new_sequence_start,
        start=primer.start - new_sequence_start,
        length=primer.length,
        three_end_temperature=mutagenic_primer.three_end_temperature,
        gc_content=mutagenic_primer.primer.get_gc_content(),
        parameters_in_range=parameters_in_range
    )


def create_overlap_output(primer_pair):
    return OverlapOutput(length=primer_pair.overlap_size, temperature=primer_pair.overlap_temp)
