from tests.test_support import sample_pas_sequences, sample_pas_config, sample_pas_mutations
from mutation_maker.pas import PASSolver

seq = sample_pas_sequences(1)
config = sample_pas_config(1)
mutations = sample_pas_mutations(1)

solver = PASSolver(config, True, False)
solver.find_solution(seq, mutations)

print('Fragments:')
for f in solver.best_solution.get_fragments():
    print(f)
    print('  Mutation sites:', f.get_mutation_sites())