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
from mutation_maker.codon_usage import e_coli
from mutation_maker.degenerate_codon import parse_degenerate_triplet, DegenerateTripletWithAminos


@given(u'i have amino {amino:w}')
def step_impl(context, amino):
    context.amino = amino


@when(u'i want to create degeneracy code')
def step_impl(context):
    context.result = str(e_coli.get_degenerate_triplet_for_amino(context.amino, 0))


@then(u'i get {result} code')
def step_impl(context, result):
    assert context.result == result, f"Code should be {result} but was {context.result}"


@given(u'i have triplets {triplets}')
def step_impl(context, triplets):
    context.triplets = [DegenerateTripletWithAminos.create_from_string(triplet, "") for triplet in triplets.split(",")]


@when(u'i want to create minimal triplets')
def step_impl(context):
    context.result = DegenerateTripletWithAminos.set_cover_with_degenerate_code(context.triplets)


@then(u'i get {triplets} triplets')
def step_impl(context, triplets):
    context.expected = [DegenerateTripletWithAminos.create_from_string(triplet, "") for triplet in triplets.split(",")]
    for triplet in context.result:
        assert triplet in context.expected, f"Triplet {triplet} not in {context.expected}"
