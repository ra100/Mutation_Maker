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

from time import time

import numpy as np
import pandas as pd
from pprint import pprint
from tqdm import tqdm

from mutation_maker.primer3_interoperability import AllPrimerGenerator, NullPrimerGenerator
from mutation_maker.ssm import ssm_solve
from mutation_maker.ssm_types import Plasmid, SSMSequences, SSMInput, SSMConfig
from mutation_maker.temperature_calculator import TemperatureConfig


def create_test_config(goi, plasmid, mutations, use_fast_approximation_algorithm):
    ssm_data = SSMInput(
        sequences=SSMSequences(
            forward_primer="PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING",
            reverse_primer="PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING",
            gene_of_interest=goi,
            plasmid=Plasmid(
                plasmid_sequence=plasmid,
            )
        ),
        config=SSMConfig(
            calculation_method="MaxMutationsCovered",
            max_three_end_ranges=1,
            temperature_config=TemperatureConfig(precision=0),
            use_fast_approximation_algorithm=use_fast_approximation_algorithm
        ),
        mutations=mutations
    )

    return ssm_data


def stats_dataframe_for_solution(solution,time):
    stats = pd.DataFrame([], columns=[
        "non_optimality",
        "in_range",
        "fw_temp", "fw_size", "fw_gc",
        "rw_temp", "rw_size", "rw_gc",
        "overlap_temp", "overlap_size","time",
    ])

    for result in solution["results"]:
        stats = stats.append({
            "non_optimality": result["non_optimality"],
            "in_range": result["parameters_in_range"],
            "fw_temp": result["forward_primer"]["three_end_temperature"],
            "fw_size": result["forward_primer"]["length"],
            "fw_gc":   result["forward_primer"]["gc_content"],
            "rw_temp": result["reverse_primer"]["three_end_temperature"],
            "rw_size": result["reverse_primer"]["length"],
            "rw_gc":   result["reverse_primer"]["gc_content"],
            "overlap_temp": result["overlap"]["temperature"],
            "overlap_size": result["overlap"]["length"],
            "time":time
        }, ignore_index=True)

    pprint(stats)
    return stats


def solver_with_input(inputs, use_fast_approximation_algorithm):
    goi, plasmid, mutations = inputs
    config = create_test_config(goi, plasmid, mutations, use_fast_approximation_algorithm)
    start = time()
    solution = ssm_solve(config, NullPrimerGenerator(), AllPrimerGenerator())
    end=time()

    return stats_dataframe_for_solution(solution,end-start)


def generate_inputs():
    sequence = np.random.choice(["A", "C", "T", "G"], 7000, True)

    goi = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"
    plasmid = "PLACE_YOUR_OWN_SEQUENCE_FOR_TESTING"

    SAFE_BOUNDS = 65
    NUM_MUTATIONS = 10

    print(len(goi))

    mutation_sites = np.random.choice(range(SAFE_BOUNDS, len(goi)//3 - SAFE_BOUNDS),
                                      NUM_MUTATIONS)

    mutations = [f"E{mutation_site}X" for mutation_site in mutation_sites]

    return goi, plasmid, mutations


def main():
    for i in tqdm(range(50)):
        inputs = generate_inputs()
        # fast_approximation_yes = solver_with_input(inputs, True)
        fast_approximation_no = solver_with_input(inputs, False)

        # fast_approximation_yes.to_csv(f"stats/stats_{i}_ds=1.csv")
        # fast_approximation_no.to_csv(f"stats/stats_{i}_ds=0.csv")

        # pprint(fast_approximation_yes)
        pprint(fast_approximation_no)


if __name__ == '__main__':
    main()