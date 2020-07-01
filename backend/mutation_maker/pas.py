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

from pprint import pprint
from typing import List
import numpy as np
from mutation_maker.basic_types import DNASequenceForMutagenesis, Offset
from mutation_maker.pas_back_track import PASOptimizer
from mutation_maker.pas_solution import PASProtoFragment, PASSolution, FragmentConstraintError, evaluate_solution
from mutation_maker.pas_types import PASConfig, PASSequences, PASInput, PASMutation, PASMutationSite, \
    PASOutput, PASResult
from mutation_maker.pas_exceptions import PASNoSolutionException
from mutation_maker.temperature_calculator import TemperatureCalculator
from mutation_maker.reverse_translation import Translator
from mutation_maker.pas_output import Output


# Time out limit in seconds
TIMEOUT = 5


def convert_to_str_arr(arr):
    """
    Converts list of string to single sitring separated by comma and removes all empty strings
    :param arr:
    :return:
    """
    return ",".join(arr).replace(' ','')


def create_muts(mutants, frequency):
    res = []
    for mutant in mutants:
        if ',' in mutant:
            for splitted in mutant.split(','):
                tmp = PASMutation(
                    mutation=splitted,
                    frequency=frequency/len(mutant.split(',')))
                res.append(tmp)
        else:
            tmp =PASMutation(
            mutation=mutant,
            frequency=frequency/len(mutants))
            res.append(tmp)
    return res


def extract_mutations(workflow_input: PASInput) -> [PASMutationSite]:
    """
    Extract mutation sites with mutations from the PASInput. All mutation sites with same position are groupped
    to single place.
    :param workflow_input:
    :return:
    """
    tmp_muts = {}
    for in_mut in workflow_input.mutations:
        if in_mut.position in tmp_muts.keys():
            pass
        else:
            tmp_muts[in_mut.position] = PASMutationSite(position=in_mut.position,
                                                        mutations=create_muts(in_mut.mutants, in_mut.frequency))

    return [tmp_muts[key] for key in sorted(tmp_muts.keys())]
# Time out limit in seconds for searching PAS solution for a specific Tm
TIMEOUT = 5
# TIMEOUT = 500  # for debugging


def pas_solve(workflow_input: PASInput) -> str:
    """
    Function which can be called by a Celery task. It parses input data and returns PASOutput in the JSON format.
    :param workflow_input:
    :return:
    """
    solver = PASSolver(workflow_input.config,
                       workflow_input.is_dna_sequence,
                       workflow_input.is_mutations_as_codons)
    # TODO remove when development ends
    pprint(workflow_input.to_json())
    pas_seq = workflow_input.sequences
    # Convert from string input into PAS mutations object
    mutations = extract_mutations(workflow_input)
    try:
        results = solver.find_solution(pas_seq, mutations)
        return PASOutput(input_data=workflow_input, results=results).to_json()
    except PASNoSolutionException as pas_exc:
        return PASOutput(input_data=workflow_input, results=[], message=str(pas_exc)).to_json()


def compute_tm_distances(gene: DNASequenceForMutagenesis, temp_calculator: TemperatureCalculator):
    """
    Computes temperature between mutation sites.
    :param gene: DNASequenceForMutagenesis contains wild sequence and mutation offsets
    :param temp_calculator:
    :return: [int] list of melting temperatures for sequences between mutation sites
    """
    to_ret = []
    for i in range(len(gene.mutation_sites) - 1):
        _from = gene.mutation_sites[i]+3
        _to = gene.mutation_sites[i + 1]
        to_ret.append(temp_calculator(gene.sequence[_from:_to]))
    return to_ret

######################################################################################################################
#                                           PAS SOLVER
######################################################################################################################


class PASSolver:
    config: PASConfig
    temp_calculator: TemperatureCalculator
    sequence: str
    gene: DNASequenceForMutagenesis
    tm_distances: [float]
    best_solution: PASSolution

    def __init__(self, pas_config: PASConfig, is_dna_sequence, is_mutations_as_codons) -> None:
        """
        :param pas_config:
        :param is_dna_sequence:
        :param is_mutations_as_codons:
        """
        self.config = pas_config
        self.temp_calculator = pas_config.temperature_config.create_calculator()
        self.is_dna_sequence = is_dna_sequence
        self.is_mutations_as_codons = is_mutations_as_codons
        self.wild_dna_sequence = ""
        self.temp_calculator = pas_config.temperature_config.create_calculator()

        self.tm_distances = []
        self.avoided_motifs = pas_config.avoided_motifs

    def find_solution(self, sequences: PASSequences, mutations: List[PASMutationSite]) -> [PASResult]:
        """
        Find a solution to the PAS problem.

        :param sequences: Amino acid or DNA sequence for the synthesised gene
        :param mutations: A list of requested mutations
        :return: String json of output.
        """
        sequence, goi_offset = sequences.get_full_sequence_with_offset()
        mutations = sorted(mutations, key=lambda m: m.position)

        mutations_offsets = [Offset(goi_offset+(mut.position - 1)*3) for mut in mutations]

        if not self.is_dna_sequence:
            print("translating")
            translator = Translator(self.config.codon_usage_frequency_threshold,
                                    [self.config.min_gc_content, self.config.max_gc_content],
                                    self.avoided_motifs,
                                    epsilon=0.05, N=600, organism_name=self.config.organism)
            sequences.translate_goi_sequences(translator)
            print("translated")

        self.wild_dna_sequence = sequences.get_full_sequence_with_offset()[0]
        self.gene = DNASequenceForMutagenesis(self.wild_dna_sequence, mutations_offsets)

        self.best_solution = self.find_best_fragments()

        # Debug trace
        if self.best_solution is not None:
            print('Best solution:')
            print('Tm={}'.format(self.best_solution.tm))
            print('Score={}'.format(evaluate_solution(self.best_solution)))
            print('Fragments:')
            for f in self.best_solution.fragments:
                print(f)

        output = Output(self.config, self.is_dna_sequence, self.is_mutations_as_codons)
        return output(self.best_solution, mutations, sequences)

    def create_proto_fragments(self, overlap_t_min: int, mutations: [Offset]):
        """
        Create proto-fragments which are based on the overlap temperature.
        Group mutations to subsets, which must be on the same fragment.
        Two consecutive mutations have to share their fragment,
        when the sequence between them has lower Tm than the minimum melting temperature for fragment overlaps.

        :param overlap_t_min: minimal temperature for overlap
        :param mutations:
        :return:
        """
        if not mutations:
            # no mutations, no need to create protofragments
            return []
        if not self.tm_distances:
            self.tm_distances = compute_tm_distances(self.gene, self.temp_calculator)

        proto_fragments = [PASProtoFragment([mutations[0]])]
        solvable = True
        for i, temp_dist in enumerate(self.tm_distances):
            if temp_dist < overlap_t_min:
                # we cannot fit overlap in-between mutations -> same fragment
                proto_fragments[-1].add_site(mutations[i + 1])
            else:
                # we can fit overlap in-between mutations -> different fragments
                proto_fragments.append(PASProtoFragment([mutations[i + 1]]))

        try:

            for p_fragment in proto_fragments:
                satisfiable = p_fragment.init_constraints(self.gene, self.config, overlap_t_min)
                solvable = solvable and satisfiable
        except FragmentConstraintError:
            # TODO logging
            # print("Exception:" + fex.message)
            print("Cannot create proto fragments for minimal temperature {}".format(overlap_t_min))
            return None
        except Exception as ex:
            raise ex

        if solvable:
            return proto_fragments
        else:
            print("Not solvable for tm: {}", format(overlap_t_min))
            return None

    def find_best_fragments(self) -> PASSolution:
        """
        Split the gene into multiple fragments depending on the configuration.
        Method:
        Loop over allowed melting temperatures T for fragment overlaps:
        1) Create fragments containing mutations, which satisfy the Tm >= T for their ends and have the minimum size
            - "protofragments".
        2) Find the best solution for this melting temperature by exploration of possible fragment splits created
           by extending the protofragments. The exploration algorithm uses backtracking and dynamic programming.

        The function return the solution with the best score, chosen from solutions for specific T values.
        When no solution is found, then the function raises PASNoSolutionException.
        :return: PASSolution
        """
        # A list of best splits of the gene to fragments, one per a melting temperature
        best_solutions: List[(PASSolution, float)] = []

        # Cycle over possible minimum melting temperatures for fragment overlaps
        eps = 1e-6
        step = self.config.temp_threshold_step
        any_proto_found = False

        for t_min in np.arange(self.config.min_overlap_tm, self.config.max_overlap_tm + eps, step):
        # for t_min in np.arange(self.config.min_overlap_tm, self.config.min_overlap_tm + 1 + eps, step):

            #
            # SPLITTING TO FRAGMENTS ("Problem #1")
            #
            # Split mutation sites to subsets called proto-fragments. Each proto-fragment contains mutations which have
            # to be kept on the fragment because of the PAS problem constraints.

            proto_fragments = self.create_proto_fragments(t_min, self.gene.mutation_sites)
            # check if we can create protofragments for this temperature which satisfy input constraints
            if proto_fragments is not None:
                any_proto_found = True
                init_solution = PASSolution(self.gene, self.config, t_min, [])
                # print("--We have protofragments for temperature {}".format(t_min))

                # Run the optimization algorithm which generates DNA fragments
                optimizer = PASOptimizer(proto_fragments, init_solution, TIMEOUT)
                optimizer.optimize()
                if optimizer.timed_out:
                    print("The fragment optimization has timed out after {}s for temperature {}".format(TIMEOUT, t_min))

                result = optimizer.get_optimal_solution()
                if result is not None:
                    solution = result[0]
                    score = evaluate_solution(solution)
                    print("We have found an optimized solution for temperature {} with score {}".format(t_min, score))
                    best_solutions.append((solution, score))
                    # Debug trace
                    for f in solution.fragments:
                        print(f)
                else:
                    print("We have not found an optimized solution for temperature {}".format(t_min))

            else:
                pass
                print("WE do not have solvable proto-fragments for temperature {}".format(t_min))
        if not any_proto_found :
            raise PASNoSolutionException("We could not find any solution. The mutations cannot be separated "
                                         "into different fragments with specified min temperature overlap and "
                                         "distance between mutations. "
                                         "Try increase max oligo size or decrease min ologo overlap length and temperature")

        # return solution with the best score
        if best_solutions:
            return min(best_solutions, key=lambda pair: pair[1])[0]
        else:
            raise PASNoSolutionException("We have not found any solution fitting parameters. "
                                         "Try expanding flanking sequences, especially the three end or "
                                         "insert less strict contrains (increase max oligo size or decrease min oligo overlap length and temperature).")
