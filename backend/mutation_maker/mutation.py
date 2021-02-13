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

import itertools
from typing import List, Iterable, Tuple, Set, Mapping, Sequence, FrozenSet

from Bio.Alphabet import IUPAC

from mutation_maker.degenerate_codon import DegenerateTripletWithAminos, CodonUsage


def parse_codon_mutation(mutation_string, gene_of_interest_offset=0) -> "AminoMutation":
    try:
        one_based_codon_position = int(mutation_string[1:-1])
    except Exception:
        raise ValueError("Position must be positive number")

    if one_based_codon_position < 1:
        raise ValueError("Position must be positive number")

    zero_based_base_position = (one_based_codon_position - 1) * 3
    return AminoMutation(zero_based_base_position + gene_of_interest_offset,
                         mutation_string[0], mutation_string[-1],
                         original_string=mutation_string,
                         original_position=one_based_codon_position)


class AminoMutation:
    """
    Represents a mutation at a single location from one AA to another.
    """
    position: int
    length: int
    old_amino: str
    new_amino: str
    original_string: str
    original_position: int

    invalid_letter = " amino acid is not valid - should be from IUPAC one letter amino acid code"

    def __init__(self, position: int, old_amino: str, new_amino: str,
                 original_string: str, original_position: int) -> None:
        if old_amino not in IUPAC.IUPACProtein.letters:
            raise ValueError("Original" + AminoMutation.invalid_letter)
        if new_amino not in IUPAC.IUPACProtein.letters and new_amino != "X":
            raise ValueError("Target" + AminoMutation.invalid_letter)
        if position < 0:
            raise ValueError("Position must be non-negative")

        self.position = position
        self.length = 3
        self.old_amino = old_amino
        self.new_amino = new_amino
        self.original_string = original_string
        self.original_position = original_position

    def __key(self):
        return self.position, self.old_amino, self.new_amino, self.length

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    def __repr__(self):
        return f"mutation from {self.old_amino} to {self.new_amino} on position {self.position}"


class ConcreteTripletMutation:
    """
    Wraps a single codon mutation together with a position in the gene
    """
    position: int
    length: int
    mutation_triplet: DegenerateTripletWithAminos

    def __init__(self, position: int, mutation_triplet: DegenerateTripletWithAminos) -> None:
        self.position = position
        self.length = 3
        self.mutation_triplet = mutation_triplet

    def degenerate_with(self, other: "ConcreteTripletMutation") -> "ConcreteTripletMutation":
        return ConcreteTripletMutation(
            self.position, self.mutation_triplet.union(other.mutation_triplet))

    def different_bases(self, other):
        return self.mutation_triplet.different_bases(other.mutation_triplet)

    def __key(self):
        return self.position, self.mutation_triplet

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    def __repr__(self):
        return f"Mutation to {self.mutation_triplet} on position {self.position}"


class MutationSite:
    """
    Represents a single mutation site with possibly multiple amino-acid mutations at that site,
    with a few codon generation utility functions.
    """
    original_mutations: Mapping[str, AminoMutation]
    position: int
    length: int
    new_aminos: FrozenSet[str]
    old_amino: str

    def __init__(self, mutations: List[AminoMutation]) -> None:
        # All `mutations` are expected to be at the same site with the same "source" AA
        self.original_mutations = {mutation.new_amino: mutation for mutation in mutations}
        original_position = {mutation.original_position for mutation in mutations}

        self.original_position = original_position.pop()
        position = {mutation.position for mutation in mutations}

        if len(position) != 1:
            raise ValueError("Mutations for multi target amino mutation must be on same position")
        self.position = position.pop()
        self.length = 3

        old_aminos: Set[str] = {mutation.old_amino for mutation in mutations}
        if len(old_aminos) != 1:
            raise ValueError("Mutations on same positions must have same amino")

        self.new_aminos = frozenset(old_aminos.union({m.new_amino for m in mutations}))
        self.old_amino = old_aminos.pop()

    def get_all_concrete_triplets(self, codon_usage_table: CodonUsage, frequency_threshold: float) \
            -> List[ConcreteTripletMutation]:
        triplets = codon_usage_table.get_all_possible_triplets_for_aminos(
            self.new_aminos, frequency_threshold)
        return [ConcreteTripletMutation(self.position, triplet) for triplet in triplets]

    def get_minimal_triplets(self, codon_usage_table: CodonUsage, frequency_threshold: float) \
            -> List[Set[DegenerateTripletWithAminos]]:
        """
        Returns a list of degenerate codons for each amino which cover only the given AAs
        and only use codons with frequency above frequency_threshold.
        """
        return codon_usage_table.get_minimal_triplets_for_aminos(
            self.new_aminos, frequency_threshold)

    def get_mutation_string(self, target_amino: str) -> str:
        """
        Simply computes the code for a mutation with a changed target amino acid.
        If the original was E42L,E42W and `target_amino == "W"`, then this returns "E42W".
        If `target_amino == "E", then this returns "E42E", even though it is not part of the original
        mutation list.

        Note: This only works if the target is the same as the source, because we want to
        include mutations to the same codon.
        """
        if target_amino == self.old_amino:
            return target_amino + str(self.original_position) + target_amino
        return self.original_mutations[target_amino].original_string

    def get_start(self):
        return self.position

    def get_end(self):
        return self.position + self.length

    def user_string_with_aminos(self, aminos: List[str]) -> str:
        return self.old_amino + str(self.original_position) + "".join(aminos)

    def __repr__(self):
        return self.old_amino + str(self.original_position) + "".join(self.new_aminos)

    def __key(self):
        return self.position, self.old_amino, self.new_aminos, self.length

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.get_start() < other.get_start()

    def __gt__(self, other):
        return self.get_start() > other.get_start()


# Info on all possibilities of concrete mutations for a sequence of consecutive mutation sites.
# With utility functions for generating options for AAs mutation combinations
# and mutation codons.
class MSDMMutationSiteSequence:
    """
    Combines multiple mutation sites together, with utility function
    for generating options for AAs mutation combinations and mutation codons.
    """
    ordered_mutations: Tuple[MutationSite, ...]
    position: int
    length: int
    primer_min_start: int
    primer_max_end: int
    concrete_mutations: List[Tuple[ConcreteTripletMutation, ...]]
    aminos_count: int

    def __init__(self, mutations: Iterable[MutationSite],
                 codon_usage_table: CodonUsage, frequency_threshold: float,
                 mutation_boundaries) -> None:
        self.ordered_mutations = tuple(sorted(mutations, key=lambda x: x.position))
        self.position = self.ordered_mutations[0].get_start()
        self.length = self.ordered_mutations[-1].get_end() - self.position + 1
        self.primer_min_start = mutation_boundaries[self.ordered_mutations[0]][0]
        self.primer_max_end = mutation_boundaries[self.ordered_mutations[-1]][1]

        # All n-tuple combinations of triplets at mutation sites which are close to each other.
        self.concrete_mutations = list(
            itertools.product(*[m.get_all_concrete_triplets(codon_usage_table, frequency_threshold)
                                for m in self.ordered_mutations]))
        self.aminos_count = 1
        for mutation in self.ordered_mutations:
            self.aminos_count = self.aminos_count * len(mutation.new_aminos)

    def has_overlap(self, other):
        for mutation in other.ordered_mutations:
            if mutation in self.ordered_mutations:
                return True
        return False

    def get_start(self):
        return self.position

    def get_end(self):
        return self.position + self.length

    def __key(self):
        return self.ordered_mutations

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    def __repr__(self):
        mutations = " ".join([str(m) for m in self.ordered_mutations])
        return f"MutCombo[{self.position}/{self.length}]:{mutations}"

    def __len__(self):
        return len(self.ordered_mutations)

    def get_amino_combinations(self) -> List[Sequence[str]]:
        return list(itertools.product(*[m.new_aminos for m in self.ordered_mutations]))

    def get_mutation_strings(self, amino_combination: Sequence[str]) -> Sequence[str]:
        """
        Returns a sequence of mutation strings for a given list of amino-acids. If the original
        mutation was E42W,E42L,E42K and the input is ["W", "L"], the output will be ["E42W", "E42L"]
        """
        return [self.ordered_mutations[i].get_mutation_string(amino_combination[i])
                for i in range(len(amino_combination))]


def create_multi_amino_mutations(codon_mutations: List[AminoMutation]) \
        -> List[MutationSite]:
    """
    Takes a list of single-amino mutations and creates a list of combined multi-amino
    mutations grouped by position (one instance per mutation site).
    """
    return [MutationSite(list(mutations)) for position, mutations in
            itertools.groupby(codon_mutations, lambda x: x.position)]
