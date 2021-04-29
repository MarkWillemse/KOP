
# to install libraries, go to File-> settings-> python interpreter -> search for libraries and install
import math
#from plxscripting.easy import *
import pandas as pd
import os
import io
import numpy as np
import easygui
## 00. setup Remote Scripting server for PLAXIS Input
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtChart import *
import itertools
import csv
password = '~K?~y352M91S?N/e'
#s_i, g_i = new_server('localhost', 10000, password=password)

class Create_Plaxis_Files(QTabWidget):   #define class
    """"A class created to set up Plaxis files in a fast way, divided in Tabs"""
    def __init__(self):                        #create objects
        super().__init__()                  #is this absolutely necessary?

        """"Booleans"""
        self.Boolean1 = False                 #create attributes, kan me voorstellen dat dit allemaal knoppen zijn in gui die als aangeklikt worden geactiveert
        self.Boolean2 = False
        self.Boolean3 = False
        self.Boolean4 = False
        self.Boolean5 = False
        self.HasProgramStarted = False
        self.BooleanThickness_1 = False
        self.BooleanThickness_2 = False
        self.BooleanThickness_3 = False     #some attributes are Booleans
        self.BooleanCollapse = True
   

        """"Empty lists"""
        self.Layer_Values = []              #some attributes are lists
        self.Plaxis_Json_Files = []
        self.Plaxis_JsonFileNames = []

        """"Functions"""
        self.barChart()
        self.Tab3()
        self.Tab4()
        self.Tab5()
        self.setFont(QFont("verbana", 16))

        self.TabCounter = 0

        self.HasProgramStarted = True
        self.Tab5_1_2_Group.setVisible(False)

    def Fill_ComboBox(self):                  #functions in the class
        self.SoilChoiceQB_1.clear()
        List_SoilTypes = [] # List to check for double soil types
        Table = TableWidget()
        if Table.DatabaseOK == True:
            File = Table.Database_File
            self.Boolean5 = True
            for row in range(int(len(File.index) - 2)):
                SoilType = File.iat[row + 2, 0]
                if not pd.isnull(SoilType) == True:
                    if str(SoilType).lower() in List_SoilTypes:
                        self.SoilChoiceQB_1.clear()
                        break
                    else:
                        List_SoilTypes.append(str(SoilType).lower())
                        self.SoilChoiceQB_1.addItem((File.iat[row + 2, 0]))
                else:
                    pass

    def Add_SoilLayer(self):
        if self.Boolean5 == True:
            self.Layer_Values = [float(i) for i in self.Layer_Values]
            Grondsoort = self.SoilChoiceQB_1.currentText()
            Laagdikte = str(self.Soil_Boundary_1.text())
            Laagdikte = Laagdikte.replace(",", ".")
            if any(c.isalpha() for c in Laagdikte) == True:        #isalpha() is true if all characters are letters
                QMessageBox.information(self, "Error", "Your boundary for this layer is not correctly specified")
            else:
                Laagdikte = (float(Laagdikte))
                if Laagdikte in self.Layer_Values:
                    QMessageBox.information(self, "Error", "Your specified boundary already exists")
                else:
                    self.Soil_Profile.insertRow(self.Soil_Profile.rowCount())
                    self.Soil_Profile.setItem(self.Soil_Profile.rowCount()-1, 0, QTableWidgetItem(str(Grondsoort)))
                    self.Soil_Profile.setItem(self.Soil_Profile.rowCount()-1, 1, QTableWidgetItem(str(Laagdikte)))
                    self.Layer_Values.append(Laagdikte)

                    self.SortLayers()
                    self.barChart()

    def Remove_Soil(self):
        if int(self.RemoveSoilLayer.value()) <= int(self.Soil_Profile.rowCount()):
            row_toremove = int(self.RemoveSoilLayer.value() - 1)
            self.Soil_Profile.removeRow(row_toremove)
            self.Layer_Values = [float(i) for i in self.Layer_Values]
            self.Layer_Values.sort(reverse=True)
            del self.Layer_Values[int(self.RemoveSoilLayer.value()-1)]
            self.barChart()
        else:

            QMessageBox.information(self, "Error", "The layer you try to remove does not exist")

    def SortLayers(self):

        number_of_rows = self.Soil_Profile.rowCount() #sqlite
        number_of_columns = self.Soil_Profile.columnCount()

        tmp_df = pd.DataFrame(columns=['Grondsoort', 'Hoogte'],
                              # Fill columnets
                              index=range(number_of_rows)  # Fill rows
                              )
        for i in range(number_of_rows):
            for j in range(number_of_columns):
                tmp_df.ix[i, j] = self.Soil_Profile.item(i, j).text()

        df = tmp_df[['Grondsoort','Hoogte']].apply(pd.to_numeric,errors='coerce').fillna(tmp_df) #convert from datatype to numeric columns

        dfsort = df.sort_values('Hoogte', ascending=False) #sort dataframe
        counter = 0
        while counter < number_of_rows:
            Grondsoort = dfsort.iloc[counter, 0]
            Hoogte = dfsort.iloc[counter, 1]
            self.Soil_Profile.setItem(counter, 0, QTableWidgetItem(str(Grondsoort)))   #add layers from dataframe to sql
            self.Soil_Profile.setItem(counter, 1, QTableWidgetItem(str(Hoogte)))
            counter += 1

    def change_GWS(self):
        Water_level = str(self.Soil_GWS.text())
        Water_level = Water_level.replace(",", ".")

        self.Soil_GWS_Value.setText(str(Water_level))

    def SaveFile(self):
        if self.Soil_Profile.rowCount() == 0:
            QMessageBox.information(self, "Error", "It looks like you want to save an empty soil profile.")

        else:
            path = QFileDialog.getSaveFileName(self, 'Save CSV', os.getenv('HOME'), 'CSV(*.csv)')
            tail = os.path.split(path[0])
            if path[0] != '':
                with open(path[0], 'w', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    header = ['Grondsoort', 'Hoogte']
                    writer.writerow(header)

                    rownumbers = self.Soil_Profile.rowCount()
                    rowcounter = 0
                    while rowcounter != rownumbers:
                        Grondsoort = self.Soil_Profile.item(rowcounter, 0)
                        Hoogte = self.Soil_Profile.item(rowcounter, 1)

                        rij = []
                        rij.append(str(Hoogte.text()))
                        rij.append(str(Grondsoort.text()))
                        rowcounter += 1
                        writer.writerow(rij)


    def OpenFile(self):
        path = QFileDialog.getOpenFileName(self, 'Laad een correct csv bestand in', filter='csv(*csv)')
        tail = os.path.split(path[0])
        if path[0] != '':
            try:
                with open(path[0], newline='') as csv_file:
                    reader = csv.reader(csv_file)
                    rowcounter = -1
                    self.Soil_Profile.setColumnCount(2)
                    self.Soil_Profile.setRowCount(0)
                    for row in reader:
                        if rowcounter > -1:
                            self.Soil_Profile.insertRow(rowcounter)
                            self.Soil_Profile.setItem(rowcounter, 1, QTableWidgetItem(row[0]))
                            self.Soil_Profile.setItem(rowcounter, 0, QTableWidgetItem(row[1]))
                            self.Layer_Values.append(row[0])
                        rowcounter += 1
                self.barChart()
            except:
                QMessageBox.information(self, "Error", "The file you selected is not correct")
                self.Soil_Profile.setRowCount(0)

    def OpenLoadFileCC(self):
        QMessageBox.information(self, "Error",
                                "The Crawler Crane option is not in use yet")

    def SaveLoadFileCC(self):
        QMessageBox.information(self, "Error",
                                "The Crawler Crane option is not in use yet")

    def SaveLoadFileOR(self):
        W_base = float(self.Widget3_2_1_3.text())
        L_base = float(self.Widget3_2_1_5.text())
        Load_base = float(self.Widget3_2_1_7.text())

        if self.M_Widget_1_1_2.isChecked():
            Dragline_1_CB = 'True'
            Dragline_1_nr = float(self.M_Widget_1_1_1.currentText())
            W_Dragline_1_1 = float(self.M_Widget_1_1_4.text())
            L_Dragline_1_1 = float(self.M_Widget_1_1_6.text())
            T_Dragline_1_1 = float(self.M_Widget_1_1_8.text())
            V_Dragline_1_1 = float(self.M_Widget_1_1_10.text())
        else:
            Dragline_1_CB = 'False'
            Dragline_1_nr = float(1)
            W_Dragline_1_1 = float()
            L_Dragline_1_1 = float()
            T_Dragline_1_1 = float()
            V_Dragline_1_1 =float()


        if Dragline_1_nr == 2:
            W_Dragline_1_2 = float(self.M_Widget_1_2_4.text())
            L_Dragline_1_2 = float(self.M_Widget_1_2_6.text())
            T_Dragline_1_2 = float(self.M_Widget_1_2_8.text())
            V_Dragline_1_2 = float(self.M_Widget_1_2_10.text())
        else:
            W_Dragline_1_2 = float()
            L_Dragline_1_2 = float()
            T_Dragline_1_2 = float()
            V_Dragline_1_2 = float()

        if self.M_Widget_2_1_2.isChecked():
            Dragline_2_CB = 'True'
            Dragline_2_nr = float(self.M_Widget_2_1_1.currentText())
            W_Dragline_2_1 = float(self.M_Widget_2_1_4.text())
            L_Dragline_2_1 = float(self.M_Widget_2_1_6.text())
            T_Dragline_2_1 = float(self.M_Widget_2_1_8.text())
            V_Dragline_2_1 = float(self.M_Widget_2_1_10.text())
        else:
            Dragline_2_CB = 'False'
            Dragline_2_nr = float(1)
            W_Dragline_2_1 = float()
            L_Dragline_2_1 = float()
            T_Dragline_2_1 = float()
            V_Dragline_2_1 = float()

        if Dragline_2_nr == 2:
            W_Dragline_2_2 = float(self.M_Widget_2_2_4.text())
            L_Dragline_2_2 = float(self.M_Widget_2_2_6.text())
            T_Dragline_2_2 = float(self.M_Widget_2_2_8.text())
            V_Dragline_2_2 = float(self.M_Widget_2_2_10.text())
        else:
            W_Dragline_2_2 = float()
            L_Dragline_2_2 = float()
            T_Dragline_2_2 = float()
            V_Dragline_2_2 = float()

        if self.M_Widget_3_1_2.isChecked():
            Dragline_3_CB = 'True'
            Dragline_3_nr = float(self.M_Widget_3_1_1.currentText())
            W_Dragline_3_1 = float(self.M_Widget_3_1_4.text())
            L_Dragline_3_1 = float(self.M_Widget_3_1_6.text())
            T_Dragline_3_1 = float(self.M_Widget_3_1_8.text())
            V_Dragline_3_1 = float(self.M_Widget_3_1_10.text())
        else:
            Dragline_3_CB = 'False'
            Dragline_3_nr = float(1)
            W_Dragline_3_1 = float()
            L_Dragline_3_1 = float()
            T_Dragline_3_1 = float()
            V_Dragline_3_1 = float()

        if Dragline_3_nr == 2:
            W_Dragline_3_2 = float(self.M_Widget_3_2_4.text())
            L_Dragline_3_2 = float(self.M_Widget_3_2_6.text())
            T_Dragline_3_2 = float(self.M_Widget_3_2_8.text())
            V_Dragline_3_2 = float(self.M_Widget_3_2_10.text())
        else:
            W_Dragline_3_2 = float()
            L_Dragline_3_2 = float()
            T_Dragline_3_2 = float()
            V_Dragline_3_2 = float()

        if self.M_Widget_4_1_2.isChecked():
            Dragline_4_CB = 'True'
            Dragline_4_nr = float(self.M_Widget_4_1_1.currentText())
            W_Dragline_4_1 = float(self.M_Widget_4_1_4.text())
            L_Dragline_4_1 = float(self.M_Widget_4_1_6.text())
            T_Dragline_4_1 = float(self.M_Widget_4_1_8.text())
            V_Dragline_4_1 = float(self.M_Widget_4_1_10.text())
        else:
            Dragline_4_CB = 'False'
            Dragline_4_nr = float(1)
            W_Dragline_4_1 = float()
            L_Dragline_4_1 = float()
            T_Dragline_4_1 = float()
            V_Dragline_4_1 = float()

        if Dragline_4_nr == 2:
            W_Dragline_4_2 = float(self.M_Widget_4_2_4.text())
            L_Dragline_4_2 = float(self.M_Widget_4_2_6.text())
            T_Dragline_4_2 = float(self.M_Widget_4_2_8.text())
            V_Dragline_4_2 = float(self.M_Widget_4_2_10.text())
        else:
            W_Dragline_4_2 = float()
            L_Dragline_4_2 = float()
            T_Dragline_4_2 = float()
            V_Dragline_4_2 = float()

        if self.Widget3_2_3_1.isChecked():
            SoilEnh_CB = 'True'
        else:
            SoilEnh_CB = 'False'

        SoilEnh_Soil = str(self.Widget3_2_3_5.currentText())

        if self.Widget3_2_3_7.isChecked():
            SoilEnh_1 = 'True'
        else:
            SoilEnh_1 = 'False'

        if self.Widget3_2_3_8.isChecked():
            SoilEnh_2 = 'True'
        else:
            SoilEnh_2 = 'False'
        if self.Widget3_2_3_9.isChecked():
            SoilEnh_3 = 'True'
        else:
            SoilEnh_3 = 'False'
        if self.Widget3_2_3_10.isChecked():
            SoilEnh_4 = 'True'
            SoilEnh_4_Value = self.Widget3_2_3_11.value()
        else:
            SoilEnh_4 = 'False'
            SoilEnh_4_Value = float()

        GG_Spread_Above = float(self.Widget3_2_4_3.text())
        GG_Spread_Below = float(self.Widget3_2_4_5.text())
        GG_Spread_Soil = str(self.Widget3_2_4_7.currentText())

        if self.Widget3_2_4_1.isChecked():
            GG = 'True'
        else:
            GG = 'False'

        if self.Widget3_2_4_8.isChecked():
            GG_Spread_1 = 'True'
        else:
            GG_Spread_1 = 'False'
        if self.Widget3_2_4_9.isChecked():
            GG_Spread_2 = 'True'
        else:
            GG_Spread_2 = 'False'
        if self.Widget3_2_4_10.isChecked():
            GG_Spread_3 = 'True'
        else:
            GG_Spread_3 = 'False'
        if self.Widget3_2_4_11.isChecked():
            GG_Spread_4 = 'True'
            GG_Spread_4_Value = self.Widget3_2_4_12.value()
        else:
            GG_Spread_4 = 'False'
            GG_Spread_4_Value = float()

        GC_Spread_Above = float(self.Widget3_2_5_3.text())
        GC_Spread_Below = float(self.Widget3_2_5_5.text())
        GC_Spread_Soil = str(self.Widget3_2_5_7.currentText())

        if self.Widget3_2_5_1.isChecked():
            GC = 'True'
        else:
            GC = 'False'

        if self.Widget3_2_5_8.isChecked():
            GC_Spread_1 = 'True'
        else:
            GC_Spread_1 = 'False'
        if self.Widget3_2_5_9.isChecked():
            GC_Spread_2 = 'True'
        else:
            GC_Spread_2 = 'False'
        if self.Widget3_2_5_10.isChecked():
            GC_Spread_3 = 'True'
        else:
            GC_Spread_3 = 'False'
        if self.Widget3_2_5_11.isChecked():
            GC_Spread_4 = 'True'
            GC_Spread_4_Value = self.Widget3_2_5_12.value()
        else:
            GC_Spread_4 = 'False'
            GC_Spread_4_Value = float()

        Variables = [W_base, L_base, Load_base, Dragline_1_CB, Dragline_1_nr, W_Dragline_1_1, L_Dragline_1_1,
                     T_Dragline_1_1, V_Dragline_1_1, W_Dragline_1_2, L_Dragline_1_2, T_Dragline_1_2, V_Dragline_1_2,
                     Dragline_2_CB, Dragline_2_nr, W_Dragline_2_1, L_Dragline_2_1,
                     T_Dragline_2_1, V_Dragline_2_1, W_Dragline_2_2, L_Dragline_2_2, T_Dragline_2_2, V_Dragline_2_2,
                     Dragline_3_CB, Dragline_3_nr, W_Dragline_3_1, L_Dragline_3_1,
                     T_Dragline_3_1, V_Dragline_3_1, W_Dragline_3_2, L_Dragline_3_2, T_Dragline_3_2, V_Dragline_3_2,
                     Dragline_4_CB, Dragline_4_nr, W_Dragline_4_1, L_Dragline_4_1,
                     T_Dragline_4_1, V_Dragline_4_1, W_Dragline_4_2, L_Dragline_4_2, T_Dragline_4_2, V_Dragline_4_2, SoilEnh_CB, SoilEnh_Soil, SoilEnh_1, SoilEnh_2, SoilEnh_3, SoilEnh_4, SoilEnh_4_Value,
                     GG_Spread_Above, GG_Spread_Below, GG_Spread_Soil, GG, GG_Spread_1, GG_Spread_2, GG_Spread_3, GG_Spread_4, GG_Spread_4_Value, GC_Spread_Above,
                     GC_Spread_Below, GC_Spread_Soil, GC, GC_Spread_1, GC_Spread_2, GC_Spread_3, GC_Spread_4, GC_Spread_4_Value]




        df = pd.DataFrame({'Variables_LoadFile': Variables})
        path = QFileDialog.getSaveFileName(self, 'Save load CSV', os.getenv('HOME'), 'csv(*.csv)')
        tail = os.path.split(path[0])
        if path[0] != '':
            with open(path[0], 'w', newline='') as csv_file:
                df.to_csv(csv_file)

    def OpenLoadFileOR(self):
        path = QFileDialog.getOpenFileName(self, 'Laad een correct load csv bestand in', filter='csv(*csv)')
        tail = os.path.split(path[0])
        if path[0] != '':
            with open(path[0], newline='') as csv_file:
                Loadfile = pd.read_csv(csv_file)


            nr = Loadfile.iat[0,1]


            self.Widget3_2_1_3.setText(str(Loadfile.iat[0,1]))
            self.Widget3_2_1_5.setText(str(Loadfile.iat[1,1]))
            self.Widget3_2_1_7.setText(str(Loadfile.iat[2,1]))

            if Loadfile.iat[3,1] == 'True':
                self.M_Widget_1_1_2.setChecked(True)
            else:
                self.M_Widget_1_1_2.setChecked(False)
            self.M_Widget_1_1_1.setCurrentIndex(int(float(Loadfile.iat[4,1]))-1)

            self.M_Widget_1_1_4.setText(str(Loadfile.iat[5,1]))
            self.M_Widget_1_1_6.setText(str(Loadfile.iat[6,1]))
            self.M_Widget_1_1_8.setText(str(Loadfile.iat[7,1]))
            self.M_Widget_1_1_10.setText(str(Loadfile.iat[8,1]))

            self.M_Widget_1_2_4.setText(str(Loadfile.iat[9,1]))
            self.M_Widget_1_2_6.setText(str(Loadfile.iat[10,1]))
            self.M_Widget_1_2_8.setText(str(Loadfile.iat[11,1]))
            self.M_Widget_1_2_10.setText(str(Loadfile.iat[12,1]))

            if Loadfile.iat[13,1] == 'True':
                self.M_Widget_2_1_2.setChecked(True)
            else:
                self.M_Widget_2_1_2.setChecked(False)

            self.M_Widget_1_1_1.setCurrentIndex(int(float(Loadfile.iat[14,1]))-1)
            self.M_Widget_2_1_4.setText(str(Loadfile.iat[15,1]))
            self.M_Widget_2_1_6.setText(str(Loadfile.iat[16,1]))
            self.M_Widget_2_1_8.setText(str(Loadfile.iat[17,1]))
            self.M_Widget_2_1_10.setText(str(Loadfile.iat[18,1]))

            self.M_Widget_2_2_4.setText(str(Loadfile.iat[19,1]))
            self.M_Widget_2_2_6.setText(str(Loadfile.iat[20,1]))
            self.M_Widget_2_2_8.setText(str(Loadfile.iat[21,1]))
            self.M_Widget_2_2_10.setText(str(Loadfile.iat[22,1]))

            if Loadfile.iat[23,1] == 'True':
                self.M_Widget_3_1_2.setChecked(True)
            else:
                self.M_Widget_3_1_2.setChecked(False)


            self.M_Widget_3_1_1.setCurrentIndex(int(float(Loadfile.iat[24,1]))-1)
            self.M_Widget_3_1_4.setText(str(Loadfile.iat[25,1]))
            self.M_Widget_3_1_6.setText(str(Loadfile.iat[26,1]))
            self.M_Widget_3_1_8.setText(str(Loadfile.iat[27,1]))
            self.M_Widget_3_1_10.setText(str(Loadfile.iat[28,1]))

            self.M_Widget_3_2_4.setText(str(Loadfile.iat[29,1]))
            self.M_Widget_3_2_6.setText(str(Loadfile.iat[30,1]))
            self.M_Widget_3_2_8.setText(str(Loadfile.iat[31,1]))
            self.M_Widget_3_2_10.setText(str(Loadfile.iat[32,1]))


            if Loadfile.iat[33,1] == 'True':
                self.M_Widget_4_1_2.setChecked(True)
            else:
                self.M_Widget_4_1_2.setChecked(False)


            self.M_Widget_4_1_1.setCurrentIndex(int(float(Loadfile.iat[34,1]))-1)
            self.M_Widget_4_1_4.setText(str(Loadfile.iat[35,1]))
            self.M_Widget_4_1_6.setText(str(Loadfile.iat[36,1]))
            self.M_Widget_4_1_8.setText(str(Loadfile.iat[37,1]))
            self.M_Widget_4_1_10.setText(str(Loadfile.iat[38,1]))

            self.M_Widget_4_2_4.setText(str(Loadfile.iat[39,1]))
            self.M_Widget_4_2_6.setText(str(Loadfile.iat[40,1]))
            self.M_Widget_4_2_8.setText(str(Loadfile.iat[41,1]))
            self.M_Widget_4_2_10.setText(str(Loadfile.iat[42,1]))


            if Loadfile.iat[43,1] == 'True':
                self.Widget3_2_3_1.setChecked(True)
            else:
                self.Widget3_2_3_1.setChecked(False)


            #self.M_Widget3_2_3_5.setText(str(Loadfile.iat[44, 1]))


            if Loadfile.iat[45,1] == 'True':
                self.Widget3_2_3_7.setChecked(True)
            else:
                self.Widget3_2_3_7.setChecked(False)

            if Loadfile.iat[46,1] == 'True':
                self.Widget3_2_3_8.setChecked(True)
            else:
                self.Widget3_2_3_8.setChecked(False)

            if Loadfile.iat[47,1] == 'True':
                self.Widget3_2_3_9.setChecked(True)
            else:
                self.Widget3_2_3_9.setChecked(False)

            if Loadfile.iat[48,1] == 'True':
                self.Widget3_2_3_10.setChecked(True)
                Loadfile.iat[49,1] = float(Loadfile.iat[49,1])
                self.Widget3_2_3_11.setValue(Loadfile.iat[49, 1])
            else:
                self.Widget3_2_3_10.setChecked(False)


            self.Widget3_2_4_3.setText(str(Loadfile.iat[50,1]))
            self.Widget3_2_4_5.setText(str(Loadfile.iat[51, 1]))
            #self.Widget3_2_4_7.currentText()

            if Loadfile.iat[53,1] == 'True':
                self.Widget3_2_4_1.setChecked(True)
            else:
                self.Widget3_2_4_1.setChecked(False)
            if Loadfile.iat[54,1] == 'True':
                self.Widget3_2_4_8.setChecked(True)
            else:
                self.Widget3_2_4_8.setChecked(False)
            if Loadfile.iat[55,1] == 'True':
                self.Widget3_2_4_9.setChecked(True)
            else:
                self.Widget3_2_4_9.setChecked(False)
            if Loadfile.iat[56,1] == 'True':
                self.Widget3_2_4_10.setChecked(True)
            else:
                self.Widget3_2_4_10.setChecked(False)
            if Loadfile.iat[57,1] == 'True':
                self.Widget3_2_4_11.setChecked(True)
                Loadfile.iat[58,1] = float(Loadfile.iat[58,1])
                self.Widget3_2_4_12.setValue(Loadfile.iat[58, 1])
            else:
                self.Widget3_2_4_11.setChecked(False)

            self.Widget3_2_5_3.setText(str(Loadfile.iat[59,1]))
            self.Widget3_2_5_5.setText(str(Loadfile.iat[60,1]))
            #self.Widget3_2_5_7.setText(str(Loadfile.iat[56,1]))

            if Loadfile.iat[62,1] == 'True':
                self.Widget3_2_5_1.setChecked(True)
            else:
                self.Widget3_2_5_1.setChecked(False)
            if Loadfile.iat[63,1] == 'True':
                self.Widget3_2_5_8.setChecked(True)
            else:
                self.Widget3_2_5_8.setChecked(False)
            if Loadfile.iat[64,1] == 'True':
                self.Widget3_2_5_9.setChecked(True)
            else:
                self.Widget3_2_5_9.setChecked(False)
            if Loadfile.iat[65,1] == 'True':
                self.Widget3_2_5_10.setChecked(True)
            else:
                self.Widget3_2_5_10.setChecked(False)

            if Loadfile.iat[66,1] == 'True':
                self.Widget3_2_5_11.setChecked(True)
                Loadfile.iat[67,1] = float(Loadfile.iat[67,1])
                self.Widget3_2_5_12.setValue(Loadfile.iat[67, 1])
            else:
                self.Widget3_2_5_11.setChecked(False)

    def Perc_load_changed(self):
        Value = 100 - int(self.Perc_permanent_load.value())
        self.Perc_Var_LoadText.setText(str("The percentage of variabel load = " + str(Value) + " %"))

    def ShowMats_1(self):
        if self.M_Widget_1_1_1.currentText() == '1':
            self.Mats_SubBox1_2.setVisible(False)
        elif self.M_Widget_1_1_1.currentText() == '2':
            self.Mats_SubBox1_2.setVisible(True)
        if self.M_Widget_2_1_1.currentText() == '1':
            self.Mats_SubBox2_2.setVisible(False)
        elif self.M_Widget_2_1_1.currentText() == '2':
            self.Mats_SubBox2_2.setVisible(True)
        if self.M_Widget_3_1_1.currentText() == '1':
            self.Mats_SubBox3_2.setVisible(False)
        elif self.M_Widget_3_1_1.currentText() == '2':
            self.Mats_SubBox3_2.setVisible(True)
        if self.M_Widget_4_1_1.currentText() == '1':
            self.Mats_SubBox4_2.setVisible(False)
        elif self.M_Widget_4_1_1.currentText() == '2':
            self.Mats_SubBox4_2.setVisible(True)

    def ShowVar(self):
        if self.Parameter_variations.isChecked():
            self.Tab5_1_2_Group.setVisible(True)
            self.Load_VariationsCB1.setVisible(False)
            self.Load_VariationsCB2.setVisible(False)
            self.tab3Stempel.setVisible(False)
            self.tab3Rups.setVisible(False)

        elif self.Load_Variations.isChecked():
            self.Tab5_1_2_Group.setVisible(False)
            self.Load_VariationsCB1.setVisible(True)
            self.Load_VariationsCB2.setVisible(True)
            self.tab3Stempel.setVisible(True)
            self.tab3Rups.setVisible(True)
    # RC wordt ingelezen
    def Calc_load_cases(self):


        """ Reliability Class """
        if self.RC0.isChecked():
            RC = 0
            self.Calc_RC(RC = RC)
        if self.RC1.isChecked():
            RC = 1
            self.Calc_RC(RC = RC)
        if self.RC2.isChecked():
            RC = 2
            self.Calc_RC(RC = RC)
        if self.RC3.isChecked():
            RC = 3
            self.Calc_RC(RC = RC)


        """Without any enhancement"""
        if self.Widget3_2_1_1.isChecked():


            W_stempel = str(self.Widget3_2_1_3.text())
            L_stempel = str(self.Widget3_2_1_5.text())
            Q_kraan   = str(self.Widget3_2_1_7.text())


            maaiveld = str(self.ViewProfile.item(0, 0).text())
            grondwaterstand = (self.Soil_GWS_Value.text())
            maaiveld = maaiveld.replace(",", ".")
            grondwaterstand = grondwaterstand.replace(",", ".")
            maaiveld = float(maaiveld)
            grondwaterstand = float(grondwaterstand)

            self.Calc_Bep_Stemp(W = float(W_stempel), L = float(L_stempel), Q = float(Q_kraan), mv = float(maaiveld), gws = float(grondwaterstand))

            #opties voor belastingen, samen met waardes. Samengevoegd in lijst met 2 lijsten. (is dict of numpy array niet handiger?)
            namen_belasting = [
                ["Stempel", "Grondv 0_5 m", "Grondv 1_0 m", "Grondv 1_5 m", "Grondv X_X m","0_5m_grid", "1_0m_grid", "1_5m_grid", "X_X_grid", "0_5m_cell", "1_0m_cell", "1_5m_cell", "X_X_cell",
                 "Schot_A", "Schot_B", "Schot_C", "Schot_D", "Schot_A + 0_5 m Grondv", "Schot_B + 0_5 m Grondv",
                 "Schot_C + 0_5 m Grondv", "Schot_D + 0_5 m Grondv", "Schot_A + 1_0 m Grondv", "Schot_B + 1_0 m Grondv",
                 "Schot_C + 1_0 m Grondv", "Schot_D + 1_0 m Grondv","Schot_A + 1_5 m Grondv", "Schot_B + 1_5 m Grondv",
                 "Schot_C + 1_5 m Grondv", "Schot_D + 1_5 m Grondv", "Schot_A + X,X m Grondv", "Schot_B + X,X m Grondv", "Schot_C + X,X m Grondv", "Schot_D + X,X m Grondv", "Schot_A + 0_5m_grid", "Schot_B + 0_5m_grid",
                 "Schot_C + 0_5m_grid", "Schot_D + 0_5m_grid", "Schot_A + 1_0m_grid", "Schot_B + 1_0m_grid",
                 "Schot_C + 1_0m_grid", "Schot_D + 1_0m_grid", "Schot_A + 1_5m_grid", "Schot_B + 1_5m_grid",
                 "Schot_C + 1_5m_grid", "Schot_D + 1_5m_grid", "Schot_A + X,X m_grid", "Schot_B + X,X m_grid", "Schot_C + X,X m_grid", "Schot_D + X,X m_grid", "Schot_A + 0_5m_cell", "Schot_B + 0_5m_cell",
                 "Schot_C + 0_5m_cell", "Schot_D + 0_5m_cell", "Schot_A + 1_0m_cell", "Schot_B + 1_0m_cell",
                 "Schot_C + 1_0m_cell", "Schot_D + 1_0m_cell", "Schot_A + 1_5m_cell", "Schot_B + 1_5m_cell",
                 "Schot_C + 1_5m_cell", "Schot_D + 1_5m_cell","Schot_A + X,X m_cell", "Schot_B + X,X m_cell", "Schot_C + X,X m_cell", "Schot_D + X,X m_cell"],
                [1000000, 1510000, 1520000, 1530000, 1540000, 1001000, 1002000, 1003000, 1003100, 1004000, 1005000, 1006000, 1007000, 1100000, 1200000, 1300000,
                 1400000, 1110000, 1210000, 1310000, 1410000, 1120000, 1220000, 1320000 ,1420000 ,1130000 ,1230000 ,1330000, 1430000, 1140000, 1240000, 1340000, 1440000, 1100100, 1200100, 1300100, 1400100, 1100200, 1200200,
                 1300200, 1400200, 1100300, 1200300, 1300300, 1400300, 1100310, 1200310, 1300310, 1400310, 1100400, 1200400, 1300400, 1400400, 1100500,
                 1200500, 1300500, 1400500, 1100600, 1200600, 1300600, 1400600, 1100700, 1200700, 1300700, 1400700]]

            ii = 0
            for row in self.Plaxis_Input:
                if row[0] in namen_belasting[1]:  #als namen overeenkomen selecteer uit namen_belasting lijst input voor plaxis
                    i_naam = namen_belasting[1].index(row[0])
                    self.Plaxis_Input[ii][0] = namen_belasting[0][i_naam]
                    ii = ii + 1
                    if ii >= len(self.Plaxis_Input):
                        break

        """Veiligheidsfilosofie - Functie voor bepalen belastingfactoren"""
    # welke belasting veranderingen op basis van RC?
    """ Berekening van RC en belastingfactoren benodigd voor berekening  belastingen"""
    def Calc_RC(self, RC):

        # Tabel A.3 verzameling A1                                       Waar is deze tabel? eurocode?
        Bel_factors = {'Factor perm. 6.10a': [1, 1.22, 1.35, 1.49],
                       'Factor verand. 6.10a': [1, 0.68, 0.75, 0.83],
                       'Factor perm. 6.10b': [1, 1.08, 1.20, 1.32],
                       'Factor verand. 6.10b': [1, 1.35, 1.5, 1.65]
                       }
        Bel_factors = pd.DataFrame(Bel_factors)

        # Invoeren van percentage permanente kraanbelasting

        PercPerm_bel_kraan = (self.Perc_permanent_load.value())/100                #lees ingevoerde waarde
        PercVer_bel_kraan = (1 - PercPerm_bel_kraan)

        # Combinatie o.b.v. ingevoerde verdeling kraanbelasting                     # bereken mogelijke  belastingen, twee categorien: 610A en 610B?
        Comb_610a = {"6.10a": Bel_factors.iloc[:, 0] * PercPerm_bel_kraan + Bel_factors.iloc[:, 2] * PercVer_bel_kraan}
        Comb_610b = Bel_factors.iloc[:, 1] * PercPerm_bel_kraan + Bel_factors.iloc[:, 3] * PercVer_bel_kraan
        Bel_factors_adj = pd.DataFrame(Comb_610a)
        Bel_factors_adj.insert(1, "6.10b", Comb_610b)

        # Maatgevende belastingfactoren
        Maat_bel_factors = Bel_factors_adj.max(axis=1)    #selecteer zwaarste belasting, dit is max() van alle berekende belastingen

        # Bepaling belasting factoren

        if Bel_factors_adj.iloc[2, 0] > Bel_factors_adj.iloc[2, 1]:  #selecteer type belasting? 610A of 610B? wat is dat precies?
            #6.10A
            self.gamma_per = Bel_factors.iloc[RC, 0]
            self.gamma_var = Bel_factors.iloc[RC, 2]
        else:
            #6.10B
            self.gamma_per = Bel_factors.iloc[RC, 1]
            self.gamma_var = Bel_factors.iloc[RC, 3]

        self.gamma_kraan = float(Maat_bel_factors.iloc[RC])

        # Invoer belastingfactor volumiek gewicht grond (defaul = 1,0)
        self.gamma_grond = 1.1 #Default is 1,1 mogelijk willen we dit later nog toevoegen als invoerveld

    #BELASTING BEREKENING VAN DE KRAAN + VERZAMEL PARAMETERS VAN VERSCHILLENDE SCHOTTEN OPTIES
    """ In onderstaande functie wordt gecheckt welke belasting opties zijn aangevinkt en op basis daarvan belasting berekend mede door het aanroepen van andere functies """
    def Calc_Bep_Stemp(self, W, L, Q, mv, gws):
        #Q is de Q_kraan, de kraanbelasting
        self.Plaxis_Input = []
        q_rep_plaxis = Q/(W*L)   #druk op de ondergrond van de belasting. Dat is gewicht/oppervlakte
        #gamma_kraan, is afgeleid van de risico factor berekening, dus afhankelijk van RC 1, 2 etc
        q_d_plaxis = Q*self.gamma_kraan/(W*L)
        W_plaxis = min(W,L)         #width
        L_plaxis = max(W,L)         #length
        fund_plaxis = mv            #aangrijppunt, dit moet misschien ook nog veranderd worden
        gws_plaxis = gws            #grondwaterstand
        D_plaxis = 0
        Gv_plaxis = "n.v.t."
        Case_nr = 1000000           #initieel case_nr, er wordt hier later bij opgeteld om cases te onderscheiden
        Case_1 = [Case_nr, q_rep_plaxis ,q_d_plaxis, W_plaxis, L_plaxis, gws_plaxis, fund_plaxis, D_plaxis,Gv_plaxis]
        self.Plaxis_Input.append(Case_1)

        # selecteer schotten parameters op basis van keuze in plaxis
        #Er zijn:
        # - 4 verschillende schotten opties
        # - Grondverbetering zonder geotextielen (en zonder schotten) (GZG)
        # - Grondverbetering met horizontale geogrids (en zonder schotten)
        # - Grondverbetering met geocellen (en zonder schotten)(GMG)

        """ Schotten sectie 1"""
        if  self.M_Widget_1_1_2.isChecked():
            Case_nr_1 = Case_nr + 100000
            B_schot_1= str(self.M_Widget_1_1_4.text())        #input lezen van gui - breedte
            L_schot_1 = str(self.M_Widget_1_1_6.text())       #lengte
            D_schot_1 = str(self.M_Widget_1_1_8.text())       #dikte
            G_schot_1 = str(self. M_Widget_1_1_10.text())     #volume gewicht
            Schot_1 = [float(B_schot_1), float(L_schot_1), float(D_schot_1), float(G_schot_1)]

            n_schot = int(self.M_Widget_1_1_1.currentText())  #aantal lagen (1 of 2)

            if n_schot == 2:
                B_schot_2 = str(self.M_Widget_1_2_4.text())
                L_schot_2 = str(self.M_Widget_1_2_6.text())
                D_schot_2 = str(self.M_Widget_1_2_8.text())
                G_schot_2 = str(self. M_Widget_1_2_10.text())
                Schot_2 = [float(B_schot_2), float(L_schot_2), float(D_schot_2), float(G_schot_2)]
            else:
                Schot_2 = []

            self.Calc_Bep_Schot(Q, mv, gws,  Schot_1, Schot_2, n_schot,Case_nr = Case_nr_1)   #run schotten berekening!

        """ Schotten sectie 2"""
        if  self.M_Widget_2_1_2.isChecked():
            Case_nr_2 = Case_nr + 200000
            B_schot_1= str(self.M_Widget_2_1_4.text())
            L_schot_1 = str(self.M_Widget_2_1_6.text())
            D_schot_1 = str(self.M_Widget_2_1_8.text())
            G_schot_1 = str(self. M_Widget_2_1_10.text())
            Schot_1 = [float(B_schot_1), float(L_schot_1), float(D_schot_1), float(G_schot_1)]

            n_schot = int(self.M_Widget_2_1_1.currentText())

            if n_schot == 2:
                B_schot_2 = str(self.M_Widget_2_2_4.text())
                L_schot_2 = str(self.M_Widget_2_2_6.text())
                D_schot_2 = str(self.M_Widget_2_2_8.text())
                G_schot_2 = str(self. M_Widget_2_2_10.text())
                Schot_2 = [float(B_schot_2), float(L_schot_2), float(D_schot_2), float(G_schot_2)]
            else:
                Schot_2 = []

            self.Calc_Bep_Schot(Q, mv, gws, Schot_1, Schot_2, n_schot, Case_nr = Case_nr_2)

        """ Schotten sectie 3"""
        if self.M_Widget_3_1_2.isChecked():
            Case_nr_3 = Case_nr + 300000
            B_schot_1= str(self.M_Widget_3_1_4.text())
            L_schot_1 = str(self.M_Widget_3_1_6.text())
            D_schot_1 = str(self.M_Widget_3_1_8.text())
            G_schot_1 = str(self. M_Widget_3_1_10.text())
            Schot_1 = [float(B_schot_1), float(L_schot_1), float(D_schot_1), float(G_schot_1)]

            n_schot = int(self.M_Widget_3_1_1.currentText())

            if n_schot == 2:
                B_schot_2 = str(self.M_Widget_3_2_4.text())
                L_schot_2 = str(self.M_Widget_3_2_6.text())
                D_schot_2 = str(self.M_Widget_3_2_8.text())
                G_schot_2 = str(self. M_Widget_3_2_10.text())
                Schot_2 = [float(B_schot_2), float(L_schot_2), float(D_schot_2), float(G_schot_2)]
            else:
                Schot_2 = []

            self.Calc_Bep_Schot(Q, mv, gws, Schot_1, Schot_2, n_schot, Case_nr = Case_nr_3)

            """ Schotten sectie 4"""
        if self.M_Widget_4_1_2.isChecked():
            Case_nr_4 = Case_nr + 400000
            B_schot_1= str(self.M_Widget_4_1_4.text())
            L_schot_1 = str(self.M_Widget_4_1_6.text())
            D_schot_1 = str(self.M_Widget_4_1_8.text())
            G_schot_1 = str(self. M_Widget_4_1_10.text())
            Schot_1 = [float(B_schot_1), float(L_schot_1), float(D_schot_1), float(G_schot_1)]

            n_schot = int(self.M_Widget_4_1_1.currentText())

            if n_schot == 2:
                B_schot_2 = str(self.M_Widget_4_2_4.text())
                L_schot_2 = str(self.M_Widget_4_2_6.text())
                D_schot_2 = str(self.M_Widget_4_2_8.text())
                G_schot_2 = str(self. M_Widget_4_2_10.text())
                Schot_2 = [float(B_schot_2), float(L_schot_2), float(D_schot_2), float(G_schot_2)]
            else:
                Schot_2 = []

            self.Calc_Bep_Schot(Q, mv, gws, Schot_1, Schot_2, n_schot, Case_nr = Case_nr_4)

            """Grondverbetering zonder geotextielen (en zonder schotten) (GZG)"""
        if self.Widget3_2_3_1.isChecked():
            Case_nr_5 = []
            D_fund_g = []
            if self.Widget3_2_3_7.isChecked():
                    Case_nr_5.append(Case_nr + 510000)
                    D_fund_g.append(0.5)
            if self.Widget3_2_3_8.isChecked():
                    Case_nr_5.append(Case_nr + 520000)
                    D_fund_g.append(1.0)
            if self.Widget3_2_3_9.isChecked():
                    Case_nr_5.append(Case_nr + 530000)
                    D_fund_g.append(1.5)
            if self.Widget3_2_3_10.isChecked():
                    Case_nr_5.append(Case_nr + 540000)
                    custom_thickness = self.Widget3_2_3_11.text()
                    custom_thickness = custom_thickness.replace(",", ".")
                    D_fund_g.append(float(custom_thickness))
            self.Calc_Combi_GZG(Q, mv, gws, Case = Case_1, Case_nr = Case_nr_5, D_fund = D_fund_g)

            """Grondverbetering met horizontale geogrids (en zonder schotten) (GMG)"""
        if self.Widget3_2_4_1.isChecked():
            Spreiding = [float(self.Widget3_2_4_3.text()), float(self.Widget3_2_4_5.text())]
            D_fund_grid = []
            Case_nr_6 = []
            Gv = str(self.Widget3_2_4_7.currentText())
            if self.Widget3_2_4_8.isChecked():
                    Case_nr_6.append(Case_nr + 1000)
                    D_fund_grid.append(0.5)
            if self.Widget3_2_4_9.isChecked():
                    Case_nr_6.append(Case_nr + 2000)
                    D_fund_grid.append(1)
            if self.Widget3_2_4_10.isChecked():
                    Case_nr_6.append(Case_nr + 3000)
                    D_fund_grid.append(1.5)
            if self.Widget3_2_4_11.isChecked():
                    Case_nr_6.append(Case_nr + 3100)
                    custom_thickness = self.Widget3_2_4_12.text()
                    custom_thickness = custom_thickness.replace(",", ".")
                    D_fund_grid.append(float(custom_thickness))
            self.Calc_Combi_GMG(Q, mv, gws, Spreiding , Gv , Case=Case_1, D_fund=D_fund_grid, Case_nr = Case_nr_6)

            """Grondverbetering met geocellen (en zonder schotten)(GMG)"""
        if self.Widget3_2_5_1.isChecked():
            Spreiding = [ float(self.Widget3_2_5_3.text()),float(self.Widget3_2_5_5.text())]
            Gv = str(self.Widget3_2_5_7.currentText())
            D_fund_cell = []
            Case_nr_7 = []
            if self.Widget3_2_5_8.isChecked():
                    Case_nr_7.append(Case_nr + 4000)
                    D_fund_cell.append(0.5)
            if self.Widget3_2_5_9.isChecked():
                    Case_nr_7.append(Case_nr + 5000)
                    D_fund_cell.append(1)
            if self.Widget3_2_5_10.isChecked():
                    Case_nr_7.append(Case_nr + 6000)
                    D_fund_cell.append(1.5)
            if self.Widget3_2_5_11.isChecked():
                    Case_nr_7.append(Case_nr + 7000)
                    custom_thickness = self.Widget3_2_5_12.text()
                    custom_thickness = custom_thickness.replace(",", ".")
                    D_fund_cell.append(float(custom_thickness))
            self.Calc_Combi_GMG(Q, mv, gws, Spreiding, Gv, Case=Case_1, D_fund =D_fund_cell, Case_nr = Case_nr_7)

    #BEREKENING SCHOTTEN BELASTING
    # berekening op basis van geselecteerde parameters in bovenstaande functie.
    """ Berekenening van belastingen, spreiding en funderingsniveaus bij toepassing van schotten """
    def Calc_Bep_Schot(self, Q , mv, gws, Schot_1, Schot_2, n_schot, Case_nr):

        #n_schot is eerder gekozen op basis van keuze in plaxis. Betekent: hoeveel lagen schotten?
        #op basis daarvan alle nodige parameters van schotten belasting berekend.

        #opties voor als er één laag schotten is
        if n_schot == 1:
            BGT_schot = Schot_1[2]*Schot_1[1]*Schot_1[0]*Schot_1[3]*9.81/1000 #schot_1 bevat breedte [0], lengte[1], dikte[2], dus dit is volume *9,81 is Belasting
            UGT_schot = BGT_schot*self.gamma_per
            q_rep_plaxis = (Q+BGT_schot)/(Schot_1[0]*Schot_1[1])  #hier is totale belasting: belasting kraan + belasting schot /(oppervlakte schot)
            q_d_plaxis = (Q*self.gamma_kraan + UGT_schot)/(Schot_1[0]*Schot_1[1])
            W_plaxis = min(Schot_1[0],Schot_1[1])  #Bepaal korte en lange kant
            L_plaxis = max(Schot_1[0],Schot_1[1])
            fund_plaxis = mv
            gws_plaxis = gws
            D_plaxis = 0
            Gv_plaxis = "n.v.t."
            Case_2 = [Case_nr, q_rep_plaxis, q_d_plaxis, W_plaxis, L_plaxis, gws_plaxis, fund_plaxis, D_plaxis, Gv_plaxis]
            self.Plaxis_Input.append(Case_2)

            #verschillende scenario's op basis van wat is geselecteerd in plaxis

            """1 laag schotten i.c.m. Grondverbetering zonder geotextielen (GZG)"""
            if self.Widget3_2_3_1.isChecked():
                Case_nr_8 = []
                D_fund_g = []
                if self.Widget3_2_3_7.isChecked():
                    Case_nr_8.append(Case_nr + 10000)
                    D_fund_g.append(0.5)
                if self.Widget3_2_3_8.isChecked():
                    Case_nr_8.append(Case_nr + 20000)
                    D_fund_g.append(1.0)
                if self.Widget3_2_3_9.isChecked():
                    Case_nr_8.append(Case_nr + 30000)
                    D_fund_g.append(1.5)
                if self.Widget3_2_3_10.isChecked():
                    Case_nr_8.append(Case_nr + 40000)
                    custom_thickness = self.Widget3_2_3_11.text()
                    custom_thickness = custom_thickness.replace(",", ".")
                    D_fund_g.append(float(custom_thickness))
                self.Calc_Combi_GZG(Q, mv, gws, Case = Case_2, Case_nr = Case_nr_8, D_fund = D_fund_g)

            """1 laag schotten i.c.m. Grondverbetering met horizontale geogrids (GMG)"""
            if self.Widget3_2_4_1.isChecked():
                Spreiding = [float(self.Widget3_2_4_3.text()), float(self.Widget3_2_4_5.text())]
                D_fund_grid = []
                Case_nr_9 = []
                Gv = str(self.Widget3_2_4_7.currentText())
                if self.Widget3_2_4_8.isChecked():
                    Case_nr_9.append(Case_nr + 100)
                    D_fund_grid.append(0.5)
                if self.Widget3_2_4_9.isChecked():
                    Case_nr_9.append(Case_nr + 200)
                    D_fund_grid.append(1)
                if self.Widget3_2_4_10.isChecked():
                    Case_nr_9.append(Case_nr + 300)
                    D_fund_grid.append(1.5)
                if self.Widget3_2_4_11.isChecked():
                    Case_nr_9.append(Case_nr + 310)
                    custom_thickness = self.Widget3_2_4_12.text()
                    custom_thickness = custom_thickness.replace(",", ".")
                    D_fund_grid.append(float(custom_thickness))
                self.Calc_Combi_GMG(Q, mv, gws, Spreiding, Gv, Case=Case_2, D_fund=D_fund_grid, Case_nr = Case_nr_9)

            """1 laag schotten i.c.m. Grondverbetering met geocellen(GMG)"""
            if self.Widget3_2_5_1.isChecked():
                Spreiding = [ float(self.Widget3_2_5_3.text()),float(self.Widget3_2_5_5.text())]
                Gv = str(self.Widget3_2_5_7.currentText())
                D_fund_cell = []
                Case_nr_10 = []
                if self.Widget3_2_5_8.isChecked():
                    Case_nr_10.append(Case_nr + 400)
                    D_fund_cell.append(0.5)
                if self.Widget3_2_5_9.isChecked():
                    Case_nr_10.append(Case_nr + 500)
                    D_fund_cell.append(1)
                if self.Widget3_2_5_10.isChecked():
                    Case_nr_10.append(Case_nr + 600)
                    D_fund_cell.append(1.5)
                if self.Widget3_2_5_11.isChecked():
                    Case_nr_10.append(Case_nr + 700)
                    custom_thickness = self.Widget3_2_5_12.text()
                    print(custom_thickness)
                    custom_thickness = custom_thickness.replace(",", ".")
                    D_fund_cell.append(float(custom_thickness))
                self.Calc_Combi_GMG(Q, mv, gws, Spreiding, Gv, Case=Case_2, D_fund =D_fund_cell, Case_nr = Case_nr_10)

        elif n_schot == 2:
            BGT_schot_1 = Schot_1[2]*Schot_1[1]*Schot_1[0]*Schot_1[3]*9.81/1000 #belasting laag schotten 1
            BGT_schot_2 = Schot_2[2]*Schot_2[1]*Schot_2[0]*Schot_2[3]*9.81/1000 #belasting laag schotten 2
            BGT_schot = BGT_schot_1 + BGT_schot_2  #totale belasting
            UGT_schot = BGT_schot_1 * self.gamma_per + BGT_schot_2 * self.gamma_per

            q_rep_plaxis = (Q+BGT_schot)/(max(Schot_1[0],Schot_2[0])*max(Schot_1[1],Schot_2[1]))
            q_d_plaxis = (Q*self.gamma_kraan + UGT_schot)/(max(Schot_1[0],Schot_2[0])*max(Schot_1[1],Schot_2[1]))
            W_plaxis = min(Schot_1[0],Schot_1[1])
            L_plaxis = max(Schot_1[0],Schot_1[1])
            fund_plaxis = mv
            gws_plaxis = gws
            D_plaxis = 0
            Gv_plaxis = "n.v.t"
            Case_2 = [Case_nr, q_rep_plaxis, q_d_plaxis, W_plaxis, L_plaxis, gws_plaxis, fund_plaxis, D_plaxis, Gv_plaxis]
            self.Plaxis_Input.append(Case_2)

            """2 lagen schotten i.c.m. Grondverbetering zonder geotextielen (GZG)"""
            if self.Widget3_2_3_1.isChecked():
                Case_nr_8 = []
                D_fund_g = []
                if self.Widget3_2_3_7.isChecked():
                    Case_nr_8.append(Case_nr + 10000)
                    D_fund_g.append(0.5)
                if self.Widget3_2_3_8.isChecked():
                    Case_nr_8.append(Case_nr + 20000)
                    D_fund_g.append(1.0)
                if self.Widget3_2_3_9.isChecked():
                    Case_nr_8.append(Case_nr + 30000)
                    D_fund_g.append(1.5)
                if self.Widget3_2_3_10.isChecked():
                    Case_nr_8.append(Case_nr + 40000)
                    custom_thickness = self.Widget3_2_3_11.text()
                    custom_thickness = custom_thickness.replace(",", ".")
                    D_fund_g.append(float(custom_thickness))
                self.Calc_Combi_GZG(Q, mv, gws, Case = Case_2, Case_nr = Case_nr_8, D_fund = D_fund_g)

            """2 lagen schotten i.c.m. Grondverbetering met horizontale geogrids (GMG)"""
            if self.Widget3_2_4_1.isChecked():
                Spreiding = [float(self.Widget3_2_4_3.text()),float(self.Widget3_2_4_5.text())]
                Gv = str(self.Widget3_2_4_7.currentText())
                D_fund_grid = []
                Case_nr_9 = []
                if self.Widget3_2_4_8.isChecked():
                    Case_nr_9.append(Case_nr + 100)
                    D_fund_grid.append(0.5)
                if self.Widget3_2_4_9.isChecked():
                    Case_nr_9.append(Case_nr + 200)
                    D_fund_grid.append(1)
                if self.Widget3_2_4_10.isChecked():
                    Case_nr_9.append(Case_nr + 300)
                    D_fund_grid.append(1.5)
                if self.Widget3_2_4_11.isChecked():
                    Case_nr_9.append(Case_nr + 310)
                    custom_thickness = self.Widget3_2_4_12.text()
                    custom_thickness = custom_thickness.replace(",", ".")
                    D_fund_grid.append(float(custom_thickness))
                self.Calc_Combi_GMG(Q, mv, gws, Spreiding, Gv, Case=Case_2, D_fund=D_fund_grid, Case_nr = Case_nr_9)

            """2 lagen schotten i.c.m. Grondverbetering met geocellen(GMG)"""
            if self.Widget3_2_5_1.isChecked():
                Spreiding = [float(self.Widget3_2_5_3.text()), float(self.Widget3_2_5_5.text())]
                Gv = str(self.Widget3_2_5_7.currentText())
                D_fund_cell = []
                Case_nr_10 = []
                if self.Widget3_2_5_8.isChecked():
                    Case_nr_10.append(Case_nr + 400)
                    D_fund_cell.append(0.5)
                if self.Widget3_2_5_9.isChecked():
                    Case_nr_10.append(Case_nr + 500)
                    D_fund_cell.append(1)
                if self.Widget3_2_5_10.isChecked():
                    Case_nr_10.append(Case_nr + 600)
                    D_fund_cell.append(1.5)
                if self.Widget3_2_5_11.isChecked():
                    Case_nr_10.append(Case_nr + 700)
                    custom_thickness = self.Widget3_2_5_12.text()
                    custom_thickness = custom_thickness.replace(",", ".")
                    D_fund_cell.append(float(custom_thickness))
                self.Calc_Combi_GMG(Q, mv, gws, Spreiding, Gv, Case=Case_2, D_fund=D_fund_cell, Case_nr = Case_nr_10)

    #APARTE FUNCTIES VOOR BEREKENINGEN ZONDER SCHOTTEN, DUS MET GRONDVERBETERING MET EN ZONDER GEOTEXTIEL
    """ Berkenening van belastingen, spreiding en funderingsnvieaus bij toepassing van grondeverbetering zonder geotextiel """
    def Calc_Combi_GZG(self, Q, mv, gws, Case, Case_nr, D_fund):
        for i in range(len(D_fund)):
            Case_3 = Case.copy()
            Case_3[0] = Case_nr[i]
            #Case_3[4] = gws kan verwijderd worden 
            Case_3[7] = D_fund[i] #Dikte van grondverbetering
            Case_3[8] = str(self.Widget3_2_3_5.currentText()) #Naam van grondverbetering
            self.Plaxis_Input.append(Case_3)

    """ Berkenening van belastingen, spreiding en funderingsnvieaus bij toepassing van grondeverbetering met geotextiel """
    def Calc_Combi_GMG(self, Q, mv, gws, Spreiding, Gv, Case, D_fund, Case_nr):
        for i in range(len(D_fund)):
            Case_4 = Case.copy()
            if mv - D_fund[i] < gws:
                add_spreiding_1 = (Spreiding[0]*(mv - gws))
                add_speiding_2 = (Spreiding[1]*(gws - (mv - D_fund[i])))
                add_spreiding = add_spreiding_1 + add_speiding_2
            elif mv - D_fund[i] >= gws:
                add_spreiding = Spreiding[0]* (mv - (mv - D_fund[i]))

            Q_rep = Case_4[1] * Case_4[3] * Case_4[4]
            Q_d =  Case_4[2] * Case_4[3] * Case_4[4]
            Case_4[0] = Case_nr[i]
            Case_4[3] = Case_4[3] + 2*add_spreiding
            Case_4[4] = Case_4[4] + 2*add_spreiding
            Case_4[1] = Q_rep / (Case_4[3] * Case_4[4])
            Case_4[2] = Q_d / (Case_4[3] * Case_4[4])
            Case_4[6] = mv - float(D_fund[i])
            Case_4[7] = D_fund[i]
            Case_4[8] = Gv
            self.Plaxis_Input.append(Case_4)


    #Ik denk dat dit is voor selectie van kleuren etc, hoe ziet het eruit in Plaxis? Afhankelijk vna het aantal bodemlagen dat geladen wordt.
    def barChart(self):
        if self.HasProgramStarted == False:
            number_of_rows = 0
            number_of_columns = 0

        else:

            number_of_rows = self.Soil_Profile.rowCount()
            number_of_columns = self.Soil_Profile.columnCount()

        tmp_df = pd.DataFrame(columns=['Grondsoort', 'Hoogte'],
                              # Fill columnets
                              index=range(number_of_rows)  # Fill rows
                              )

        for i in range(number_of_rows):
            for j in range(number_of_columns):
                tmp_df.ix[i, j] = self.Soil_Profile.item(i, j).text()

        counter = 0

        if not tmp_df.empty:
            self.SoilProfile_Picture.removeAllSeries()
            self.series = QStackedBarSeries()

            a = len(tmp_df.index)  #aantal grondlagen
            axis_y = QValueAxis()
            axis_y.setTickCount(10)
            axis_y.applyNiceNumbers()

            Colors = []
            QtColors = [Qt.red, Qt.yellow, Qt.darkGray, Qt.darkBlue, Qt.darkRed, Qt.darkYellow, Qt.darkGreen, Qt.green,
                        Qt.blue, Qt.black, Qt.magenta, Qt.darkMagenta]
            ColorCounter = 0

            axis_y.setRange(float(tmp_df.iloc[a - 1][1]) - 2, float(tmp_df.iloc[0][1]))
            self.SoilProfile_Picture.setAxisY(axis_y)
            if a >= 1: #eerst laag een vaste kleur aangegeven
                self.Laag1 = QBarSet(str(tmp_df.iloc[a - 1][0]))
                Colors.append(str(tmp_df.iloc[a - 1][0]))
                self.Laag1.setBrush(QtColors[ColorCounter])
                ColorCounter = + 1
                self.Laag1 << 2  # abs(-20-float(tmp_df.iloc[a-1][0]))
                self.series.append(self.Laag1)

                #als laag 2 er is dan laag 2 aangewezen, etc.
                if a >= 2:
                    self.Laag2 = QBarSet(str(tmp_df.iloc[a - 2][0]))
                    self.Laag2 << abs(float(tmp_df.iloc[a - 1][1]) - float(tmp_df.iloc[a - 2][1]))
                    if str(tmp_df.iloc[a - 2][0]) in Colors:
                        Colornumber = Colors.index(str(tmp_df.iloc[a - 2][0]))
                        self.Laag2.setBrush(QtColors[Colornumber])
                    else:
                        Colors.append(str(tmp_df.iloc[a - 2][0]))
                        self.Laag2.setBrush(QtColors[ColorCounter])
                        ColorCounter = ColorCounter + 1
                    self.series.append(self.Laag2)

                    if a >= 3:
                        self.Laag3 = QBarSet(str(tmp_df.iloc[a - 3][0]))
                        self.Laag3 << abs(float(tmp_df.iloc[a - 2][1]) - float(tmp_df.iloc[a - 3][1]))
                        if str(tmp_df.iloc[a - 3][0]) in Colors:
                            Colornumber = Colors.index(str(tmp_df.iloc[a - 3][0]))
                            self.Laag3.setBrush(QtColors[Colornumber])
                        else:
                            Colors.append(str(tmp_df.iloc[a - 3][0]))
                            self.Laag3.setBrush(QtColors[ColorCounter])
                            ColorCounter = ColorCounter + 1

                        self.series.append(self.Laag3)
                        if a >= 4:
                            self.Laag4 = QBarSet(str(tmp_df.iloc[a - 4][0]))
                            self.Laag4 << abs(float(tmp_df.iloc[a - 3][1]) - float(tmp_df.iloc[a - 4][1]))
                            if str(tmp_df.iloc[a - 4][0]) in Colors:
                                Colornumber = Colors.index(str(tmp_df.iloc[a - 4][0]))
                                self.Laag4.setBrush(QtColors[Colornumber])
                            else:

                                Colors.append(str(tmp_df.iloc[a - 4][0]))
                                self.Laag4.setBrush(QtColors[ColorCounter])
                                ColorCounter = ColorCounter + 1

                            self.series.append(self.Laag4)
                            if a >= 5:
                                self.Laag5 = QBarSet(str(tmp_df.iloc[a - 5][0]))
                                self.Laag5 << abs(float(tmp_df.iloc[a - 4][1]) - float(tmp_df.iloc[a - 5][1]))
                                if str(tmp_df.iloc[a - 5][0]) in Colors:
                                    Colornumber = Colors.index(str(tmp_df.iloc[a - 5][0]))
                                    self.Laag5.setBrush(QtColors[Colornumber])
                                else:

                                    Colors.append(str(tmp_df.iloc[a - 5][0]))
                                    self.Laag5.setBrush(QtColors[ColorCounter])
                                    ColorCounter = ColorCounter + 1

                                self.series.append(self.Laag5)
                                if a >= 6:
                                    self.Laag6 = QBarSet(str(tmp_df.iloc[a - 6][0]))
                                    self.Laag6 << abs(float(tmp_df.iloc[a - 5][1]) - float(tmp_df.iloc[a - 6][1]))
                                    if str(tmp_df.iloc[a - 6][0]) in Colors:
                                        Colornumber = Colors.index(str(tmp_df.iloc[a - 6][0]))
                                        self.Laag6.setBrush(QtColors[Colornumber])
                                    else:
                                        Colors.append(str(tmp_df.iloc[a - 6][0]))
                                        self.Laag6.setBrush(QtColors[ColorCounter])
                                        ColorCounter = ColorCounter + 1

                                    self.series.append(self.Laag6)
                                    if a >= 7:
                                        self.Laag7 = QBarSet(str(tmp_df.iloc[a - 7][0]))
                                        self.Laag7 << abs(float(tmp_df.iloc[a - 6][1]) - float(tmp_df.iloc[a - 7][1]))
                                        if str(tmp_df.iloc[a - 7][0]) in Colors:
                                            Colornumber = Colors.index(str(tmp_df.iloc[a - 7][0]))
                                            self.Laag7.setBrush(QtColors[Colornumber])
                                        else:
                                            Colors.append(str(tmp_df.iloc[a - 7][0]))
                                            self.Laag7.setBrush(QtColors[ColorCounter])
                                            ColorCounter = ColorCounter + 1
                                        self.series.append(self.Laag7)
                                        if a >= 8:
                                            self.Laag8 = QBarSet(str(tmp_df.iloc[a - 8][0]))
                                            self.Laag8 << abs(
                                                float(tmp_df.iloc[a - 7][1]) - float(tmp_df.iloc[a - 8][1]))
                                            if str(tmp_df.iloc[a - 8][0]) in Colors:
                                                Colornumber = Colors.index(str(tmp_df.iloc[a - 8][0]))
                                                self.Laag8.setBrush(QtColors[Colornumber])
                                            else:
                                                Colors.append(str(tmp_df.iloc[a - 8][0]))
                                                self.Laag8.setBrush(QtColors[ColorCounter])
                                                ColorCounter = ColorCounter + 1
                                            self.series.append(self.Laag7)

                                            self.series.append(self.Laag8)
                                            if a >= 9:
                                                self.Laag9 = QBarSet(str(tmp_df.iloc[a - 9][0]))
                                                self.Laag9 << abs(
                                                    float(tmp_df.iloc[a - 8][1]) - float(tmp_df.iloc[a - 9][1]))
                                                if str(tmp_df.iloc[a - 9][0]) in Colors:
                                                    Colornumber = Colors.index(str(tmp_df.iloc[a - 9][0]))
                                                    self.Laag9.setBrush(QtColors[Colornumber])
                                                else:
                                                    Colors.append(str(tmp_df.iloc[a - 9][0]))
                                                    self.Laag9.setBrush(QtColors[ColorCounter])
                                                    ColorCounter = ColorCounter + 1
                                                self.series.append(self.Laag9)
                                                if a >= 10:
                                                    self.Laag10 = QBarSet(str(tmp_df.iloc[a - 10][0]))
                                                    self.Laag10 << abs(
                                                        float(tmp_df.iloc[a - 9][1]) - float(tmp_df.iloc[a - 10][1]))
                                                    if str(tmp_df.iloc[a - 10][0]) in Colors:
                                                        Colornumber = Colors.index(str(tmp_df.iloc[a - 10][0]))
                                                        self.Laag10.setBrush(QtColors[Colornumber])
                                                    else:
                                                        Colors.append(str(tmp_df.iloc[a - 10][0]))
                                                        self.Laag10.setBrush(QtColors[ColorCounter])
                                                        ColorCounter = ColorCounter + 1
                                                    self.series.append(self.Laag10)
                                                    if a >= 11:
                                                        self.Laag11 = QBarSet(str(tmp_df.iloc[a - 11][0]))
                                                        self.Laag11 << abs(float(tmp_df.iloc[a - 10][1]) - float(
                                                            tmp_df.iloc[a - 11][1]))
                                                        if str(tmp_df.iloc[a - 11][0]) in Colors:
                                                            Colornumber = Colors.index(str(tmp_df.iloc[a - 11][0]))
                                                            self.Laag11.setBrush(QtColors[Colornumber])
                                                        else:
                                                            Colors.append(str(tmp_df.iloc[a - 11][0]))
                                                            self.Laag11.setBrush(QtColors[ColorCounter])
                                                            ColorCounter = ColorCounter + 1
                                                        self.series.append(self.Laag11)
                                                        if a >= 12:
                                                            self.Laag12 = QBarSet(str(tmp_df.iloc[a - 12][0]))
                                                            self.Laag12 << abs(float(tmp_df.iloc[a - 11][1]) - float(
                                                                tmp_df.iloc[a - 12][1]))
                                                            if str(tmp_df.iloc[a - 12][0]) in Colors:
                                                                Colornumber = Colors.index(str(tmp_df.iloc[a - 12][0]))
                                                                self.Laag12.setBrush(QtColors[Colornumber])
                                                            else:
                                                                Colors.append(str(tmp_df.iloc[a - 12][0]))
                                                                self.Laag12.setBrush(QtColors[ColorCounter])
                                                                ColorCounter = ColorCounter + 1
                                                            self.series.append(self.Laag12)
            self.SoilProfile_Picture.addSeries(self.series)

            self.chartView.repaint()

        else:
            self.set0 = QBarSet("")

            self.set0 << 0

            self.series = QStackedBarSeries()
            self.series.append(self.set0)

            self.SoilProfile_Picture = QChart()
            axis_x = QBarCategoryAxis()
            axis_x.append('Grondprofile')
            self.SoilProfile_Picture.setAxisX(axis_x, self.series)
            axis_y = QValueAxis()
            axis_y.setRange(-20, 5)
            self.SoilProfile_Picture.setAxisY(axis_y)
            self.SoilProfile_Picture.addSeries(self.series)
            self.SoilProfile_Picture.setAnimationOptions(QChart.SeriesAnimations)
            self.SoilProfile_Picture.legend().setAlignment(Qt.AlignLeft)
            self.chartView = QChartView(self.SoilProfile_Picture)
            self.chartView.setRenderHint(QPainter.Antialiasing)
            self.chartView.setMinimumWidth(300)

    def AddTabs(self):
        if self.Parameter_variations.isChecked() == True:
            self.AddTabs_Variations_in_parameters()
        elif self.Load_Variations.isChecked() == True:
            self.Calc_load_cases()
            self.AddTabs_Variations_in_loads()

    #om een reeks van berekeningen uit te voeren, een aantal variaties kan worden doorgevoerd:
    # - verschillende loads (belastingen)
    # - verschillende bodem parameter variaties

    def AddTabs_Variations_in_loads(self):
        if self.ViewProfile.rowCount() < 2:
           QMessageBox.information(self, "Error", "You should first enter a soilprofile, a database and match those in this tab")
        else:
            self.Plaxis_Json_Files.clear()
            self.Plaxis_JsonFileNames.clear()
            #[q_rep_plaxis, q_d_plaxis, W_plaxis, L_plaxis, gws_plaxis, fund_plaxis, D_plaxis, Gv_plaxis]
            for _ in reversed(range(self.TabCounter)):  # this loop removes previous variations if the tabs are filled with them
                self.tab5_3.removeTab(_)
            self.TabCounter = 0

            self.Plx_Variations2.setText(str(len(self.Plaxis_Input)))

            for Variation in range(len(self.Plaxis_Input)): #this loop goes trough all variations
                List_with_parameters = self.Plaxis_Input[Variation]
                string = str("Plx_file_" + str(List_with_parameters[0]))  # TAB name
                Type = QTableWidget()
                Type.setColumnCount(int(self.ViewProfile.columnCount() + 7))
                Type.setHorizontalHeaderLabels(self.Labels)

                for row in range(self.ViewProfile.rowCount()):  # this loop fills every type with the standard soil profile. Variations arent made yet
                    Type.insertRow(row)
                    for column in range(self.ViewProfile.columnCount()):
                        Type.setItem(row, column, QTableWidgetItem(self.ViewProfile.item(row, column).text()))
                        Type.setItem(row, 24, QTableWidgetItem(str(List_with_parameters[4])))
                        Type.setItem(row, 25, QTableWidgetItem(str(List_with_parameters[3])))
                        Type.setItem(row, 26, QTableWidgetItem(str(List_with_parameters[1])))
                        Type.setItem(row, 27, QTableWidgetItem(str(List_with_parameters[2])))
                        Type.setItem(row, 28, QTableWidgetItem(str(List_with_parameters[6])))
                        Type.setItem(row, 29, QTableWidgetItem(str(List_with_parameters[8])))
                        Type.setItem(row, 30, QTableWidgetItem(str(List_with_parameters[7])))





                """ In this piece of code Panda Dataframes will be created, filled with data of the different variations"""
                dataframe = pd.DataFrame(index=np.arange(int(Type.rowCount())), columns=self.Labels)
                for row in range(Type.rowCount()):
                    for column in range(Type.columnCount()):
                        dataframe.iloc[row, column] = Type.item(row, column).text()
                filename = str(string + ".json")
                self.Plaxis_JsonFileNames.append(filename)
                self.Plaxis_Json_Files.append(dataframe)
                self.tab5_3.addTab(Type, str(string))
                self.TabCounter = self.TabCounter + 1

    def AddTabs_Variations_in_parameters(self):
        """This function fills the table with all variations, so you can check if the desired variations are made correctly"""

        All_Variations_of_Parameters = []
        #hier worden het aantal variaties bepaald:
        Variations_Counter_Parameters = int(np.floor_divide((float(self.Tab5_1_2_Variations8.text())-float(self.Tab5_1_2_Variations6.text())), float(self.Tab5_1_2_Variations10.text()))) #aantal variaties bepalen op basis van lower en upper bound en interval
        Variations_Counter_Parameters +=2 # om de begin en eindwaarde erbij op te tellen


        for Variation in range(Variations_Counter_Parameters-1):
            All_Variations_of_Parameters.append(float(float(self.Tab5_1_2_Variations10.text())*Variation)+ float(self.Tab5_1_2_Variations6.text()))
        All_Variations_of_Parameters.append(float(self.Tab5_1_2_Variations8.text()))

        if All_Variations_of_Parameters[-1] == All_Variations_of_Parameters[-2]: #check of er geen dubbele waarden voorkomen doordat het interval precies op een grens komt. Indien nodig verwijderen
            del All_Variations_of_Parameters[-1]
            Variations_Counter_Parameters -=1
        self.Plx_Variations2.setText(str(Variations_Counter_Parameters))

        ChangedParameter = self.Tab5_1_2_Variations2.currentText() #deze parameter wordt aangepast
        columnPar = self.Labels.index(str(ChangedParameter))
        rowPar = self.Tab5_1_2_Variations4.value() - 1
        if rowPar > int(self.ViewProfile.rowCount()-1):
            QMessageBox.information(self, "Error", "This layer does not exist")
        if columnPar == 2 or 0 and rowPar ==0:
            QMessageBox.information(self, "Error", "You cant vary the first layer upwards. It is not allowed to change maaiveld")
        else:
            for _ in reversed(range(self.TabCounter)): #this loop removes previous variations if the tabs are filled with them
                self.tab5_3.removeTab(_)
            self.TabCounter = 0
            Reverse_variations = All_Variations_of_Parameters
            Reverse_variations.reverse()

            """Here an list is created which will be filled with panda dataframes in the end, which contains the variations"""
            dirName = 'Plaxis_jsonFiles'
            self.Plaxis_Json_Files.clear()
            self.Plaxis_JsonFileNames.clear()
            try:
                os.mkdir(dirName)
                print("Directory ", dirName, " Created ")
            except FileExistsError:
                print("Directory ", dirName, " already exists")


            for _ in range(Variations_Counter_Parameters): # this for loop runs through all variations
                self.BooleanThickness_1 = False

                string = str("Plx_file_" + str(_)) #TAB name
                Type = QTableWidget()
                Type.setColumnCount(int(self.ViewProfile.columnCount()+7))
                Type.setHorizontalHeaderLabels(self.Labels)


                for row in range(self.ViewProfile.rowCount()): #this loop fills every type with the standard soil profile. Variations arent made yet
                    Type.insertRow(row)
                    for column in range(self.ViewProfile.columnCount()):
                        Type.setItem(row, column, QTableWidgetItem(self.ViewProfile.item(row, column).text()))

                    Type.setItem(row, 24, QTableWidgetItem(str(self.Tab5_1_2_Variations13.text())))
                    Type.setItem(row, 25, QTableWidgetItem(str(self.Tab5_1_2_Variations15.text())))
                    Type.setItem(row, 26, QTableWidgetItem(str(self.Tab5_1_2_Variations17.text())))
                    Type.setItem(row, 27, QTableWidgetItem(str('not used in this model')))
                    Type.setItem(row, 28, QTableWidgetItem(str('not used in this model')))
                    Type.setItem(row, 29, QTableWidgetItem(str('not used in this model')))
                    Type.setItem(row, 30, QTableWidgetItem(str('not used in this model')))



                """This piece of code will set the variations which do not influence soil boundaries"""
                Oldydry = float(Type.item(rowPar, 4).text())
                Oldysaturated = float(Type.item(rowPar, 5).text())
                if columnPar > 2:  # check if the variable is not one of the first three columns (upper layer, lower layer, boundary thickness)
                    Type.setItem(rowPar, columnPar, QTableWidgetItem(str(All_Variations_of_Parameters[_])))
                    Type.item(rowPar, columnPar).setBackground(Qt.red)

                    if columnPar == 4:
                        ydry = float(All_Variations_of_Parameters[_])
                        print(Oldydry)
                        ysaturated = float(Type.item(rowPar, 5).text())
                        y_dif = ysaturated - Oldydry
                        Newysaturated = ydry + y_dif
                        Type.setItem(rowPar, 5, QTableWidgetItem(str(Newysaturated)))
                        Type.item(rowPar, 5).setBackground(Qt.green)

                    if columnPar == 5:
                        ysaturated = float(All_Variations_of_Parameters[_])
                        ydry = float(Type.item(rowPar, 4).text())
                        y_dif = ydry - Oldysaturated
                        Newydry = ysaturated + y_dif
                        Type.setItem(rowPar, 4, QTableWidgetItem(str(Newydry)))
                        Type.item(rowPar, 4).setBackground(Qt.green)

                    if columnPar == 7:
                        phi = float(All_Variations_of_Parameters[_])
                        convDelta = float(Type.item(rowPar, 6).text())
                        NewDelta = convDelta*phi
                        Type.setItem(rowPar, 8, QTableWidgetItem(str(NewDelta)))
                        Type.item(rowPar, 8).setBackground(Qt.green)

                        NewInter = np.tan(np.radians(NewDelta))/np.tan(np.radians(phi))
                        Type.setItem(rowPar, 17, QTableWidgetItem(str(NewInter)))
                        Type.item(rowPar, 17).setBackground(Qt.green)

                        G0ref = float(Type.item(rowPar, 18).text())
                        Cohesion = float(Type.item(rowPar, 9).text())

                        NewGamma07 = (((1 / (9 * G0ref)) * (2 * Cohesion * (1 + np.cos(np.radians(phi) )) +( 100 * (
                                    1 + (1-np.sin(np.radians(phi)))) * np.sin(np.radians(2*phi) )))))
                        Type.setItem(rowPar, 19, QTableWidgetItem(str(NewGamma07)))
                        Type.item(rowPar, 19).setBackground(Qt.green)

                    if columnPar == 9:
                        Cohesion = float(All_Variations_of_Parameters[_])
                        phi = float(Type.item(rowPar, 7).text())

                        G0ref = float(Type.item(rowPar, 18).text())

                        NewGamma07 = (((1 / (9 * G0ref)) * (2 * Cohesion * (1 + np.cos(np.radians(phi) )) +( 100 * (
                                    1 + (1-np.sin(np.radians(phi)))) * np.sin(np.radians(2*phi) )))))

                        Type.setItem(rowPar, 19, QTableWidgetItem(str(NewGamma07)))
                        Type.item(rowPar, 19).setBackground(Qt.green)

                    if columnPar == 13:
                        Eoed = float(All_Variations_of_Parameters[_])
                        E50conv = float(Type.item(rowPar, 10).text())
                        E50new = E50conv * Eoed
                        Type.setItem(rowPar, 14, QTableWidgetItem(str(E50new)))
                        Type.item(rowPar, 14).setBackground(Qt.green)

                        Eurconv = float(Type.item(rowPar, 11).text())
                        Eurnew = Eurconv * E50new
                        Type.setItem(rowPar, 15, QTableWidgetItem(str(Eurnew)))
                        Type.item(rowPar, 15).setBackground(Qt.green)

                        Cohesion = float(Type.item(rowPar, 9).text())
                        phi = float(Type.item(rowPar, 7).text())

                        NewG0ref = float((Eurnew*4)/(2*(1+0.2)))
                        Type.setItem(rowPar, 18, QTableWidgetItem(str(NewG0ref)))
                        Type.item(rowPar, 18).setBackground(Qt.green)

                        Gamma07 = (((1 / (9 * NewG0ref)) * (2 * Cohesion * (1 + np.cos(np.radians(phi) )) +( 100 * (
                                    1 + (1-np.sin(np.radians(phi)))) * np.sin(np.radians(2*phi) )))))
                        Type.setItem(rowPar, 19, QTableWidgetItem(str(Gamma07)))
                        Type.item(rowPar, 19).setBackground(Qt.green)


                    """This piece of code will set the variations which influences soil boundaries"""
                elif columnPar == 0: #upper boundary variation
                    if float(self.Tab5_1_2_Variations6.text()) <= float(Type.item(rowPar, columnPar+1).text()):
                        QMessageBox.information(self, "Error", "The lower boundary for the upper layer variations may not be lower or equal than the bottom boundary of the soil")
                        break
                    elif float(self.Tab5_1_2_Variations8.text()) > float(Type.item(0, 0).text()):
                        QMessageBox.information(self, "Error", "The upper boundary for the upper layer variations may not be higher than the bottom boundary of the soil")
                        break
                    else:
                        Type.setItem(rowPar, columnPar, QTableWidgetItem(str(All_Variations_of_Parameters[_])))
                        Type.setItem(rowPar-1, columnPar+1, QTableWidgetItem(str(All_Variations_of_Parameters[_])))
                        

                        while self.BooleanThickness_1 == False:
                            DoubleLayersCheck = []
                            for soil in range(Type.rowCount()):
                                top_boundary = float(Type.item(soil, 0).text())
                                lower_boundary = float(Type.item(soil, 1).text())
                                if top_boundary <= lower_boundary:
                                    DoubleLayersCheck.append(int(soil))
                                    if soil > 0:
                                        Type.setItem((soil-1), columnPar+1, QTableWidgetItem(str(All_Variations_of_Parameters[_])))


                            for soil in DoubleLayersCheck:
                                Type.removeRow(soil)

                            for row in range(Type.rowCount()):
                                Dikte = float(Type.item(row, 0).text()) - float(Type.item(row, 1).text())
                                Type.setItem(row, 2, QTableWidgetItem(str(Dikte)))


                            if not DoubleLayersCheck:
                                self.BooleanThickness_1 = True

                elif columnPar == 1: # lower boundary variation
                    if float(self.Tab5_1_2_Variations8.text()) >= float(Type.item(rowPar, columnPar-1).text()):
                        QMessageBox.information(self, "Error", "The upper boundary for the lower layer variations may not be higher or equal than the top boundary of the soil")
                        break
                    else:
                        Type.setItem(rowPar, columnPar, QTableWidgetItem(str(Reverse_variations[_])))
                        layertoremove = []
                        for row in range(Type.rowCount()):
                            bound_value = float(Type.item(row, 1).text())
                            if bound_value >= Reverse_variations[_]:
                                layertoremove.append(float(row))
                                if float(rowPar) in layertoremove:
                                    layertoremove.remove(rowPar)
                        layertoremove.reverse()
                        for row in layertoremove:
                            Type.removeRow(row)
                        Type.setItem(rowPar + 1, columnPar - 1, QTableWidgetItem(str(Reverse_variations[_])))
                        Type.item(rowPar+1, columnPar-1).setBackground(Qt.red) #change color to make changes visible


                        for row in range(Type.rowCount()):
                            Dikte = float(Type.item(row, 0).text()) - float(Type.item(row, 1).text())
                            Type.setItem(row, 2, QTableWidgetItem(str(Dikte)))

                """ In this piece of code Panda Dataframes will be created, filled with data of the different variations"""
                dataframe = pd.DataFrame(index=np.arange(int(Type.rowCount())), columns=self.Labels)
                for row in range(Type.rowCount()):
                    for column in range(len(self.Labels)):
                        item = Type.item(row, column).text()
                        dataframe.iloc[row, column] = Type.item(row, column).text()


                filename = str(string + ".json")
                self.Plaxis_JsonFileNames.append(filename)
                self.Plaxis_Json_Files.append(dataframe)
                self.tab5_3.addTab(Type, str(string))
                self.TabCounter = self.TabCounter + 1

    def Load_Finished_Data(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText('Are  you sure that the Soil profile you gave in matches the parameters on the left side?' +
                    ' Do you wish to continue?')
        msg.setWindowTitle('Confirmation requested')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        retval = msg.exec_()


        #reply = QMessageBox.question(self, "Question", "Are you sure that the given Soil Profile matches the parameters displayed at the left side of the page?", QMessageBox_StandardButtons=QMessageBox.No|QMessageBox.Yes )


        #retval = reply.exec_()

        if retval == QMessageBox.Yes:

            self.ViewProfile.setRowCount(0)
            Viewer = TableWidget()
            if Viewer.DatabaseOK == True:
                if self.Soil_Profile.rowCount() != 0:
                    File = Viewer.Database_File
                    self.ViewProfile.setColumnCount(24)
                    self.Labels = ["Upper soil boundary\n[m]", "Lower soil boundary\n[m]", "Thickness\n[m]", "Soil type\n[-]",
                                   "ydry\n[kN/m^3]", "ysaturated\n[kN/m^3]","Phi / Delta", "Internal friction\nangle", "Delta\n[]",
                                   "Cohesion\n[kPa]", "E50 / E0ed\n[-]",
                                   "Eur / E50 \n[-]", "Conusfactor\n[-]", "Eoed\n[kPa]", "E'50ref\n[kPa]",
                                   "EurRef\n[kPa]", "Power\n[-]", "RInter\n[-]", "Initial shear\nstrain modulus\n[kPa]",
                                   "Shear strain\n[-]", "OCR\n[-]", "POP\n[-]", "DrainageType\n[-]", "GWL\n[m]", "Area Length\n[m]",
                                   "Area Width\n[m]", "q_rep\n[kN/m]", "q_d\n[kN/m]", 'Z, relative to\nNAP\n[m]',
                                   "Soil type\nenhancement", "Thickness Soil\nEnhancement [m]"]
                    self.ViewProfile.setHorizontalHeaderLabels(self.Labels)
                    self.Labels_var = ["Upper soil boundary\n[m]", "Lower soil boundary\n[m]", "Thickness\n[m]", "ydry\n[kN/m^3]","ysaturated\n[kN/m^3]", "Internal friction\nangle","Cohesion\n[kPa]",
                                                                "Eoed\n[kPa]" , "OCR\n[-]", "POP\n[-]", "GWL\n[m]"]
                    self.Labels_var_Correlations = ["None", "None", "None", "ywet", "ydry", "Rinter and Î³0,7", "Î³0,7", "E'50ref, y0,7 , Eurref and	G0ref", "POP", "OCR", "None"]

                    for _ in self.Labels_var:
                        self.Tab5_1_2_Variations2.addItem(_)
                    counter = 0
                    for Soil_Type in File['Laag grondsoort']:  # here we fill the combobox for stamp crane soil enhancement, textiles and geocells with the soil values in the database
                        if counter < 2:
                            'do nothing'
                            counter = counter + 1
                        else:
                            self.Widget3_2_3_5.addItem(str(Soil_Type))
                            self.Widget3_2_4_7.addItem(str(Soil_Type))
                            self.Widget3_2_5_7.addItem(str(Soil_Type))

                    for row in range(self.Soil_Profile.rowCount()):
                        self.ViewProfile.insertRow(row)
                        if float(row+1) == float(self.Soil_Profile.rowCount()):
                            Onderste_Laaggrens = str("-15.0")
                            self.ViewProfile.setItem(row, 1, QTableWidgetItem(Onderste_Laaggrens))
                        else:
                            Onderste_Laaggrens = str(self.Soil_Profile.item(row + 1, 1).text())
                            self.ViewProfile.setItem(row, 1, QTableWidgetItem(Onderste_Laaggrens))
                        self.ViewProfile.setItem(row, 0, QTableWidgetItem(self.Soil_Profile.item(row, 1).text()))
                        self.ViewProfile.setItem(row, 3, QTableWidgetItem(self.Soil_Profile.item(row, 0).text()))
                        Dikte = str(float(self.Soil_Profile.item(row, 1).text()) - float(Onderste_Laaggrens))
                        self.ViewProfile.setItem(row, 2, QTableWidgetItem(Dikte))


                        SoilLayer_to_Match = str(self.Soil_Profile.item(row, 0).text())
                        SoilParameters = File.loc[File['Laag grondsoort'] == SoilLayer_to_Match]
                        if len(SoilParameters) == 0:
                            QMessageBox.information(self,"Error", "You uploaded a soil profile which contains a layer of which its parameters are not included in the uploaded database. \n The soil layer of which its parameters are not included is" + str(SoilLayer_to_Match))
                            self.ViewProfile.clear()
                            self.ViewProfile.setColumnCount(0)
                            self.ViewProfile.setRowCount(0)
                            self.Widget3_2_3_5.clear()
                            self.Widget3_2_4_7.clear()
                            self.Widget3_2_5_7.clear()
                            break
                        elif self.Soil_GWS_Value.text() == "":
                            QMessageBox.information(self, "Error",
                                                    "You uploaded a soil profile without setting the GWL" )
                            self.ViewProfile.setColumnCount(0)
                            self.ViewProfile.setRowCount(0)
                            break

                        else:

                            for _ in range(19):
                                self.ViewProfile.setItem(row, int((int(_) + 4)), QTableWidgetItem(str(SoilParameters.iat[0, (int(_) + 1)])))
                            self.ViewProfile.setItem(row, 23,QTableWidgetItem(str(self.Soil_GWS_Value.text())))

                else:
                    QMessageBox.information(self, "Error", "No Soil Profile has been loaded")

            else:
                QMessageBox.information(self, "Error", "No Database has been loaded")



        if retval == QMessageBox.No:
            print("do nothing")

    def FillVariations_relations(self):
        """Code to fill the table which includes the relations between the different parameters"""
        counter = 0
        for _ in self.Labels_var:
            text = str(_).lower()
            if text == str(self.Tab5_1_2_Variations2.currentText()).lower():
                break
            else:
                counter +=1
        self.Variations_relations.clear()
        self.Variations_relations.setColumnCount(1)
        self.Variations_relations.setRowCount(1)
        self.Variations_relations.setItem(0, 0, QTableWidgetItem(str(self.Labels_var_Correlations[counter])))

    def Create_JSON_Files(self):
        if len(self.Plaxis_JsonFileNames) > 0:
            Folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
            for n_PlaxisFile in range(len(self.Plaxis_Json_Files)):
                self.Plaxis_Json_Files[n_PlaxisFile].to_json((os.path.join(Folder, self.Plaxis_JsonFileNames[n_PlaxisFile])))

            SoilTypeEnhancementList = []
            Viewer = TableWidget()
            File = Viewer.Database_File
            SoilLayer_to_Match1 = str(self.Widget3_2_3_5.currentText())
            SoilParameters1 = File.loc[File['Laag grondsoort'] == SoilLayer_to_Match1]
            SoilLayer_to_Match2 = str(self.Widget3_2_5_7.currentText())
            SoilParameters2 = File.loc[File['Laag grondsoort'] == SoilLayer_to_Match2]
            SoilLayer_to_Match3 = str(self.Widget3_2_4_7.currentText())
            SoilParameters3 = File.loc[File['Laag grondsoort'] == SoilLayer_to_Match3]
            lst = [SoilParameters1, SoilParameters2, SoilParameters3]
            result = pd.concat(lst)


            filename = Folder + str('\SoilTypes_PLAXIS.csv')
            result.to_csv(filename, index=False)
        else:
            QMessageBox.information(self, "Error", "No files to export")

    def RemoveComma(self, String_to_Check):
        variable = str(String_to_Check.text())
        Corrected_Variable = variable.replace(",", ".")
        String_to_Check.setText(str(Corrected_Variable))


    def Tab3(self):
        # Tab 3

        tab3 = QWidget()
        tab3.layout = QGridLayout()


        """"Tab 3.1 Rupskraan"""
        self.tab3Rups = QGroupBox("Crawler crane (CC)")
        self.tab3Rups.setFont(QFont("verbana", 14))
        #self.tab3Rups.setMinimumHeight(1800)
        self.tab3Rups.setMaximumSize(400, 1500)
        self.tab3RupsBox = QVBoxLayout()
        self.tab3Rups.setLayout(self.tab3RupsBox)
        scroll = QScrollArea()
        scroll.setWidget(self.tab3Rups)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(800)


        """"Load combinations"""
        LoadCombiWidget1 = QLabel("For the crawler crane, consider the")
        LoadCombiWidget2 = QCheckBox("Triangular load distribution")
        LoadCombiWidget3 = QCheckBox("Rectangular load distribution")

        self.tab3RupsBox.addWidget(LoadCombiWidget1)
        self.tab3RupsBox.addWidget(LoadCombiWidget2)
        self.tab3RupsBox.addWidget(LoadCombiWidget3)

        """"Without any enhancement"""

        tab3_1_1_Box = QGroupBox("Without any enhancement")
        tab3_1_1_Box.setFont(QFont("verbana", 14))
        tab3_1_1 = QVBoxLayout()
        tab3_1_1_Box.setLayout(tab3_1_1)

        tab3_1_1_1 = QHBoxLayout()
        tab3_1_1_2 = QHBoxLayout()
        tab3_1_1_3 = QHBoxLayout()

        Widget3_1_1_1 = QCheckBox("Include situation without enhancement")
        Widget3_1_1_2 = QLabel("W [m] =")
        Widget3_1_1_3 = QLineEdit("8.2")
        Widget3_1_1_3.setMaximumWidth(120)
        Widget3_1_1_4 = QLabel("L [m] =")
        Widget3_1_1_5 = QLineEdit("1.84")
        Widget3_1_1_5.setMaximumWidth(120)
        Widget3_1_1_6 = QLabel("Crane load \n(q-load) [kN]")
        Widget3_1_1_7 = QLineEdit()
        Widget3_1_1_7.setMaximumWidth(120)

        tab3_1_1_1.addWidget(Widget3_1_1_2)
        tab3_1_1_1.addWidget(Widget3_1_1_3)
        tab3_1_1_2.addWidget(Widget3_1_1_4)
        tab3_1_1_2.addWidget(Widget3_1_1_5)
        tab3_1_1_3.addWidget(Widget3_1_1_6)
        tab3_1_1_3.addWidget(Widget3_1_1_7)

        tab3_1_1.addWidget(Widget3_1_1_1)
        tab3_1_1.addLayout(tab3_1_1_1)
        tab3_1_1.addLayout(tab3_1_1_2)
        tab3_1_1.addLayout(tab3_1_1_3)

        self.tab3RupsBox.addWidget(tab3_1_1_Box)

        """""Draglineschotten Rupskraan"""

        tab3_1_2_Box = QGroupBox("Dragline mats CC")
        tab3_1_2_Box.setFont(QFont("verbana", 14))
        tab3_1_2 = QVBoxLayout()
        tab3_1_2_Box.setLayout(tab3_1_2)

        tab3_1_2_1 = QHBoxLayout()
        tab3_1_2_2 = QHBoxLayout()
        tab3_1_2_3 = QHBoxLayout()
        tab3_1_2_4 = QHBoxLayout()

        Widget3_1_2_1 = QCheckBox("Include situation with dragline mats ")
        Widget3_1_2_2 = QLabel("W [m] =")
        Widget3_1_2_3 = QLineEdit("12")
        Widget3_1_2_3.setMaximumWidth(120)
        Widget3_1_2_4 = QLabel("L [m] =")
        Widget3_1_2_5 = QLineEdit("6")
        Widget3_1_2_5.setMaximumWidth(120)
        Widget3_1_2_6 = QLabel("Crane load \n(q-load)[kN]")
        Widget3_1_2_7 = QLineEdit()
        Widget3_1_2_7.setMaximumWidth(120)
        Widget3_1_2_8 = QLabel("Load of crane mats \n(q-load)[kN]")
        Widget3_1_2_9 = QLineEdit()
        Widget3_1_2_9.setMaximumWidth(120)


        tab3_1_2_1.addWidget(Widget3_1_2_2)
        tab3_1_2_1.addWidget(Widget3_1_2_3)
        tab3_1_2_2.addWidget(Widget3_1_2_4)
        tab3_1_2_2.addWidget(Widget3_1_2_5)
        tab3_1_2_3.addWidget(Widget3_1_2_6)
        tab3_1_2_3.addWidget(Widget3_1_2_7)
        tab3_1_2_4.addWidget(Widget3_1_2_8)
        tab3_1_2_4.addWidget(Widget3_1_2_9)

        tab3_1_2.addWidget(Widget3_1_2_1)
        tab3_1_2.addLayout(tab3_1_2_1)
        tab3_1_2.addLayout(tab3_1_2_2)
        tab3_1_2.addLayout(tab3_1_2_3)
        tab3_1_2.addLayout(tab3_1_2_4)

        self.tab3RupsBox.addSpacing(20)
        self.tab3RupsBox.addWidget(tab3_1_2_Box)

        """""Grondverbetering Rupskraan"""

        tab3_1_3_Box = QGroupBox("Soil Enhancement CC")
        tab3_1_3_Box.setFont(QFont("verbana", 14))
        tab3_1_3 = QVBoxLayout()
        tab3_1_3_Box.setLayout(tab3_1_3)

        tab3_1_3_1 = QHBoxLayout()
        tab3_1_3_2 = QHBoxLayout()
        tab3_1_3_3 = QHBoxLayout()
        tab3_1_3_4 = QHBoxLayout()

        Widget3_1_3_1 = QCheckBox("Include situation with Soil Enhancement")

        Widget3_1_3_2 = QLabel("Depth of excavation [m]")
        Widget3_1_3_3 = QLineEdit()
        Widget3_1_3_3.setMaximumWidth(120)
        Widget3_1_3_4 = QLabel("Removed soil needs\nto be replaced by")
        Widget3_1_3_5 = QComboBox()
        Widget3_1_3_5.setMaximumWidth(120)
        Widget3_1_3_6 = QLabel("Please note that, in order to use this box,\nthe first box 'Without enhancement', needs\nto be filled in. The load, Width and Lenght\nfrom this box will be used")

        self.Widget3_1_3_7 = QCheckBox("D = 0.5 m")
        self.Widget3_1_3_8 = QCheckBox("D = 1.0 m")
        self.Widget3_1_3_9 = QCheckBox("D = 1.5 m")

        tab3_1_3_1.addWidget(Widget3_1_3_2)
        tab3_1_3_1.addWidget(Widget3_1_3_3)
        tab3_1_3_2.addWidget(Widget3_1_3_4)
        tab3_1_3_2.addWidget(Widget3_1_3_5)
        tab3_1_3_3.addWidget(Widget3_1_3_6)

        tab3_1_3_4.addWidget(self.Widget3_1_3_7)
        tab3_1_3_4.addWidget(self.Widget3_1_3_8)
        tab3_1_3_4.addWidget(self.Widget3_1_3_9)


        tab3_1_3.addWidget(Widget3_1_3_1)
        tab3_1_3.addLayout(tab3_1_3_1)
        tab3_1_3.addLayout(tab3_1_3_2)
        tab3_1_3.addLayout(tab3_1_3_3)
        tab3_1_3.addLayout(tab3_1_3_4)

        self.tab3RupsBox.addSpacing(5)
        self.tab3RupsBox.addWidget(tab3_1_3_Box)

        """""Geotextielen Rupskraan"""

        tab3_1_4_Box = QGroupBox("Geotextiles CC")
        tab3_1_4_Box.setFont(QFont("verbana", 14))
        tab3_1_4 = QVBoxLayout()
        tab3_1_4_Box.setLayout(tab3_1_4)

        tab3_1_4_1 = QHBoxLayout()
        tab3_1_4_2 = QHBoxLayout()
        tab3_1_4_3 = QHBoxLayout()
        tab3_1_4_4 = QHBoxLayout()

        Widget3_1_4_1 = QCheckBox("Include situation with Geotextiles")
        Widget3_1_4_2 = QLabel("W [m] =")
        self.Widget3_1_4_3 = QLineEdit("12")
        self.Widget3_1_4_3.setMaximumWidth(120)
        Widget3_1_4_4 = QLabel("L [m] =")
        self.Widget3_1_4_5 = QLineEdit("6")
        self.Widget3_1_4_5.setMaximumWidth(120)
        Widget3_1_4_6 = QLabel("Crane load \n(q-load)[kN]")
        self.Widget3_1_4_7 = QLineEdit()
        self.Widget3_1_4_7.setMaximumWidth(120)
        Widget3_1_4_8 = QLabel("Load of geotextiles \n(q-load)[kN]")
        Widget3_1_4_9 = QLineEdit()
        Widget3_1_4_9.setMaximumWidth(120)

        tab3_1_4_1.addWidget(Widget3_1_4_2)
        tab3_1_4_1.addWidget(self.Widget3_1_4_3)
        tab3_1_4_2.addWidget(Widget3_1_4_4)
        tab3_1_4_2.addWidget(self.Widget3_1_4_5)
        tab3_1_4_3.addWidget(Widget3_1_4_6)
        tab3_1_4_3.addWidget(self.Widget3_1_4_7)
        tab3_1_4_4.addWidget(Widget3_1_4_8)
        tab3_1_4_4.addWidget(Widget3_1_4_9)

        tab3_1_4.addWidget(Widget3_1_4_1)
        tab3_1_4.addLayout(tab3_1_4_1)
        tab3_1_4.addLayout(tab3_1_4_2)
        tab3_1_4.addLayout(tab3_1_4_3)
        tab3_1_4.addLayout(tab3_1_4_4)

        self.tab3RupsBox.addSpacing(20)
        self.tab3RupsBox.addWidget(tab3_1_4_Box)

        """""Geogrids Rupskraan"""

        tab3_1_5_Box = QGroupBox("Geogrids CC")
        tab3_1_5_Box.setFont(QFont("verbana", 14))
        tab3_1_5 = QVBoxLayout()
        tab3_1_5_Box.setLayout(tab3_1_5)

        tab3_1_5_1 = QHBoxLayout()
        tab3_1_5_2 = QHBoxLayout()
        tab3_1_5_3 = QHBoxLayout()
        tab3_1_5_4 = QHBoxLayout()

        Widget3_1_5_1 = QCheckBox("Include situation with Geogrids")
        Widget3_1_5_2 = QLabel("W [m] =")
        Widget3_1_5_3 = QLineEdit("12")
        Widget3_1_5_3.setMaximumWidth(120)
        Widget3_1_5_4 = QLabel("L [m] =")
        Widget3_1_5_5 = QLineEdit("6")
        Widget3_1_5_5.setMaximumWidth(120)
        Widget3_1_5_6 = QLabel("Crane load \n(q-load)[kN]")
        Widget3_1_5_7 = QLineEdit()
        Widget3_1_5_7.setMaximumWidth(120)
        Widget3_1_5_8 = QLabel("Load of geogrids \n(q-load)[kN]")
        Widget3_1_5_9 = QLineEdit()
        Widget3_1_5_9.setMaximumWidth(120)

        tab3_1_5_1.addWidget(Widget3_1_5_2)
        tab3_1_5_1.addWidget(Widget3_1_5_3)
        tab3_1_5_2.addWidget(Widget3_1_5_4)
        tab3_1_5_2.addWidget(Widget3_1_5_5)
        tab3_1_5_3.addWidget(Widget3_1_5_6)
        tab3_1_5_3.addWidget(Widget3_1_5_7)
        tab3_1_5_4.addWidget(Widget3_1_5_8)
        tab3_1_5_4.addWidget(Widget3_1_5_9)

        tab3_1_5.addWidget(Widget3_1_5_1)
        tab3_1_5.addLayout(tab3_1_5_1)
        tab3_1_5.addLayout(tab3_1_5_2)
        tab3_1_5.addLayout(tab3_1_5_3)
        tab3_1_5.addLayout(tab3_1_5_4)

        self.tab3RupsBox.addSpacing(20)
        self.tab3RupsBox.addWidget(tab3_1_5_Box)

        tab3.layout.addWidget(scroll, 1, 0)

        """Tab 3.2 outrigger crane"""
        """"Stempelkraan"""
        self.tab3Stempel = QGroupBox("Outrigger crane")
        self.tab3Stempel.setFont(QFont("verbana", 14))
        # self.tab3Stempel.setMinimumHeight(1800)
        self.tab3Stempel.setMaximumSize(400, 2700)
        self.tab3StempelBox = QVBoxLayout()
        self.tab3Stempel.setLayout(self.tab3StempelBox)
        scrollStempel = QScrollArea()
        scrollStempel.setWidget(self.tab3Stempel)
        scrollStempel.setWidgetResizable(True)
        scrollStempel.setFixedHeight(800)


        """"Without any enhancement"""

        tab3_2_1_Box = QGroupBox("No enhancement (initial phase)")
        tab3_2_1_Box.setFont(QFont("verbana", 14))
        tab3_2_1 = QVBoxLayout()
        tab3_2_1_Box.setLayout(tab3_2_1)

        tab3_2_1_1 = QHBoxLayout()
        tab3_2_1_2 = QHBoxLayout()
        tab3_2_1_3 = QHBoxLayout()

        self.Widget3_2_1_1 = QCheckBox("Include situation without enhancement")
        self.Widget3_2_1_1.setChecked(True)
        self.Widget3_2_1_1.setEnabled(False)
        Widget3_2_1_2 = QLabel("W (width of plate under outrigger) [m] =")
        self.Widget3_2_1_3 = QLineEdit("")
        self.Widget3_2_1_3.setMaximumWidth(120)
        self.Widget3_2_1_3.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.Widget3_2_1_3))
        Widget3_2_1_4 = QLabel("L (length of plate under outrigger) [m] =")
        self.Widget3_2_1_5 = QLineEdit("")
        self.Widget3_2_1_5.setMaximumWidth(120)
        self.Widget3_2_1_5.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.Widget3_2_1_5))
        Widget3_2_1_6 = QLabel("Crane load (q-load) [kN]")
        self.Widget3_2_1_7 = QLineEdit("")
        self.Widget3_2_1_7.setMaximumWidth(120)
        self.Widget3_2_1_7.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.Widget3_2_1_7))

        tab3_2_1_1.addWidget(Widget3_2_1_2)
        tab3_2_1_1.addWidget(self.Widget3_2_1_3)
        tab3_2_1_2.addWidget(Widget3_2_1_4)
        tab3_2_1_2.addWidget(self.Widget3_2_1_5)
        tab3_2_1_3.addWidget(Widget3_2_1_6)
        tab3_2_1_3.addWidget(self.Widget3_2_1_7)

        tab3_2_1.addWidget(self.Widget3_2_1_1)
        tab3_2_1.addLayout(tab3_2_1_1)
        tab3_2_1.addLayout(tab3_2_1_2)
        tab3_2_1.addLayout(tab3_2_1_3)

        self.tab3StempelBox.addWidget(tab3_2_1_Box)


        """""Draglineschotten Stempelkraan"""

        """Laag 1"""

        self.Mats_Main_Box = QGroupBox("Dragline mats") #the load needs to be filled in somewhere

        self.Mats_SubBox1_1 = QGroupBox("Layer 1 - always the lower mat layer")
        self.Mats_SubBox1_2 = QGroupBox("Layer 2 - always the upper mat layer")
        self.Mats_SubBox1_2.setVisible(False)

        SubboxFont = QFont("verbana", 12)
        SubboxFont.setBold(True)

        self.Mats_Main_Box.setFont(QFont("verbana", 14))
        # self.Mats_SubBox1_1.setFont(SubboxFont)
        # self.Mats_SubBox1_2.setFont(SubboxFont)

        Mats_Box_Layout = QVBoxLayout()

        Mats_1_1 = QVBoxLayout()

        Mats_1_1_1 = QHBoxLayout()
        Mats_1_1_2 = QHBoxLayout()
        Mats_1_1_3 = QHBoxLayout()
        Mats_1_1_4 = QHBoxLayout()

        M_Widget_1_1_1_Text = QLabel("Amount of mat layers")
        self.M_Widget_1_1_1 = QComboBox()
        self.M_Widget_1_1_1.signalsBlocked() # om ervoor te zorgen dat de combobox niet van waarde veranderd tijdens het scrollen
        self.M_Widget_1_1_1.addItem('1')
        self.M_Widget_1_1_1.addItem('2')
        self.M_Widget_1_1_1.activated.connect(self.ShowMats_1)
        self.M_Widget_1_1_2 = QCheckBox("Include situation A with dragline mats  ")
        self.M_Widget_1_1_2.setFont(SubboxFont)
        M_Widget_1_1_3 = QLabel("Total width of mats [m] =")
        self.M_Widget_1_1_4 = QLineEdit("")
        self.M_Widget_1_1_4.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_1_1_4))
        self.M_Widget_1_1_4.setMaximumWidth(120)
        M_Widget_1_1_5 = QLabel("Total length of mats [m] =")
        self.M_Widget_1_1_6 = QLineEdit("")
        self.M_Widget_1_1_6.setMaximumWidth(120)
        self.M_Widget_1_1_6.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_1_1_6))
        M_Widget_1_1_7 = QLabel("Thickness of one mat [m]")
        self.M_Widget_1_1_8 = QLineEdit("")
        self.M_Widget_1_1_8.setMaximumWidth(120)
        self.M_Widget_1_1_8.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_1_1_8))
        M_Widget_1_1_9 = QLabel("Volumetric weight of mats [kg/m3]")
        self.M_Widget_1_1_10 = QLineEdit("")
        self.M_Widget_1_1_10.setMaximumWidth(120)
        self.M_Widget_1_1_10.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_1_1_10))

        Mats_1_1_1.addWidget(M_Widget_1_1_3)
        Mats_1_1_1.addWidget(self.M_Widget_1_1_4)
        Mats_1_1_2.addWidget(M_Widget_1_1_5)
        Mats_1_1_2.addWidget(self.M_Widget_1_1_6)
        Mats_1_1_3.addWidget(M_Widget_1_1_7)
        Mats_1_1_3.addWidget(self.M_Widget_1_1_8)
        Mats_1_1_4.addWidget(M_Widget_1_1_9)
        Mats_1_1_4.addWidget(self.M_Widget_1_1_10)

        Mats_1_1.addSpacing(10)
        Mats_1_1.addLayout(Mats_1_1_1)
        Mats_1_1.addLayout(Mats_1_1_2)
        Mats_1_1.addLayout(Mats_1_1_3)
        Mats_1_1.addLayout(Mats_1_1_4)

        #self.tab3StempelBox.addSpacing(20)

        self.Mats_SubBox1_1.setLayout(Mats_1_1)

        Mats_Box_Layout.addWidget(self.M_Widget_1_1_2)
        Mats_Box_Layout.addWidget(M_Widget_1_1_1_Text)
        Mats_Box_Layout.addWidget(self.M_Widget_1_1_1)
        Mats_Box_Layout.addWidget(self.Mats_SubBox1_1)

        """ Laag 1.2"""

        Mats_1_2 = QVBoxLayout()

        Mats_1_2_1 = QHBoxLayout()
        Mats_1_2_2 = QHBoxLayout()
        Mats_1_2_3 = QHBoxLayout()
        Mats_1_2_4 = QHBoxLayout()

        M_Widget_1_2_3 = QLabel("Total width of mats [m] =")
        self.M_Widget_1_2_4 = QLineEdit("")
        self.M_Widget_1_2_4.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_1_2_4))
        self.M_Widget_1_2_4.setMaximumWidth(120)
        M_Widget_1_2_5 = QLabel("Total length of mats [m] =")
        self.M_Widget_1_2_6 = QLineEdit("")
        self.M_Widget_1_2_6.setMaximumWidth(120)
        self.M_Widget_1_2_6.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_1_2_6))
        M_Widget_1_2_7 = QLabel("Thickness of one mat [m]")
        self.M_Widget_1_2_8 = QLineEdit("")
        self.M_Widget_1_2_8.setMaximumWidth(120)
        self.M_Widget_1_2_8.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_1_2_8))
        M_Widget_1_2_9 = QLabel("Volumetric weight of mats [kg/m3]")
        self.M_Widget_1_2_10 = QLineEdit("")
        self.M_Widget_1_2_10.setMaximumWidth(120)
        self.M_Widget_1_2_10.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_1_2_10))

        Mats_1_2_1.addWidget(M_Widget_1_2_3)
        Mats_1_2_1.addWidget(self.M_Widget_1_2_4)
        Mats_1_2_2.addWidget(M_Widget_1_2_5)
        Mats_1_2_2.addWidget(self.M_Widget_1_2_6)
        Mats_1_2_3.addWidget(M_Widget_1_2_7)
        Mats_1_2_3.addWidget(self.M_Widget_1_2_8)
        Mats_1_2_4.addWidget(M_Widget_1_2_9)
        Mats_1_2_4.addWidget(self.M_Widget_1_2_10)

        Mats_1_2.addLayout(Mats_1_2_1)
        Mats_1_2.addLayout(Mats_1_2_2)
        Mats_1_2.addLayout(Mats_1_2_3)
        Mats_1_2.addLayout(Mats_1_2_4)

        #self.tab3StempelBox.addSpacing(20)

        self.Mats_SubBox1_2.setLayout(Mats_1_2)

        Mats_Box_Layout.addWidget(self.Mats_SubBox1_2)

        """Laag 2.1"""

        self.Mats_SubBox2_1 = QGroupBox("Layer 1 - always the lower mat layer ")
        self.Mats_SubBox2_2 = QGroupBox("Layer 1 - always the upper mat layer ")
        self.Mats_SubBox2_2.setVisible(False)

        Mats_2_1 = QVBoxLayout()

        Mats_2_1_1 = QHBoxLayout()
        Mats_2_2_2 = QHBoxLayout()
        Mats_2_1_3 = QHBoxLayout()
        Mats_2_1_4 = QHBoxLayout()

        M_Widget_2_1_1_Text = QLabel("Amount of mat layers")
        self.M_Widget_2_1_1 = QComboBox()
        self.M_Widget_2_1_1.signalsBlocked()  # om ervoor te zorgen dat de combobox niet van waarde veranderd tijdens het scrollen
        self.M_Widget_2_1_1.addItem('1')
        self.M_Widget_2_1_1.addItem('2')
        self.M_Widget_2_1_1.activated.connect(self.ShowMats_1)
        self.M_Widget_2_1_2 = QCheckBox("Include situation B with dragline mats  ")
        self.M_Widget_2_1_2.setFont(SubboxFont)
        M_Widget_2_1_3 = QLabel("Total width of mats [m] =")
        self.M_Widget_2_1_4 = QLineEdit("")
        self.M_Widget_2_1_4.setMaximumWidth(120)
        self.M_Widget_2_1_4.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_2_1_4))
        M_Widget_2_1_5 = QLabel("Total length of mats [m] =")
        self.M_Widget_2_1_6 = QLineEdit("")
        self.M_Widget_2_1_6.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_2_1_6))
        self.M_Widget_2_1_6.setMaximumWidth(120)
        M_Widget_2_1_7 = QLabel("Thickness of one mat [m]")
        self.M_Widget_2_1_8 = QLineEdit("")
        self.M_Widget_2_1_8.setMaximumWidth(120)
        self.M_Widget_2_1_8.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_2_1_8))
        M_Widget_2_1_9 = QLabel("Volumetric weight of mats [kg/m3]")
        self.M_Widget_2_1_10 = QLineEdit("")
        self.M_Widget_2_1_10.setMaximumWidth(120)
        self.M_Widget_2_1_10.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_2_1_10))

        Mats_2_1_1.addWidget(M_Widget_2_1_3)
        Mats_2_1_1.addWidget(self.M_Widget_2_1_4)
        Mats_2_2_2.addWidget(M_Widget_2_1_5)
        Mats_2_2_2.addWidget(self.M_Widget_2_1_6)
        Mats_2_1_3.addWidget(M_Widget_2_1_7)
        Mats_2_1_3.addWidget(self.M_Widget_2_1_8)
        Mats_2_1_4.addWidget(M_Widget_2_1_9)
        Mats_2_1_4.addWidget(self.M_Widget_2_1_10)

        Mats_2_1.addLayout(Mats_2_1_1)
        Mats_2_1.addLayout(Mats_2_2_2)
        Mats_2_1.addLayout(Mats_2_1_3)
        Mats_2_1.addLayout(Mats_2_1_4)

        self.Mats_SubBox2_1.setLayout(Mats_2_1)

        Mats_Box_Layout.addWidget(self.M_Widget_2_1_2)
        Mats_Box_Layout.addWidget(M_Widget_2_1_1_Text)
        Mats_Box_Layout.addWidget(self.M_Widget_2_1_1)
        Mats_Box_Layout.addWidget(self.Mats_SubBox2_1)

        """ Laag 2.2"""

        Mats_2_2 = QVBoxLayout()

        Mats_2_2_1 = QHBoxLayout()
        Mats_2_2_2 = QHBoxLayout()
        Mats_2_2_3 = QHBoxLayout()
        Mats_2_2_4 = QHBoxLayout()

        M_Widget_2_2_3 = QLabel("Total width of mats [m] =")
        self.M_Widget_2_2_4 = QLineEdit("")
        self.M_Widget_2_2_4.setMaximumWidth(120)
        self.M_Widget_2_2_4.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_2_2_4))
        M_Widget_2_2_5 = QLabel("Total length of mats [m] =")
        self.M_Widget_2_2_6 = QLineEdit("")
        self.M_Widget_2_2_6.setMaximumWidth(120)
        self.M_Widget_2_2_6.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_2_2_6))
        M_Widget_2_2_7 = QLabel("Thickness of one mat [m]")
        self.M_Widget_2_2_8 = QLineEdit("")
        self.M_Widget_2_2_8.setMaximumWidth(120)
        self.M_Widget_2_2_8.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_2_2_8))
        M_Widget_2_2_9 = QLabel("Volumetric weight of mats [kg/m3]")
        self.M_Widget_2_2_10 = QLineEdit("")
        self.M_Widget_2_2_10.setMaximumWidth(120)
        self.M_Widget_2_2_10.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_2_2_10))

        Mats_2_2_1.addWidget(M_Widget_2_2_3)
        Mats_2_2_1.addWidget(self.M_Widget_2_2_4)
        Mats_2_2_2.addWidget(M_Widget_2_2_5)
        Mats_2_2_2.addWidget(self.M_Widget_2_2_6)
        Mats_2_2_3.addWidget(M_Widget_2_2_7)
        Mats_2_2_3.addWidget(self.M_Widget_2_2_8)
        Mats_2_2_4.addWidget(M_Widget_2_2_9)
        Mats_2_2_4.addWidget(self.M_Widget_2_2_10)

        Mats_2_2.addLayout(Mats_2_2_1)
        Mats_2_2.addLayout(Mats_2_2_2)
        Mats_2_2.addLayout(Mats_2_2_3)
        Mats_2_2.addLayout(Mats_2_2_4)

        self.Mats_SubBox2_2.setLayout(Mats_2_2)

        Mats_Box_Layout.addWidget(self.Mats_SubBox2_2)

        """Laag 3.1"""

        self.Mats_SubBox3_1 = QGroupBox("Layer 1 - always the lower mat layer ")
        self.Mats_SubBox3_2 = QGroupBox("Layer 2 - always the upper mat layer ")
        self.Mats_SubBox3_2.setVisible(False)

        Mats_3_1 = QVBoxLayout()

        Mats_3_1_1 = QHBoxLayout()
        Mats_3_2_2 = QHBoxLayout()
        Mats_3_1_3 = QHBoxLayout()
        Mats_3_1_4 = QHBoxLayout()

        M_Widget_3_1_1_Text = QLabel("Amount of mat layers")
        self.M_Widget_3_1_1 = QComboBox()
        self.M_Widget_3_1_1.signalsBlocked()  # om ervoor te zorgen dat de combobox niet van waarde veranderd tijdens het scrollen
        self.M_Widget_3_1_1.addItem('1')
        self.M_Widget_3_1_1.addItem('2')
        self.M_Widget_3_1_1.activated.connect(self.ShowMats_1)
        self.M_Widget_3_1_2 = QCheckBox("Include situation C with dragline mats  ")
        self.M_Widget_3_1_2.setFont(SubboxFont)
        M_Widget_3_1_3 = QLabel("Total width of mats [m] =")
        self.M_Widget_3_1_4 = QLineEdit("")
        self.M_Widget_3_1_4.setMaximumWidth(120)
        self.M_Widget_3_1_4.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_3_1_4))
        M_Widget_3_1_5 = QLabel("Total length of mats [m] =")
        self.M_Widget_3_1_6 = QLineEdit("")
        self.M_Widget_3_1_6.setMaximumWidth(120)
        self.M_Widget_3_1_6.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_3_1_6))
        M_Widget_3_1_7 = QLabel("Thickness of one mat [m]")
        self.M_Widget_3_1_8 = QLineEdit("")
        self.M_Widget_3_1_8.setMaximumWidth(120)
        self.M_Widget_3_1_8.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_3_1_8))
        M_Widget_3_1_9 = QLabel("Volumetric weight of mats [kg/m3]")
        self.M_Widget_3_1_10 = QLineEdit("")
        self.M_Widget_3_1_10.setMaximumWidth(120)
        self.M_Widget_3_1_10.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_3_1_10))

        Mats_3_1_1.addWidget(M_Widget_3_1_3)
        Mats_3_1_1.addWidget(self.M_Widget_3_1_4)
        Mats_3_2_2.addWidget(M_Widget_3_1_5)
        Mats_3_2_2.addWidget(self.M_Widget_3_1_6)
        Mats_3_1_3.addWidget(M_Widget_3_1_7)
        Mats_3_1_3.addWidget(self.M_Widget_3_1_8)
        Mats_3_1_4.addWidget(M_Widget_3_1_9)
        Mats_3_1_4.addWidget(self.M_Widget_3_1_10)

        Mats_3_1.addLayout(Mats_3_1_1)
        Mats_3_1.addLayout(Mats_3_2_2)
        Mats_3_1.addLayout(Mats_3_1_3)
        Mats_3_1.addLayout(Mats_3_1_4)

        self.Mats_SubBox3_1.setLayout(Mats_3_1)

        Mats_Box_Layout.addWidget(self.M_Widget_3_1_2)
        Mats_Box_Layout.addWidget(M_Widget_3_1_1_Text)
        Mats_Box_Layout.addWidget(self.M_Widget_3_1_1)
        Mats_Box_Layout.addWidget(self.Mats_SubBox3_1)

        """ Laag 3.2"""

        Mats_3_2 = QVBoxLayout()

        Mats_2_3_1 = QHBoxLayout()
        Mats_3_2_2 = QHBoxLayout()
        Mats_3_2_3 = QHBoxLayout()
        Mats_3_2_4 = QHBoxLayout()

        M_Widget_3_2_3 = QLabel("Total width of mats [m] =")
        self.M_Widget_3_2_4 = QLineEdit("")
        self.M_Widget_3_2_4.setMaximumWidth(120)
        self.M_Widget_3_2_4.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_3_2_4))
        M_Widget_3_2_5 = QLabel("Total length of mats [m] =")
        self.M_Widget_3_2_6 = QLineEdit("")
        self.M_Widget_3_2_6.setMaximumWidth(120)
        self.M_Widget_3_2_6.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_3_2_6))
        M_Widget_3_2_7 = QLabel("Thickness of one mat [m]")
        self.M_Widget_3_2_8 = QLineEdit("")
        self.M_Widget_3_2_8.setMaximumWidth(120)
        self.M_Widget_3_2_8.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_3_2_8))
        M_Widget_3_2_9 = QLabel("Volumetric weight of mats [kg/m3]")
        self.M_Widget_3_2_10 = QLineEdit("")
        self.M_Widget_3_2_10.setMaximumWidth(120)
        self.M_Widget_3_2_10.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_3_2_10))

        Mats_2_3_1.addWidget(M_Widget_3_2_3)
        Mats_2_3_1.addWidget(self.M_Widget_3_2_4)
        Mats_3_2_2.addWidget(M_Widget_3_2_5)
        Mats_3_2_2.addWidget(self.M_Widget_3_2_6)
        Mats_3_2_3.addWidget(M_Widget_3_2_7)
        Mats_3_2_3.addWidget(self.M_Widget_3_2_8)
        Mats_3_2_4.addWidget(M_Widget_3_2_9)
        Mats_3_2_4.addWidget(self.M_Widget_3_2_10)

        Mats_3_2.addLayout(Mats_2_3_1)
        Mats_3_2.addLayout(Mats_3_2_2)
        Mats_3_2.addLayout(Mats_3_2_3)
        Mats_3_2.addLayout(Mats_3_2_4)

        self.Mats_SubBox3_2.setLayout(Mats_3_2)

        Mats_Box_Layout.addWidget(self.Mats_SubBox3_2)

        """Laag 4.1"""

        self.Mats_SubBox4_1 = QGroupBox("Layer 1 - always the lower mat layer ")
        self.Mats_SubBox4_2 = QGroupBox("Layer 2 - always the upper mat layer ")
        self.Mats_SubBox4_2.setVisible(False)

        Mats_4_1 = QVBoxLayout()

        Mats_4_1_1 = QHBoxLayout()
        Mats_4_2_2 = QHBoxLayout()
        Mats_4_1_3 = QHBoxLayout()
        Mats_4_1_4 = QHBoxLayout()

        M_Widget_4_1_1_Text = QLabel("Amount of mat layers")
        self.M_Widget_4_1_1 = QComboBox()
        self.M_Widget_4_1_1.signalsBlocked()  # om ervoor te zorgen dat de combobox niet van waarde veranderd tijdens het scrollen
        self.M_Widget_4_1_1.addItem('1')
        self.M_Widget_4_1_1.addItem('2')
        self.M_Widget_4_1_1.activated.connect(self.ShowMats_1)
        self.M_Widget_4_1_2 = QCheckBox("Include situation D with dragline mats  ")
        self.M_Widget_4_1_2.setFont(SubboxFont)
        M_Widget_4_1_3 = QLabel("Total width of mats [m] =")
        self.M_Widget_4_1_4 = QLineEdit("")
        self.M_Widget_4_1_4.setMaximumWidth(120)
        self.M_Widget_4_1_4.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_4_1_4))
        M_Widget_4_1_5 = QLabel("Total length of mats [m] =")
        self.M_Widget_4_1_6 = QLineEdit("")
        self.M_Widget_4_1_6.setMaximumWidth(120)
        self.M_Widget_4_1_6.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_4_1_6))
        M_Widget_4_1_7 = QLabel("Thickness of one mat [m]")
        self.M_Widget_4_1_8 = QLineEdit("")
        self.M_Widget_4_1_8.setMaximumWidth(120)
        self.M_Widget_4_1_8.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_4_1_8))
        M_Widget_4_1_9 = QLabel("Volumetric weight of mats [kg/m3]")
        self.M_Widget_4_1_10 = QLineEdit("")
        self.M_Widget_4_1_10.setMaximumWidth(120)
        self.M_Widget_4_1_10.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_4_1_10))

        Mats_4_1_1.addWidget(M_Widget_4_1_3)
        Mats_4_1_1.addWidget(self.M_Widget_4_1_4)
        Mats_4_2_2.addWidget(M_Widget_4_1_5)
        Mats_4_2_2.addWidget(self.M_Widget_4_1_6)
        Mats_4_1_3.addWidget(M_Widget_4_1_7)
        Mats_4_1_3.addWidget(self.M_Widget_4_1_8)
        Mats_4_1_4.addWidget(M_Widget_4_1_9)
        Mats_4_1_4.addWidget(self.M_Widget_4_1_10)

        Mats_4_1.addLayout(Mats_4_1_1)
        Mats_4_1.addLayout(Mats_4_2_2)
        Mats_4_1.addLayout(Mats_4_1_3)
        Mats_4_1.addLayout(Mats_4_1_4)

        self.Mats_SubBox4_1.setLayout(Mats_4_1)

        Mats_Box_Layout.addWidget(self.M_Widget_4_1_2)
        Mats_Box_Layout.addWidget(M_Widget_4_1_1_Text)
        Mats_Box_Layout.addWidget(self.M_Widget_4_1_1)
        Mats_Box_Layout.addWidget(self.Mats_SubBox4_1)

        """ Laag 4.2"""

        Mats_4_2 = QVBoxLayout()

        Mats_2_4_1 = QHBoxLayout()
        Mats_4_2_2 = QHBoxLayout()
        Mats_4_2_3 = QHBoxLayout()
        Mats_4_2_4 = QHBoxLayout()

        M_Widget_4_2_3 = QLabel("Total width of mats [m] =")
        self.M_Widget_4_2_4 = QLineEdit("")
        self.M_Widget_4_2_4.setMaximumWidth(120)
        self.M_Widget_4_2_4.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_4_2_4))
        M_Widget_4_2_5 = QLabel("Total length of mats [m] =")
        self.M_Widget_4_2_6 = QLineEdit("")
        self.M_Widget_4_2_6.setMaximumWidth(120)
        self.M_Widget_4_2_6.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_4_2_6))
        M_Widget_4_2_7 = QLabel("Thickness of one mat [m]")
        self.M_Widget_4_2_8 = QLineEdit("")
        self.M_Widget_4_2_8.setMaximumWidth(120)
        self.M_Widget_4_2_8.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_4_2_8))
        M_Widget_4_2_9 = QLabel("Volumetric weight of mats [kg/m3]")
        self.M_Widget_4_2_10 = QLineEdit("")
        self.M_Widget_4_2_10.setMaximumWidth(120)
        self.M_Widget_4_2_10.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.M_Widget_4_2_10))

        Mats_2_4_1.addWidget(M_Widget_4_2_3)
        Mats_2_4_1.addWidget(self.M_Widget_4_2_4)
        Mats_4_2_2.addWidget(M_Widget_4_2_5)
        Mats_4_2_2.addWidget(self.M_Widget_4_2_6)
        Mats_4_2_3.addWidget(M_Widget_4_2_7)
        Mats_4_2_3.addWidget(self.M_Widget_4_2_8)
        Mats_4_2_4.addWidget(M_Widget_4_2_9)
        Mats_4_2_4.addWidget(self.M_Widget_4_2_10)

        Mats_4_2.addLayout(Mats_2_4_1)
        Mats_4_2.addLayout(Mats_4_2_2)
        Mats_4_2.addLayout(Mats_4_2_3)
        Mats_4_2.addLayout(Mats_4_2_4)

        self.tab3StempelBox.addSpacing(20)

        self.Mats_SubBox4_2.setLayout(Mats_4_2)

        Mats_Box_Layout.addWidget(self.Mats_SubBox4_2)


        self.Mats_Main_Box.setLayout(Mats_Box_Layout)
        self.tab3StempelBox.addWidget(self.Mats_Main_Box)




        """""Grondverbetering Stempelkraan"""

        tab3_2_3_Box = QGroupBox("Soil Enhancement")
        tab3_2_3_Box.setFont(QFont("verbana", 14))
        tab3_2_3 = QVBoxLayout()
        tab3_2_3_Box.setLayout(tab3_2_3)

        tab3_2_3_1 = QHBoxLayout()  ####
        tab3_2_3_2 = QHBoxLayout()
        tab3_2_3_3 = QHBoxLayout()
        tab3_2_3_4 = QHBoxLayout()

        self.Widget3_2_3_1 = QCheckBox("Include situation with Soil Enhancement")  ####
        self.Widget3_2_3_1.setFont(SubboxFont)

        Widget3_2_3_2 = QLabel("Depth of excavation [m]")
        self.Widget3_2_3_3 = QLineEdit("1")
        self.Widget3_2_3_3.setMaximumWidth(120)
        Widget3_2_3_4 = QLabel("Removed soil needs\nto be replaced by")
        self.Widget3_2_3_5 = QComboBox()
        self.Widget3_2_3_5.setMaximumWidth(120)
        Widget3_2_3_6 = QLabel(
            "Please note that, in order to use this box,\nthe first box 'Without enhancement', needs\nto be filled in. The load, Width and Lenght\nfrom this box will be used")
        self.Widget3_2_3_7 = QCheckBox('D = 0.5 m')
        self.Widget3_2_3_8 = QCheckBox('D = 1.0 m')
        self.Widget3_2_3_9 = QCheckBox('D = 1.5 m')
        self.Widget3_2_3_10 = QCheckBox('D =')
        self.Widget3_2_3_11 = QDoubleSpinBox()
        self.Widget3_2_3_11.setMaximum(10)
        self.Widget3_2_3_11.setMinimum(0)
        self.Widget3_2_3_11.setSingleStep(0.05)
        self.Widget3_2_3_11.setMaximumWidth(120)
        self.Widget3_2_3_12 = QLabel("m")

        tab3_2_3_2.addWidget(Widget3_2_3_4)
        tab3_2_3_2.addWidget(self.Widget3_2_3_5)
        tab3_2_3_3.addWidget(Widget3_2_3_6)
        tab3_2_3_4.addWidget(self.Widget3_2_3_7)
        tab3_2_3_4.addWidget(self.Widget3_2_3_8)
        tab3_2_3_4.addWidget(self.Widget3_2_3_9)
        tab3_2_3_4.addWidget(self.Widget3_2_3_10)
        tab3_2_3_4.addWidget(self.Widget3_2_3_11)
        tab3_2_3_4.addWidget(self.Widget3_2_3_12)


        tab3_2_3.addWidget(self.Widget3_2_3_1)  ###
        tab3_2_3.addLayout(tab3_2_3_1)  ###
        tab3_2_3.addLayout(tab3_2_3_2)
        tab3_2_3.addLayout(tab3_2_3_3)
        tab3_2_3.addLayout(tab3_2_3_4)

        self.tab3StempelBox.addSpacing(5)
        self.tab3StempelBox.addWidget(tab3_2_3_Box)

        """""Horizontale geogrids Stempelkraan"""

        tab3_2_4_Box = QGroupBox("Horizontal geogrids")
        tab3_2_4_Box.setFont(QFont("verbana", 14))
        tab3_2_4 = QVBoxLayout()
        tab3_2_4_Box.setLayout(tab3_2_4)

        tab3_2_4_1 = QHBoxLayout()
        tab3_2_4_2 = QHBoxLayout()
        tab3_2_4_3 = QHBoxLayout()
        tab3_2_4_4 = QHBoxLayout()

        self.Widget3_2_4_1 = QCheckBox("Include situation with Horizontal Geogrids")
        self.Widget3_2_4_1.setFont(SubboxFont)
        Widget3_2_4_2 = QLabel("Load spread of Hor. Geogrids above GWL = 1 :")
        self.Widget3_2_4_3 = QLineEdit("1")
        self.Widget3_2_4_3.setMaximumWidth(120)
        Widget3_2_4_4 = QLabel("Load spread of Hor. Geogrids below GWL = 1 : ")
        self.Widget3_2_4_5 = QLineEdit("1")
        self.Widget3_2_4_5.setMaximumWidth(120)
        Widget3_2_4_6 = QLabel("Fill Hor. Geogrids with")
        self.Widget3_2_4_7 = QComboBox()

        self.Widget3_2_4_8 = QCheckBox("D = 0.5 m")
        self.Widget3_2_4_9 = QCheckBox("D = 1.0 m")
        self.Widget3_2_4_10 = QCheckBox("D = 1.5 m")
        self.Widget3_2_4_11 = QCheckBox("D =")
        self.Widget3_2_4_12 = QDoubleSpinBox()
        self.Widget3_2_4_12.setMaximum(10)
        self.Widget3_2_4_12.setMinimum(0)
        self.Widget3_2_4_12.setSingleStep(0.05)
        self.Widget3_2_4_13 = QLabel("m")

        tab3_2_4_1.addWidget(Widget3_2_4_2)
        tab3_2_4_1.addWidget(self.Widget3_2_4_3)
        tab3_2_4_2.addWidget(Widget3_2_4_4)
        tab3_2_4_2.addWidget(self.Widget3_2_4_5)
        tab3_2_4_3.addWidget(Widget3_2_4_6)
        tab3_2_4_3.addWidget(self.Widget3_2_4_7)
        tab3_2_4_4.addWidget(self.Widget3_2_4_8)
        tab3_2_4_4.addWidget(self.Widget3_2_4_9)
        tab3_2_4_4.addWidget(self.Widget3_2_4_10)
        tab3_2_4_4.addWidget(self.Widget3_2_4_11)
        tab3_2_4_4.addWidget(self.Widget3_2_4_12)
        tab3_2_4_4.addWidget(self.Widget3_2_4_13)


        tab3_2_4.addWidget(self.Widget3_2_4_1)
        tab3_2_4.addLayout(tab3_2_4_1)
        tab3_2_4.addLayout(tab3_2_4_2)
        tab3_2_4.addLayout(tab3_2_4_3)
        tab3_2_4.addLayout(tab3_2_4_4)

        self.tab3StempelBox.addSpacing(20)
        self.tab3StempelBox.addWidget(tab3_2_4_Box)

        """""Geocellen stempelkraan"""

        tab3_2_5_Box = QGroupBox("Geocells")
        tab3_2_5_Box.setFont(QFont("verbana", 14))
        tab3_2_5 = QVBoxLayout()
        tab3_2_5_Box.setLayout(tab3_2_5)

        tab3_2_5_1 = QHBoxLayout()
        tab3_2_5_2 = QHBoxLayout()
        tab3_2_5_3 = QHBoxLayout()
        tab3_2_5_4 = QHBoxLayout()

        self.Widget3_2_5_1 = QCheckBox("Include situation with Geocells")
        self.Widget3_2_5_1.setFont(SubboxFont)
        Widget3_2_5_2 = QLabel("Load spread of Geocells above GWL = 1 :")
        self.Widget3_2_5_3 = QLineEdit("2")
        self.Widget3_2_5_3.setMaximumWidth(120)
        Widget3_2_5_4 = QLabel("Load spread of Geocells below GWL = 1 :")
        self.Widget3_2_5_5 = QLineEdit("1")
        self.Widget3_2_5_5.setMaximumWidth(120)
        Widget3_2_5_6 = QLabel("Fill Geocells with")
        self.Widget3_2_5_7 = QComboBox()

        self.Widget3_2_5_8 = QCheckBox("D = 0.5 m")
        self.Widget3_2_5_9 = QCheckBox("D = 1.0 m")
        self.Widget3_2_5_10 = QCheckBox("D = 1.5 m")
        self.Widget3_2_5_11 = QCheckBox("D =")
        self.Widget3_2_5_12 = QDoubleSpinBox()
        self.Widget3_2_5_12.setMaximum(10)
        self.Widget3_2_5_12.setMinimum(0)
        self.Widget3_2_5_12.setSingleStep(0.05)
        self.Widget3_2_5_13 = QLabel("m")

        tab3_2_5_1.addWidget(Widget3_2_5_2)
        tab3_2_5_1.addWidget(self.Widget3_2_5_3)
        tab3_2_5_2.addWidget(Widget3_2_5_4)
        tab3_2_5_2.addWidget(self.Widget3_2_5_5)
        tab3_2_5_3.addWidget(Widget3_2_5_6)
        tab3_2_5_3.addWidget(self.Widget3_2_5_7)
        tab3_2_5_4.addWidget(self.Widget3_2_5_8)
        tab3_2_5_4.addWidget(self.Widget3_2_5_9)
        tab3_2_5_4.addWidget(self.Widget3_2_5_10)
        tab3_2_5_4.addWidget(self.Widget3_2_5_11)
        tab3_2_5_4.addWidget(self.Widget3_2_5_12)
        tab3_2_5_4.addWidget(self.Widget3_2_5_13)

        tab3_2_5.addWidget(self.Widget3_2_5_1)
        tab3_2_5.addLayout(tab3_2_5_1)
        tab3_2_5.addLayout(tab3_2_5_2)
        tab3_2_5.addLayout(tab3_2_5_3)
        tab3_2_5.addLayout(tab3_2_5_4)

        self.tab3StempelBox.addSpacing(20)
        self.tab3StempelBox.addWidget(tab3_2_5_Box)

        tab3.layout.addWidget(scrollStempel, 1, 1)

        """Tab 3.3 Open and Save load situations"""
        tab3_3_1 = QHBoxLayout()
        tab3_3_2 = QHBoxLayout()

        Widget3_3_1_1 = QPushButton("Open loads - Crawler Crane")
        Widget3_3_1_1.clicked.connect(self.OpenLoadFileCC)
        Widget3_3_1_2 = QPushButton("Save loads - Crawler Crane")
        Widget3_3_1_2.clicked.connect(self.SaveLoadFileCC)
        tab3_3_1.addWidget(Widget3_3_1_1)
        tab3_3_1.addWidget(Widget3_3_1_2)

        Widget3_3_1_3 = QPushButton("Open loads - Outrigger crane")
        Widget3_3_1_3.clicked.connect(self.OpenLoadFileOR)
        Widget3_3_1_4 = QPushButton("Save loads - Outrigger crane")
        Widget3_3_1_4.clicked.connect(self.SaveLoadFileOR)
        tab3_3_2.addWidget(Widget3_3_1_3)
        tab3_3_2.addWidget(Widget3_3_1_4)


        tab3.layout.addLayout(tab3_3_1, 0, 0)
        tab3.layout.addLayout(tab3_3_2, 0, 1)


        """Tab 3.4 Safety regulations"""
        """Tab 3.4.1 Model type"""

        tab3_4_1 = QVBoxLayout()
        tab3_4_1Label = QLabel("Select which Plaxis model\n you would like to use")
        tab3_4_1Label.setFont(QFont("verbana", 14))
        Mohr_Coulomb = QRadioButton("Apply Mohr Coulomb")
        Mohr_Coulomb.setFont(QFont("verbana", 12))
        HS_ss = QRadioButton("Apply HS small")
        HS_ss.setFont(QFont("verbana", 12))
        HS_ss.setChecked(True)
        HS_ss.setEnabled(False)
        Mohr_Coulomb.setEnabled(False)
        tab3_4_1Group = QButtonGroup(tab3)
        tab3_4_1Group.addButton(Mohr_Coulomb)
        tab3_4_1Group.addButton(HS_ss)

        tab3_4_1.addWidget(tab3_4_1Label)
        tab3_4_1.addWidget(Mohr_Coulomb)
        tab3_4_1.addWidget(HS_ss)


        """tab 3.4.2 Reliability classes"""

        RC_text = QLabel("Select the Reliability Class")
        RC_text.setFont(QFont("verbana", 14))
        self.RC0 = QRadioButton("RC0")
        self.RC1 = QRadioButton("RC1")
        self.RC1.setChecked(True)
        self.RC2 = QRadioButton("RC2")
        self.RC3 = QRadioButton("RC3")
        tab3_4_2Group = QButtonGroup(tab3)
        tab3_4_2Group.addButton(self.RC0)
        tab3_4_2Group.addButton(self.RC1)
        tab3_4_2Group.addButton(self.RC2)
        tab3_4_2Group.addButton(self.RC3)

        tab3_4_1.addWidget(RC_text)
        tab3_4_1.addWidget(self.RC0)
        tab3_4_1.addWidget(self.RC1)
        tab3_4_1.addWidget(self.RC2)
        tab3_4_1.addWidget(self.RC3)

        """Tab 3.4.3 Other"""


        self.Perc_permanent_load = QSpinBox()
        self.Perc_permanent_load.setRange(0, 100)
        self.Perc_permanent_load.setValue(50)
        Perc_permanent_loadText = QLabel("The percentage of permanent crane load =")

        Value = self.Perc_permanent_load.value()
        self.Perc_Var_LoadText = QLabel("The percentage of variable crane load = 50 %")
        self.Perc_permanent_load.valueChanged.connect(self.Perc_load_changed)





        tab3_4_1.addWidget(Perc_permanent_loadText)
        tab3_4_1.addWidget(self.Perc_permanent_load)
        tab3_4_1.addWidget(self.Perc_Var_LoadText)


        tab3.layout.addLayout(tab3_4_1, 1, 2, alignment=Qt.AlignTop)


        tab3.setLayout(tab3.layout)


        self.tab3 = tab3

    def Tab4(self):
        """Tab 4"""

        tab4_1 = QWidget()
        tab4_1.layout = QVBoxLayout()

        """tab 4.1"""
        OpenProfile_1 = QPushButton('Open file')
        OpenProfile_1.clicked.connect(self.OpenFile)
        SaveProfile_1 = QPushButton('Save file')
        SaveProfile_1.clicked.connect(self.SaveFile)

        """tab 4.2"""
        self.Soil_Profile = QTableWidget()
        self.Soil_Profile.setColumnCount(2)
        self.Soil_Profile.setEditTriggers(QTableWidget.NoEditTriggers)
        self.Soil_Profile.setHorizontalHeaderLabels(["Soil Type", 'Upper border\n[m NAP]'])

        self.SoilChoiceQB_1 = QComboBox()
        self.SoilChoiceQB_1.setMinimumWidth(125)

        Soil_Boundary_1 = QLineEdit()
        Soil_Boundary_1.textChanged.connect(lambda: self.RemoveComma(String_to_Check=self.Soil_Boundary_1))
        Soil_Boundary_1_text = QLabel("Add a layer")
        Soil_Boundary_1.setPlaceholderText("Upper boundary")
        self.Soil_Boundary_1 = Soil_Boundary_1
        Soil_Boundary_1.setFixedWidth(75)
        Soil_Boundary_1_add = QPushButton("Add")
        Soil_Boundary_1_add.clicked.connect(self.Add_SoilLayer)
        Soil_Boundary_1_add.setFixedHeight(27)
        Soil_GWS = QDoubleSpinBox()
        Soil_GWS.setMaximum(10)
        Soil_GWS.setMinimum(-20)
        Soil_GWS.setSingleStep(0.10)
        self.Soil_GWS = Soil_GWS
        Soil_GWS_text = QLabel("Ground water level:")
        Soil_GWS_Set = QPushButton("Set")
        Soil_GWS_Set.clicked.connect(self.change_GWS)
        Soil_GWS_Value_2 = QLabel("Current water level [m] NAP = ")
        self.Soil_GWS_Value = QLabel()
        self.Soil_GWS_Value.setText("1.5")

        Soil_GWS_Set.setFixedHeight(27)

        SoilChoiceLaagnummertxt_1 = QLabel("To remove a soil layer, specify a number =")
        self.RemoveSoilLayer = QSpinBox()
        self.RemoveSoilLayer.setMinimum(1)
        SoilChoiceVerwijder_1 = QPushButton('Remove')
        SoilChoiceVerwijder_1.setMaximumHeight(27)
        SoilChoiceVerwijder_1.clicked.connect(self.Remove_Soil)

        tab4_1_1 = QHBoxLayout()
        tab4_1_1.addWidget(OpenProfile_1)
        tab4_1_1.addWidget(SaveProfile_1)

        tab4_1_2 = QHBoxLayout()
        tab4_1_2.addWidget(self.Soil_Profile)
        tab4_1_2.addWidget(self.chartView)

        tab4_1_3 = QHBoxLayout()
        tab4_1_3.addWidget(Soil_Boundary_1_text)
        tab4_1_3.addWidget(self.SoilChoiceQB_1)
        tab4_1_3.addWidget(Soil_Boundary_1)
        tab4_1_3.addWidget(Soil_Boundary_1_add)
        tab4_1_3.addSpacing(50)
        tab4_1_3.addWidget(Soil_GWS_text)
        tab4_1_3.addWidget(Soil_GWS)
        tab4_1_3.addWidget(Soil_GWS_Set)
        tab4_1_3.addWidget(Soil_GWS_Value_2)
        tab4_1_3.addWidget(self.Soil_GWS_Value)

        tab4_1_4 = QHBoxLayout()
        tab4_1_4.addWidget(SoilChoiceLaagnummertxt_1)
        tab4_1_4.addWidget(self.RemoveSoilLayer)
        tab4_1_4.addWidget(SoilChoiceVerwijder_1)

        tab4_1.layout.addLayout(tab4_1_1)
        text4_1_1Text = QLabel("Use the buttons to change the values")
        text4_1_1Text.setFont(QFont("verbana", 14))
        tab4_1.layout.addWidget(text4_1_1Text)
        tab4_1.layout.addLayout(tab4_1_2)
        text4_1_3 = QLabel("Add and remove layers and set Water level [m], relative to NAP")
        text4_1_3.setFont(QFont("verbana", 14))
        tab4_1.layout.addWidget(text4_1_3, alignment=Qt.AlignHCenter)
        tab4_1.layout.addLayout(tab4_1_3)
        tab4_1.layout.addLayout(tab4_1_4)

        tab4_1.setLayout(tab4_1.layout)

        self.tab4_1 = tab4_1

    def Tab5(self):
        Table = TableWidget()


        LoadSoilProfile = QPushButton("Load soil profile and the additional database")
        LoadSoilProfile.clicked.connect(self.Load_Finished_Data)

        self.ViewProfile = QTableWidget()
        self.ViewProfile.setMaximumHeight(400)

        Tab5_1_2_Variations1 = QLabel("The following parameter has to be variated:")
        self.Tab5_1_2_Variations2 = QComboBox()
        self.Tab5_1_2_Variations2.highlighted[str].connect(self.FillVariations_relations)
        self.Tab5_1_2_Variations2.setFixedWidth(150)
        self.Tab5_1_2_Variations2.setFixedHeight(35)
        Tab5_1_2_Variations3 = QLabel("of soil layer:")
        self.Tab5_1_2_Variations4 = QSpinBox()
        self.Tab5_1_2_Variations4.setMinimum(1)
        Tab5_1_2_Variations5 = QLabel("The lower boundary is:")
        self.Tab5_1_2_Variations6 = QLineEdit()
        self.Tab5_1_2_Variations6.setText("2.5")
        self.Tab5_1_2_Variations6.setPlaceholderText("Lower boundary")
        self.Tab5_1_2_Variations6.setMaximumWidth(75)
        Tab5_1_2_Variations7 = QLabel("The upper boundary is:")
        self.Tab5_1_2_Variations8 = QLineEdit()
        self.Tab5_1_2_Variations8.setText("4")
        self.Tab5_1_2_Variations8.setPlaceholderText("upper boundary")
        self.Tab5_1_2_Variations8.setMaximumWidth(75)
        Tab5_1_2_Variations9 = QLabel("The interval for each variation = ")
        self.Tab5_1_2_Variations10 = QLineEdit()
        self.Tab5_1_2_Variations10.setPlaceholderText("step size")
        self.Tab5_1_2_Variations10.setText("0.5")
        self.Tab5_1_2_Variations10.setMaximumWidth(75)


        Tab5_1_2_Variations11 = QLabel("While making variations within the parameters, its not possible to combine them with the different loads. Therefore, specify an area and load here")
        Tab5_1_2_Variations12 = QLabel("L [m] = ")
        self.Tab5_1_2_Variations13 = QLineEdit()
        self.Tab5_1_2_Variations13.setText("8.2")
        self.Tab5_1_2_Variations13.setMaximumWidth(120)
        Tab5_1_2_Variations14 = QLabel("W [m] = ")
        self.Tab5_1_2_Variations15 = QLineEdit()
        self.Tab5_1_2_Variations15.setText("1.84")
        self.Tab5_1_2_Variations15.setMaximumWidth(120)
        Tab5_1_2_Variations16 = QLabel("Load [kN] = ")
        self.Tab5_1_2_Variations17 = QLineEdit()
        self.Tab5_1_2_Variations17.setText("3800")
        self.Tab5_1_2_Variations17.setMaximumWidth(120)
        Tab5_1_2_Variations18 = QLabel("Z (relative to NAP)[m] = ")
        self.Tab5_1_2_Variations19 = QLineEdit()
        self.Tab5_1_2_Variations19.setText("0.0")
        self.Tab5_1_2_Variations19.setMaximumWidth(80)

        Variations_relations = QTableWidget()
        Variations_relations.setMaximumWidth(150)
        Variations_relations.setMaximumHeight(150)
        Variations_relations.setRowCount(0)
        Variations_relations.setColumnCount(1)
        Variations_relations.setHorizontalHeaderLabels(["The following parameters\nwill be adapted as\nwell, due to correlations"])
        Variations_relations.setColumnWidth(0, 150)
        self.Variations_relations = Variations_relations

        Plx_Variations = QLabel("The amount of PLAXIS files which will be generated right now = ")
        Plx_Variations.setFont(QFont("verdana", 14))
        self.Plx_Variations2 = QLabel("0")
        self.Plx_Variations2.setFont(QFont("verdana", 14))
        Plx_Variations3 = QPushButton("Create variations")
        Plx_Variations3.clicked.connect(self.AddTabs)

        Generate_Plaxis = QPushButton("Generate PLAXIS files")
        Generate_Plaxis.clicked.connect(self.Create_JSON_Files)

        """""tab 5.1.1 """

        tab5_1 = QWidget()
        tab5_1.layout = QVBoxLayout()

        tab5_1_1 = QHBoxLayout()
        tab5_1_1.addWidget(LoadSoilProfile)

        tab5_1.layout.addLayout(tab5_1_1)

        tab5_1.layout.addWidget(self.ViewProfile)

        text5_1_1 = QLabel("You can set the desired variations in this box")
        text5_1_1.setFont(QFont("verbana", 14))
        tab5_1.layout.addWidget(text5_1_1, alignment=Qt.AlignHCenter)

        tab5_1_1Box = QGroupBox("Type of parametric design")
        tab5_1_1Box.setFont(QFont("verbana", 14))
        tab5_1_1Box.setMaximumSize(350, 1500)
        tab5_1_1Box_Layout = QVBoxLayout()
        tab5_1_1Box.setLayout(tab5_1_1Box_Layout)

        self.Parameter_variations = QRadioButton("Vary with different types of parameters")
        self.Parameter_variations.clicked.connect(self.ShowVar)
        self.Load_Variations = QRadioButton("Vary with different types of CHS foundation")
        self.Load_Variations.clicked.connect(self.ShowVar)
        self.Load_VariationsCB1 = QCheckBox('Include crawler crane loads')
        self.Load_VariationsCB1.setEnabled(False)
        self.Load_VariationsCB2 = QCheckBox('Include outrigger crane loads')
        self.Load_VariationsCB2.setChecked(True)
        tab5_1_1Group = QButtonGroup(tab5_1)
        tab5_1_1Group.addButton(self.Parameter_variations)
        tab5_1_1Group.addButton(self.Load_Variations)
        tab5_1_1Box_Layout.addWidget(self.Parameter_variations)
        tab5_1_1Box_Layout.addWidget(self.Load_Variations)
        tab5_1_1Box_Layout.addWidget(self.Load_VariationsCB1)
        tab5_1_1Box_Layout.addWidget(self.Load_VariationsCB2)



        tab5_1.layout.addWidget(tab5_1_1Box, alignment=Qt.AlignHCenter)


        """Tab5.1.2 """
        self.Tab5_1_2_Group = QGroupBox()
        Tab5_1_2_GroupLayout = QVBoxLayout()
        tab5_1_2_1 = QHBoxLayout()

        tab5_1_2_1.addWidget(Tab5_1_2_Variations1, alignment=Qt.AlignTop)
        tab5_1_2_1.addWidget(self.Tab5_1_2_Variations2)
        tab5_1_2_1.addWidget(Tab5_1_2_Variations3)
        tab5_1_2_1.addWidget(self.Tab5_1_2_Variations4)
        tab5_1_2_1.addWidget(Tab5_1_2_Variations5)
        tab5_1_2_1.addWidget(self.Tab5_1_2_Variations6)
        tab5_1_2_1.addWidget(Tab5_1_2_Variations7)
        tab5_1_2_1.addWidget(self.Tab5_1_2_Variations8)
        tab5_1_2_1.addWidget(Tab5_1_2_Variations9)
        tab5_1_2_1.addWidget(self.Tab5_1_2_Variations10)

        tab5_1_2_2 = QHBoxLayout()
        tab5_1_2_2.addWidget(Tab5_1_2_Variations11)
        tab5_1_2_2.addWidget(Tab5_1_2_Variations12)
        tab5_1_2_2.addWidget(self.Tab5_1_2_Variations13)
        tab5_1_2_2.addWidget(Tab5_1_2_Variations14)
        tab5_1_2_2.addWidget(self.Tab5_1_2_Variations15)
        tab5_1_2_2.addWidget(Tab5_1_2_Variations16)
        tab5_1_2_2.addWidget(self.Tab5_1_2_Variations17)
        tab5_1_2_2.addWidget(Tab5_1_2_Variations18)
        tab5_1_2_2.addWidget(self.Tab5_1_2_Variations19)

        Tab5_1_2_GroupLayout.addLayout(tab5_1_2_1)
        Tab5_1_2_GroupLayout.addLayout(tab5_1_2_2)


        self.Tab5_1_2_Group.setLayout(Tab5_1_2_GroupLayout)

        tab5_1.layout.addWidget(self.Tab5_1_2_Group)


        """"Tab 5.1.3"""
        tab5_1_3 = QHBoxLayout()

        tab5_1.layout.addLayout(tab5_1_3)

        """Tab 5.1.4"""
        tab5_1_4 = QHBoxLayout()
        tab5_1_4.addWidget(Variations_relations)
        tab5_1_4.addWidget(Plx_Variations)
        tab5_1_4.addWidget(self.Plx_Variations2)
        tab5_1_4.addWidget(Plx_Variations3)

        tab5_1.layout.addLayout(tab5_1_4)
        tab5_1.layout.addWidget(Generate_Plaxis)

        tab5_1.setLayout(tab5_1.layout)

        tab5_2 = QWidget()
        tab5_2.layout = QHBoxLayout()

        self.Widget5_2_2 = 10
        self.Widget5_2_3 = "Hoek van interne wrijving"
        self.Widget5_2_4 = 4
        Widget5_2_1 = QLabel("In this viewer you can \nsee the variations which are created\n and can be send to Plaxis.")

        self.tab5_3 = QTabWidget()
        tab5_3_1 = QWidget()

        tab5_2.layout.addWidget(Widget5_2_1)
        tab5_2.layout.addWidget(self.tab5_3)


        tab5_2.setLayout(tab5_2.layout)

        tab5 = QTabWidget()
        tab5.addTab(tab5_1, "Settings")
        tab5.setFont(QFont("verbana", 12))

        tab5.addTab(tab5_2, "Viewer of variations")
        tab5.setFont(QFont("verbana", 12))
        self.tab5 = tab5



class TableWidget(QTableWidget):
    def __init__(self):
        super().__init__(1, 20)

        self.setHorizontalHeaderItem(0, QTableWidgetItem("Soil Type\n[-]"))
        self.setHorizontalHeaderItem(1, QTableWidgetItem("ydry\n[kN/m^3]"))
        self.setHorizontalHeaderItem(2, QTableWidgetItem("ysaturated\n[kN/m^3]"))
        self.setHorizontalHeaderItem(3, QTableWidgetItem("Phi/Delta\n[-]"))
        self.setHorizontalHeaderItem(4, QTableWidgetItem("Internal friction angle\n[φ]"))
        self.setHorizontalHeaderItem(5, QTableWidgetItem("Delta\n[]"))
        self.setHorizontalHeaderItem(6, QTableWidgetItem("Cohesion\n[kPa]"))
        self.setHorizontalHeaderItem(7, QTableWidgetItem("E50 / E0ed\n[-]"))
        self.setHorizontalHeaderItem(8, QTableWidgetItem("Eur / E50\n[-]"))
        self.setHorizontalHeaderItem(9, QTableWidgetItem("Conusfactor\n[-]"))
        self.setHorizontalHeaderItem(10, QTableWidgetItem("Eoed\n[kPa]"))
        self.setHorizontalHeaderItem(11, QTableWidgetItem("E'50ref\n[kPa]"))
        self.setHorizontalHeaderItem(12, QTableWidgetItem("EurRef\n[kPa]"))
        self.setHorizontalHeaderItem(13, QTableWidgetItem("Power\n[-]"))
        self.setHorizontalHeaderItem(14, QTableWidgetItem("Interface\n[-]"))
        self.setHorizontalHeaderItem(15, QTableWidgetItem("Initial shear\nstrain modulus\n[kPa]"))
        self.setHorizontalHeaderItem(16, QTableWidgetItem("Shear strain\n[-]"))
        self.setHorizontalHeaderItem(17, QTableWidgetItem("OCR\n[-]"))
        self.setHorizontalHeaderItem(18, QTableWidgetItem("POP\n[-]"))
        self.setHorizontalHeaderItem(19, QTableWidgetItem("DrainageType\n[-]"))

        self.setEditTriggers(QTableWidget.NoEditTriggers)



        self.setMaximumWidth(1200)
        self.setMinimumHeight(600)
        self.setMaximumHeight(800)
        self.setMinimumWidth(500)


        self.verticalHeader().setDefaultSectionSize(50)
        self.horizontalHeader().setDefaultSectionSize(250)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

    def Load_Database(self):
        List_SoilTypes = []
        Variations = Create_Plaxis_Files()
        self.setRowCount(0)

        path = QFileDialog.getOpenFileName(self, 'Load a correct S.310.0104.010 v1.a Bepaling Parameterset PLAXIS 2D (HS-ss) sheet in', filter='xlsx(*xlsx)')
        file = path[0]
        if file != '':

            if file.lower().endswith('.xlsx'):
                Database_File = pd.read_excel(file, sheet_name='Invoer Python')


                self.insertRow(self.rowCount())
                self.setItem(0, 0, QTableWidgetItem(str(Database_File.iat[2, 0])))

                for row in range(int(len(Database_File.index) - 2)):
                    item_toCheckIfNan = Database_File.iat[row+2,0]
                    if pd.isnull(item_toCheckIfNan) == True:
                        'do not continue'
                        break
                    else:
                        if str(item_toCheckIfNan.lower()) in List_SoilTypes:
                            QMessageBox.information(self, "Error",
                                                "You have entered multiple layers with the same name. To prevent mistakes, the program wont accept this")
                            self.setRowCount(0)
                            break
                        else:
                            List_SoilTypes.append(str(item_toCheckIfNan).lower())

                        self.insertRow(self.rowCount())
                        for column in range(20):
                            item = Database_File.iat[row+2,column]
                            try:
                                item = float(item)
                                item = np.round(item, 3)
                            except:
                                pass
                            self.setItem(row, column, QTableWidgetItem(str(item)))
                self.removeRow(self.rowCount() - 1)
                self.resizeColumnsToContents()
                TableWidget.Database_File = Database_File
                TableWidget.DatabaseOK = True
            else:
                QMessageBox.information(self, "Error", " That was no valid file.  Try again...")
                TableWidget.DatabaseOK = False
        else:
            TableWidget.DatabaseOK = False



class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1600, 600)
        self.showMaximized()

        mainLayout = QHBoxLayout()
        mainLayoutSub = QVBoxLayout()
        table = TableWidget()
        Variations = Create_Plaxis_Files()
        table.resizeColumnsToContents()
        readonly = QLabel('This table is read-only')
        readonly.setFont(QFont("verdana", 14))

        mainLayoutSub.addWidget(table, alignment=Qt.AlignTop)
        mainLayoutSub.addWidget(readonly, alignment=Qt.AlignTop)

        mainLayout.addLayout(mainLayoutSub)
        mainLayout.addWidget(Variations)

        # Tab 1
        tab1_1 = QWidget()
        tab1_1.layout = QVBoxLayout()
        tab1_1.setMinimumWidth(1400)

        button_LoadData = QPushButton('Load Database')
        button_LoadData.clicked.connect(table.Load_Database)
        #button_LoadData.clicked.connect(Variations.Fill_Top_layers)
        #button_LoadData.clicked.connect(Variations.Fill_Lower_layers)
        button_LoadData.clicked.connect(Variations.Fill_ComboBox)
        tab1_1.layout.addWidget(button_LoadData)

        info = QLabel('BTG Parametrisch KOP ontwerp - BTG_KOP2\n'
                      'Version : v1, 18-11-2020\n'
                      'Background information regarding this program can be found in the document "Opzet optimalisatie KOP berekeningen". \n Technical explanations for the correct use of this program can be found in "Uitgangspunten KOP"')
                      # 'Background information regarding this program can be found in the document "Opzet optimalisatie KOP berekeningen". \n Technical explanations for the correct use of this program can be found in "Uitgangspunten KOP"')
        info.setFont(QFont("verdana", 14))
        tab1_1.layout.addWidget(info)

        tab1_1.setLayout(tab1_1.layout)

        Variations.addTab(tab1_1, "General")
        Variations.addTab(Variations.tab4_1, "Soil Profile")
        Variations.addTab(Variations.tab5, "Variations")
        Variations.addTab(Variations.tab3, 'Crane loads')
        self.setLayout(mainLayout)


app = QApplication(sys.argv)
app.setStyleSheet('QPushButton{font-size: 20px; width: 200px; height: 50px}')
demo = AppDemo()
demo.show()
sys.exit(app.exec_())

#this is an update #2

#here I'm adding another update to show that this is the active github file

#pycharm commit test