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

from typing import Sized, Tuple

from Bio.SeqUtils import GC

from mutation_maker.mutation import AminoMutation
from mutation_maker.temperature_calculator import TemperatureCalculator


def mutate_sequence(sequence: str, sequence_position: int,
                    mutation, mutation_position):
    mutation_offset = mutation_position - sequence_position
    mutation_length = len(mutation)
    return sequence[:mutation_offset] + \
        str(mutation) + \
        sequence[mutation_offset + mutation_length:]


def get_gc_clamp(sequence):
    gc_clamp = 0
    for base in sequence:
        if base == "G" or base == "C":
            gc_clamp = gc_clamp + 1
        else:
            break
    return gc_clamp


class Primer(Sized):
    """
    Represents a primer sequence together with its position, length, direction
    sequence in normal order.
    """
    FORWARD = "forward"
    REVERSE = "reverse"

    direction: str
    start: int
    length: int
    normal_order_sequence: str
    normal_start: int
    normal_end: int

    def __init__(self, parent_sequence: str, direction: str, start: int, length: int):
        Primer.validate_parent_sequence(parent_sequence)
        Primer.validate_direction(direction)
        Primer.validate_start(parent_sequence, start)
        Primer.validate_length(parent_sequence, direction, start, length)

        self.direction = direction
        self.start = start
        self.length = length
        if self.direction == Primer.FORWARD:
            self.normal_order_sequence = parent_sequence[start:start + length]
        elif self.direction == Primer.REVERSE:
            self.normal_order_sequence = parent_sequence[start - length + 1:start + 1]

        self.normal_start = self._get_normal_start()
        self.normal_end = self._get_normal_end()

    def get_five_end_size_from_mutation(self, mutation: AminoMutation) -> int:
        if self.direction == Primer.FORWARD:
            return mutation.position - self.get_normal_start()
        if self.direction == Primer.REVERSE:
            return self.get_normal_end() - mutation.position - mutation.length

    def get_three_end_size_from_mutation(self, mutation: AminoMutation) -> int:
        if self.direction == Primer.FORWARD:
            return self.get_normal_end() - mutation.position - mutation.length
        if self.direction == Primer.REVERSE:
            return mutation.position - self.get_normal_start()

    def get_normal_start(self) -> int:
        return self.normal_start

    def get_normal_end(self) -> int:
        return self.normal_end

    def _get_normal_start(self) -> int:
        if self.direction == Primer.FORWARD:
            return self.start
        if self.direction == Primer.REVERSE:
            return (self.start - self.length) + 1

    def _get_normal_end(self) -> int:
        if self.direction == Primer.FORWARD:
            return self.start + self.length
        if self.direction == Primer.REVERSE:
            return self.start + 1

    def get_gc_content(self, precision: int = 2) -> float:
        return round(GC(self.normal_order_sequence), precision)

    def get_gc_clamp(self) -> int:
        if self.direction == Primer.FORWARD:
            return get_gc_clamp(reversed(self.normal_order_sequence))
        if self.direction == Primer.REVERSE:
            return get_gc_clamp(self.normal_order_sequence)

    def get_three_end_melting_temperature(self, mutation: AminoMutation,
                                          temperature_calculator: TemperatureCalculator) -> float:
        three_end = self.get_three_end_sequence(mutation)
        return temperature_calculator(three_end)

    def get_three_end_temperature_with_size(self, size: int,
                                            temperature_calculator: TemperatureCalculator) -> float:
        if size > 0:
            three_end = self.get_three_end_with_size(size)
            return temperature_calculator(three_end)
        return -1

    def get_melting_temperature(self, temperature_calculator: TemperatureCalculator) -> float:
        return temperature_calculator(self.normal_order_sequence)

    def get_melting_temperature_of_mutated_primer(self, temperature_calculator: TemperatureCalculator,
                                                  mutation_position: int, mutation_sequence: str) -> float:
        return temperature_calculator(self.get_mutated_sequence(mutation_position,
                                                                mutation_sequence))

    def get_mutated_sequence(self, mutation_position: int, mutation_sequence: str) -> str:
        return mutate_sequence(self.normal_order_sequence, self.get_normal_start(),
                               mutation_sequence, mutation_position)

    def get_three_end_sequence(self, mutation: AminoMutation) -> str:
        size = self.get_three_end_size_from_mutation(mutation)
        return self.get_three_end_with_size(size)

    def get_three_end_with_size(self, size: int) -> str:
        if self.direction == Primer.FORWARD:
            return self.normal_order_sequence[-size:]
        if self.direction == Primer.REVERSE:
            return self.normal_order_sequence[:size]

    def get_overlap(self, other_primer: "Primer") -> Tuple[str, int]:
        start = max(self.get_normal_start(), other_primer.get_normal_start())
        end = min(self.get_normal_end(), other_primer.get_normal_end())

        if start >= end:
            return "", 0

        start_offset = start - self.get_normal_start()
        end_offset = end - self.get_normal_start()
        overlap_len = end_offset - start_offset

        return self.normal_order_sequence[start_offset:end_offset], overlap_len

    def __repr__(self):
        return f"{self.direction} primer {self.normal_order_sequence} on position {self.start}"

    def __len__(self):
        return self.length

    def __key(self):
        return self.normal_order_sequence, self.start

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    @staticmethod
    def is_end_in_sequence(parent_sequence, direction, start, length) -> bool:
        if direction == Primer.FORWARD:
            return Primer.is_in_sequence(parent_sequence, start + length - 1)
        elif direction == Primer.REVERSE:
            return Primer.is_in_sequence(parent_sequence, start - length + 1)

    @staticmethod
    def is_in_sequence(sequence, position) -> bool:
        return 0 <= position < len(sequence)

    @staticmethod
    def validate_parent_sequence(parent_sequence):
        if parent_sequence is None:
            raise ValueError("Parent sequence must be defined to create primer")

    @staticmethod
    def validate_direction(direction):
        if direction is None:
            raise ValueError("Primer direction must be specified")
        if direction != Primer.FORWARD and direction != Primer.REVERSE:
            raise ValueError("Direction must be either forward or reverse")

    @staticmethod
    def validate_start(parent_sequence, start):
        if start is None:
            raise ValueError("Primer start must be specified")
        if not Primer.is_in_sequence(parent_sequence, start):
            raise ValueError("Primer start is not in sequence")

    @staticmethod
    def validate_length(parent_sequence, direction, start, length):
        if length is None:
            raise ValueError("Primer length must be specified")
        if length <= 0:
            raise ValueError("Length must be greater than zero")
        if not Primer.is_end_in_sequence(parent_sequence, direction, start, length):
            raise ValueError("Primer end is not in sequence")
