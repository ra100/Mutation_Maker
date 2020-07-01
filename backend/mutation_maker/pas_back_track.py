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

"""
File containing pas back-tracking solution
the goal of back-tracking algorithm is to create longest possible fragments
"""
import sys
import time
from typing import Dict, Optional, Tuple, List

from mutation_maker.basic_types import Offset
from mutation_maker.pas_solution import PASSolution, PASFragment, PASProtoFragment, compute_solution_score, pas_fragment_score
from mutation_maker.pas_types import PASConfig
from primer3 import calcHairpin, calcHomodimer


class PASOptimizer:
    """
    Contains functions for creating an optimized split into DNA fragments for the PAS workflow.
    Based on backtracking and dynamic programming.
    """

    def __init__(self, proto_fragments: List[PASProtoFragment], init_solution: PASSolution, timeout=None):
        """
        :param proto_fragments:
        :param init_solution:
        """
        # proto fragments which can be used for creating the solution
        self.proto_fragments = sorted(proto_fragments, key=lambda p: p.first_mutation_offset)
        # An initial partial solution with fragments covering an initial segment
        # of the GOI, or with no fragments.
        self.init_solution = init_solution
        self.gene: str = self.init_solution.gene.sequence
        self.gene_length = len(self.gene)

        # PAS config shortcut
        self.config: PASConfig = init_solution.config

        # Stored intermediate results
        self.best_solution: Optional[PASSolution] = None  # The best solution found so far.
        self.best_solution_score: Optional[float] = None  # The best solution score. Lower is better.
        # Best scores for partial solutions covering the gene up to an offset
        # and having even or odd number of fragments. 'True' means 'even' here (tuned for performance).
        self.best_partial_score: Dict[Tuple[int, bool], float] = {}

        # Possible fragment lengths ordered by distance from the optimal length
        self.fragment_lengths_ordered = \
            sorted(list(range(self.config.min_oligo_size, self.config.max_oligo_size + 1)),
                   key=lambda x: abs(x - self.config.opt_oligo_size))

        # Create a map for hairpins and homodimers on the gene
        self.self_binding_ranges: List[Tuple[int, int, float]] = self._find_self_binding_ranges()  # a list of (from_offset, to_offset, Tm)

        # Convert the found self-binding ranges to a Pandas DataFrame
        # self.self_binding = pd.DataFrame(data=self_binding_ranges, columns=['from', 'to'])
        # self.self_binding.set_index('from')
        # self.self_binding.set_index('to')

       # Timeout setup
        if timeout is not None:
            self.timeout = timeout
        else:
            self.timeout = sys.maxsize

        self.start_time = None
        self.timed_out = False

    def optimize(self):
        """
        Run an optimization algorithm.
        :return: Optimal solution, or None if none was found.
        """
        # Run the optimization algorithm from scratch
        self.best_solution = None
        self.best_solution_score = float('inf')
        self.best_partial_score = {}

        self.timed_out = False
        self.start_time = time.time()
        self._find_best_fragments(self.init_solution.fragments, 0, self.proto_fragments)

    def get_optimal_solution(self) -> Optional[Tuple[PASSolution, float]]:
        """
        Returns the optimal solution and its score, or None.
        """
        if self.best_solution is None:
            return None
        else:
            return self.best_solution, self.best_solution_score

    def _find_self_binding_ranges(self) -> List[Tuple[int, int, float]]:
        """
        Find segments of the gene which can form a hairpin or homodimer for given Tm.
        :return: A list of triples (from_offset, to_offset, Tm), each representing a start/end and mel;ting temperature for
        a hairpin or homodimer region.
        """
        hairpin_lengths = [5, 10]  # Lengths of DNA segments evaluated for possible hairpins
        homodimer_lengths = [25, 50]
        homodimer_offset_step = 10  # step, in bp, for the start for potential homodimers tested

        monovalent_conc = self.config.temperature_config.k
        divalent_conc = self.config.temperature_config.mg
        dntp_conc = self.config.temperature_config.dntp

        hairpin_segments = []
        for length in hairpin_lengths:
            for start in range(0, self.gene_length - length):
                end = start + length - 1
                thermo_result = calcHairpin(self.gene[start:end], monovalent_conc, divalent_conc, dntp_conc)
                if self._is_new_hairpin_or_homodimer(start, end, thermo_result, hairpin_segments):
                    hairpin_segments.append((start, end, thermo_result.tm))

        homodimer_segments = []
        for length in homodimer_lengths:
            for start in range(0, self.gene_length - length, homodimer_offset_step):
                end = start + length - 1
                thermo_result = calcHomodimer(self.gene[start:end], monovalent_conc, divalent_conc, dntp_conc)
                if thermo_result.structure_found:
                    if self._is_new_hairpin_or_homodimer(start, end, thermo_result, hairpin_segments):
                        homodimer_segments.append((start, end, thermo_result.tm))

        return hairpin_segments + homodimer_segments

    def _is_new_hairpin_or_homodimer(self, start, end, thermo_result, segments):
        """
        Does (start, end) represent a region forming a hairpin/homodimer, which is not already covered in the 'segments' list?
        """
        if thermo_result.structure_found:
            if thermo_result.tm > self.init_solution.tm - self.config.safe_temp_difference:
                return len([s for s in segments if s[0] >= start and s[1] <= end]) == 0
        else:
            return False

    def _find_best_fragments(self, partial_solution: List[PASFragment], avg_fragment_score: float, proto_fragments: List[PASProtoFragment]):
        """
        An internal optimization procedure. Updates self.best_solution and self.best_solution_score with a better
        solution, if it finds any. Uses self.best_partial_score for storing intermediate results.
        :param partial_solution: A partial solution of the PAS problem given by fragments covering a continuous segment
        starting at the beginning of the GOI.
        :param avg_fragment_score: An average fragment score for the partial solution
        :param proto_fragments: Proto fragments from which the rest of a PAS solution can be generated.
        """
        # Debug trace
        # if len(partial_solution) == 2:
        #     print(partial_solution)

        # Timeout
        if time.time() - self.start_time > self.timeout:
            self.timed_out = True
            return

        if not self._record_if_best(partial_solution, avg_fragment_score):
            return  # we already have a better partial solution of this length and parity

        if self._accept(partial_solution):
            return  # we have found a new best complete solution

        if partial_solution and partial_solution[-1].end + 1 == self.gene_length:
            return  # we have a solution covering the whole gene, which is however not the best, or has odd number of fragments

        # Create a fragment which connects to the last fragment of the current partial solution which is closest to the optimal fragment length
        new_fragment, remaining_proto_fragments = self._optimal_length_fragment(partial_solution, proto_fragments)
        while new_fragment is not None:
            # Explore partial solutions which have the fragment added to the current fragments.
            extended_solution = partial_solution + [new_fragment]

            # Compute the new average score
            new_score = (avg_fragment_score * len(partial_solution) +
                         pas_fragment_score(new_fragment.start, new_fragment.end,
                                            self.config.opt_oligo_size, self.self_binding_ranges,
                                            self.config.length_weight, self.config.hairpin_homodimer_weight,
                                            self.init_solution.tm, self.config.safe_temp_difference)) \
                / len(extended_solution)

            self._find_best_fragments(extended_solution, new_score, remaining_proto_fragments)

            if self.timed_out:
                return  # we are out of time
            # Get the next shorter fragment
            new_fragment, remaining_proto_fragments = self._next_fragment(new_fragment, proto_fragments)

    def _optimal_length_fragment(self, partial_solution: List[PASFragment], proto_fragments: [PASProtoFragment]) -> Tuple[Optional[PASFragment], List[PASProtoFragment]]:
        """
        Find a fragment linked to the last fragment of the partial solution, which satisfies fragment size constraints and does not break constraints
        for proto-fragments from the proto_fragments list. If the solution does not contain any fragments, then the function construct an initial fragment.
        The function tries fragment lengths in the order given by self.fragment_lengths_ordered.
        :param partial_solution: A list of fragments covering an initial portion of the gene
        :param proto_fragments: Sorted list of valid proto-fragment
        :return: The resulting fragment and a list of input proto-fragments which were not consumed by the new fragment, or None.
        """
        # Find the offset of the new fragment
        if not partial_solution:
            start = 0
        else:
            start = self._get_last_overlap_offset(partial_solution)
            if start is None:
                return None, proto_fragments

        length_idx = self._find_first_valid_fragment_length_idx(start, 0, proto_fragments)
        if length_idx is None:
            return None, proto_fragments

        end = start + self.fragment_lengths_ordered[length_idx] - 1

        # Convert encapsulated proto-fragment into the new fragment, and return also the remaining proto-fragment list
        return self._consume_proto_fragments(start, end, proto_fragments)

    def _next_fragment(self, previous_fragment: PASFragment, proto_fragments: [PASProtoFragment]) -> Tuple[Optional[PASFragment], List[PASProtoFragment]]:
        """
        Finds the next length for a fragment, taken from self.fragment_lengths_ordered, which does not cause the
        resulting fragment to break into the mutation region of some proto-fragment.
        The fragment starts at the same offset as 'previous_fragment'.
        """
        start = previous_fragment.get_start()
        previous_length_idx = self.fragment_lengths_ordered.index(previous_fragment.length)
        if previous_length_idx == len(self.fragment_lengths_ordered):
            return None, proto_fragments  # we have tried all possible lengths

        length_idx = self._find_first_valid_fragment_length_idx(start, previous_length_idx + 1, proto_fragments)
        if length_idx is None:
            return None, proto_fragments

        end = start + self.fragment_lengths_ordered[length_idx] - 1

        # Convert encapsulated proto-fragment into the new fragment, and return also the remaining proto-fragment list
        return self._consume_proto_fragments(start, end, proto_fragments)

    def _find_first_valid_fragment_length_idx(self, start, init_length_idx, proto_fragments) -> Optional[int]:
        """
        Finds the first fragment length from self.fragment_lengths_ordered[init_length_idx:] which does lead to a fragment
        ending between the first mutation and the minimal end of some proto-fragment.
        :param start:
        :param init_length_idx:
        :return: The index of the length of the fragment in self.fragment_lengths_ordered[init_length_idx:].
        """
        fragment_length_idx = init_length_idx
        # loop over possible fragment lengths
        while fragment_length_idx < len(self.fragment_lengths_ordered):
            end = start + self.fragment_lengths_ordered[fragment_length_idx] - 1
            if end < len(self.init_solution.gene.sequence):  # the fragment fits into the gene
                last_included_proto_fragment_idx = None

                # Find the last included proto-fragment
                for (i, p) in enumerate(proto_fragments):
                    if p.get_constraints().min_end <= end:
                        last_included_proto_fragment_idx = i
                    else:
                        break

                # Check whether the fragment ends before the first mutation of the next proto-fragment
                if last_included_proto_fragment_idx is not None and last_included_proto_fragment_idx == len(proto_fragments) - 1 \
                        or not proto_fragments:  # there is no next proto-fragment
                    return fragment_length_idx

                if last_included_proto_fragment_idx is None:
                    next_proto_fragment_idx = 0
                else:
                    next_proto_fragment_idx = last_included_proto_fragment_idx + 1

                if start + self.fragment_lengths_ordered[fragment_length_idx] < \
                        proto_fragments[next_proto_fragment_idx].get_first_mut_site_position():
                    return fragment_length_idx  # the fragment does not intrude the next proto-fragment

            fragment_length_idx += 1   # let's try another fragment length

        return None  # No fragment length from self.fragment_lengths_ordered[init_length_idx:] is suitable

    @staticmethod
    def _consume_proto_fragments(start, end, proto_fragments) -> Tuple[PASFragment, List[PASProtoFragment]]:
        # Create a fragment with a given start and end from proto-fragments encapsulated by this interval.
        # Return this new fragment, and proto-fragments from 'proto-fragments', which are not included in the fragment.

        # Select included mutation sites and proto-fragments which won't be included
        included_mut_sites: List[Offset] = []
        remaining_proto_fragments = []

        for p in proto_fragments:
            if p.get_constraints().min_end <= end:
                included_mut_sites.extend(p.get_sites())
            else:
                remaining_proto_fragments.append(p)

        return PASFragment(included_mut_sites, start, end - start + 1), remaining_proto_fragments

    def _record_if_best(self, partial_solution: List[PASFragment], score: float) -> bool:
        """
        Check, whether a partial solution has a chance to be completed to an eligible solution with the best score.
        If so, then record its score as the best for the given length and parity of the number of fragments, and return True.
        The solution must start at 0. Continuity of the solution fragments is not checked.
        If the last fragment ends at the last nucleotide, then it always returns True.
        :param partial_solution: A partial solution covering an initial part of the GOI.
        """
        if partial_solution:
            start = partial_solution[0].start
        else:
            return True  # nothing to do for an empty solution

        if start > 0:
            return False  # Fragments don't cover beginning of the gene

        length = partial_solution[-1].end - start + 1
        if length == self.gene_length:
            return True  # we should not compare complete solutions with a partial metric
                         # (see the call of the average_fragment_score() function below)

        parity = len(partial_solution) % 2 == 0
        best_so_far = self.best_partial_score.get((length, parity))
        if best_so_far is None or score < best_so_far:
            self.best_partial_score[(length, parity)] = score
            return True
        else:
            return False

    def _accept(self, partial_solution: List[PASFragment]) -> bool:
        """
        Check whether the solution is complete and has the best score so far.
        If so, then record it.
        :param partial_solution:
        :return:
        """
        # check if solution is complete
        if partial_solution and len(partial_solution) % 2 == 0 and partial_solution[-1].get_end() + 1 == self.gene_length:
            complete_solution = PASSolution(self.init_solution.gene, self.init_solution.config, self.init_solution.tm,
                                            partial_solution, self.self_binding_ranges)
            complete_solution.mark_as_complete()
            score = compute_solution_score(complete_solution)
            if score < self.best_solution_score:
                self.best_solution_score = score
                self.best_solution = complete_solution
                return True
        return False

    def _get_last_overlap_offset(self, partial_solution: List[PASFragment]) -> Optional[int]:
        """
        Returns the offset of the overlap at the end of the last fragment of a partial solution, or None.
        :return:
        """
        if partial_solution is None:
            return None

        last_bp_offset = partial_solution[-1].get_end()
        last_fragment_mutations = partial_solution[-1].get_mutation_sites()
        if last_fragment_mutations:
            min_overlap_offset = max(last_fragment_mutations) + 3
        else:
            if len(partial_solution) > 1:
                min_overlap_offset = partial_solution[-2].get_end() + 1
            else:
                min_overlap_offset = 0

        min_overlap_offset = max(min_overlap_offset, last_bp_offset - self.init_solution.config.max_overlap_length)
        max_overlap_offset = last_bp_offset - self.init_solution.config.min_overlap_length

        # Find the shortest overlap with Tm > self.tm
        overlap_offset = max_overlap_offset
        while self.init_solution.temp_calculator(self.init_solution.gene.sequence[overlap_offset:last_bp_offset]) <= self.init_solution.tm \
                and overlap_offset >= min_overlap_offset:
            overlap_offset -= 1

        if overlap_offset >= min_overlap_offset \
                and self.init_solution.temp_calculator(self.init_solution.gene.sequence[overlap_offset:last_bp_offset]) <= self.init_solution.config.temp_range_size + self.init_solution.tm:
            return overlap_offset
        else:
            return None
