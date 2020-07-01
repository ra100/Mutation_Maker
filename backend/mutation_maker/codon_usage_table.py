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

import re
import pickle
import Bio.Seq as Seq
from Bio.Data import CodonTable as ct
import os

path = os.path.dirname(__file__) +'/codon_usage_data/'

###################################################################################
###################################################################################
# Class organism holds the data for give tax_id.
# For returning codon table call: get_codon_usage_table(name, tran_table_id)
# For returning organism class call:generate_organism(name, tran_table_id)
# Translation table is set to standard table if table id is not provided
#
# speciesInfo.table:
# names,tex_id and translation table number
#
# spsum files:
# Raw frequencies data on the Kazusa page are provided in several files: *.spsum
# these can be updated or recalculated.
#
# SPSUM.LABEL:
# contains ordering of codons according to Kazusa.or.jp
#
# types.p:
# holds all tex_id and in what *.spsum file are the related raw frequencies
###################################################################################
###################################################################################


class Organism:

    def __init__(self, name: str):
        self.tax_id = get_and_check_tax_id(name)
        self.name = name
        self.translation_table = get_tran_table(name)
        self.file = path + get_file_name(self.tax_id)
        self.raw_frequencies = get_freq(self.file, name)
        self.codon_table = get_codon_table(self.raw_frequencies, self.translation_table)


# organism factory, also check if the organism exists in database
def generate_organism(name):
    return Organism(name)

###########################################
# Functions for generating organism input
###########################################


def get_organism_name(tax_id):
    """
    Gets organism name by regexp matching.
    The regexp is trying to find the provided id in the species.table entries.
    In case the organism is not rises exception.
    :param tax_id: string id of organism
    :return: string name of organism
    """
    try:
        with open(path + 'species.table', 'r') as fin:
            all_data = fin.read()
            string2match = '.*(?='+tax_id+')'
            name = re.search(string2match, all_data)

            if name is not None:
                return name.group(0)

            else:
                raise Exception('Organism not found by tax id: {}'.format(tax_id))

    except IOError:
        print('An error occured trying to read the file: {}'.format(path + 'species.table'))


def get_tran_table(name):
    """
    returns one of the 33 translation's tables for given organism
    https://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi
    https://biopython.org/DIST/docs/api/Bio.Data.CodonTable-module.html
    :param name:
    :return:
    """
    with open (path + 'speciesInfo.table', 'r') as fin:
        all_data = fin.read()
        string2match = '(?<=' + name + ').+'
        table_number = re.search(string2match, all_data)

        if table_number:
            table_number = table_number.group(0).split(' ')[-1]

            if int(table_number) in range(1, 34):
                table = ct.unambiguous_dna_by_id[int(table_number)]
            else:
                raise Exception('Wrong number({}) of translation table'.format(table_number))
        else:
            raise Exception('Organism {} not in the data: speciesInfo.table'.format(name))

    return table


# finds the right file for the given tax_id
def get_file_name(tax_id):
    try:
        with open(path + 'types.p', 'rb') as fp:
            data_dict = pickle.load(fp)
            file_name = ''

            for key, values in data_dict.items():
                if tax_id in values:
                    file_name = key + '.spsum'
                    return file_name

            if file_name == '':
                raise Exception('Organism not in types.p file')

    except IOError:
        print('An error occured trying to read the file: {}'.format(path + 'types.p'))


def get_freq(file_in, name):
    """
    Loads raw frequencies from file. The entry is identified by regexp matching.
    If no entry is matched the source file the method rises exception.
    :param file_in: path to file with frequency tables
    :param name: name/id of frequency table
    :return:
    """
    try:
        with open(file_in, 'r') as fin:
            all_data = fin.read()
            string2match = name + ':.*\n(.+)'
            # calling strip before split will remove unnecesarry white characters from start & end of sequence
            frequencies = re.search(string2match, all_data).group(1).strip().split(' ')
            if frequencies:
                # convert to int before retuning
                return [int(freq) for freq in frequencies]
            else:
                raise Exception('Raw frequencies not found in {}'.format(file_in))
    except IOError:
        print('An error occured trying to read the file: {}'.format(file_in))


# returns codon table with relative frequencies, AA translation should be done with specific organism codon table
def get_codon_table(raw_frequencies, translation_table):
    if raw_frequencies == '':
        return {}
    else:
        with open(path + 'CODON_LABEL', 'r') as fin:
            codon_seq = fin.readlines()[1].strip().replace('U', 'T')
            codons = codon_seq.split(' ')

        # data needs to be translated to AA in order to be grouped for calculating frequencies from raw f.
        aa_seq = Seq.Seq(codon_seq.replace(' ', '')).translate(translation_table)
        aa_raw_seq = zip(aa_seq, raw_frequencies)
        relative_frequencies = calc_relative_frequencies(aa_raw_seq)

        # zip ends if one sequence is shorter than other. Better to make sure they are equal
        assert len(codons)==len(relative_frequencies)
        codon_dict = dict(zip(codons, relative_frequencies))
        # except:
        #     codon_dict = {}

        return codon_dict


# calculates relative frequencies from raw frequencies
def calc_relative_frequencies(aa_raw_seq):
    """
    Computes relative frequencies for amino acids.
    Raw frequencies are presented as a zip of aminos and frequencies for each amino.
    The frequencies are relative to single amino group.
    The computation is as following
    1. gather all frequencis for a single group of amino acid
    2. if we detect new amino acid group we compute relative frequencies for previous group
    :param aa_raw_seq: zip of amino and raw frequencies. eg (R,1) (R,2) (R, 5) (T,1)...
    :return: list of relative frequencies rounded to 4 decimal points
    """

    frequencies_for_aa = []
    previous_aa = None
    relative_frequencies = []

    for aa, freq in aa_raw_seq:
        if previous_aa is None: # for the first cycle
            previous_aa = aa
        if aa == previous_aa:
            frequencies_for_aa.append(freq)
        else:
            # we add frequencies for a single aminoacid to the return list of all relative
            relative_frequencies.extend([f/(sum(frequencies_for_aa)+0.000000000000001) for f in frequencies_for_aa])
            previous_aa = aa
            frequencies_for_aa = [freq]

    # we need to add the last sequence
    relative_frequencies.extend([f / (sum(frequencies_for_aa) + 0.000000000000001) for f in frequencies_for_aa])

    return [round(s, 4) for s in relative_frequencies]


# check if the name exists in database and returns tax_id
def get_and_check_tax_id(name):
    try:
        with open(path + 'species.table', 'r') as fin:
            all_data = fin.read()
            tax_id_search = re.search('(?<=' + re.escape(name) + '\s)\d+', all_data)
            if tax_id_search is not None:
                return tax_id_search.group(0)

            else:
                raise Exception('Organism {} not found'.format(name))

    except IOError:
        print('An error occurred trying to read the file: {}'.format(path + 'species.table'))


def get_organism_names():
    """
    Returns all possible organims names
    :rtype: [str]
    :return: [string]
    """
    with open("mutation_maker/codon_usage_data/speciesInfo.table", 'r') as fin:
        return [" ".join(line.split()[:-2]) for line in fin.read().splitlines()]


def get_organism_names_with_ids():
    """
    Returns all possible organims names with their ID as dictionary.
    :return: {"name":"id value"}
    """
    with open("mutation_maker/codon_usage_data/speciesInfo.table", 'r') as fin:
        res_dict = []
        for line in fin.read().splitlines():
            species = {'name': " ".join(line.split()[:-2]),
                       'id': line.split()[-2]}
            res_dict.append(species)
        return res_dict


# call this to get codon usage table
def get_codon_usage_table(name):
    organism = generate_organism(name)

    if organism is not None:
        return organism.codon_table

    else:
        raise Exception('Object organism does not exists')


if __name__ == '__main__':
    ole = generate_organism('AKR (endogenous) murine leukemia virus')
    print(ole.codon_table)

