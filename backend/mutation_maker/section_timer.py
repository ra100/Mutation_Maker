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

from decimal import Decimal
from timeit import default_timer


class SectionTimer(object):
    def __init__(self, name, print_results=True, indent=0):
        self.elapsed = Decimal()
        self._name = name
        self._print_results = print_results
        self._start_time = None
        self._children = {}
        self._indent = indent

    def __enter__(self):
        # print(f" ... {'  ' * self._indent}> {self._name}")
        self.start()

        return self

    def __exit__(self, *_):
        self.stop()

        if self._print_results:
            self.print_results()

    def child(self, name):
        try:
            return self._children[name]
        except KeyError:
            result = SectionTimer(name, print_results=False, indent=self._indent + 1)
            self._children[name] = result

            return result

    def start(self):
        self._start_time = self._get_time()

    def stop(self):
        self.elapsed += self._get_time() - self._start_time

    def print_results(self):
        print(self.format_results())

    def format_results(self, indent='  '):
        result = '%s: %.3fs' % (self._name, self.elapsed)
        children = self._children.values()

        for child in sorted(children, key=lambda c: c.elapsed, reverse=True):
            child_lines = child.format_results(indent).split('\n')
            child_percent = child.elapsed / self.elapsed * 100
            child_lines[0] += ' (%d%%)' % child_percent

            for line in child_lines:
                result += '\n' + indent + line

        return result

    def _get_time(self):
        return Decimal(default_timer())
