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

from Bio.SeqUtils import GC

from mutation_maker.basic_types import PrimerSpec, DNASequenceForMutagenesis
from mutation_maker.msdm_types import MSDMConfig
from mutation_maker.site_split import SiteSet


class PrimerScoring:
    """ Function object for calculating a score for a primer and reaction temperature."""

    def __init__(self, base: DNASequenceForMutagenesis, config: MSDMConfig):
        self.base = base
        self.config = config

    def __call__(self, primer_spec: PrimerSpec, site_set: SiteSet,
                 primer_melting_temp: float, hairpin_tm: float, homodimer_tm: float,
                 reaction_temp: float) -> float:

        primer_seq = primer_spec.get_sequence(self.base)

        cfg: MSDMConfig = self.config

        opt_target_gc_content = (cfg.max_gc_content + cfg.min_gc_content) / 2

        opt_melting = cfg.temp_weight * (primer_melting_temp - reaction_temp)
        opt_gc_content = cfg.gc_content_weight * (opt_target_gc_content - GC(primer_seq))
        opt_length = cfg.primer_size_weight * (len(primer_seq) - cfg.min_primer_size)

        three_end_size = min(site_set) - primer_spec.offset
        opt_three_end = cfg.three_end_size_weight * (three_end_size - cfg.min_three_end_size)

        five_end_size = primer_spec.offset + primer_spec.length - max(site_set)
        opt_five_end = cfg.five_end_size_weight * (five_end_size - cfg.min_five_end_size)

        opt_hairpin = opt_primer_dimer = 0

        if cfg.use_primer3:
            safe_self_bind_limit = reaction_temp - 2 * cfg.temp_range_size
            if hairpin_tm > safe_self_bind_limit:
                opt_hairpin = cfg.hairpin_temperature_weight * (hairpin_tm - safe_self_bind_limit)

            if homodimer_tm > safe_self_bind_limit:
                opt_primer_dimer = cfg.primer_dimer_temperature_weight * (homodimer_tm - safe_self_bind_limit)

        return math.sqrt(opt_melting**2 + opt_gc_content**2 + opt_length**2
                         + opt_three_end**2 + opt_five_end**2
                         + opt_hairpin**2 + opt_primer_dimer**2)
