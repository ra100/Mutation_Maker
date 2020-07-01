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

from math import sqrt
from typing import List, Set, Tuple, Optional
from dataclasses import dataclass
from mutation_maker.basic_types import Offset, DNASequenceForMutagenesis
from mutation_maker.pas_types import PASConfig, PASMutationSite
from Bio.SeqUtils import GC


@dataclass
class FragmentConstraints:
    """
    Minimum and maximum positions for start/end of a fragment. In bp, zero based.
    The end of the fragment is defined as the index of the first bp after the fragment, so that the fragment occupies
    positions start, start+1, ..., end-1.
    """
    min_start: int
    max_start: int
    min_end: int
    max_end: int

    def __hash__(self):
        return hash(str(self.min_start) + str(self.max_start) + str(self.min_end) + str(self.max_end))

    def __eq__(self, other):
        return self.min_start == other.min_start and self.max_start == other.max_start and \
            self.min_end == other.min_end and self.max_end == other.max_end


class FragmentConstraintError(Exception):
    """Exception raised when there is no way how we can construct a DNA fragment given its mutation sites.

    Attributes:
        fragment_mutations -- positions of mutations which were supposed to be on the fragment, in bp, zero based.
        message -- explanation of the error
    """

    def __init__(self, fragment_mutations: Set[Offset], message):
        self.fragment_mutations = fragment_mutations
        self.message = message


def fragment_constraints(fragment_mutations: Set[Offset], gene: DNASequenceForMutagenesis, config: PASConfig, t_min) \
        -> Tuple[bool, FragmentConstraints]:
    """
    Computes constraints for a fragment containing
    :param fragment_mutations: Offsets for mutations which belong to the fragment
    :param gene:
    :param config:
    :param t_min: The minimum melting temperature for fragment overlaps
    :return: A tuple, with the first component indicating whether it's possible to construct a fragment
    with given constraints.
    The function raises exception FragmentConstraintError when it is not possible to satisfy the constraints regardless
    of the minimum melting temperature.
    """
    mut_start = min(fragment_mutations)
    # including start excluding end
    mut_end = max(fragment_mutations) + 3

    # Limit the fragment start/end based on the minimum overlap and positions of other mutations
    all_mutations = sorted(gene.mutation_sites)
    prev_mutations = [m for m in all_mutations if m < mut_start]
    if prev_mutations:
        previous_mutation_end = prev_mutations[-1] + 3
    else:
        previous_mutation_end = 0
    next_mutations = [m for m in all_mutations if m >= mut_end]
    if next_mutations:
        next_mutation_start = next_mutations[0]
    else:
        next_mutation_start = len(gene.sequence)

    max_start = mut_start - config.min_overlap_length
    min_end = mut_end + config.min_overlap_length
    min_start = max(previous_mutation_end, min_end - config.max_oligo_size)
    max_end = min(next_mutation_start, max_start + config.max_oligo_size)

    # If it's not possible to construct a fragment because of overlap size constraints, raise an exception.
    if min_end - max_start > config.max_oligo_size or max_start < 0 or min_end > len(gene.sequence) \
            or min_start > max_start or min_end > max_end:
        raise FragmentConstraintError(fragment_mutations,
                                      "fragment_constraints(): Unable to satisfy size constraints for a fragment")

    # Extend the fragment sequence in the direction to the start of the gene, until the overlap reaches Tmin
    calculator = config.temperature_config.create_calculator()
    while calculator(gene.sequence[max_start:mut_start]) < t_min:
        max_start -= 1
        if max_start < min_start:
            return False, FragmentConstraints(min_start, max_start, min_end, max_end)

    # The same for the overlap after the fragment
    while calculator(gene.sequence[mut_end:min_end]) < t_min:
        min_end += 1
        if min_end > max_end:
            return False, FragmentConstraints(min_start, max_start, min_end, max_end)

    return True, FragmentConstraints(min_start, max_start, min_end, max_end)


class PASProtoFragment:
    """ Stores info about a consecutive sequence of mutation sites which can be placed on a single fragment.
    """
    def __init__(self, sites: List[Offset], constraints: FragmentConstraints = None):
        """

        :param sites: offsets of mutation sites which belong to the proto-fragment.
        :param constraints: Constraints for the fragment limits
        """
        self.sites = sorted(sites)  # sorted by position
        self.constraints = constraints
        self.first_mutation_offset = min(sites)  # useful for sorting

    def get_constraints(self) -> FragmentConstraints:
        return self.constraints

    def add_site(self, new_site: PASMutationSite):
        self.sites.append(new_site)

    def get_last_mut_site_position(self):
        # This method should not be called on fragment with empty mutations
        if self.sites:
            return max(self.sites)
        return -1

    def get_first_mut_site_position(self):
        # This method should not be called on fragment with empty mutations
        if self.sites:
            return min(self.sites)
        return -1

    def init_constraints(self, gene: DNASequenceForMutagenesis, config: PASConfig, tm) -> bool:

        ret, self.constraints = fragment_constraints(set(self.sites), gene, config, tm)
        return ret

    def get_sites(self):
        return self.sites

    def position_satisfies_constraints(self, position):
        """
        Position can be either start or end of fragment.
        Basically we cannot have start or end between max start and min end
        :param position:
        :return:
        """
        return not self.constraints.max_start < position < self.constraints.min_end

    def possible_overlap(self, position):
        return self.constraints.min_start <= position <= self.constraints.max_start

    def is_ready(self, start, end):
        return self.constraints.min_start <= start <= self.constraints.max_start and \
               self.constraints.min_end <= end <= self.constraints.max_end

    def mergeable(self, other, max_size):
        if self != other:
            return other.constraints.min_end - self.constraints.max_start <= max_size
        return False


class PASFragment:
    """
    A DNA fragment which is a result of splitting a gene for the PAS workflow.
    """

    def __init__(self, sites: List[Offset], start, length):
        self.sites = sites
        self.start: Offset = start
        self.length = length
        self.end = self.start + self.length - 1
        self.score = None  # Here you can cache the fragment score during optimization

    def get_mutation_sites(self) -> List[Offset]:
        """
        Returns mutation sites on the fragments
        :return:
        """
        return self.sites if self.sites is not None else []

    def get_start(self) -> Offset:
        """ Returns the offset of the first nucleotide in bp """
        return self.start

    def get_length(self) -> int:
        """ Returns fragment length in bp """
        return self.length

    def get_end(self):
        return self.end

    def get_sequence(self, gene):
        return gene[self.start:self.get_end()]

    def put_score(self, score: float):
        self.score = score

    def get_score(self) -> Optional[float]:
        return self.score

    def get_overlap_seq(self, other, gene):
        """
        Returns overlap sequence between two fragments.
        :param other: other fragment
        :param gene: gene sequence -> we need it because fragments store only starting and ending position in the full
        gene sequence (gene sequence = five_end flanking sequence + gene of interest + three end flanking sequence)
        :return:
        """
        if self.get_length() == 0:
            return ""

        if other.get_start() > self.get_start():
            return gene[other.get_start(): self.get_end()]
        else:
            return gene[self.get_start(): other.get_end()]

    def __str__(self):
        return "PAS Fragment from {} to {} with length {} and mutations {}".format(
            self.get_start(), self.get_end(), self.length, self.get_mutation_sites())

    __repr__ = __str__


class PASSolution:
    """
    A (partial) PAS workflow solution, as described in the algorithm for Problem #1 in Gene synthesis workflow.
    """
    def __init__(self, gene: DNASequenceForMutagenesis, config: PASConfig, t_min: float, fragments: List[PASFragment],
                 self_binding_ranges: List[Tuple[int, int, float]] = None):
        self.gene = gene
        self.config = config
        self.tm = t_min  # min. melting temperature required fragment overlaps

        # fragments sorted by the start index
        self.fragments = sorted(fragments, key=lambda f: f.start)
        if self.fragments:
            self.start = self.fragments[0].get_start()  # the start position of the first fragment in bp
            self.end = self.fragments[-1].get_end()  # the end position of the last fragment in bp
        else:
            self.start = None
            self.end = None

        self.is_complete = False  # Does the solution cover the whole gene?
        self.temp_calculator = config.temperature_config.create_calculator()

        # A list of self-binding DNA regions with their Tm, used to create the solution
        self.self_binding_ranges = self_binding_ranges

    def add_fragment(self, fragment: PASFragment):
        self.fragments.append(fragment)
        self.fragments = sorted(self.fragments, key=lambda f: f.start)
        self.start = self.fragments[0].get_start()
        self.end = self.fragments[-1].get_end()
        if self.get_length() == len(self.gene.sequence):
            self.mark_as_complete()

    def get_first_fragment(self) -> Optional[PASFragment]:
        if self.fragments:
            return self.fragments[0]
        else:
            return None

    def get_last_fragment(self) -> Optional[PASFragment]:
        if self.fragments:
            return self.fragments[-1]
        else:
            return None

    def get_start(self) -> Optional[Offset]:
        """ Returns the start position of the first fragment in bp, zero-based """
        if self.fragments:
            return self.fragments[0].get_start()
        else:
            return None

    def get_end(self) -> Optional[Offset]:
        """ Returns the end position of the last fragment in bp, zero-based """
        if self.fragments:
            return self.fragments[-1].get_end()
        else:
            return None

    def get_length(self) -> Optional[int]:
        """ Returns the difference between the end of the last fragment and the start of the first fragment +1 in bp.
            Returns 0 if the solution does not contain any fragments.
        """
        if self.fragments:
            # last_fragment = max(self.fragments, key=lambda f: f.start)
            # return last_fragment.get_start() + last_fragment.get_length() - self.get_start()
            return self.get_end() - self.get_start() + 1
        else:
            return 0

    def mark_as_complete(self):
        """ Indicate that the solution covers the whole gene """
        self.is_complete = True

    def is_acceptable(self):
        # TODO: check constraints
        """
        Checks if current PASSolution spans whole gene that we wanted to fragment
        and if we have even number of fragments
        :return:
        """
        return self.is_complete and len(self.fragments) % 2 == 0

    def get_fragments(self) -> List[PASFragment]:
        """
        Returns fragments sorted w.r.t. the start index.
        :return:
        """
        return self.fragments

    def is_empty(self):
        """
        Check if solution is empty
        :return:
        """
        return len(self.fragments) == 0


######################################################################################################################
#                                           SCORING FUNCTIONS
######################################################################################################################

def pas_fragment_score(fragment_start, fragment_end, opt_len: int, self_binding_ranges: List[Tuple[int, int, float]],
                       len_w, self_bind_w, tm: float, safe_temp_difference) -> float:
    """
    A low-level procedure for computing score for a single PAS fragment.
    :param fragment_start:
    :param fragment_end:
    :param opt_len:
    :param self_binding_ranges:
    :param len_w:
    :param self_bind_w:
    :param tm:
    :param safe_temp_difference:
    :return:
    """
    fragment_length = fragment_end - fragment_start + 1
    score = len_w * (fragment_length - opt_len)**2

    # Find self-binding regions inside the fragment with high enough Tm
    safe_self_bind_limit = tm - safe_temp_difference
    score += self_bind_w * \
             sum([(r[2] - safe_self_bind_limit)**2 for r in self_binding_ranges
                  if r[0] >= fragment_start and r[1] <= fragment_end and r[2] > safe_self_bind_limit])

    return sqrt(score)


def pas_fragment_scores(fragments: List[PASFragment], config: PASConfig,
                        self_binding_ranges: List[Tuple[int, int, float]], tm: float) -> List[float]:
    """
    Returns  scores for a list of PAS fragments.
    :param fragments:
    :param config:
    :param self_binding_ranges:
    :param tm:
    :return:
    """
    if not fragments:
        return []

    optim_length = config.opt_oligo_size
    len_w = config.length_weight
    self_bind_w = config.hairpin_homodimer_weight
    scores = []
    for f in fragments:
        score = pas_fragment_score(f.start, f.end, optim_length, self_binding_ranges, len_w, self_bind_w,
                                   tm, config.safe_temp_difference)
        scores.append(score)
    return scores


def compute_solution_score(solution: PASSolution) -> float:
    """
    Computes score for solution. The solution has two main components, score for fragments and overlaps.
    FRAGMENTS score is sum of:
        -  squared deviation from optimal length
    OVERLAPS score is sum of:
        - squared deviation from optimal overlap length
        - squared deviation from optimal overlap temperature
        - squared deviation from optimal overlap gc-content
    :param solution: PAS Solution containing fragments for scoring
    :return: float score for solution overlaps and fragments
    """
    calc = solution.config.temperature_config.create_calculator()
    fragments = solution.fragments

    fragment_scores = pas_fragment_scores(fragments, solution.config, solution.self_binding_ranges, solution.tm)

    overlap_scores = []
    for i, frag in enumerate(fragments):
        overlap_score = 0

        if i < len(solution.get_fragments()) - 1:
            # overlap length
            diff_len_ov = frag.get_end() - solution.fragments[i + 1].get_start() + 1 - solution.config.opt_overlap_length
            overlap_score += solution.config.temp_weight * (diff_len_ov ** 2)

            # overlap gc
            overlap = solution.gene.sequence[solution.fragments[i + 1].get_start():frag.get_end()]
            calc_gc = GC(overlap)
            gc_opt = (solution.config.max_gc_content - solution.config.min_gc_content) / 2
            diff_gc_ov = calc_gc - gc_opt
            overlap_score += solution.config.gc_content_weight * (diff_gc_ov ** 2)

            # overlap temperature
            temp = calc(overlap)
            diff_temp_ov = solution.config.opt_overlap_tm - temp
            overlap_score += solution.config.temp_weight * (diff_temp_ov ** 2)

            overlap_scores.append(sqrt(overlap_score))

    return sum(overlap_scores) + sum(fragment_scores)


def evaluate_solution(solution: PASSolution) -> float:
    """
    Evaluates solution by normalising solution score by the number of fragments.
    For more detailed description see compute_solution_score() functions
    :param solution: PAS solution
    :return: normalised score of solution
    """
    return compute_solution_score(solution) / len(solution.get_fragments())
