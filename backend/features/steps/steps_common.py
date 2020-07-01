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

@given(u'gene sequence is {sequence:Sequence}')
@given(u'gene of interest is {sequence:Sequence}')
def step_impl(context, sequence):
    context.goi = sequence


@given(u'direction is {direction:w}')
@given(u'primer direction is {direction:w}')
def step_define_primer_direction(context, direction):
    context.direction = direction


@then(u'i get following sequence {sequence:Sequence}')
def step_impl(context, sequence):
    assert context.error is None, f"Exception was expected not expected but was {context.error}"
    assert sequence == context.result, f"Expected {sequence} but get {context.result}"
