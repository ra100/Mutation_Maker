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

import json
import os
import subprocess
from abc import abstractmethod, ABC
from typing import List

from collections import OrderedDict

from .lambda_client import invoke_design_primers, invoke_multiple
from .primer import Primer


def _formatBoulderIO(primer3_config, terminate=True):
    boulder_str = ''.join([f'{k}={v}\n' for k, v in primer3_config.items()])

    if terminate:
        boulder_str += '=\n'

    return boulder_str


def _parseBoulderIO(boulder_str):
    data_dict = OrderedDict()
    for line in boulder_str.split('\n'):
        try:
            k, v = line.strip().split('=')
            data_dict[k] = v
        except Exception:
            pass
    return data_dict


PRIMER3_DIRECTION_FORWARD = "LEFT"
PRIMER3_DIRECTION_REVERSE = "RIGHT"


def parse_primers(raw_primers) -> List[Primer]:
    forward = parse_primers_in_direction(raw_primers, PRIMER3_DIRECTION_FORWARD)
    reverse = parse_primers_in_direction(raw_primers, PRIMER3_DIRECTION_REVERSE)
    return forward + reverse


def parse_primers_from_generator(raw_primers) -> List[Primer]:
    all_primers = []
    splitted = raw_primers.split("\n")
    template = splitted[0]
    all_raw_primers = splitted[1:]
    for raw_primer in all_raw_primers:
        direction, start, length = raw_primer.split(",")
        all_primers.append(Primer(template, direction, int(start), int(length)))
    return all_primers


def extract_primer_position(raw_value):
    one_based_start, length = raw_value.split(',')
    return int(one_based_start) - 1, int(length)


def parse_primers_in_direction(raw_primers, direction) -> List[Primer]:
    primers_count = int(raw_primers["PRIMER_{}_NUM_RETURNED".format(direction)])
    parent_sequence = raw_primers["SEQUENCE_TEMPLATE"]

    if direction == PRIMER3_DIRECTION_FORWARD:
        primer_direction = Primer.FORWARD
    elif direction == PRIMER3_DIRECTION_REVERSE:
        primer_direction = Primer.REVERSE
    else:
        raise NotImplemented()

    positions = [extract_primer_position(raw_primers[name]) for name in
                 ["PRIMER_{}_{}".format(direction, i) for i in range(primers_count)]]
    return [Primer(parent_sequence, primer_direction, start, length) for start, length in positions]


class PrimerGenerator(ABC):
    @abstractmethod
    def design_primers(self, primer3_config) -> List[Primer]:
        pass

    @abstractmethod
    def design_primers_for_all_mutations(self, config_list) -> List[List[Primer]]:
        pass


class NullPrimerGenerator(PrimerGenerator):
    def design_primers(self, primer3_config) -> List[Primer]:
        return []

    def design_primers_for_all_mutations(self, config_list) -> List[List[Primer]]:
        return [[] for config in config_list]


class AllPrimerGenerator(PrimerGenerator):
    def design_primers(self, primer3_config) -> List[Primer]:
        direction = primer3_config.get_direction()

        if direction == Primer.FORWARD:
            result = self.design_all_primers_in_direction(
                primer3_config, lambda start, length: start)
        elif direction == Primer.REVERSE:
            result = self.design_all_primers_in_direction(
                primer3_config, lambda start, length: start + length - 1)
        else:
            raise RuntimeError(f"Invalid value of {primer3_config.get_direction()}")

        # Generate DNA sequences for primers from their direction, position and length
        # specifications.
        return parse_primers_from_generator(result)

    def design_primers_for_all_mutations(self, config_list) -> List[List[Primer]]:
        return [self.design_primers(config) for config in config_list]

    # Params:
    # start_generator: A function that sets the start position for the primer.
    # Output:
    # Specification of primers a a string
    # "{direction, start_position, length}*"
    def design_all_primers_in_direction(self, primer3_config, start_generator):
        template = primer3_config.get_template()
        direction = primer3_config.get_direction()
        search_area_start, search_area_len = primer3_config.get_search_area()
        min_len, max_len = primer3_config.get_primer_length_range()

        all_primers = [template]
        for primer_length in range(min_len, max_len + 1):
            for start in range(search_area_start,
                               search_area_start + search_area_len - primer_length):
                start_position = start_generator(start, primer_length)
                all_primers.append(f"{direction},{start_position},{primer_length}")

        return "\n".join(all_primers)


class Primer3(PrimerGenerator):
    def __init__(self, primer3_path=None):
        if primer3_path is None:
            if not os.environ.get("PRIMER3HOME"):
                raise Exception("""Primer 3 path is not set - must be passed as parameter or set \
as environment variable PRIMER3HOME""")
            else:
                primer3_base_path = os.environ.get("PRIMER3HOME")
        else:
            primer3_base_path = primer3_path
        self.binary = os.path.join(primer3_base_path, 'primer3_core')
        self.thermodynamic_parameters_path = os.path.join(
            primer3_base_path, 'primer3_config/')

    def design_primers_for_all_mutations(self, config_list) -> List[List[Primer]]:
        return self.design_multiple_lambda_primers(config_list)

    def design_multiple_lambda_primers(self, configs):
        str_configs = [self.create_raw_primer3_input_string(config) for config in configs]
        results = invoke_multiple(str_configs)
        return [parse_primers(_parseBoulderIO(result)) for result in results]

    def design_lambda_primers(self, primer3_config):
        aws_response = invoke_design_primers(self.create_raw_primer3_input_string(primer3_config))
        aws_json = json.loads(aws_response["Payload"].read().decode("ascii"))
        return parse_primers(_parseBoulderIO(aws_json))

    def design_multiple_local_primers(self, config_list):
        return [self.design_primers(config) for config in config_list]

    def design_primers(self, primer3_config) -> List[Primer]:
        input_string = self.create_primer3_input_string(primer3_config)
        input_bytes = input_string.encode('ascii')

        process = subprocess.Popen(self.binary,
                                   stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        out, err = process.communicate(input=input_bytes)
        output_string = out.decode('ascii')

        return parse_primers(_parseBoulderIO(output_string))

    def create_raw_primer3_input_string(self, primer3_config):
        return _formatBoulderIO(primer3_config.config, terminate=False)

    def create_primer3_input_string(self, primer3_config):
        primer3_config.set_thermodynamic_parameters_path(
            self.thermodynamic_parameters_path)
        return _formatBoulderIO(primer3_config.config)


class Primer3Config:
    def __init__(self):
        self.config = {}
        self.primer_count_to_design(2147483647)

    def get_template(self):
        return self.config["SEQUENCE_TEMPLATE"]

    def get_direction(self):
        if "PRIMER_PICK_LEFT_PRIMER" not in self.config:
            return Primer.FORWARD
        if "PRIMER_PICK_RIGHT_PRIMER" not in self.config:
            return Primer.REVERSE
        if self.config["PRIMER_PICK_LEFT_PRIMER"] == 1:
            return Primer.FORWARD
        if self.config["PRIMER_PICK_RIGHT_PRIMER"] == 1:
            return Primer.REVERSE

    def get_search_area(self):
        if self.get_direction() == Primer.FORWARD:
            fw_start, fw_len, _, _ = self.config["SEQUENCE_PRIMER_PAIR_OK_REGION_LIST"].split(",")
            return int(fw_start), int(fw_len)
        if self.get_direction() == Primer.REVERSE:
            _, _, rw_start, rw_len = self.config["SEQUENCE_PRIMER_PAIR_OK_REGION_LIST"].split(",")
            return int(rw_start), int(rw_len)

    def get_primer_length_range(self):
        return int(self.config["PRIMER_MIN_SIZE"]), int(self.config["PRIMER_MAX_SIZE"])

    def set_thermodynamic_parameters_path(self, path):
        self.config.setdefault('PRIMER_THERMODYNAMIC_PARAMETERS_PATH', path)

    def force_forward_primer(self, forward_primer):
        self.config["SEQUENCE_PRIMER"] = forward_primer
        self.config["PRIMER_PICK_LEFT_PRIMER"] = 0

    def force_reverse_primer(self, reverse_primer):
        self.config["SEQUENCE_PRIMER_REVCOMP"] = reverse_primer
        self.config["PRIMER_PICK_RIGHT_PRIMER"] = 0

    def pick_only_forward_primer(self):
        self.config["PRIMER_PICK_LEFT_PRIMER"] = 1
        self.config["PRIMER_PICK_RIGHT_PRIMER"] = 0

    def template_sequence(self, sequence):
        self.config["SEQUENCE_TEMPLATE"] = sequence

    def size_range(self, minimum=None, optimum=None, maximum=None):
        if minimum is not None:
            self.config["PRIMER_MIN_SIZE"] = minimum
        if optimum is not None:
            self.config["PRIMER_OPT_SIZE"] = optimum
        if maximum is not None:
            self.config["PRIMER_MAX_SIZE"] = maximum

    def gc_content_range(self, minimum=None, optimum=None, maximum=None):
        if minimum is not None:
            self.config["PRIMER_MIN_GC"] = minimum
        if optimum is not None:
            self.config["PRIMER_OPT_GC_PERCENT"] = optimum
        if maximum is not None:
            self.config["PRIMER_MAX_GC"] = maximum

    def temperature_range(self, minimum=None, optimum=None, maximum=None):
        if minimum is not None:
            self.config["PRIMER_MIN_TM"] = minimum
        if optimum is not None:
            self.config["PRIMER_OPT_TM"] = optimum
        if maximum is not None:
            self.config["PRIMER_MAX_TM"] = maximum

    def gc_clamp(self, gc_clamp):
        self.config["PRIMER_GC_CLAMP"] = gc_clamp

    def primer_count_to_design(self, primer_count):
        self.config["PRIMER_NUM_RETURN"] = primer_count

    def search_region(self,
                      forward_from=None, forward_len=None,
                      reverse_from=None, reverse_len=None):
        search_area = "{},{},{},{}".format(forward_from if forward_from is not None else "",
                                           forward_len if forward_len is not None else "",
                                           reverse_from if reverse_from is not None else "",
                                           reverse_len if reverse_len is not None else "")
        self.config["SEQUENCE_PRIMER_PAIR_OK_REGION_LIST"] = search_area
