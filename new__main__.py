#! /usr/bin/python
# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Program Name:              vis
# Program Description:       Measures sequences of vertical intervals.
#
# Filename: __main__.py
# Purpose: Provide the graphical interface for vis.
#
# Attribution:  Based on the 'harrisonHarmony.py' module available at...
#               https://github.com/crantila/harrisonHarmony/
#
# Copyright (C) 2012 Christopher Antila
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------

# Python
import sys
from os.path import isfile, join, splitext
from os import walk
from itertools import chain
# PyQt4
from PyQt4 import Qt, QtCore, QtGui
#from PyQt4.QtCore import pyqtSlot, QObject
# music21
from music21 import converter
from music21.converter import ConverterException, ConverterFileException
# vis
from gui_files.Ui_select_offset import Ui_Select_Offset
from gui_files.Ui_new_main_window import Ui_MainWindow
#from gui_files.Ui_select_voices import Ui_select_voices
from problems import NonsensicalInputError, MissingInformationError
from Vertical_Interval_Statistics import Vertical_Interval_Statistics



# Subclass for Signal Handling -------------------------------------------------
class Vis_MainWindow( Ui_MainWindow ):

   # "self" Objects
   #---------------
   # self.gui_file_list :
   # self.gui_pieces_list :
   # self.statistics
   # self.piece_checkboxes
   # -- Index values for columns in self.gui_pieces_list --
   # self.model_offset

   # Create the settings and statistics objects for vis.
   def setup_vis( self ):
      self.gui_file_list.setModel( self.analysis_files )
      self.gui_pieces_list.setModel( self.analysis_pieces )
      self.statistics = Vertical_Interval_Statistics()
      # Hold a list of checkboxes that represent the parts in a piece
      self.piece_checkboxes = None

      # These be the index values for columns in the list-of-pieces model.
      self.model_filename = 0 # filename of the piece
      self.model_score = 1 # Score object and title
      self.model_parts_list = 2 # list of names of parts
      self.model_offset = 3 # offset Duration between vertical intervals
      self.model_n = 4 # values of "n" to find
      self.model_compare_parts = 5 # list of two-element lists of part indices



   # Link all the signals with their methods.
   def setup_signals( self ):
      self.tool_analyze()
      self.btn_choose_files.clicked.connect( self.tool_choose )
      self.btn_about.clicked.connect( self.tool_about )
      self.btn_analyze.clicked.connect( self.tool_analyze )
      self.btn_show.clicked.connect( self.tool_show )
      self.rdo_intervals.clicked.connect( self.choose_intervals )
      self.rdo_ngrams.clicked.connect( self.choose_ngrams )
      self.rdo_targeted_score.clicked.connect( self.choose_targeted_score )
      self.rdo_chart.clicked.connect( self.unchoose_targeted_score )
      self.rdo_score.clicked.connect( self.unchoose_targeted_score )
      self.rdo_list.clicked.connect( self.unchoose_targeted_score )
      self.btn_dir_add.clicked.connect( self.add_dir )
      self.btn_file_add.clicked.connect( self.get_files )
      self.btn_file_remove.clicked.connect( self.remove_files )
      self.chk_all_voice_combos.stateChanged.connect( self.adjust_bs )
      self.btn_step1.clicked.connect( self.progress_to_assemble )
      self.btn_load_statistics.clicked.connect( self.load_statistics )
      self.gui_pieces_list.clicked.connect( self.update_pieces_selection )
      self.chk_all_voice_combos.clicked.connect( self.all_voice_combos )
      self.chk_basso_seguente.clicked.connect( self.chose_bs )
      self.btn_add_check_combo.clicked.connect( self.add_parts_combination )
      self.line_compare_these_parts.editingFinished.connect( self.add_parts_combo_by_lineEdit )
      self.line_values_of_n.editingFinished.connect( self.update_values_of_n )
      self.line_offset_interval.editingFinished.connect( self.update_offset_interval )
      self.btn_choose_note.clicked.connect( self.launch_offset_selection )

   # GUI Things (Main Menu Toolbar) ------------------------
   def tool_choose( self ):
      self.main_screen.setCurrentWidget( self.page_choose )
      self.btn_analyze.setEnabled( False )

   def tool_analyze( self ):
      self.main_screen.setCurrentWidget( self.page_analyze )

   def tool_working( self ):
      self.main_screen.setCurrentWidget( self.page_working )

   def tool_show( self ):
      self.main_screen.setCurrentWidget( self.page_show )

   def tool_about( self ):
      self.main_screen.setCurrentWidget( self.page_about )

   # GUI Things ("Show" Panel) -----------------------------
   def choose_intervals( self ):
      self.groupBox_n.setEnabled( False )
      self.lbl_most_common.setText( 'most common intervals.' )
      self.lbl_exclude_if_fewer.setText( 'Exclude intervals with fewer than' )
      self.rdo_name.setText( 'interval' )

   def choose_ngrams( self ):
      self.groupBox_n.setEnabled( True )
      self.lbl_most_common.setText( 'most common n-grams.' )
      self.lbl_exclude_if_fewer.setText( 'Exclude n-grams with fewer than' )
      self.rdo_name.setText( 'n-gram' )

   def choose_targeted_score( self ):
      self.groupBox_sorted_by.setEnabled( False )
      self.groupBox_sort_order.setEnabled( False )
      self.groupBox_targeted_score.setEnabled( True )

   def unchoose_targeted_score( self ):
      self.groupBox_sorted_by.setEnabled( True )
      self.groupBox_sort_order.setEnabled( True )
      self.groupBox_targeted_score.setEnabled( False )

   # GUI Things ("Choose Files" Panel) ---------------------
   def add_dir( self ):
      d = QtGui.QFileDialog.getExistingDirectory(\
          None,
          "Choose Directory to Analyze",
          '',
          QtGui.QFileDialog.ShowDirsOnly)
      d = str(d)
      extensions = ['.mid','.midi','.mxl','.krn','.xml','.md']
      possible_files = chain(*[[join(path,fp) for fp in files if
                              splitext(fp)[1] in extensions]
                             for path,names,files in walk(d)])
      self.add_files(possible_files)

   def get_files( self ):
      # Get the list of files to add
      possible_files = QtGui.QFileDialog.getOpenFileNames(\
         None,
         "Choose Files to Analyze",
         '',
         '*.mid *.midi *.mxl *.krn *.xml *.md',
         None)
      self.add_files(possible_files)

   def add_files( self, possible_files ):
      # Make sure we don't add files that are already there
      list_of_files = [fp for fp in possible_files if
                       not self.analysis_files.alreadyThere(fp)]

      # Add the right number of rows to the list
      start_row = self.analysis_files.rowCount()
      self.analysis_files.insertRows( start_row, len(list_of_files), )

      # Add the files to the model
      i = start_row
      for file in list_of_files:
         index = self.analysis_files.createIndex( i, 0 )
         self.analysis_files.setData( index, file, QtCore.Qt.EditRole )
         i += 1
   # End add_files()

   def remove_files( self ):
      # get a list of QModelIndex objects to remove
      to_remove = self.gui_file_list.selectedIndexes()

      # remove them
      for file in to_remove:
         self.analysis_files.removeRows( file.row(), 1 )

   def progress_to_assemble( self ):
      # move the GUI to the "working" panel
      failed_files = []
      self.tool_working()
      self.progress_bar.setMinimum(0)
      self.progress_bar.setMaximum(self.analysis_files.rowCount())
      for i,fp in enumerate(list(self.analysis_files.iterator()),start=1):
         self.lbl_status_text.setText("Please wait... importing "+fp)
         score = None
         try:
            score = converter.parse(str(fp))
         except (ConverterException,ConverterFileException) as e:
            failed_files.append(fp)
            continue
         last = self.analysis_pieces.rowCount()
         self.analysis_pieces.insertRows(last,1)
         index = self.analysis_pieces.createIndex(last,0)
         self.analysis_pieces.setData(index,fp,QtCore.Qt.EditRole)
         index = self.analysis_pieces.createIndex(last,1)
         self.analysis_pieces.setData(index,score,QtCore.Qt.EditRole)
         index = self.analysis_pieces.createIndex(last,2)
         self.analysis_pieces.setData(index,[p.id for p in score.parts],QtCore.Qt.EditRole)
         self.progress_bar.setValue(i)

      # finally, move the GUI to the "assemble" panel
      self.btn_analyze.setEnabled( True )
      self.btn_analyze.setChecked( True )
      self.tool_analyze()

   # GUI Things ("Assemble" Panel) -------------------------
   def load_statistics( self ):
      statistics_file = QtGui.QFileDialog.getOpenFileName(\
                        self.centralwidget,\
                        "Choose Statistics File",\
                        "",
                        "JSON Files (*.json)",
                        None)
      if isfile(statistics_file):
         fp = open(statistics_file,"r")
         json_string = fp.read()
         new_vis = None
         try:
            new_vis = Vertical_Interval_Statistics.from_json(json_string)
         except (NonsensicalInputError, MissingInformationError) as e:
            error_dialog = QtGui.QErrorMessage()
            error_dialog.showMessage('The selected statistics file is not valid: '+str(e))
            error_dialog.exec_()
            return
         self.statistics.extend(new_vis)

   def adjust_bs( self ):
      # Adjusts the "basso seguente" checkbox depending on whether "all
      # combinations" is selected
      if self.chk_all_voice_combos.isChecked():
         self.chk_basso_seguente.setText( 'Every part against Basso Seguente' )
      else:
         self.chk_basso_seguente.setText( 'Basso Seguente' )

   def all_voice_combos( self ):
      # Are we enabling "all" or disabling?
      if self.chk_all_voice_combos.isChecked():
         # Enabling
         # Are there specific part names? If so, disable those checkboxes
         if self.piece_checkboxes is not None:
            for box in self.piece_checkboxes:
               box.setEnabled( False )

         self.btn_add_check_combo.setEnabled( False )
         part_spec = '[all]'
      else:
         # Disabling
         # Are there specific part names? If so, enable those checkboxes
         if self.piece_checkboxes is not None:
            for box in self.piece_checkboxes:
               box.setEnabled( True )

         self.btn_add_check_combo.setEnabled( True )
         part_spec = '(no selection)'

      self.update_parts_selection( part_spec )

   def chose_bs( self ):
      # When somebody chooses the "basso seguente" checkbox, if "all" is also
      # selected, we should update the QLineEdit
      if self.chk_all_voice_combos.isChecked():
         if self.chk_basso_seguente.isChecked():
            part_spec = '[all,bs]'
         else:
            part_spec = '[all]'

         self.update_parts_selection( part_spec )

   def add_parts_combination( self ):
      '''
      When users choose the "Add Combination" button to add the currently
      selected part combination to the list of parts to analyze.
      '''

      # If there are no named parts, we can't do this
      if self.piece_checkboxes is None:
         return None

      # Hold indices of the selected checkboxes
      selected_checkboxes = [i for i,cb in enumerate(self.piece_checkboxes)
                             if cb.isChecked()]

      # Hold the vis-format specification
      vis_format = None

      # How many checkboxes are selected?
      if 1 == len(selected_checkboxes):
         # If we have one checkbox and bs, okay
         if self.chk_basso_seguente.isChecked():
            vis_format = '[' + str(selected_checkboxes[0]) + ',bs]'
         # Otherwise, complain
         else:
            QtGui.QMessageBox.warning(None,
               "Unusable Part Selection",
               "Please select two parts at a time.",
               QtGui.QMessageBox.StandardButtons(\
                  QtGui.QMessageBox.Ok),
               QtGui.QMessageBox.Ok)
      elif 2 == len(selected_checkboxes):
         # Is "basso seguente" also selected?
         if self.chk_basso_seguente.isChecked():
            # That's not good
            QtGui.QMessageBox.warning(None,
               "Cannot Add Part",
               "When you choose \"basso seguente,\" you can only choose one other part.",
               QtGui.QMessageBox.StandardButtons(\
                  QtGui.QMessageBox.Ok),
               QtGui.QMessageBox.Ok)
         else:
            # We have two parts; choose them.
            vis_format = '[' + str(selected_checkboxes[0]) + ',' + \
                               str(selected_checkboxes[1]) + ']'
      else:
         # Greater or fewer than two parts?
         QtGui.QMessageBox.warning(None,
            "Unusable Part Selection",
            "Please select two parts at a time.",
            QtGui.QMessageBox.StandardButtons(\
               QtGui.QMessageBox.Ok),
            QtGui.QMessageBox.Ok)

      # Now update the lists
      if vis_format is not None:
         # Hold the new part-combinations specification
         new_spec = ''

         # What's the current specification?
         curr_spec = str(self.line_compare_these_parts.text())

         # Is curr_spec the default filler?
         if 'e.g., [0,3] or [[0,3],[1,3]]' == curr_spec or \
            '(no selection)' == curr_spec or \
            '' == curr_spec:
            # Then just make a new one
            new_spec = '[' + vis_format + ']'

            # Update the parts selection
            self.update_parts_selection( new_spec )
         # Does curr_spec contain vis_format?
         elif vis_format in curr_spec:
            pass
         # Else we must add this new thing
         else:
            # Otherwise, we should remove the final ']' in the list, and put
            # our new combo on the end
            new_spec = curr_spec[:-1] + ',' + vis_format + ']'

            # Update the parts selection
            self.update_parts_selection( new_spec )

      # Also clear the part-selection checkboxes
      self.chk_basso_seguente.setChecked( False )
      for box in self.piece_checkboxes:
         box.setChecked( False )
   # End add_parts_combination() ---------------------------

   def add_parts_combo_by_lineEdit( self ):
      # TODO: input validation using QValidator

      # For now, just take the contents of the line_compare_these_parts and
      # put it in the pieces
      self.update_parts_selection( str(self.line_compare_these_parts.text()) )

   def update_parts_selection( self, part_spec ):
      '''
      Updates line_compare_these_parts and the model data for all selected
      pieces so that the "parts to compare" contains part_spec.
      '''

      # update the UI
      self.line_compare_these_parts.setText( part_spec )

      # Update the selected pieces
      # get the list of selected cells... for each one that is the "voices"
      # column(), set it to the thing specified
      selected_cells = self.gui_pieces_list.selectedIndexes()
      for cell in selected_cells:
         if self.model_compare_parts == cell.column():
            self.analysis_pieces.setData( cell, part_spec, QtCore.Qt.EditRole )

   def update_values_of_n( self ):
      # TODO: input validation using QValidator

      # For now, just take the contents of line_values_of_n and put it in
      # the pieces
      new_n = str(self.line_values_of_n.text())

      # Update the selected pieces
      # get the list of selected cells... for each one that is the "n"
      # column(), set it to the thing specified
      selected_cells = self.gui_pieces_list.selectedIndexes()
      for cell in selected_cells:
         if self.model_n == cell.column():
            self.analysis_pieces.setData( cell, new_n, QtCore.Qt.EditRole )

   def update_offset_interval( self ):
      # TODO: input validation using QValidator

      # For now, just take the contents of line_values_of_n and put it in
      # the pieces
      new_offset_interval = str(self.line_offset_interval.text())

      # Update the selected pieces
      # get the list of selected cells... for each one that is the "n"
      # column(), set it to the thing specified
      selected_cells = self.gui_pieces_list.selectedIndexes()
      for cell in selected_cells:
         if self.model_offset == cell.column():
            self.analysis_pieces.setData( cell, new_offset_interval, QtCore.Qt.EditRole )

   def update_pieces_selection( self ):
      # TODO: finish the other things for this method
      # When the user changes the piece(s) selected in self.gui_pieces_list

      # Which piece is/pieces are selected?
      currently_selected = self.gui_pieces_list.selectedIndexes()

      # NB: we get a list of all the cells selected, and this is definitely done
      # in rows, so because each row has 6 things, if we have 6 cells, it means
      # we have only one row... but more than 6 cells means more than one row
      if len(currently_selected) == 0:
         # (1) Enable all the controls
         self.line_values_of_n.setEnabled( False )
         self.line_offset_interval.setEnabled( False )
         self.btn_choose_note.setEnabled( False )
         self.line_compare_these_parts.setEnabled( False )
         self.chk_all_voice_combos.setEnabled( False )
         self.chk_basso_seguente.setEnabled( False )
         self.btn_add_check_combo.setEnabled( False )
         # (2) Remove the part list
         if self.piece_checkboxes is not None:
            for part in self.piece_checkboxes:
               self.verticalLayout_22.removeWidget( part )
            self.piece_checkboxes = None
      elif len(currently_selected) > 6:
         # Multiple pieces selected... possible customization
         # (1) Enable all the controls
         self.line_values_of_n.setEnabled( True )
         self.line_offset_interval.setEnabled( True )
         self.btn_choose_note.setEnabled( True )
         self.line_compare_these_parts.setEnabled( True )
         self.chk_all_voice_combos.setEnabled( True )
         self.chk_basso_seguente.setEnabled( True )
         self.btn_add_check_combo.setEnabled( True )
         # (2) if the pieces have the same part names, display them
         first_parts = None
         for cell in currently_selected:
            if self.model_parts_list == cell.column():
               if first_parts is None:
                  first_parts = self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject()
               elif first_parts == self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject():
                  continue
               else:
                  first_parts = ''
                  break
         if '' != first_parts:
            # Then they all have the same name, so we can use them
            self.update_part_checkboxes( currently_selected )
         else:
            # Then they don't all have the same name.
            self.chk_all_voice_combos.setEnabled( False )
            self.chk_basso_seguente.setEnabled( False )
            #self.all_voice_combos()
            self.adjust_bs()
         # (3) if the pieces have the same offset interval, display it
         first_offset = None
         for cell in currently_selected:
            if self.model_offset == cell.column():
               if first_offset is None:
                  first_offset = self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject()
               elif first_offset == self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject():
                  continue
               else:
                  first_offset = ''
                  break
         self.line_offset_interval.setText( str(first_offset) )
         # (4) if the pieces have the same values of n, display them
         first_n = None
         for cell in currently_selected:
            if self.model_n == cell.column():
               if first_n is None:
                  first_n = self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject()
               elif first_n == self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject():
                  continue
               else:
                  first_n = ''
                  break
         self.line_values_of_n.setText( first_n )
         # (5) Update "Compare These Parts"
         first_comp = None
         for cell in currently_selected:
            if self.model_compare_parts == cell.column():
               if first_comp is None:
                  first_comp = self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject()
               elif first_comp == self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject():
                  continue
               else:
                  first_comp = ''
                  break
         if '' == first_comp:
            # Multiple parts have different specs
            self.line_compare_these_parts.setText( '' )
            self.chk_all_voice_combos.setChecked( False )
            self.chk_basso_seguente.setChecked( False )
            self.adjust_bs()
         else:
            # Multiple parts have the same spec
            self.update_comparison_parts( currently_selected )
      else:
         # Only one piece... customize for it
         # (1) Enable all the controls
         self.line_values_of_n.setEnabled( True )
         self.line_offset_interval.setEnabled( True )
         self.btn_choose_note.setEnabled( True )
         self.line_compare_these_parts.setEnabled( True )
         self.chk_all_voice_combos.setEnabled( True )
         self.chk_basso_seguente.setEnabled( True )
         self.btn_add_check_combo.setEnabled( True )
         # (2) Populate the part list
         self.update_part_checkboxes( currently_selected )
         # (3) Update "values of n"
         for cell in currently_selected:
            if self.model_n == cell.column():
               self.line_values_of_n.setText( str(self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject()) )
               break
         # (4) Update "offset interval"
         for cell in currently_selected:
            if self.model_offset == cell.column():
               self.line_offset_interval.setText( str(self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject()) )
               break
         # (5) Update "Compare These Parts"
         self.update_comparison_parts( currently_selected )
   # End update_pieces_selection() -------------------------

   def update_comparison_parts( self, currently_selected ):
      '''
      When a different part combination is selected, call this method to update
      the "All Combinations" and "Basso Seguente" checkboxes.

      You should only call this method if all of the selected pieces have the
      same part names (which is true when only one part is selected).

      The argument should be a list of the currently selected cells.
      '''

      for cell in currently_selected:
         if self.model_compare_parts == cell.column():
            comparison_parts = str(self.analysis_pieces.data( cell, QtCore.Qt.DisplayRole ).toPyObject())
            self.line_compare_these_parts.setText( comparison_parts )
            if '[all]' == comparison_parts:
               self.chk_all_voice_combos.setChecked( True )
               self.chk_basso_seguente.setChecked( False )
               # Update the QCheckBox for "All Combinations" and "Basso Seguente"
               self.all_voice_combos()
               self.chose_bs()
            elif '[all,bs]' == comparison_parts:
               self.chk_all_voice_combos.setChecked( True )
               self.chk_basso_seguente.setChecked( True )
               # Update the QCheckBox for "All Combinations" and "Basso Seguente"
               self.all_voice_combos()
               self.chose_bs()
            else:
               self.chk_all_voice_combos.setChecked( False )
               self.chk_basso_seguente.setChecked( False )
            break

      # Adjust the text for "Basso Seguente," if needed
      self.adjust_bs()
   # End update_comparison_parts() -------------------------

   def update_part_checkboxes( self, currently_selected ):
      '''
      Update the part-selection QCheckBox objects to reflect the currently
      selected part(s).

      You should only call this method if all of the selected pieces have the
      same part names (which is true when only one part is selected).

      The argument should be a list of the currently selected cells.
      '''

      # (1) Remove previous checkboxes from the layout
      if self.piece_checkboxes is not None:
         for part in self.piece_checkboxes:
            self.verticalLayout_22.removeWidget( part )
         self.piece_checkboxes = None

      # (2) Get the list of parts
      list_of_parts = None
      for cell in currently_selected:
         if self.model_parts_list == cell.column():
            list_of_parts = self.analysis_pieces.data( cell, 'raw_list' ).toPyObject()
            break

      # (3) Put up a checkbox for each part
      self.piece_checkboxes = []
      for part_name in list_of_parts:
         # "n_c_b" means "new check box"
         n_c_b = QtGui.QCheckBox( self.widget_5 )
         n_c_b.setObjectName( "chk_" + part_name )
         n_c_b.setText( part_name )
         self.piece_checkboxes.append( n_c_b )

      # (4) Add all the widgets to the layout
      for part in self.piece_checkboxes:
         self.verticalLayout_22.addWidget( part )
   # End update_part_checkboxes() --------------------------

   def launch_offset_selection( self ):
      # Launch the offset-selection QDialog
      selector = Vis_Select_Offset()
      chosen_offset = selector.trigger()

      # Update the QLineEdit
      self.line_offset_interval.setText( str(chosen_offset) )

      # Set values in the model
      selected_cells = self.gui_pieces_list.selectedIndexes()
      for cell in selected_cells:
         if self.model_offset == cell.column():
            self.analysis_pieces.setData( cell, chosen_offset, QtCore.Qt.EditRole )

# Model for "Choose Files" Panel -----------------------------------------------
class List_of_Files( QtCore.QAbstractListModel ):
   def __init__( self, parent=None, *args ):
      QtCore.QAbstractListModel.__init__(self, parent, *args)
      self.files = []

   def rowCount( self, parent=QtCore.QModelIndex() ):
      return len( self.files )

   def data(self, index, role):
      if index.isValid() and QtCore.Qt.DisplayRole == role:
         return QtCore.QVariant( self.files[index.row()] )
      else:
         return QtCore.QVariant()

   # NB: I *should* implement these, but I don't know how, so for now I won't
   #def headerData( self ):
      #pass

   #def flags():
      #pass

   def setData( self, index, value, role ):
      if QtCore.Qt.EditRole == role:
         self.files[index.row()] = value
         self.dataChanged.emit( index, index )
         return True
      else:
         return False

   def insertRows( self, row, count, parent=QtCore.QModelIndex() ):
      self.beginInsertRows( parent, row, row+count )
      new_files = self.files[:row]
      for zed in xrange( count ):
         new_files.append( '' )
      new_files += self.files[row:]
      self.files = new_files
      self.endInsertRows()

   def alreadyThere( self, candidate ):
      '''
      Tests whether 'candidate' is already present in this list of files.
      '''
      return candidate in self.files

   def iterator( self ):
      for f in self.files:
         yield f

   def removeRows( self, row, count, parent=QtCore.QModelIndex() ):
      self.beginRemoveRows( parent, row, row )
      self.files = self.files[:row] + self.files[row+count:]
      self.endRemoveRows()
# End Class List_of_Files ------------------------------------------------------



# Model for "Assemble" Panel -----------------------------------------------
class List_of_Pieces( QtCore.QAbstractTableModel ):
   # Here's the data model:
   # self.pieces : a list of lists. For each sub-list...
   #    sublist[0] : filename
   #    sublist[1] : a music21 score object corresponding to the filename
   #    sublist[2] : list of names of parts in the score
   #    sublist[3] : offset interval
   #    sublist[4] : list of values of n to look for
   #    sublist[5] : list of pairs of indices for parts

   def __init__( self, parent=QtCore.QModelIndex() ):
      QtCore.QAbstractTableModel.__init__( self, parent )
      # "Constant" values for what each column is and the index blah
      # NOTE: When you change these, be sure to change them in Vis_MainWindow too!
      self.model_filename = 0 # filename of the piece
      self.model_score = 1 # Score object and title
      self.model_parts_list = 2 # list of names of parts
      self.model_offset = 3 # offset Duration between vertical intervals
      self.model_n = 4 # values of "n" to find
      self.model_compare_parts = 5 # list of two-element lists of part indices

      self.pieces = []

   def rowCount( self, parent=QtCore.QModelIndex() ):
      return len(self.pieces)

   def columnCount( self, parent=QtCore.QModelIndex() ):
      # There are 6 columns (see "data model" above)
      return 6

   def data(self, index, role):
      if index.isValid():
         if QtCore.Qt.DisplayRole == role:
            if self.model_score == index.column():
               score = self.pieces[index.row()][index.column()]
               if score.metadata is not None:
                  return QtCore.QVariant( score.metadata.title )
               else:
                  return QtCore.QVariant('')
            elif self.model_parts_list == index.column():
               # this is for the part names
               return QtCore.QVariant( str([str(p) for p in self.pieces[index.row()][index.column()]])[1:-1] )
            elif self.model_n == index.column():
               return ",".join(str(n) for n in self.pieces[index.row()][index.column()])
            else:
               return QtCore.QVariant( self.pieces[index.row()][index.column()] )
         elif 'raw_list' == role:
            return QtCore.QVariant( self.pieces[index.row()][index.column()] )
         else:
            return QtCore.QVariant()

   def headerData( self, section, orientation, role ):
      header_names = ['Path', 'Title', 'List of Part Names', 'Offset', 'n', \
                      'Compare These Parts']

      if QtCore.Qt.Horizontal == orientation and QtCore.Qt.DisplayRole == role:
         return header_names[section]
      else:
         return QtCore.QVariant()

   def setData( self, index, value, role ):
      # NB: use this pattern
      # index = self.analysis_pieces.createIndex( 0, 1 )
      # self.analysis_pieces.setData( index, 'ballz', QtCore.Qt.EditRole )
      if QtCore.Qt.EditRole == role:
         self.pieces[index.row()][index.column()] = value
         self.dataChanged.emit( index, index )
         return True
      else:
         return False

   def insertRows( self, row, count, parent=QtCore.QModelIndex() ):
      self.beginInsertRows( parent, row, row+count )
      for zed in xrange(count):
         self.pieces.insert(row,['',None,[],0.5,[2],[]])
      self.endInsertRows()

   def removeRows( self, row, count, parent=QtCore.QModelIndex() ):
      self.beginRemoveRows( parent, row, row+count )
      self.pieces = self.pieces[:row] + self.pieces[row+count:]
      self.endRemoveRows()
# End Class List_of_Pieces ------------------------------------------------------



class Vis_Select_Offset( Ui_Select_Offset ):
   '''
   Display and assign actions for the offset-selection window.
   '''

   def trigger( self ):
      # UI setup stuff
      self.select_offset = QtGui.QDialog()
      self.setupUi( self.select_offset )

      # Setup signals
      self.btn_submit.clicked.connect( self.submit_button )
      self.btn_8.clicked.connect( self.button_8 )
      self.btn_4.clicked.connect( self.button_4 )
      self.btn_2.clicked.connect( self.button_2 )
      self.btn_1.clicked.connect( self.button_1 )
      self.btn_0_5.clicked.connect( self.button_0_5 )
      self.btn_0_25.clicked.connect( self.button_0_25 )
      self.btn_0_125.clicked.connect( self.button_0_125 )
      self.btn_0_0625.clicked.connect( self.button_0_0625 )

      # Variable to hold the currently-selected duration
      self.current_duration = 0.5

      # Show the form!
      self.select_offset.exec_()

      # (User chooses stuff)

      # Return the currently-selected duration
      return self.current_duration

   def submit_button( self ):
      self.select_offset.done( 0 )

   def button_8( self ):
      self.current_duration = 8.0
      self.line_music21_duration.setText( str(self.current_duration) )

   def button_4( self ):
      self.current_duration = 4.0
      self.line_music21_duration.setText( str(self.current_duration) )

   def button_2( self ):
      self.current_duration = 2.0
      self.line_music21_duration.setText( str(self.current_duration) )

   def button_1( self ):
      self.current_duration = 1.0
      self.line_music21_duration.setText( str(self.current_duration) )

   def button_0_5( self ):
      self.current_duration = 0.5
      self.line_music21_duration.setText( str(self.current_duration) )

   def button_0_25( self ):
      self.current_duration = 0.25
      self.line_music21_duration.setText( str(self.current_duration) )

   def button_0_125( self ):
      self.current_duration = 0.125
      self.line_music21_duration.setText( str(self.current_duration) )

   def button_0_0625( self ):
      self.current_duration = 0.0625
      self.line_music21_duration.setText( str(self.current_duration) )
# End Class Vis_Select_Offset --------------------------------------------------



# "Main" Method ----------------------------------------------------------------
def main():
   # Standard stuff
   app = QtGui.QApplication( sys.argv )
   MainWindow = QtGui.QMainWindow()
   vis_ui = Vis_MainWindow()
   vis_ui.setupUi( MainWindow )
   # vis stuff
   vis_ui.analysis_files = List_of_Files( vis_ui.gui_file_list )
   vis_ui.analysis_pieces = List_of_Pieces( vis_ui.gui_pieces_list )
   vis_ui.setup_vis()
   vis_ui.setup_signals()
   vis_ui.tool_choose()
   # Standard stuff
   MainWindow.show()
   sys.exit( app.exec_() )

if __name__ == '__main__':
   main()
