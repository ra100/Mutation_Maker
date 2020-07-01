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

from behave import given, then, when
from mutation_maker.mutation import *


@given(u'input string is {input_string}')
def step_set_input(context, input_string):
    strings = input_string.split(" ")
    if len(strings) == 1:
        context.input = input_string
        context.inputs = None
    else:
        context.input = None
        context.inputs = strings


@when(u'i want to create mutation')
def step_create_mutation(context):
    try:
        context.mutation = parse_codon_mutation(context.input)
        context.error = None
    except Exception as e:
        context.error = e
        context.mutation = None


@then(u'mutation is created successfully')
def step_check_mutation(context):
    assert context.error is None, f"Error while creating mutation {context.error}"
    assert context.mutation is not None, "Mutation was not created"


@then(u'original amino is {original_amino:w}')
def step_check_original_amino(context, original_amino):
    assert context.mutation.old_amino == original_amino, \
        f"Original amino should be {original_amino} but is {context.mutation.old_amino}"


@then(u'position is {position:d}')
def step_check_position(context, position):
    assert context.mutation.position == position, \
        f"Position should be {position} but is {context.mutation.position}"


@then(u'target amino is {new_amino:w}')
def step_check_target_amino(context, new_amino):
    assert context.mutation.new_amino == new_amino, \
        f"Target amino should be {new_amino} but is {context.mutation.new_amino}"


def check_exception(context, expected_msg):
    assert context.error is not None, "Exception was expected"
    assert str(context.error) == expected_msg, f"Wrong error message {context.error}"


@then(u'invalid original amino error is raised')
def step_impl(context):
    check_exception(
        context,
        "Original amino acid is not valid - should be from IUPAC one letter amino acid code")


@then(u'invalid target amino error is raised')
def step_impl(context):
    check_exception(
        context,
        "Target amino acid is not valid - should be from IUPAC one letter amino acid code")


@then(u'invalid position error is raised')
def step_impl(context):
    check_exception(context, "Position must be positive number")


@when(u'i want to create multi amino target mutation')
def step_impl(context):
    try:
        if context.inputs is not None:
            mutations = [parse_codon_mutation(s) for s in context.inputs]
        if context.input is not None:
            mutations = [parse_codon_mutation(context.input)]
        context.mutation = MutationSite(mutations)
        context.error = None
    except Exception as e:
        context.error = e
        context.mutation = None


@then(u'target aminos are {target_aminos}')
def step_impl(context, target_aminos):
    aminos = target_aminos.split(',')
    for amino in aminos:
        assert amino in context.mutation.new_aminos, \
            f"Amino {amino} is not present in {context.mutation.new_aminos}"


@then(u'inconsistent positions error is raised')
def step_impl(context):
    check_exception(context, "Mutations for multi target amino mutation must be on same position")


@then(u'inconsistent original aminos error is raised')
def step_impl(context):
    check_exception(context, "Mutations on same positions must have same amino")
