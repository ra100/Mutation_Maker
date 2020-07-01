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
from mutation_maker.mutation import AminoMutation
from mutation_maker.ssm import calculate_mutagenic_primer_search_area, SSMConfig


@given(u'mutation starts at {mutation_start:d} base')
def step_impl(context, mutation_start):
    context.mutation = AminoMutation(mutation_start, "A", "F")


@given(u'max primer size is {max_primer_size:d}')
def step_impl(context, max_primer_size):
    context.max_primer_size = max_primer_size


@given(u'length of three end needs to be between {min_three_end_size:d} and {max_three_end_size:d}')
def step_impl(context, min_three_end_size, max_three_end_size):
    context.min_three_end_size = min_three_end_size
    context.max_three_end_size = max_three_end_size


@when(u'i calculate mutagenic primer search area')
def step_impl(context):
    config = SSMConfig(max_primer_size=context.max_primer_size,
                       min_three_end_size=context.min_three_end_size,
                       max_three_end_size=context.max_three_end_size)
    context.primer_search_area = calculate_mutagenic_primer_search_area(context.mutation,
                                                                        config,
                                                                        context.direction)


@then(u'i get area from {area_from:d} to {area_to:d}')
def step_impl(context, area_from, area_to):
    total_length = area_to - area_from
    result_start, result_length = context.primer_search_area
    error_msg = "Area should be from {} but is from {}".format(area_from, result_start)
    assert area_from == result_start, error_msg
    error_msg = "Area length should be {} but is {}".format(total_length, result_length)
    assert total_length == result_length, error_msg
