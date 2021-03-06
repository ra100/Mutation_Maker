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

from mutation_maker.basic_types import AminoAcid, Offset
from mutation_maker.qclm_types import SetOfMutationSiteSequences
from mutation_maker.mutation import QCLMMutationSiteSequence
from typing import Tuple, List, Set, FrozenSet, Sequence, Iterable, MutableMapping, NewType

# A sequence of mutation sites identified by their offsets.
SiteSequence = Sequence[Offset]

SiteSet = FrozenSet[Offset]


class SiteSequenceAminos:
    """
    Selection of amino acids for a sequence of mutation sites encoded
    by a joint primer (possibly degenerate).
    """

    # This has to be Tuple[FrozenSet[...]] because anything else is not hashable.
    aminos: Tuple[FrozenSet[AminoAcid], ...]

    def __init__(self, aminos: Tuple[FrozenSet[AminoAcid], ...]) -> None:
        self.aminos = aminos

    def get_aminos(self, i: int) -> FrozenSet[AminoAcid]:
        """ Aminos generated by the primer at the i-th mutation site (zero based) """
        return self.aminos[i]

    def __key(self):
        return self.aminos

    def __eq__(self, y) -> bool:
        return self.__key() == y.__key()

    def __hash__(self) -> int:
        return hash(self.__key())

    @staticmethod
    def merge_amino_sequences(amino_subsets: Iterable["SiteSequenceAminos"]) \
            -> List[Set[AminoAcid]]:
        """
        Takes a list of amino sequences and merges them together into a single list
        of sets of aminos for each site.

        The input is essentially converting a set cover at each site to its union.
        """
        result: List[Set[AminoAcid]] = []

        # Here we just make sure that all `SiteSequenceAminos` cover the
        # same number of sites.
        site_counts = [len(seq.aminos) for seq in amino_subsets]
        assert len(set(site_counts)) == 1

        number_of_sites = site_counts[0]

        for site in range(number_of_sites):
            all_aminos_at_site: Set[AminoAcid] = set()

            for site_sequence_aminos in amino_subsets:
                site_aminos = site_sequence_aminos.get_aminos(site)

                # Since we assume the input is a set cover, lets make sure and check
                # the site sequences don't overlap at any of the sites.
                # assert len(all_aminos_at_site.intersection(site_aminos)) == 0

                all_aminos_at_site.update(site_aminos)

            result.append(all_aminos_at_site)

        return result


SiteSplit = NewType('SiteSplit', Sequence[SiteSequence])


class SiteSplits:
    """ A storage for solutions of splitting mutation sites to sequences
        that can be covered by a joint primer."""

    splits: List[SiteSplit]
    __site_sequences: Set[SiteSet]  # All site sequences which appear in 'splits'

    def __init__(self):
        self.splits = []
        self.__site_sequences = set()

    def add(self, split: SiteSplit):
        """
        Add the contents of a site split.
        """

        seq: SiteSequence
        for seq in split:
            site_set = frozenset(seq)
            if site_set not in self.__site_sequences:
                self.__site_sequences.add(site_set)

        self.splits.append(split)

    def get_site_sequences(self) -> Sequence[SiteSequence]:
        """ Get site sequences appearing in any stored split.
            Offsets in the site sequences are sorted. """
        return [sorted(site_set) for site_set in self.__site_sequences]

    def get_site_sets(self) -> Set[SiteSet]:
        """ Get sets of offsets for site sequences appearing in any stored split. """
        return self.__site_sequences

    @classmethod
    def from_list_of_SetOfMutationSiteSequences(cls, mut_combos: List[SetOfMutationSiteSequences]) -> 'SiteSplits':

        result = cls()

        for site_seq_set in mut_combos:
            seq_list: List[QCLMMutationSiteSequence] = sorted(site_seq_set.mutations, key=lambda x: x.position)
            split = []
            for seq in seq_list:
                split.append([mutation_site.position for mutation_site in seq.ordered_mutations])

            result.add(split)

        return result