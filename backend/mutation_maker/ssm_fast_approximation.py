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
from typing import List, Tuple


from mutation_maker.mutation import AminoMutation
from mutation_maker.ssm_types import SSMGrownSolution, SSMPrimerSpec, SSMConfig, SSMFlankingSequences
from mutation_maker.temperature_calculator import TemperatureCalculator, PrimerDimerCalculator


def find_best_overlaps(sequence: str, min_five_end_size: int, min_overlap_size: int, max_overlap_size: int,
                       mutations: List[AminoMutation], overlap_temp: float,
                       temp_calculator: TemperatureCalculator, half_temp_range: float) \
        -> List[SSMPrimerSpec]:
    """
    Takes a list of mutations and a target overlap temperature and finds one overlap at each site
    such that they are all close to the given overlap temperature.
    """
    results: List[SSMPrimerSpec] = []

    overlap_sizes = range(min_overlap_size, max_overlap_size - 1)

    for mutation in mutations:
        best_offset = None
        best_length = None
        best_tm = None

        for length in overlap_sizes:
            for offset in range((mutation.position + mutation.length) - length, mutation.position - 1):
                right_padding = (offset + length) <= (mutation.position + mutation.length + min_five_end_size)
                left_padding = (offset + min_five_end_size) >= mutation.position

                if right_padding or left_padding:
                    continue

                overlap = sequence[offset:(offset + length)]
                tm = temp_calculator(overlap)

                if (best_tm is None) or (tm < best_tm):
                    best_offset = offset
                    best_length = length
                    best_tm = tm

                if abs(best_tm - overlap_temp) < half_temp_range:
                    break

        if best_offset is None:
            raise RuntimeError("Primer parameters are too restrictive and resulted in no possible overlap." +
                               "Consider lowering min 5' size.")

        results.append(SSMPrimerSpec(best_offset, best_length, 0, best_tm))

    return results


def grow_forward_primer(max_primer_size: int, min_three_end_size: int, sequence: str, mutation: AminoMutation,
                        overlap: SSMPrimerSpec, temp_threshold: float,
                        temp_calculator: TemperatureCalculator) -> SSMPrimerSpec:
    """
    Grows a forward primer from a given overlap, and returns the shortest primer which has
    3' Tm above the temperature threshold. The 3' is defined by the given mutation.
    """
    for length in range(overlap.length + 1, max_primer_size):
        mutation_end = mutation.position + mutation.length
        fw_three_end_size = (overlap.offset + length) - mutation_end
        fw_three_end_sequence = sequence[mutation_end:(mutation_end + fw_three_end_size)]
        fw_three_end_temp = temp_calculator(fw_three_end_sequence)

        if fw_three_end_temp > temp_threshold and fw_three_end_size >= min_three_end_size:
            break

    return SSMPrimerSpec(overlap.offset, length, fw_three_end_size, fw_three_end_temp)


def grow_reverse_primer(max_primer_size: int, min_three_end_size: int, sequence: str, mutation: AminoMutation,
                        overlap: SSMPrimerSpec, temp_threshold: float,
                        temp_calculator: TemperatureCalculator) -> SSMPrimerSpec:
    """
    Grows a reverse primer from a given overlap, and returns the shortest primer which has
    3' Tm above the temperature threshold. The 3' is defined by the given mutation.
    """
    overlap_end = overlap.offset + overlap.length
    min_offset = max(0, overlap_end - max_primer_size)

    for offset in reversed(range(min_offset, overlap.offset)):
        rw_three_end_sequence = sequence[offset:mutation.position]
        rw_three_end_temp = temp_calculator(rw_three_end_sequence)

        if rw_three_end_temp > temp_threshold and len(rw_three_end_sequence) >= min_three_end_size:
            break

    return SSMPrimerSpec(offset, overlap_end - offset, mutation.position - offset, rw_three_end_temp)


def grow_primers(max_primer_size: int, min_three_end_size: int, sequence: str, mutations: List[AminoMutation],
                 overlaps: List[SSMPrimerSpec], fw_temp_threshold: float, rw_temp_threshold: float,
                 temp_calculator: TemperatureCalculator) \
        -> Tuple[List[SSMPrimerSpec], List[SSMPrimerSpec]]:
    """
    Takes a list of overlaps and temp thresholds and returns grown primers which are just above the overlap,
    both forward and reverse.
    """
    fw_primers: List[SSMPrimerSpec] = []
    rw_primers: List[SSMPrimerSpec] = []

    for mutation, overlap in zip(mutations, overlaps):
        fw_primers.append(grow_forward_primer(max_primer_size, min_three_end_size, sequence, mutation,
                                              overlap, fw_temp_threshold, temp_calculator))
        rw_primers.append(grow_reverse_primer(max_primer_size, min_three_end_size, sequence, mutation,
                                              overlap, rw_temp_threshold, temp_calculator))

    return fw_primers, rw_primers


def compute_heterodimer_err(fw_sequence: str, rw_sequence: str,
                            solution: SSMGrownSolution, flanks: SSMFlankingSequences,
                            pd_calc: PrimerDimerCalculator):
    """
    Computes error of hetrodimer temperature for forward and reverse primers
    :param fw_sequence: forward primer sequence
    :param rw_sequence:  reverse primer sequence
    :param solution: current solution -> needed for solution temperature
    :param flanks: flanking primers
    :param pd_calc: primer dimer calculator
    :return:
    """

    if flanks.forward_flank is None or flanks.reverse_flank is None:
        return 0

    return (pd_calc.heterodimer(fw_sequence, flanks.reverse_flank) - solution.fw_temp) ** 2 + \
           (pd_calc.heterodimer(rw_sequence, flanks.forward_flank) - solution.rw_temp) ** 2


def calc_GC_content(sequence):
    """
    Calculates percentage occurrence of G and C in sequence
    :param sequence: string sequence
    :return:
    """
    return (sequence.upper().count('G') + sequence.upper().count('G')) / len(sequence) * 100


def get_GC_overflow(sequence, min_gc, max_gc):
    """
    Function returns how much is GC content outside of desired boundaries
    :param sequence:
    :param min_gc:
    :param max_gc:
    :return:
    """
    percentage = calc_GC_content(sequence)
    return max(0, min_gc-percentage) + max(0, percentage-max_gc)


def compute_grown_solution_score(config: SSMConfig, sequence: str, solution: SSMGrownSolution,
                                 flanks: SSMFlankingSequences, pd_calc: PrimerDimerCalculator) -> \
        List[float]:
    """
    Calculates the scores for a given grown solution.
    """
    scores = []
    min_primer_size = config.min_primer_size
    max_temp_range = config.three_end_temp_range / 2

    for fw, rw, overlap in zip(solution.fw_primers, solution.rw_primers, solution.overlaps):
        fw_sequence = sequence[fw.offset:(fw.offset + fw.length)]
        rw_sequence = sequence[rw.offset:(rw.offset + rw.length)]

        fw_temp_err = abs(fw.three_end_temp - solution.fw_temp)
        fw_temp_err = 0 if fw_temp_err < max_temp_range else fw_temp_err ** 2
        rw_temp_err = abs(rw.three_end_temp - solution.rw_temp)
        rw_temp_err = 0 if rw_temp_err < max_temp_range else rw_temp_err ** 2
        overlap_temp_err = abs(overlap.three_end_temp - solution.overlap_temp)
        overlap_temp_err = 0 if overlap_temp_err < max_temp_range else overlap_temp_err**2

        fw_size_err = (fw.length - min_primer_size) ** 2
        rw_size_err = (rw.length - min_primer_size) ** 2

        # compute how much we are
        gc_overflow_err = get_GC_overflow(fw_sequence, config.min_gc_content, config.max_gc_content)**2
        gc_overflow_err += get_GC_overflow(rw_sequence, config.min_gc_content, config.max_gc_content)**2

        score = math.sqrt(
                config.three_end_temp_weight * fw_temp_err +
                config.three_end_temp_weight * rw_temp_err +
                config.overlap_temp_weight * overlap_temp_err +
                config.three_end_size_weight * fw_size_err +
                config.three_end_size_weight * rw_size_err +
                config.gc_content_weight * gc_overflow_err
        )

        if config.compute_hairpin_homodimer:

            fw_hairpin_err = (solution.fw_temp - pd_calc.hairpin(fw_sequence)) ** 2
            rw_hairpin_err = (solution.rw_temp - pd_calc.hairpin(rw_sequence)) ** 2

            fw_homodimer_err = (solution.fw_temp - pd_calc.homodimer(fw_sequence)) ** 2
            rw_homodimer_err = (solution.rw_temp - pd_calc.homodimer(rw_sequence)) ** 2

            heterodimer_err = compute_heterodimer_err(fw_sequence, rw_sequence,
                                                      solution, flanks, pd_calc)
            # we need to do square root here because we want to keep consistent score computation to
            # primer3 workflow in ssm.py at line 530 -> we cannot do it together therefore we separate it here too
            score += math.sqrt(
                    config.hairpin_temperature_weight * fw_hairpin_err +
                    config.hairpin_temperature_weight * rw_hairpin_err +
                    config.primer_dimer_temperature_weight * fw_homodimer_err +
                    config.primer_dimer_temperature_weight * rw_homodimer_err +
                    config.primer_dimer_temperature_weight * heterodimer_err
            )

        scores.append(score)
    return scores


def pick_best_grown_solution(config: SSMConfig, sequence: str, solutions: List[SSMGrownSolution],
                             flanks: SSMFlankingSequences) -> SSMGrownSolution:
    best_solution = solutions[0]
    # we create calculator here because it contains cache of precomputed temperatures
    pd_calc = PrimerDimerCalculator(config.temperature_config.k,
                                    config.temperature_config.mg,
                                    config.temperature_config.dntp,
                                    cached=True)
    best_score = sum(compute_grown_solution_score(config, sequence, best_solution, flanks, pd_calc))

    for current_solution in solutions:
        current_score = sum(compute_grown_solution_score(config, sequence, current_solution, flanks, pd_calc))

        if current_score < best_score:
            best_solution = current_solution
            best_score = current_score

    return best_solution
