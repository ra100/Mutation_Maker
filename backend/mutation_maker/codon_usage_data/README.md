# Codon usage table

codon_usage_table.py is used for computing codon usages from raw frequencies for the given organism.
All the needed data are in the codon_usage_data directory.
The table is calculated from raw frequencies taken from ftp://ftp.ebi.ac.uk/pub/databases/cutg/
These databases contain raw frequencies computed from codon occurrences in certain genes. (mirror also provides databases of used genes).
Raw frequencies are recalculated to relative frequencies, for this purpose translation table of the given organism has to be provided.
Database computed by kazusa.or.jp is from 2007.
In case of update of the database following files may be redownloaded and recalculated.


**Data from kazusa.or.jp**

_*.spsum:_

raw frequencies

*species.table:*

names and taxID table


*SPSUM_LABEL:*

list and ordering of codons


*CODON_LABEL:*

list and ordering of codons


**Files created for computing the frequencies:**

*types.p:*

dictionary of taxas and in which spsum file they belong to

*speciesInfo.table:*

table with translation table number for the given organism


*taxons.p*

dictionary with translation tables



# Libraries

Bio

# How to use
codon_usage_table.py contains class that holds following information:

    class Organism:
    
        def __init__(self):
            self.tax_id = ''                # unique taxID of the given organism
            self.translation_table = ''     # codon to AA translation table
            self.name = ''                  # name of the organism provided for object creation
            self.file = ''                  # name of spsum file for the given organism
            self.raw_frequencies = ''       # dictionary of raw frequencies
            self.codon_table = ''           # ditionary of relative frequencies


**Object creation:**

organism = generate_organism('Gremmeniella abietina RNA virus L1')

codon_table = organism.codon_table


**codon_table is in format:**

{'CGA': 0.32, 'CGC': 0.12, 'CGG': 0.37, 'CGT': 0.07, 'AGA': 0.12, 'AGG': 0.35, 'CTA': 0.25, 'CTC': 0.11...}


