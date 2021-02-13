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
import sys
from enum import IntEnum
from pprint import pformat
from statistics import mean

from Bio.SeqUtils import GC

from mutation_maker.codon_usage_table import Organism
from mutation_maker.degenerate_codon import DegenerateTriplet, CodonUsage
from mutation_maker.mutation import MutationSite
from mutation_maker.primer_scoring import PrimerScoring
from mutation_maker.site_split import SiteSet, SiteSplits, SiteSplit
from mutation_maker.basic_types import AminoAcid, Offset, PrimerSpec, Temperatures, Codon, DNASequenceForMutagenesis, \
    CODON_LENGTH, MAX_PRIMER3_PRIMER_SIZE
from mutation_maker.msdm_types import MSDMConfig
from mutation_maker.temperature_calculator import TemperatureCalculator, TemperatureConfig, SelfBindingTemps, \
    SelfBindingCalculator
from typing import Iterable, Sequence, Tuple, MutableMapping, List, \
    Set, Dict, Optional, NamedTuple, Mapping


class PrimersAndTemps:
    """"
    A unique list of primers, possibly degenerate, with melting temperatures for each primer.
    Degenerate primers can have a sorted list of temperatures reflecting the fact that the melting
    temperature can be different for different concrete codon combinations covered by a degenerate primer.
    """

    _primers_and_temps: Dict[PrimerSpec, Temperatures]
    _primers_by_codons: Dict[Tuple[Codon, ...], Set[PrimerSpec]]

    def __init__(self) -> None:
        self._primers_and_temps = {}
        self._primers_by_codons = {}

    def add_or_update(self, primer: PrimerSpec, temps: Iterable[float]):
        """
        Add or update primer and its temperatures.
        Temperatures are SORTED by their numerical value during saving.
        """

        self._primers_and_temps[primer] = list(sorted(temps))
        assert len(self._primers_and_temps) > 0

        if self._primers_by_codons.get(primer.codons) is None:
            self._primers_by_codons[primer.codons] = set()
        self._primers_by_codons[primer.codons].add(primer)

    def remove(self, primer: PrimerSpec) -> Optional[Tuple[PrimerSpec, Temperatures]]:
        """ Remove a primer from the collection. """
        temp = self._primers_and_temps.get(primer)
        if temp is None:
            return None
        self._primers_by_codons[primer.codons].discard(primer)
        self._primers_and_temps.pop(primer)

        return primer, temp

    def get_primers_and_temps(self) -> Dict[PrimerSpec, Temperatures]:
        return self._primers_and_temps

    def get_temps(self, primer: PrimerSpec):
        return self._primers_and_temps.get(primer)

    def get_by_codons(self, codons: Tuple[Codon, ...]) -> Sequence[Tuple[PrimerSpec, Temperatures]]:
        """ Get all primers which have a given codon sequence.
        """
        if self._primers_by_codons.get(codons) is None:
            return []
        else:
            return [(primer, self.get_temps(primer)) for primer in self._primers_by_codons[codons]]

    def count(self) -> int:
        return len(self._primers_and_temps)

    def __repr__(self):
        return pformat(self._primers_and_temps)


class PrimerError(IntEnum):
    NO_ERROR = 0
    LENGTH = 1
    THREE_END_SIZE = 2
    FIVE_END_SIZE = 4
    TM = 8
    HAIRPIN_TM = 16
    PRIMER_DIMER_TM = 32
    GC_CONTENT = 64


class PrimerFailure(NamedTuple):
    primer: PrimerSpec
    error_code: int  # constraint breaches encoded using PrimerError values


class ScoredPrimer(NamedTuple):
    spec: PrimerSpec
    score: float
    tm: float


class MSDMSolution:
    """ A solution for the MSDM problem.
        It contains only one mutation site split.
        There is only one primer for each codon combination for each mutation site sequence.
    """

    mutations: List[MutationSite]
    primers: MutableMapping[SiteSet, List[ScoredPrimer]]
    temperature: float
    config: MSDMConfig

    __self_bind_calculator: SelfBindingCalculator

    def __init__(self, mutations: List[MutationSite], temperature: float, msdm_config: MSDMConfig):
        self.primers = {}
        self.mutations = mutations
        self.temperature = temperature
        self.config = msdm_config
        cfgt: TemperatureConfig = msdm_config.temperature_config
        self.__self_bind_calculator = SelfBindingCalculator(cfgt.k, cfgt.mg, cfgt.dntp)
        if msdm_config.organism == "e-coli":
            self.usages = CodonUsage("e-coli")
        elif msdm_config.organism == "yeast":
            self.usages = CodonUsage("yeast")
        else:
            org = Organism(msdm_config.organism)
            self.usages = org.translation_table

    def add_primer(self, site_set: SiteSet, primer_spec: PrimerSpec, primer_temp: float, score: float):

        if not self.primers.get(site_set):
            if bool(self.primers):
                overlapping = site_set & set.union(*[set(s) for s in self.primers.keys()])
                assert not overlapping
            self.primers[site_set] = []

        assert len([p for p in self.primers[site_set] if p.spec.codons == primer_spec.codons]) == 0
        # TODO move penalisation of heterodimers here because we use tuples....
        self.primers[site_set].append(ScoredPrimer(primer_spec, score, primer_temp))

    def site_split(self) -> SiteSplit:
        """ Get the site split used by this solution """
        return [sorted(site_set) for site_set in self.primers.keys()]

    def mutation_coverage(self) -> float:
        """ Returns a ratio (in [0,1]), of number of aminos generated by the solution primers and
            the number of amino acid mutations requested.
        """

        aminos_for_sites = [(set(AminoAcid(a) for a in mut.new_aminos) | {AminoAcid(mut.old_amino)})
                            for mut in self.mutations]

        mut_site_offsets = [Offset(m.position) for m in self.mutations]
        index_of_site = {offset: i for (i, offset) in enumerate(mut_site_offsets)}

        aminos_covered: List[Set[AminoAcid]] = [set() for _ in self.mutations]

        for site_set, primers in self.primers.items():
            site_list = sorted(site_set)
            for primer in primers:
                for i, codon in enumerate(primer.spec.codons):
                    aminos = DegenerateTriplet.degenerate_codon_to_aminos(codon, self.usages.table.forward_table)
                    aminos_covered[index_of_site[site_list[i]]].update(aminos)

        total_aminos = sum(len(amino_set) for amino_set in aminos_for_sites)

        total_aminos_covered = sum(len(amino_set & amino_set_covered) for (amino_set, amino_set_covered)
                                   in zip(aminos_for_sites, aminos_covered))

        return total_aminos_covered / total_aminos

    def temperature_interval(self) -> Tuple[float, float]:
        """ Returns the interval of melting temperatures for the solution primers. """

        primer_temps = self.primer_temperatures()
        return min(primer_temps), max(primer_temps)

    def primer_temperatures(self) -> List[float]:
        return [p.tm for site_set in self.primers for p in self.primers[site_set]]

    def score(self) -> float:
        """ Compute a score for the solution. """

        # Compute the mean score for all primers:
        s = 0.
        n = 0

        for site_set in self.primers:
            for primer in self.primers[site_set]:
                s += primer.score
                n += 1

        if n == 0:  # no primers in the solution
            return math.inf

        mean_primer_score = s / n

        # Mutation coverage part
        mutation_non_coverage = 1 - self.mutation_coverage()

        return self.config.mutation_coverage_weight * mutation_non_coverage + mean_primer_score

    def get_breaking_primers(self, base: str) -> List[PrimerFailure]:
        """ Get the solution primers which break input constraints. """

        result = []
        cfg = self.config

        primer_temps = self.primer_temperatures()

        for site_set, primers in self.primers.items():
            for primer in primers:
                errors = 0

                # Check length constraints
                if cfg.primer_size_weight > 0 and not cfg.min_primer_size <= primer.spec.length <= cfg.max_primer_size:
                    errors += PrimerError.LENGTH

                five_end_size = min(site_set) - primer.spec.offset
                if cfg.five_end_size_weight and not cfg.min_five_end_size <= five_end_size <= cfg.max_five_end_size:
                    errors += PrimerError.FIVE_END_SIZE

                three_end_size = primer.spec.offset + primer.spec.length - max(site_set)
                if cfg.three_end_size_weight and not cfg.min_three_end_size <= three_end_size <= cfg.max_three_end_size:
                    errors += PrimerError.THREE_END_SIZE

                # Check whether the primer melting temperature is within the limits
                if max(primer_temps) - min(primer_temps) > cfg.temp_range_size:
                    if abs(primer.tm - mean(primer_temps)) > cfg.temp_range_size / 2:
                        errors += PrimerError.TM

                # Check hairpin and primer-dimer temperatures
                mutated_dna_sequence_with_primer_sites = DNASequenceForMutagenesis(base, sorted(site_set))
                primer_sequence = primer.spec.get_sequence(mutated_dna_sequence_with_primer_sites)

                if cfg.use_primer3:
                    self_tm = self.__self_bind_calculator(primer_sequence)

                    safe_self_bind_limit = self.temperature - 2 * cfg.temp_range_size

                    if self_tm.hairpin_tm > safe_self_bind_limit:
                        errors += PrimerError.HAIRPIN_TM

                    if self_tm.homodimer_tm > safe_self_bind_limit:
                        errors += PrimerError.HOMODIMER_TM

                # Check GC content
                if cfg.gc_content_weight > 0 and not cfg.min_gc_content <= GC(primer_sequence) <= cfg.max_gc_content:
                    errors += PrimerError.GC_CONTENT

                if errors != 0:
                    result.append(PrimerFailure(primer.spec, errors))

        return result

    def __repr__(self):

        no_primers = sum(len(site_set_primers) for site_set_primers in self.primers.values())

        return f"Solution: site_split={self.site_split()}, no_primers={no_primers}, score={self.score():.1f}, " \
               f"mutation_coverage={self.mutation_coverage():.2f}, primer Tm interval={self.temperature_interval()}, " \
               f"reaction temperature={self.temperature}"


class MSDMPrimers:
    """ A structure for storing intermediate results for a MSDM solution."""

    base: DNASequenceForMutagenesis
    config: MSDMConfig
    temp_calculator: TemperatureCalculator

    # Primer codons for site sequences appearing in __site_splits.
    __primer_defs: MutableMapping[SiteSet, Set[Tuple[Codon, ...]]]

    # Primers for site sequences appearing in __site_splits.
    __primers: MutableMapping[SiteSet, PrimersAndTemps]

    __self_bind_calculator: SelfBindingCalculator
    __self_binding_tm_cache: MutableMapping[PrimerSpec, SelfBindingTemps]

    def __init__(self, splits: SiteSplits, base: DNASequenceForMutagenesis,
                 msdm_config: MSDMConfig, temp_calculator: TemperatureCalculator):
        self.__primer_defs = {}
        self.__primers = {}
        self.__self_binding_tm_cache = {}
        for site_set in splits.get_site_sets():
            self.__primer_defs[site_set] = set()
            self.__primers[site_set] = PrimersAndTemps()

        self.base = base
        self.config = msdm_config
        self.temp_calculator = temp_calculator

        cfgt: TemperatureConfig = msdm_config.temperature_config
        self.__self_bind_calculator = SelfBindingCalculator(cfgt.k, cfgt.mg, cfgt.dntp)

    def get_primers(self) -> MutableMapping[SiteSet, PrimersAndTemps]:
        return self.__primers

    def range(self, site_set: SiteSet) -> Tuple[int, int]:
        """ Returns [min, max) range of the primers for a given site set.
            It means that the offset 'off' of any nucleotide in any of
            these primers satisfies inequality min <= off < max.
        """
        min_start = sys.maxsize
        max_limit = 0
        primers = self.__primers.get(site_set)
        if primers is not None:
            for p in primers.get_primers_and_temps().keys():
                if p.offset < min_start:
                    min_start = p.offset
                if p.offset + p.length > max_limit:
                    max_limit = p.offset + p.length

        return min_start, max_limit

    def add_minimal_primers(self, site_set: SiteSet, codons: Iterable[Codon], min_start: int):
        """ Add primer definitions of minimal length given their mutation sites and codons.
            Creates a minimum length primer for each possible offset of the primer.
            The input set of mutation sites must be present in at least one stored site split.
        """
        assert self.__primer_defs.get(site_set) is not None
        self.__primer_defs[site_set].add(tuple(codons))

        assert self.__primers.get(site_set) is not None

        first_site = min(site_set)
        last_site = max(site_set)
        num_sites = len(site_set)
        site_offsets = self.base.mutation_sites
        prev_site_index = site_offsets.index(first_site) - 1
        next_site_index = site_offsets.index(last_site) + 1

        assert next_site_index - prev_site_index == num_sites + 1

        # Set the min/max primer offset so that it conforms to the input requirements
        # and the primer does not hit the previous mutation site.
        min_primer_offset = max(first_site - self.config.max_five_end_size, min_start, 0)
        if prev_site_index >= 0:
            min_primer_offset = max(min_primer_offset, site_offsets[prev_site_index] + CODON_LENGTH)

        max_primer_offset = first_site - self.config.min_five_end_size

        # Add primers
        for start in range(min_primer_offset, max_primer_offset + 1):
            # Find the minimum primer length that conforms to the requirements
            length = last_site + CODON_LENGTH + self.config.min_three_end_size - start
            length = max(length, self.config.min_primer_size)

            if length > self.config.max_primer_size:
                continue

            if next_site_index < len(site_offsets) and start + length > site_offsets[next_site_index]:
                # we hit the next mutation site
                break

            if start + length > len(self.base.sequence):  # we hit the end of the mutated DNA
                break

            primer_spec = PrimerSpec(start, length, codons)

            # Calculate Tm for the new primer
            tm = self.temp_calculator(primer_spec.get_mismatch_sequence(self.base))
            self.__primers[site_set].add_or_update(primer_spec, [tm])

    def grow(self, temp_threshold: float):
        """
        Add nucleotides to 5' ends of stored primers until their melting temperature is greater or equal
        to a threshold.
        The original primers is replaced by the shortest extension which reaches the temperature threshold.
        If it's not possible to reach the threshold, then the primer is replaced by its longest
        possible 5' extension (which also has the highest melting temperature).
        """

        sorted_site_sequences = sorted(self.__primers.keys(), key=lambda s: min(s))

        for ind, seq in enumerate(sorted_site_sequences):
            primers_for_seq = self.__primers[seq]
            # Get the limit for the end of the primers, if we compute a solution with non-overlapping primers
            primer_end_limit = self.range(sorted_site_sequences[ind+1])[0] \
                               if self.config.non_overlapping_primers and ind < len(sorted_site_sequences) - 1 \
                               else sys.maxsize

            for primer_spec, temp in primers_for_seq.get_primers_and_temps().copy().items():
                # Find the shortest 5' extension of the primer with Tm over temp_threshold
                if temp[0] >= temp_threshold:
                    continue    # The original primer already crossed the threshold

                extended = PrimerSpec(primer_spec.offset, primer_spec.length + 1, primer_spec.codons)
                three_end_size = primer_spec.offset + primer_spec.length - max(seq)

                while self._primer_not_too_long(extended, seq, end_limit=primer_end_limit):
                    tm = self._primer_temperature(extended)
                    if tm >= temp_threshold and three_end_size >= self.config.min_three_end_size:
                        break
                    extended.length += 1
                    three_end_size += 1
                else:  # The extension is too long, let's step back
                    extended.length -= 1
                    tm = self._primer_temperature(extended)

                # Replace the original primer with its extension
                primers_for_seq.remove(primer_spec)
                primers_for_seq.add_or_update(extended, [tm])

    def _primer_temperature(self, primer_spec: PrimerSpec) -> float:
        return self.temp_calculator(primer_spec.get_mismatch_sequence(self.base))

    def _primer_not_too_long(self, primer_spec: PrimerSpec, site_set: SiteSet, end_limit: int) -> bool:
        """ Check whether a primer does dot run into limits of the following constraints:
            - the size of mutated DNA sequence
            - region of the DNA sequence which the primer can cover
            - maximum allowed primer length
            - maximum allowed three- or five end sizes
        """
        if primer_spec.offset + primer_spec.length >= end_limit:
            return False

        dna_seq_length = len(self.base.sequence)
        if primer_spec.offset < 0 or primer_spec.offset + primer_spec.length > dna_seq_length:
            return False

        if primer_spec.length > self.config.max_primer_size:
            return False

        first_site = min(site_set)
        last_site = max(site_set)

        five_end_size = first_site - primer_spec.offset
        three_end_size = primer_spec.offset + primer_spec.length - last_site

        if three_end_size > self.config.max_three_end_size or five_end_size > self.config.max_five_end_size:
            return False

        sites_covered = len([o for o in self.base.mutation_sites
                            if primer_spec.offset - CODON_LENGTH <= o < primer_spec.offset + primer_spec.length])

        if sites_covered != len(primer_spec.codons):
            return False

        return True

    def collect_best_primers(self, score_fun: PrimerScoring, temperature: float) \
            -> Mapping[SiteSet, Sequence[ScoredPrimer]]:
        """ Select primers with the lowest score for each pair of (site set, codon list).
            Primers with infinity scores are not included, even if these are the ony ones for
            a (site set, codon list) combination.
            The output is split w.r.t. the site sets.
        """

        result = {site_set: [] for site_set in self.__primers.keys()}

        for site_set in self.__primers.keys():
            for codons in self.__primer_defs[site_set]:
                # Find a primer with the given codon combination which has the lowest score
                best_score = math.inf
                best_primer = None
                for primer in self.__primers[site_set].get_by_codons(codons):
                    primer_spec, temp = primer

                    self_bind_temps: SelfBindingTemps = self._get_self_binding_temps(primer_spec)

                    primer_score = score_fun(primer_spec, site_set, temp[0],
                                             self_bind_temps.hairpin_tm, self_bind_temps.homodimer_tm, temperature)
                    if primer_score < best_score:
                        best_primer = primer
                        best_score = primer_score

                if best_score < math.inf:
                    primer_spec, temp = best_primer
                    result[site_set].append(ScoredPrimer(spec=primer_spec, score=best_score, tm=temp[0]))

        return result

    def _get_self_binding_temps(self, primer_spec: PrimerSpec) -> SelfBindingTemps:
        if self.config.use_primer3 and primer_spec.length <= MAX_PRIMER3_PRIMER_SIZE:
            # TODO that should not be cached
            if self.__self_binding_tm_cache.get(primer_spec) is None:
                primer_seq = primer_spec.get_sequence(self.base)
                self_tm = self.__self_bind_calculator(primer_seq)

                self.__self_binding_tm_cache[primer_spec] = \
                    SelfBindingTemps(self_tm.hairpin_tm, self_tm.homodimer_tm)

            return self.__self_binding_tm_cache[primer_spec]
        else:
            return SelfBindingTemps(0, 0)
