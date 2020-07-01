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

from behave import given, when, then
from mutation_maker.primer3_interoperability import Primer3Config, Primer3
from behave.api.async_step import async_run_until_complete
import os
import asyncio


@given(u'i have some example primer3 config')
def step_create_example_primer3_config(context):
    sequence = """ATGCATCACCACCATCACCACGGCAGCGATAGCGAAGTTAACCAAGAGGCGAAACCTGAAGTTAAGCCAGAAGTCAAACC\
GGAAACCCACATTAATCTGAAAGTGTCCGACGGCAGCAGCGAGATCTTCTTCAAGATCAAAAAGACCACGCCGCTGCGTCGCCTGATGGAAGCT\
TTTGCGAAGCGTCAGGGTAAAGAAATGGACTCTCTGACCTTTCTGTATGACGGTATCGAGATCCAAGCCGATCAGACGCCGGAAGATTTGGACA\
TGGAAGATAATGACATTATTGAAGCGCATCGTGAGCAAATTGGTGGCGAGAACCTGTACTTCCAGGGTGGCGGCCCGCGCCTGCGCGAAGTATT\
GAGCAGACTGAGCCTGGGCCGTCAAGATGTTTCCGAGGCATCGGGCTTGGTTAATCAAGTCGTGAGCCAGCTGATCCAGGCCATTCGTAGCCAA\
GAAGGCTCCTTTGGCAGCATTGAGCGTCTGAATACCGGTAGCTATTACGAACATGTCAAAATCAGCGAACCGAACGAATTTGACATTATGCTGG\
TTATGCCGGTTAGCCGCCTTCAATTGGACGAGTGTGACGATACGGGTGCGTTCTATTATCTGACCTTTAAACGTAATAGCAAAGATAAGCACTT\
GTTCAAGTTTCTGGATGAAGATGGCAAGCTGAGCGCGTTCAAGATGCTGCAGGCACTGCGTGACATCATCAAACGTGAAGTCAAGAATATCAAA\
AATGCAGAGGTCACCGTCAAGCGTAAAAAAGCTGGCAGCCCGGCGATTACGCTGCAAATCAAAAACCCGCCGGCCGTGATCAGCGTTGATATTA\
TCCTGACTCTGGAACCACAACAAAGCTGGCCGCCGTCTACCCAGGACGGCCTGAAAATTGAGAAATGGCTGGGTCGCAAAGTGCGTGGTCAGTT\
CCGTAACAAGTCACTGTATTTGGTTGCGAAGCAAAACAAGCGCGAAAAAGTTCTGCGCGGTAACACGTGGCGCATTAGCTTTAGCCATATTGAA\
AAAGATATGCTGAACAACCACGGCAGCTCTAAAACGTGCTGTGAATCCGACGGTCTGAAGTGCTGCCGCAAGGGTTGCTATAAGCTGCTGAAAT\
ATCTGCTCGAACGTCTGAAGATGAAATACCCGCATCAGTTGGAGAAACGTAGCAGCTACGAAGTGAAAACCGCGTTCTTCCACTCTTGCGTGAT\
GTGGCCGAATGACAGCGACTGGCATTTGAGCGATTTGGACTACTGTTTTCAGAAATATCTGGGTTACTTTCTGGACTGCCTGCAGAAAAGCGAG\
CTGCCACACTTCTTTATCCCACAGTACAATTTACTGAGCCTGGAAGATAAGGCAAGCAATGACTTTCTGAGCCGCCAGATTAACTACGAACTGA\
ATAACCGTTTCCCGATTTTCCAAGAGCGTTACTAA"""
    config = Primer3Config()
    config.primer_count_to_design(1)
    config.template_sequence(sequence)
    context.primer3_config = config


@given(u'PRIMER3HOME environment variable is set to primer3 path')
def step_check_primer3_home_is_set(context):
    assert os.environ.get('PRIMER3HOME'), \
                          "PRIMER3HOME environment variable must be set for this test"


@when(u'i run primer3 through primer3 process manager')
@async_run_until_complete
async def step_run_primer3(context):
    process_manager = Primer3()
    result = process_manager.design_primers(context.primer3_config)
    context.results = [result]


@when(u'i run primer3 {n:d} times through primer3 process manager')
@async_run_until_complete
async def step_run_primer3_n_times(context, n):
    process_manager = Primer3()
    futures = [process_manager.design_primers(context.primer3_config) for _ in range(n)]
    context.results = await asyncio.wait(futures)


@then(u'i get some results')
def step_check_result(context):
    for result in context.results:
        assert result is not None, "Result is not valid"
