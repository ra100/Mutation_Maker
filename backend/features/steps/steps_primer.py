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
from mutation_maker.primer import Primer
from mutation_maker.mutation import AminoMutation


@given(u'parent sequence is specified as {parent_sequence:w}')
def step_define_parent_sequence(context, parent_sequence):
    context.parent_sequence = parent_sequence


@given(u'parent sequence is not specified')
def step_parent_sequence_not_specified(context):
    context.parent_sequence = None


@given(u'direction is not specified')
def step_(context):
    context.direction = None


@given(u'start of the primer is {start:d}')
def step_define_primer_start(context, start):
    context.start = start


@given(u'length of the primer is {length:d}')
def step_define_primer_length(context, length):
    context.length = length


@given(u'i create primer with these settings')
@when(u'i want to create the primer')
def step_create_primer(context):
    try:
        context.primer = Primer(getattr(context, "parent_sequence", None),
                                getattr(context, "direction", None),
                                getattr(context, "start", None),
                                getattr(context, "length", None))
        context.error = None
    except Exception as e:
        context.error = e
        context.primer = None


@then(u'primer is created successfully')
def step_assert_primer_exist(context):
    assert context.error is None, f"Error while creating primer {context.error}"
    assert context.primer is not None, "Primer was not created"


def check_exception(context, expected_msg):
    assert context.error is not None, "Exception was expected"
    assert str(context.error) == expected_msg, f"Wrong error message {context.error}"


@then(u'parent sequence missing error is raised')
def step_expect_sequence_missing_error(context):
    check_exception(context, "Parent sequence must be defined to create primer")


@then(u'invalid direction error is raised')
def step_expect_invalid_direction_error(context):
    check_exception(context, "Direction must be either forward or reverse")


@then(u'direction missing error is raised')
def step_expect_direction_missing_error(context):
    check_exception(context, "Primer direction must be specified")


@then(u'invalid start position error is raised')
def step_expect_invalid_start_position_error(context):
    check_exception(context, "Primer start is not in sequence")


@given(u'start is not specified')
def step_start_not_specified(context):
    context.start = None


@then(u'start missing error is raised')
def step_expect_start_missing_error(context):
    check_exception(context, "Primer start must be specified")


@given(u'length of the primer is not specified')
def step_length_not_specified(context):
    context.length = None


@then(u'start missing length is raised')
def step_expect_length_missing_error(context):
    check_exception(context, "Primer length must be specified")


@then(u'invalid end position error is raised')
def step_expect_invalid_end_position(context):
    check_exception(context, "Primer end is not is sequence")


@then(u'primer length error is raised')
def step_expect_length_error(context):
    check_exception(context, "Length must be greater than zero")


@when(u'i want to calculate primer start in normal order')
def step_impl(context):
    context.normal_start = context.primer.get_normal_start()


@when(u'i want to calculate primer end in normal order')
def step_impl(context):
    context.normal_end = context.primer.get_normal_end()


@then(u'start of the primer in normal order is {start:d}')
def step_impl(context, start):
    assert context.normal_start == start, \
     f"Normal start should be {start} but was {context.normal_start}"


@then(u'end of the primer in normal order is {end:d}')
def step_impl(context, end):
    assert context.normal_end == end, \
     f"Normal start should be {end} but was {context.normal_end}"


@then(u'i get following three end size {size:d}')
def step_impl(context, size):
    assert context.three_end_size == size, \
     f"Three end size should be {size} but was {context.three_end_size}"


@when(u'i want to calculate three end size from codon mutation starting at {mutation_start:d}')
def step_impl(context, mutation_start):
    context.three_end_size = context.primer.get_three_end_size_from_mutation(
        AminoMutation(mutation_start, "A", "F"))


@then(u'i get following five end size {size:d}')
def step_impl(context, size):
    assert context.five_end_size == size, \
     f"Five end size should be {size} but was {context.five_end_size}"


@when(u'i want to calculate five end size from codon mutation starting at {mutation_start:d}')
def step_impl(context, mutation_start):
    context.five_end_size = context.primer.get_five_end_size_from_mutation(
        AminoMutation(mutation_start, "A", "F"))


@given(u'primer sequence is {sequence:Sequence}')
def step_impl(context, sequence):
    context.primer_sequence = sequence


def create_primer(context):
    context.error = None
    sequence = str(context.primer_sequence)
    if context.direction == Primer.FORWARD:
        return Primer(sequence, context.direction, 0, len(sequence))
    elif context.direction == Primer.REVERSE:
        return Primer(sequence, context.direction, len(sequence) - 1, len(sequence))


@when(u'i want to calculate gc content')
def step_impl(context):
    primer = create_primer(context)
    context.gc_content = primer.get_gc_content()


@then(u'i get following gc content {gc_content:g}')
def step_impl(context, gc_content):
    assert context.gc_content == gc_content, \
     f"GC content should be {gc_content} but was {context.gc_content}"


@given(u'codon mutation starts at base {mutation_start:d}')
def step_impl(context, mutation_start):
    context.mutation = AminoMutation(mutation_start, "A", "F")


@when(u'i want to get three end sequence')
def step_impl(context):
    primer = create_primer(context)
    context.result = primer.get_three_end_sequence(context.mutation)


@when(u'i want to get mutated sequence with mutation triplet {triplet}')
def step_impl(context, triplet):
    primer = create_primer(context)
    context.result = primer.get_mutated_sequence(context.mutation.position, triplet)


@when(u'i want to get gc_clamp')
def step_impl(context):
    primer = create_primer(context)
    context.gc_clamp = primer.get_gc_clamp()


@then(u'i get following gc_clamp {gc_clamp:d}')
def step_impl(context, gc_clamp):
    assert context.gc_clamp == gc_clamp, \
     f"GC clamp should be {gc_clamp} but was {context.gc_clamp}"
