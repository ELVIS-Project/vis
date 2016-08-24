#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           vis
# Program Description:    Helps analyze music with computers.
#
# Filename:               models/indexed_piece.py
# Purpose:                Hold the model representing an indexed and analyzed piece of music.
#
# Copyright (C) 2013, 2014 Christopher Antila, Jamie Klassen
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
.. codeauthor:: Jamie Klassen <michigan.j.frog@gmail.com>
.. codeauthor:: Christopher Antila <crantila@fedoraproject.org>

This model represents an indexed and analyzed piece of music.
"""

# Imports
import os
import six
from six.moves import range, xrange  # pylint: disable=import-error,redefined-builtin
from music21 import converter, stream
from vis.analyzers.experimenter import Experimenter
from vis.analyzers.indexer import Indexer
from vis.analyzers.indexers import noterest


# the title given to a piece when we cannot determine its title
_UNKNOWN_PIECE_TITLE = 'Unknown Piece'


def _find_piece_title(the_score):
    """
    Find the title of a score. If there is none, return the filename without an extension.

    :param the_score: The score of which to find the title.
    :type the_score: :class:`music21.stream.Score`

    :returns: The title of the score.
    :rtype: str
    """
    # First try to get the title from a Metadata object, but if it doesn't
    # exist, use the filename without directory.
    if the_score.metadata is not None:
        post = the_score.metadata.title
    elif hasattr(the_score, 'filePath'):
        post = os.path.basename(the_score.filePath)
    else:  # if the Score was part of an Opus
        post = _UNKNOWN_PIECE_TITLE

    # Now check that there is no file extension. This could happen either if
    # we used the filename or if music21 did a less-than-great job at the
    # Metadata object.
    # TODO: test this "if" stuff
    if not isinstance(post, six.string_types):  # uh-oh
        try:
            post = str(post)
        except UnicodeEncodeError:
            post = unicode(post) if six.PY2 else _UNKNOWN_PIECE_TITLE
    post = os.path.splitext(post)[0]

    return post


def _find_part_names(the_score):
    """
    Return a list of part names in a score. If the score does not have proper part names, return a
    list of enumerated parts.

    :param the_score: The score in which to find the part names.
    :type the_score: :class:`music21.stream.Score`

    :returns: The title of the score.
    :rtype: :obj:`list` of str
    """
    # hold the list of part names
    post = []

    # First try to find Instrument objects. If that doesn't work, use the "id"
    for each_part in the_score.parts:
        instr = each_part.getInstrument()
        if instr is not None and instr.partName != '' and instr.partName is not None:
            post.append(instr.partName)
        elif each_part.id is not None:
            if isinstance(each_part.id, six.string_types):
                # part ID is a string, so that's what we were hoping for
                post.append(each_part.id)
            else:
                # the part name is probably an integer, so we'll try to rename it
                post.append('rename')
        else:
            post.append('rename')

    # Make sure none of the part names are just numbers; if they are, use
    # a part name like "Part 1" instead.
    for i, part_name in enumerate(post):
        if 'rename' == part_name:
            post[i] = 'Part {}'.format(i + 1)

    return post

def _get_offset(event):
    """
    This method finds the offset of a music21 event. The first part of this equation is the offset 
    of the beginning of the event's containing measure, and the second is the offset from the 
    beginning of that measure to the event.
    """
    return (event.sites.getAttrByName('offset') + event.offset)

def _eliminate_ties(event):
    """
    Gets rid of the notes and rests that have non-start ties. This should be used for the noterest, 
    and beatstrength indexers.
    """
    if hasattr(event, 'tie') and event.tie is not None and event.tie.type != 'start':
        return float('nan')
    return event


class OpusWarning(RuntimeWarning):
    """
    The :class:`OpusWarning` is raised by :meth:`IndexedPiece.get_data` when ``known_opus`` is
    ``False`` but the file imports as a :class:`music21.stream.Opus` object, and when ``known_opus``
    is ``True`` but the file does not import as a :class:`music21.stream.Opus` object.

    Internally, the warning is actually raised by :meth:`IndexedPiece._import_score`.
    """
    pass


class IndexedPiece(object):
    """
    Hold indexed data from a musical score.
    """

    # When get_data() is missing the "data" argument.
    _MISSING_DATA = '{} is missing required data from another analyzer.'

    # When get_data() gets something that isn't an Indexer or Experimenter
    _NOT_AN_ANALYZER = 'IndexedPiece requires an Indexer or Experimenter (received {})'

    # When metadata() gets an invalid field name
    _INVALID_FIELD = 'metadata(): invalid field ({})'

    # When metadata()'s "field" is not a string
    _META_INVALID_TYPE = "metadata(): parameter 'field' must be of type 'string'"

    # When _import_score() gets an unexpected Opus
    _UNEXP_OPUS = '{} is a music21.stream.Opus (refer to the IndexedPiece.get_data() documentation)'

    # When _import_score() gets an unexpected Opus
    _UNEXP_NONOPUS = ('You expected a music21.stream.Opus but {} is not an Opus (refer to the '
                      'IndexedPiece.get_data() documentation)')

    def __init__(self, pathname, opus_id=None):
        """
        :param str pathname: Pathname to the file music21 will import for this :class:`IndexedPiece`.
        :param opus_id: The index of the :class:`Score` for this :class:`IndexedPiece`, if the file
            imports as a :class:`music21.stream.Opus`.

        :returns: A new :class:`IndexedPiece`.
        :rtype: :class:`IndexedPiece`
        """
        def init_metadata():
            """
            Initialize valid metadata fields with a zero-length string.
            """
            field_list = ['opusNumber', 'movementName', 'composer', 'number', 'anacrusis',
                'movementNumber', 'date', 'composers', 'alternativeTitle', 'title',
                'localeOfComposition', 'parts']
            for field in field_list:
                self._metadata[field] = ''
            self._metadata['pathname'] = pathname

        super(IndexedPiece, self).__init__()
        self._imported = False
        self._analyses = {}
        self._noterest_results = None
        self._metadata = {}
        self._known_opus = False
        self._opus_id = opus_id  # if the file imports as an Opus, this is the index of the Score
        init_metadata()

    def __repr__(self):
        return "vis.models.indexed_piece.IndexedPiece('{}')".format(self.metadata('pathname'))

    def __str__(self):
        post = []
        if self._imported:
            return '<IndexedPiece ({} by {})>'.format(self.metadata('title'), self.metadata('composer'))
        else:
            return '<IndexedPiece ({})>'.format(self.metadata('pathname'))

    def __unicode__(self):
        return six.u(str(self))

    def _import_score(self, known_opus=False):
        """
        Import the score to music21 format.

        :param known_opus: Whether you expect the file to import as a :class:`Opus`.
        :type known_opus: boolean

        :returns: the score
        :rtype: :class:`music21.stream.Score`

        :raises: :exc:`OpusWarning` if the file imports as a :class:`music21.stream.Opus` but
            ``known_opus`` if ``False``, or if ``known_opus`` is ``True`` but the file does not
            import as an :class:`Opus`.
        """
        score = converter.Converter()
        score.parseFile(self.metadata('pathname'), forceSource=True, storePickle=False)
        score = score.stream
        if isinstance(score, stream.Opus):
            if known_opus is False and self._opus_id is None:
                # unexpected Opus---can't continue
                raise OpusWarning(IndexedPiece._UNEXP_OPUS.format(self.metadata('pathname')))
            elif self._opus_id is None:
                # we'll make new IndexedPiece objects
                score = [IndexedPiece(self.metadata('pathname'), i) for i in xrange(len(score))]
            else:
                # we'll return the appropriate Score
                score = score.scores[self._opus_id]
        elif known_opus is True:
            raise OpusWarning(IndexedPiece._UNEXP_NONOPUS.format(self.metadata('pathname')))
        elif not self._imported:
            for field in self._metadata:
                if hasattr(score.metadata, field):
                    self._metadata[field] = getattr(score.metadata, field)
                    if self._metadata[field] is None:
                        self._metadata[field] = '???'
            self._metadata['parts'] = _find_part_names(score)
            self._metadata['title'] = _find_piece_title(score)
            self._imported = True
        return score

    def metadata(self, field, value=None):
        """
        Get or set metadata about the piece.

        .. note:: Some metadata fields may not be available for all pieces. The available metadata
            fields depend on the specific file imported. Unavailable fields return ``None``.
            We guarantee real values for ``pathname``, ``title``, and ``parts``.

        :param str field: The name of the field to be accessed or modified.
        :param value: If not ``None``, the value to be assigned to ``field``.
        :type value: object or ``None``

        :returns: The value of the requested field or ``None``, if assigning, or if accessing
            a non-existant field or a field that has not yet been initialized.
        :rtype: object or ``None`` (usually a string)

        :raises: :exc:`TypeError` if ``field`` is not a string.
        :raises: :exc:`AttributeError` if accessing an invalid ``field`` (see valid fields below).

        **Metadata Field Descriptions**

        All fields are taken directly from music21 unless otherwise noted.

        +---------------------+--------------------------------------------------------------------+
        | Metadata Field      | Description                                                        |
        +=====================+====================================================================+
        | alternativeTitle    | A possible alternate title for the piece; e.g. Bruckner's          |
        |                     | Symphony No. 8 in C minor is known as "The German Michael."        |
        +---------------------+--------------------------------------------------------------------+
        | anacrusis           | The length of the pick-up measure, if there is one. This is not    |
        |                     | determined by music21.                                             |
        +---------------------+--------------------------------------------------------------------+
        | composer            | The author of the piece.                                           |
        +---------------------+--------------------------------------------------------------------+
        | composers           | If the piece has multiple authors.                                 |
        +---------------------+--------------------------------------------------------------------+
        | date                | The date that the piece was composed or published.                 |
        +---------------------+--------------------------------------------------------------------+
        | localeOfComposition | Where the piece was composed.                                      |
        +---------------------+--------------------------------------------------------------------+
        | movementName        | If the piece is part of a larger work, the name of this            |
        |                     | subsection.                                                        |
        +---------------------+--------------------------------------------------------------------+
        | movementNumber      | If the piece is part of a larger work, the number of this          |
        |                     | subsection.                                                        |
        +---------------------+--------------------------------------------------------------------+
        | number              | Taken from music21.                                                |
        +---------------------+--------------------------------------------------------------------+
        | opusNumber          | Number assigned by the composer to the piece or a group            |
        |                     | containing it, to help with identification or cataloguing.         |
        +---------------------+--------------------------------------------------------------------+
        | parts               | A list of the parts in a multi-voice work. This is determined      |
        |                     | partially by music21.                                              |
        +---------------------+--------------------------------------------------------------------+
        | pathname            | The filesystem path to the music file encoding the piece. This is  |
        |                     | not determined by music21.                                         |
        +---------------------+--------------------------------------------------------------------+
        | title               | The title of the piece. This is determined partially by music21.   |
        +---------------------+--------------------------------------------------------------------+

        **Examples**

        >>> piece = IndexedPiece('a_sibelius_symphony.mei')
        >>> piece.metadata('composer')
        'Jean Sibelius'
        >>> piece.metadata('date', 1919)
        >>> piece.metadata('date')
        1919
        >>> piece.metadata('parts')
        ['Flute 1'{'Flute 2'{'Oboe 1'{'Oboe 2'{'Clarinet 1'{'Clarinet 2', ... ]
        """
        if not isinstance(field, six.string_types):
            raise TypeError(IndexedPiece._META_INVALID_TYPE)
        elif field not in self._metadata:
            raise AttributeError(IndexedPiece._INVALID_FIELD.format(field))
        if value is None:
            return self._metadata[field]
        else:
            self._metadata[field] = value

    def _get_part_streams(self):
        if 'part_streams' not in self._analyses:
            self._analyses['part_streams'] = self._import_score(known_opus=self._known_opus).parts
        return self._analyses['part_streams']

    def _get_m21_objs(self):
        """
        Return the all the music21 objects found in the piece. This is a list of pandas.Series 
        where each series contains the events in one voice. It is not concatenated into a 
        dataframe at this stage because this step should be done after filtering for a certain
        type of event in order to get the proper index.

        This list of voices with their events can easily be turned into a dataframe of music21 
        objects that can be filtered to contain, for example, just the note and rest objects.
        Filtered dataframes of music21 objects like this can then have an indexer_func applied 
        to them all at once using df.applymap(indexer_func).

        :returns: All the objects found in the music21 voice streams. These streams are made 
            into pandas.Series and collected in a list.
        :rtype: list of :class:`pandas.Series`
        """
        if 'm21_objs' not in self._analyses:
            # save the results as a list of series in the indexed_piece attributes
            self._analyses['m21_objs'] = [pandas.Series(x.recurse()) for x in self._get_part_streams()]
        return self._analyses['m21_objs']

    def _get_m21_nrc_objs(self):
        """
        This method takes a list of pandas.Series of music21 objects in each part in a piece and
        filters them to reveal just the 'Note', 'Rest', and 'Chord' objects. It then aligns these
        events with their offsets, and returns a list of the altered series. In the list 
        comprehension, the variable sers is the resultant list of series, and s corresponds to each 
        series in that list. The difference between this method and the _get_m21_nr_objs() method is 
        that the result of this one still has the chord objects, whereas the other method unpacks 
        them into their containing objects.

        :returns: The note, rest, and chord music21 objects in each part of a piece.
        :rtype: A list of pandas.Series of music21 note, rest, and chord objects.
        """
        if 'm21_noterest' not in self._analyses:
            # get rid of all m21 objects that aren't notes, rests, or chords and index  the offsets
            sers = [s.apply(noterest._type_func).dropna().apply(_get_offset)
                    for s in self._get_m21_objs(self._known_opus)]
            self._analyses['m21_noterest'] = pandas.concat(sers, axis=1)
        return self._analyses['m21_noterest']

    def _get_m21_nrc_objs_no_tied(self):
        if 'm21_noterest_no_tied' not in self._analyses:
            self._analyses['m21_noterest_no_tied'] = self._get_m21_nrc_objs(self._known_opus).applymap(_eliminate_ties).dropna(how='all')
        return self._analyses['m21_noterest_no_tied']

    def _get_noterest(self):
        if 'noterest' not in self._analyses:
            self._analyses['noterest'] = noterest.NoteRestIndexer(self._get_m21_nrc_objs_no_tied()).run()
        return self._analyses['noterest']

    @staticmethod
    def _type_verifier(cls_list):
        """
        Verify that all classes in the list are a subclass of :class:`vis.analyzers.indexer.Indexer`
        or :class:`~vis.analyzers.experimenter.Experimenter`.

        :param cls_list: A list of the classes to check.
        :type cls_list: list of class
        :returns: ``None``.
        :rtype: None
        :raises: :exc:`TypeError` if a class is not a subclass of :class:`Indexer` or
            :class:`Experimenter`.

        ..note:: This is a separate function so it can be replaced with a :class:`MagicMock` in
            testing.
        """
        for each_cls in cls_list:
            if not issubclass(each_cls, (Indexer, Experimenter)):
                raise TypeError(IndexedPiece._NOT_AN_ANALYZER.format(cls_list))

    def get_data(self, analyzer_cls, settings=None, data=None, known_opus=False):
        """
        Get the results of an Experimenter or Indexer run on this :class:`IndexedPiece`.

        :param analyzer_cls: The analyzers to run, in the order they should be run.
        :type analyzer_cls: list of type
        :param settings: Settings to be used with the analyzers.
        :type settings: dict
        :param data: Input data for the first analyzer to run. If the first indexer uses a
            :class:`~music21.stream.Score`, you should leave this as ``None``.
        :type data: list of :class:`pandas.Series` or :class:`pandas.DataFrame`
        :param known_opus: Whether the caller knows this file will be imported as a
            :class:`music21.stream.Opus` object. Refer to the "Note about Opus Objects" below.
        :type known_opus: boolean

        :returns: Results of the analyzer.
        :rtype: :class:`pandas.DataFrame` or list of :class:`pandas.Series`

        :raises: :exc:`TypeError` if the ``analyzer_cls`` is invalid or cannot be found.
        :raises: :exc:`RuntimeError` if the first analyzer class in ``analyzer_cls`` does not use
            :class:`~music21.stream.Score` objects, and ``data`` is ``None``.
        :raises: :exc:`~vis.models.indexed_piece.OpusWarning` if the file imports as a
            :class:`music21.stream.Opus` object and ``known_opus`` is ``False``.
        :raises: :exc:`~vis.models.indexed_piece.OpusWarning` if ``known_opus`` is ``True`` but the
            file does not import as an :class:`Opus`.

        **Note about Opus Objects**

        Correctly importing :class:`~music21.stream.Opus` objects is a little awkward because
        we only know a file imports to an :class:`Opus` *after* we import it, but an
        :class:`Opus` should be treated as multiple :class:`IndexedPiece` objects.

        We recommend you handle :class:`Opus` objects like this:

        #. Try to call :meth:`get_data` on the :class:`IndexedPiece`.
        #. If :meth:`get_data` raises an :exc:`OpusWarning`, the file contains an :class:`Opus`.
        #. Call :meth:`get_data` again with the ``known_opus`` parameter set to ``True``.
        #. :meth:`get_data` will return multiple :class:`IndexedPiece` objects, each \
            corresponding to a :class:`~music21.stream.Score` held in the :class:`Opus`.
        #. Then call :meth:`get_data` on the new :class:`IndexedPiece` objects to get the results \
            initially desired.

        Refer to the source code for :meth:`vis.workflow.WorkflowManager.load` for an example
        implementation.
        """
        IndexedPiece._type_verifier(analyzer_cls)
        if data is None:
            if analyzer_cls[0] is noterest.NoteRestIndexer:
                data = self._get_note_rest_index(known_opus=known_opus)
            # NB: Experimenter subclasses don't have "required_score_type"
            elif (hasattr(analyzer_cls[0], 'required_score_type') and
                  analyzer_cls[0].required_score_type == 'stream.Part'):
                data = self._import_score(known_opus=known_opus)
                data = [x for x in data.parts]  # Indexers require a list of Parts
            elif (hasattr(analyzer_cls[0], 'required_score_type') and
                  analyzer_cls[0].required_score_type == 'stream.Score'):
                data = [self._import_score(known_opus=known_opus)]
            else:
                raise RuntimeError(IndexedPiece._MISSING_DATA.format(analyzer_cls[0]))
        if len(analyzer_cls) > 1:
            if analyzer_cls[0] is noterest.NoteRestIndexer:
                return self.get_data(analyzer_cls[1:], settings, data)
            return self.get_data(analyzer_cls[1:], settings, analyzer_cls[0](data, settings).run())
        else:
            if analyzer_cls[0] is noterest.NoteRestIndexer:
                return data
            else:
                return analyzer_cls[0](data, settings).run()
