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
import subprocess


def lambda_handler(payload, context):
    binary = os.path.abspath("primer3_core")

    # config_str_template = open("config_string").read()
    thermo_params_path = os.path.join(os.path.abspath("."), "thermo-params/")

    config_content = f"{payload}PRIMER_THERMODYNAMIC_PARAMETERS_PATH={thermo_params_path}\n="

    temp_config_file_path = "/tmp/p3_config_file.txt"

    with open(temp_config_file_path, "w") as f:
        f.write(config_content)

    temp_config_file = open(temp_config_file_path, "r")

    process = subprocess.Popen(binary,
                               stdout=subprocess.PIPE,
                               stdin=temp_config_file,
                               stderr=subprocess.STDOUT)
    out, err = process.communicate()
    return out.decode("ascii")
