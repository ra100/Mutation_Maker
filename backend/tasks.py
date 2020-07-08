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

import os
import json

from celery import Celery

from mutation_maker.codon_usage_table import get_organism_names, get_organism_names_with_ids
from mutation_maker.ssm import ssm_solve
from mutation_maker.qclm import qclm_solve, QCLMInput, QCLMOutput
from mutation_maker.primer3_interoperability import Primer3, AllPrimerGenerator, NullPrimerGenerator
from mutation_maker.ssm_types import SSMInput, SSMOutput
from mutation_maker.pas import pas_solve
from mutation_maker.pas_types import PASInput

print("Mutation Maker version: 1.0.0")

PRIMER3_PATH = os.environ.get('PRIMER3HOME')
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379'),
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')

celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
primer3 = Primer3(primer3_path=PRIMER3_PATH)
secondary_generator = AllPrimerGenerator()


@celery.task(name='tasks.ssm')
def ssm(ssm_input):
    data = parse_body(ssm_input)
    input = SSMInput(data)

    if input.config.use_primer3:
        main_generator = primer3
    else:
        main_generator = NullPrimerGenerator()

    return ssm_solve(input, main_generator, secondary_generator)


@celery.task(name='tasks.qclm')
def qclm(qclm_input):
    data = parse_body(qclm_input)
    input = QCLMInput(data)

    return qclm_solve(input)

@celery.task(name='tasks.species_table')
def species_table(args):
    organisms = get_organism_names_with_ids()
    print("Returning {} organisms".format(len(organisms)))
    return organisms

@celery.task(name='tasks.pas')
def pas(pas_input):
    data = parse_body(pas_input)
    input = PASInput(data)
    output = pas_solve(input)
    return output

def parse_body(body):
    if body is None:
        raise ValueError("Body must contain workflow input JSON data")
    body_type = type(body)
    if body_type is dict:
        return body
    if body_type is str:
        return json.loads(body)
    return ValueError("Invalid type of data use application/json or text/plain")
