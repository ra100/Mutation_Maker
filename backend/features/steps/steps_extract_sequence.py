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
from mutation_maker.ssm import SSMSequences
from mutation_maker.ssm_types import Plasmid


@given(u'plasmid is {sequence:Sequence}')
def step_impl(context, sequence):
    context.plasmid = sequence
    context.five_flanking = None
    context.three_flanking = None
    context.gene_start = None
    context.gene_end = None


@given(u'forward primer is {primer:Sequence}')
def step_impl(context, primer):
    context.fw_primer = primer


@given(u'reverse primer is {primer:Sequence}')
def step_impl(context, primer):
    context.rw_primer = primer


@given(u'five end flanking sequence is {sequence:Sequence}')
def step_impl(context, sequence):
    context.five_flanking = sequence


@given(u'three end flanking sequence is {sequence:Sequence}')
def step_impl(context, sequence):
    context.three_flanking = sequence


@given(u'gene is located from {position_from:d} to {position_to:d}')
def step_impl(context, position_from, position_to):
    context.gene_start = position_from
    context.gene_end = position_to


@when(u'i want to extract full sequence')
def step_impl(context):
    try:
        sequences = SSMSequences(
            forward_primer=get_sequence_string(context.fw_primer),
            reverse_primer=get_sequence_string(context.rw_primer),
            gene_of_interest=get_sequence_string(context.goi),
            five_end_flanking_sequence=get_sequence_string(context.five_flanking),
            three_end_flanking_sequence=get_sequence_string(context.three_flanking),
            plasmid=Plasmid(plasmid_sequence=get_sequence_string(context.plasmid),
                            gene_start_in_plasmid=context.gene_start,
                            gene_end_in_plasmid=context.gene_end))
        context.result, context.offset = sequences.get_full_sequence_with_offset()
        context.error = None
    except Exception as e:
        context.result = None
        context.offset = None
        context.error = e


def get_sequence_string(sequence):
    return sequence if sequence is None else str(sequence)


def check_exception(context, expected_msg):
    assert context.error is not None, "Exception was expected"
    assert str(context.error) == expected_msg, f"Wrong error message {context.error}"


@then(u'gene is offset by {offset:d} bases')
def step_impl(context, offset):
    assert offset == context.offset[0], \
        "Expected offset {} but get {}".format(offset, context.offset[0])


@then(u'gene of interest not found error is raised')
def step_impl(context):
    check_exception(context, "Gene of interest was not found in plasmid")


@then(u'forward primer not found error is raised')
def step_impl(context):
    check_exception(context, "Forward primer was not found in plasmid")


@then(u'reverse primer not found error is raised')
def step_impl(context):
    check_exception(context, "Reverse primer was not found in plasmid")


@then(u'gene of interest position ambiguous error is raised')
def step_impl(context):
    check_exception(context, "Gene of interest position is ambiguous")
