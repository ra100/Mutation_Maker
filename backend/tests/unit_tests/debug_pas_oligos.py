from tests.test_support import sample_pas_sequences, sample_pas_config, sample_pas_mutations
from mutation_maker.generate_oligos import OligoGenerator
from mutation_maker.degenerate_codon import DegenerateTriplet, CodonUsage

# Setup
seq = sample_pas_sequences(1)
config = sample_pas_config(1)
# Disable motif avoidance if possible
if hasattr(config, 'avoided_motifs'):
    config.avoided_motifs = []
mutations_raw = sample_pas_mutations(1)

def expand_mutations(mutations):
    expanded = []
    for msite in mutations:
        for mut in msite.mutations:
            # Handle comma-separated mutation strings
            muts = mut.mutation.split(',')
            freq = mut.frequency / len(muts)
            for aa in muts:
                expanded.append(type(mut)(mutation=aa, frequency=freq))
        yield type(msite)(position=msite.position, mutations=[type(mut)(mutation=aa, frequency=freq) for aa in muts])
    return expanded

# Expand mutations for correct parsing
mutations = list(expand_mutations(mutations_raw))
goi_offset = 0
frag_start = 0
frag_end = len(seq.gene_of_interest)

class Frag:
    def get_start(self): return frag_start
    def get_end(self): return frag_end
    def get_sequence(self, s): return seq.gene_of_interest

frag = Frag()
generator = OligoGenerator(config, False, 'e-coli')
oligos = generator(seq.gene_of_interest, mutations, frag, goi_offset, 200)
cu = CodonUsage('e-coli')
pos = 19

# Collect codons at position 19
codons = set([o.sequence[(pos-1)*3:(pos-1)*3+3] for o in oligos])
print(f'Codons at position {pos}: {codons}')
for codon in codons:
    aas = DegenerateTriplet.degenerate_codon_to_aminos(codon, cu.table.forward_table)
    print(f'{codon}: {aas}')