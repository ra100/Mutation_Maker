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

from typing import NewType, Sequence, NamedTuple, Tuple, Iterable

AminoAcid = NewType('AminoAcid', str)

Offset = NewType('Offset', int)

Codon = str

Temperatures = Sequence[float]

CODON_LENGTH = 3

MAX_PRIMER3_PRIMER_SIZE = 60

class DNASequenceForMutagenesis(NamedTuple):
    """ The mutated DNA sequence, with mutation site offsets, zero based """
    sequence: str
    mutation_sites: Sequence[Offset]


class PrimerSpec:
    """
    A general primer. Can cover multiple mutation sites and be degenerate
    """

    offset: Offset              # Offset of the first base of the primer in the mutated DNA sequence, zero based
    length: int                 # Length of the primer (number of bases)
    codons: Tuple[Codon, ...]   # Codons in the primer in each of the mutated site it covers.
                                # Note that this has to be Tuple[...] because other types are not hashable.

    def __init__(self, offset: int, length: int, codons: Iterable[Codon]) -> None:
        self.offset = offset
        self.length = length
        self.codons = tuple(codons)

    # TODO: write a few tests
    def get_sequence(self, base: DNASequenceForMutagenesis) -> str:
        """
        Get the DNA sequence for the primer.
        The primer must have codons for all mutation sites within its range.
        """

        dna_sequence, mutation_offsets = base

        # Select those mutation sites which appear in the primer
        mutation_offsets = [o for o in mutation_offsets if self.offset <= o < self.offset + self.length]

        assert len(mutation_offsets) == len(self.codons)

        primer_sequence = dna_sequence[self.offset:(self.offset + self.length)]

        for i, mutation_offset in enumerate(mutation_offsets):
            relative_offset = mutation_offset - self.offset

            primer_sequence = primer_sequence[:relative_offset] + self.codons[i] + \
                primer_sequence[(relative_offset + CODON_LENGTH):]

        return primer_sequence

    def get_mismatch_sequence(self, base: DNASequenceForMutagenesis) -> str:
        """
        Get the DNA sequence of the primer, with mismatches replaced by "X".
        The primer must have codons for all mutation sites within its range.
        """
        mutated_sequence = self.get_sequence(base)
        original_sequence = base.sequence[self.offset:(self.offset + self.length)]

        return "".join([x[0] if x[0] == x[1] else "X"
                        for x in zip(original_sequence, mutated_sequence)])

    def __key(self):
        return self.offset, self.length, self.codons

    def __eq__(self, y):
        return self.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    def __repr__(self):
        return f"Primer:  offset={self.offset}, length={self.length}, codons: {self.codons}"

