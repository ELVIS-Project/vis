#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               vis/analyzers/experimenters/lilypond.py
# Purpose:                Experimenters related to LilyPond output.
#
# Copyright (C) 2014 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------
"""
.. codeauthor:: Christopher Antila <christopher@antila.ca>

Experimenters related to producing LilyPond-format output from the VIS Framework. Also refer to the
:mod:`vis.analyzers.indexers.lilypond` module.

The :class:`LilyPondIndexer` uses the :mod:`outputlilypond` module to produce a LilyPond file
corresponding to the score.
"""

# Disable "string statement has no effect"
# pylint: disable=W0105

from math import fsum
import pandas
from music21 import stream, note, duration
import outputlilypond
from outputlilypond import settings as oly_settings
from vis.analyzers import experimenter


class PartNotesExperimenter(experimenter.Experimenter):
    """
    From a :class:`Series` full of :class:`Note` objects, craft a :class:`music21.stream.Part`. The
    offset of each :class:`Note` in the output matches its index in the input :class:`Series`, and
    each ``duration`` property is set to match.

    To print a "name" along with the first item in a part, for example to indicate to which part
    or part combinations the annotations belong, use the optional ``part_names`` setting.
    """

    required_score_type = pandas.Series
    default_settings = {}
    possible_settings = ['part_names']
    """
    :param part_names: Names for the annotation parts, in order. If there are more part names than
        parts, extra names will be ignored. If there are fewer part names than parts, some parts
        will not be named.
    :type part_names: list of basestring
    """

    _IMPOSSIBLE_QUARTERLENGTH = 'Impossible \'quarterLength\': {}.'

    def __init__(self, score, settings=None):
        """
        :param score: The input from which to produce a new index.
        :type score: list of :class:`pandas.Series` of :class:`music21.note.Note`

        :param settings: Nothing.
        :type settings: dict or NoneType

        :raises: :exc:`RuntimeError` if ``score`` is the wrong type.
        :raises: :exc:`RuntimeError` if ``score`` is not a list of the same types.
        """
        super(PartNotesExperimenter, self).__init__(score, None)
        if settings is not None and 'part_names' in settings:
            self._settings['part_names'] = settings['part_names']
        else:
            settings = {}

    @staticmethod
    def _fill_space_between_offsets(start_o, end_o):
        """
        Given two offsets, finds the ``quarterLength`` values that fill the whole duration.

        :param start_o: The starting offset.
        :type start_o: ``float``
        :param end_o: The ending offset.
        :type end_o: ``float``

        :returns: The ``quarterLength`` values that fill the whole duration (see below).
        :rtype: list of float

        The algorithm tries to use as few ``quarterLength`` values as possible, but prefers multiple
        values to a single dotted value. The longest single value is ``4.0`` (a whole note).
        """
        VALID_DURATIONS = (2.0, 1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625, 0.0)  # pylint: disable=invalid-name

        def find_highest_valid_ql(this_ql, recursor=0):
            """
            Returns the largest quarterLength that is less then "this_ql" but not greater than 2.0.
            """
            if VALID_DURATIONS[recursor] <= this_ql:
                return VALID_DURATIONS[recursor]
            else:
                return find_highest_valid_ql(this_ql, recursor + 1)

        def the_solver(ql_remains):
            """
            Given the "quarterLength that remains to be dealt with," this method returns
            the solution.
            """
            if 0.0 == ql_remains:
                return [0.0]
            elif 4.0 == ql_remains:
                return [4.0]
            elif ql_remains > 4.0:
                return [4.0] + the_solver(ql_remains - 4.0)
            elif 4.0 > ql_remains >= 0.015625:
                highest = find_highest_valid_ql(ql_remains)
                if highest == ql_remains:
                    return [ql_remains]
                else:
                    return [highest] + the_solver(ql_remains - highest)
            else:
                raise RuntimeError(PartNotesExperimenter._IMPOSSIBLE_QUARTERLENGTH.format(end_o - start_o))

        return the_solver(float(end_o) - float(start_o))

    @staticmethod
    def _set_durations(in_part):
        """
        Set the durations for (:class:`Note`) objects in a :class:`Part` according to the offset
        values. Each :class`Note` will either occupy all the time until the next, or :class:`Rest`
        objects will be inserted so all the time is filled regardless. The final :class:`Note`
        will have a duration of 1.0.

        :param in_part: The :class:`Part` with :class:`~music21.note.Note` objects
            of which the :attr:`~music21.note.Note.duration` attribute will be modified.
        :type param: :class:`music21.stream.Part`

        :returns: A *new* :class:`Part` with modified :class:`Note` objects.
        :rtype: :class:`music21.stream.Part`

        **Examples**

        Input: [Note(offset=0.0), Note(offset=4.0)]
        Output: [Note(offset=0.0, duration=4.0), Note(offset=4.0, duration=1.0)]

        Input: [Note(offset=0.0), Note(offset=3.0)]
        Output: [Note(offset=0.0, duration=2.0),
                 Rest(offset=2.0, duration=1.0),
                 Note(offset=4.0, duration=1.0)]
        """
        in_len = len(in_part)
        ret_part = stream.Part()
        for i in xrange(in_len):
            qls = None
            try:
                qls = PartNotesExperimenter._fill_space_between_offsets(in_part[i].offset,
                                                                   in_part[i + 1].offset)
            except stream.StreamException:  # when we try to access the note after the last
                qls = [1.0]
            in_part[i].duration = duration.Duration(quarterLength=qls[0])
            ret_part.insert(in_part[i].offset, in_part[i])
            for j in xrange(len(qls[1:])):
                # the offset for insertion is...
                #   offset of the Note object, plus
                #   duration of the Note object, plus
                #   duration of all the previously-inserted Rest objects
                ret_part.insert(in_part[i].offset + qls[0] + fsum(qls[1:j + 1]),
                                note.Rest(quarterLength=qls[j + 1]))
        if hasattr(in_part, u'lily_analysis_voice'):
            ret_part.lily_analysis_voice = in_part.lily_analysis_voice
        if hasattr(in_part, u'lily_instruction'):
            ret_part.lily_instruction = in_part.lily_instruction
        return ret_part

    @staticmethod
    def _prepend_rests(in_part):
        """
        Prepends rest objects to fill empty space at the beginning of a :class:`Series`. That is,
        if the first object in the :class:`Series` doesn't have offset ``0.0``, we add a
        :class:`Rest` at offset ``0.0``, and enough additional :class:`Rest` objects to fill the
        duration until the first inputted object.

        If the first object in the inputed :class:`Series` is at offset 0.0, no changes are made.

        :param in_part: The part to fill in.
        :type in_part: :class:`pandas.Series`

        :returns: The filled-in part.
        :type in_part: :class:`pandas.Series`
        """
        if 0.0 != in_part.index[0]:
            durations = PartNotesExperimenter._fill_space_between_offsets(0.0, in_part.index[0])
            offsets = [max(0.0, sum(durations[:i])) for i in xrange(len(durations))]
            for i, offset in enumerate(offsets):
                in_part[offset] = note.Rest(quarterLength=durations[i])
            return in_part.sort_index()
        else:
            return in_part

    def run(self):
        """
        Make a new index of the piece.

        :returns: A list of the new indices. The index of each :class:`Part` corresponds to the
            index of the :class:`Series` used to generate it, in the order specified to the
            constructor. Each element in the :class:`Part` is a :class:`Note`.
        :rtype: list of :class:`music21.stream.Part`
        """
        post = []
        for i, each_series in enumerate(self._index):
            each_series = PartNotesExperimenter._prepend_rests(each_series)
            new_part = stream.Part()
            new_part.lily_analysis_voice = True
            if 'part_names' in self._settings:
                new_part.lily_instruction = (u'\t\\textLengthOn\n'
                                             u'\t\\set Staff.instrumentName = "%s"\n'
                                             u'\t\\set Staff.shortInstrumentName = "%s"\n'
                                             % (self._settings['part_names'][i],
                                                self._settings['part_names'][i]))
            else:
                new_part.lily_instruction = u'\t\\textLengthOn\n'
            # put the Note objects into a new stream.Part, using the right offset
            for off, obj in each_series.iteritems():
                new_part.insert(off, obj)

            post.append(PartNotesExperimenter._set_durations(new_part))
        return post
