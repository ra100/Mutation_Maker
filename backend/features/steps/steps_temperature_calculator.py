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
from mutation_maker.temperature_calculator import (TemperatureCalculator,
                                                   get_all_temp_ranges_between)

@given(u'i have temperature calculator with precision {precision:d}')
def step_impl(context, precision):
    context.calculator = TemperatureCalculator(None, precision)


@given(u'i work with temperature range of {range:d} degrees')
def step_impl(context, range):
    context.range = range


@when(u'i want to create all possible ranges from {min:d} to {max:d}')
def step_impl(context, min, max):
    context.result = get_all_temp_ranges_between(min, max,
        context.range, context.calculator.precision_increment)


@then(u'i get {expected:d} intervals')
def step_impl(context, expected):
    real = len(context.result)
    assert real == expected, f"Number of intervals should be {expected} but was {real}"


def parse_interval(context, interval):
    minimum, maximum = interval.split("-")
    return (float(minimum), float(maximum))


def check_interval(i1, i2):
    assert i1[0] == i2[0], \
        f"Minimum of interval should be {i1[0]} but was {i2[0]}"
    assert i1[1] == i2[1], \
        f"Minimum of interval should be {i1[1]} but was {i2[1]}"


@then(u'first interval is {interval}')
def step_impl(context, interval):
    expected = parse_interval(context, interval)
    check_interval(expected, context.result[0])


@then(u'last interval is {interval}')
def step_impl(context, interval):
    expected = parse_interval(context, interval)
    check_interval(expected, context.result[len(context.result) - 1])
