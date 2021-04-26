import math
from plxscripting.easy import *
import pandas as pd
import os
import io
import numpy as np
import easygui
## 00. setup Remote Scripting server for PLAXIS Input

password = 'x6NrX~$s^S+vAL!G'
s_i, g_i = new_server('localhost', 10000, password=password)


while True:
    
    f = easygui.fileopenbox()
    if f.lower().endswith('.xlsx'):
        File = pd.read_excel(f)
        break
    else:
       print("Oops!  That was no valid file.  Try again...")


def Filter_Plaxis_Parameters(g_i):
    rowcounter = 0
    """""Deel Een van het script"""
    for row_value in File["Bepaling parameterset PLAXIS 2D (HS-ss)"]:
        #Grondwaterstand vinden
        if row_value == "Grondwaterstand":
            GWS = File.iloc[rowcounter]
            unique_index = pd.Index(GWS)
            value = unique_index.get_loc('GWS')
            Location_of_GWS = int(value) + 2
            Grondwaterstand = GWS.iloc[Location_of_GWS]

        #Stijghoogte vinden
        elif row_value == "Stijghoogte":
            SH = File.iloc[rowcounter]
            unique_index = pd.Index(SH)
            value = unique_index.get_loc('SH')
            Location_of_SH = int(value) + 2
            Stijghoogte = GWS.iloc[Location_of_SH]

        elif row_value == "uitvoer parameters":
            Plaxis_Table_Start = rowcounter
            end_of_table = rowcounter+10
            break
        else:
            #File.drop(File.index[0], axis=0)
            pass
        rowcounter += 1

    Table = File.iloc[Plaxis_Table_Start:] #de waarde Plaxis_Table_Start is een getal die bepaald wordt om te kijken welke regels uit de excel behouden moeten blijven om data uit te lezen. De rest wordt verwijderd
    Table.drop(Table.columns[23:44], axis=1, inplace=True)
    #Nu creeren we de kolomnamen voor de tabel die data gaat sorteren voor Plaxis
    Table.columns = ["Laagnummer","Laag beschrijving", "Laagdikte","Bovenkant laag t.o.v. NAP","Onderkant laag t.o.v. NAP","Grondsoort","F","Conusfactor","Stijfheidsparameter Eoed","Stijfheidsparameter E50ref","Stijfheidsparameter E_urref","Macht", "G","Interface","Initial shear strain modulus","Shear strain",
        "OCR", "POP", "Drainage type",'Cohesie', 'Hoek van inwendige wrijving','Natte dikte grondlaag','Droge dikte grondlaag','Volumiek gewicht nat','Volumiek gewicht droog', 'Grondwaterstand', 'Stijghoogte']


    #Hieronder is code geschreven om alle witregels uit de excel te verwijderen
    Row_indexes_to_keep = [4, 5]
    Table.drop(["F","G"], inplace = True, axis=1)
    Counter = len(Table.index)
    for number in range(Counter):
        if (number % 2) == 0:
            'do nothing'
        else:
            'do nothing'
            if number >= 6:
                Row_indexes_to_keep.append(number)


    Table_nieuw = Table.take(Row_indexes_to_keep)
    Cells_ToBe_Replaced = Table_nieuw['Laag beschrijving'].isnull().sum()

    #Verwijder het hekje hieronder om een test excel te maken. Hierin staat alle data uit de onderste tabel in excel.
    #Table_nieuw.to_excel('Testfile.xlsx', index=False)

    """""Deel twee van het script"""
    #In onderstaande regels code wordt de tweede sheet uitgelezen, beginnend met 'Invoer bodemopbouw'
    rowcounter = 0
    for row_value in File["Bepaling parameterset PLAXIS 2D (HS-ss)"]:
        if row_value == "invoer bodemopbouw":
            Plaxis_Table2_Start = rowcounter
            break
        rowcounter += 1



    #Hieronder wordt weer een tabel gecreerd met data.
    Table2 = File.iloc[Plaxis_Table2_Start:Plaxis_Table_Start] #de waarden plaxis_Table2_Start en Plaxis_Table_Start zijn getallen die bepaald zijn om te kijken welke regels uit de excel behouden moeten blijven om data uit te lezen. De rest wordt verwijderd.
    Table2.drop(Table2.columns[20:55], axis=1, inplace=True)
    Table2 = Table2.iloc[4:]
    Table2.columns = ["Laagnummer",'Beschrijving van laag',"Laagdikte","Niveau b.k.laag", "Niveau o.k.laag","Laag grondsoort","A", "Droog of nat","Volumiek gewicht","Dikte droog nat", "Hoek van inwendige wrijving","Delta", "B", "Cohesie", "Genormaliseerde gemiddelde conusweerstand", "Waterspanning op basis van", "Gemiddelde effectieve korrelspanning", "OCR", "POP", "Drainage type"]
    #Table2.drop(["A", "B"], inplace=True, axis=1)
    #Table2.to_excel('Testfile3.xlsx', index=False)

    #Code om de cohesie en phi per grondlaag te filteren
    Cohesie = Table2[['Cohesie','Hoek van inwendige wrijving', "OCR", "POP", "Drainage type"]]
    Cohesie.dropna(axis=0, how='any',inplace=True)
    
    #Om de juiste input parameters voor plaxis te krijgen, moeten de waarden in de tabel Drainaige Type aangepast worden. Dat gebeurt hieronder
    Cohesie["Drainage type"].replace({"Undrained (A)": 'undraineda', "Drained": "drained","Undrained (B)": 'undrainedb' }, inplace=True)


    #Code om dikte van de droge en natte grondlagen te bepalen

    Table_DroogNat_Dikte = Table2["Dikte droog nat"]
    Table_Volumiekgewicht = Table2["Volumiek gewicht"]

    Table_Volumiek_Droog = pd.DataFrame(columns=['Volumiek gewicht droog'])
    Table_Volumiek_Nat = pd.DataFrame(columns=['Volumiek gewicht nat'])
    Table_Volumiek_Droog_Values = ['Ydroog']
    Table_Volumiek_Nat_Values = ["Ynat"]
    Table_Droog = pd.DataFrame(columns=['Droge dikte grondlaag'])
    Table_Nat = pd.DataFrame(columns=['Natte dikte grondlaag'])
    Table_Nat_Values = ["m"]
    Table_Droog_Values = ["m"]

    Table_GWS = pd.DataFrame(columns=['Grondwaterstand'])
    Table_SH = pd.DataFrame(columns=['Stijghoogte'])
    Grondwaterstand_list = ['m']
    Grondwaterstand_list.append(Grondwaterstand)
    Stijghoogte_list = ['m']
    Stijghoogte_list.append(Stijghoogte)





    Count_Cells = len(Table_DroogNat_Dikte)-1

    for Counter in range(Count_Cells):
        if Counter == 0:
            pass
        elif (Counter% 2) == 0:
            Table_Nat_Values.append(Table_DroogNat_Dikte.iloc[Counter])
            Table_Volumiek_Nat_Values.append(Table_Volumiekgewicht.iloc[Counter])

        else:
            Table_Droog_Values.append(Table_DroogNat_Dikte.iloc[Counter])
            Table_Volumiek_Droog_Values.append(Table_Volumiekgewicht.iloc[Counter])




    Table_Nat['Natte dikte grondlaag'] = pd.Series(Table_Nat_Values).values
    Table_Droog['Droge dikte grondlaag'] = pd.Series(Table_Droog_Values).values
    Table_Volumiek_Nat['Volumiek gewicht nat'] = pd.Series(Table_Volumiek_Nat_Values).values
    Table_Volumiek_Droog['Volumiek gewicht droog'] = pd.Series(Table_Volumiek_Droog_Values).values
    Table_GWS['Grondwaterstand'] = pd.Series(Grondwaterstand_list).values
    Table_SH['Stijghoogte'] = pd.Series(Stijghoogte_list).values


    #Bovenstaande tabellen bevatten de waarden benodigd om de tabel uit fase 1 verder aan te vullen



    Table_nieuw = Table_nieuw.reset_index(drop=True)
    Cohesie = Cohesie.reset_index(drop=True)
    Table_Nat = Table_Nat.reset_index(drop=True)
    Table_Droog = Table_Droog.reset_index(drop=True)
    Table_Volumiek_Nat = Table_Volumiek_Nat.reset_index(drop=True)
    Table_Volumiek_Droog = Table_Volumiek_Droog.reset_index(drop=True)

    #Hieronder worden ze toegevoegd aan de table_nieuw, de uiteindelijke data tabel voor plaxis, dit is een belangrijke output van executable!

    Table_nieuw[['Cohesie','Hoek van inwendige wrijving', 'OCR', 'POP', 'Drainage type']] = Cohesie[['Cohesie','Hoek van inwendige wrijving','OCR', 'POP', 'Drainage type']]
    Table_nieuw['Natte dikte grondlaag'] = Table_Nat['Natte dikte grondlaag']
    Table_nieuw['Droge dikte grondlaag'] = Table_Droog['Droge dikte grondlaag']
    Table_nieuw['Volumiek gewicht nat'] = Table_Volumiek_Nat['Volumiek gewicht nat']
    Table_nieuw['Volumiek gewicht droog'] = Table_Volumiek_Droog['Volumiek gewicht droog']
    Table_nieuw['Grondwaterstand'] = Table_GWS['Grondwaterstand']
    Table_nieuw['Stijghoogte'] = Table_SH['Stijghoogte']
    Table_nieuw = Table_nieuw[:-int(Cells_ToBe_Replaced)]
    Aantal_Grondlagen = len(Table_nieuw.index)-1
    

   
    #dit is de tabel met data
    #Table_nieuw.to_excel('Testfile.xlsx', index=False)
    create_materials(Amount_of_Soil_Layers=Aantal_Grondlagen, SoilData=Table_nieuw, g_i=g_i)
    

def Create_Boreholes(Amount_of_Soil_Layers,SoilData, g_i, List_Soillayers):
    Materials = List_Soillayers

    xmin = -60
    xmax = 60
    ymax = float(SoilData.iat[1,3])
    ymin = SoilData.iat[Amount_of_Soil_Layers,4]
    g_i.SoilContour.initializerectangular(xmin, ymin, xmax, ymax)
    borehole_main = g_i.borehole(0)
    
    
    #Loop door de data van de grondprofielen, zet de bovenste grenzen van de lagen en maak de lagen aan.
    for number in range(Amount_of_Soil_Layers):
        g_i.soillayer(SoilData.iat[1,23]) #creert een grondlaag
        g_i.setsoillayerlevel(borehole_main, number, float(SoilData.iat[(number+1),3]))   #creert een laaglevel
        
    #Nu plaatsen we de laatste laag-lijn
    g_i.setsoillayerlevel(borehole_main, (Amount_of_Soil_Layers), ymin)
    
    for number in range(Amount_of_Soil_Layers):
        g_i.Soils[number].Material = Materials[number]
    borehole_main.Head = SoilData.iat[1,23]
    
            
    
    
    
    
    
    #g_i.Soils[0].Material = List_Soillayers[0]
    #g_i.Soils[1].Material = List_Soillayers[1]
    #g_i.Soils[2].Material = List_Soillayers[2]
    #g_i.Soils[3].Material = List_Soillayers[3]
    #g_i.Soils[4].Material = List_Soillayers[4]
    #g_i.Soils[5].Material = List_Soillayers[5]
    #g_i.Soils[6].Material = List_Soillayers[6]
    
    #for layerlevel in SoilData['Bovenkant laag t.o.v. NAP']:
    #    if First_Layer == True or layerlevel == ymax:
    #        First_Layer = False
    #    else:
    #        Level = np.round(layerlevel, decimals=2)
    #        g_i.setsoillayerlevel(borehole_left, Laagnummer, Level)
    #        g_i.Soils[Laagnummer].Material = g_i.loam



    # g_i.setsoillayerlevel(borehole_left, 0, 0)
    # g_i.setsoillayerlevel(borehole_left, 1, -28)
    # g_i.setsoillayerlevel(borehole_left, 2, -40)
    #
    #
    # # assign materials, top - down
    # g_i.Soils[0].Material = g_i.Loam
    # g_i.Soils[1].Material = g_i.Sand


def create_materials(Amount_of_Soil_Layers,SoilData, g_i):
    
    ## 02. Create material datasets
    #Testlaag 1
    #print("Laagnummer")
    #print(SoilData.iat[1,0])	
    #print("Laag beschrijving")	
    #print(SoilData.iat[1,1])    #weg
    #print("Laagdikte")	
    #print("Bovenkant laag t.o.v. NAP")		
    #print("Onderkant laag t.o.v. NAP")		
    #print("Grondsoort")		
    #print("Conusfactor")		
    #print("Stijfheidsparameter Eoed")     #weg
    #print(SoilData.iat[1,7])
    #print("Stijfheidsparameter E50ref")   #weg
    #print(SoilData.iat[1,8])    
    #print("Stijfheidsparameter E_urref")  #weg
    #print(SoilData.iat[1,9])
    #print("Macht")                          #weg
    #print(SoilData.iat[1,10])
    #print("Rinter")                         #weg
    #print(SoilData.iat[1,11])
    #print("Initial shear strain modulus G0ref") #weg
    #print(SoilData.iat[1,12])
    #print( "Shear straingamma07")  #weg
    #print(SoilData.iat[1,13])
    #print("OCR")
    #print(SoilData.iat[1,14])    
    #print("POP")
    #print(SoilData.iat[1,15])
    #print("Cohesie")                   #weg
    #print(SoilData.iat[1,16])
    #print("Hoek van inwendige wrijving")     #weg
    #print(SoilData.iat[1,17])    
    #print("Natte dikte grondlaag")		
    #print("Droge dikte grondlaag")		
    #print("Volumiek gewicht nat")    #weg
    #print(SoilData.iat[1,20])   
    #print("Volumiek gewicht droog") #weg
    #print(SoilData.iat[1,21])
    #print("Grondwaterstand")
    #print(SoilData.iat[1,22])
    #print("Stijghoogte")
    #print(SoilData.iat[1,23])
    
    Plx_Materials = []
    for SoilLayer in range(Amount_of_Soil_Layers):
        Plx_Materials.append(SoilLayer)
    
   
    for Soil_Level_nr in range(Amount_of_Soil_Layers):
        #Omdat Soil_Level_nr begint bij 0, maar de eerste datarij met materialen in SoilData met 1, moeten we er 1 optellen
        Index = Soil_Level_nr + 1
        KOnc = 1-np.sin(SoilData.iat[Index,18]*np.pi/180) 
        Soil_params = [("MaterialName", SoilData.iat[Soil_Level_nr+1,1]),
                   ("SoilModel", 4),
                   ("POP", SoilData.iat[Index,15]),
                   ("OCR", SoilData.iat[Index,14]),
                   ("gammaUnsat", SoilData.iat[Index,22]),
                   ("gammaSat", SoilData.iat[Index,21]),
                   ("cref", SoilData.iat[Index,17]),
                   ("E50ref", SoilData.iat[Index,8]),
                   ("Eoedref", SoilData.iat[Index,7]),
                   ("Eurref", SoilData.iat[Index,9]),
                   ("K0NC", KOnc),        
                   ("gamma07",SoilData.iat[Index,13]),
                   ("G0ref", SoilData.iat[Index,12]),
                   ("phi", SoilData.iat[Index,18]),
                   ("Rinter",SoilData.iat[Index,11]),
                   ("powerm", SoilData.iat[Index,10]),
                   ('DrainageType', SoilData.iat[Index,16])]
        #Soilname = g_i.soilmat(*Soil_params)
        
        Plx_Materials[Soil_Level_nr] = g_i.soilmat(*Soil_params)
        incorrectness = Plx_Materials[Soil_Level_nr].validate()
        
        if "Error"in incorrectness:
            easygui.msgbox(str(Soil_params[0]) + " " + incorrectness , "Let op! Onderstaand materiaal wordt wel aangemaakt in Plaxis, maar zodra de berekening wordt gedraaid worden de parameters automatisch aangepast!")
        try:
            Plx_Materials[Soil_Level_nr].DefaultValuesAdvanced = False
        except: 
            pass

        
       
    Create_Boreholes(Amount_of_Soil_Layers=Amount_of_Soil_Layers, SoilData=SoilData, g_i=g_i, List_Soillayers=Plx_Materials)

    
def create_soillayers(g_i):
    ## 03. Define soil layers
    # define soil contour:
    xmin = -60
    xmax = 60
    ymin = -40
    ymax = 0
    g_i.SoilContour.initializerectangular(xmin, ymin, xmax, ymax)

    # create borehole and soil layers
    borehole_left = g_i.borehole(xmin)
    g_i.soillayer(0)
    g_i.soillayer(0)

    g_i.setsoillayerlevel(borehole_left, 0, 0)
    g_i.setsoillayerlevel(borehole_left, 1, -28)
    g_i.setsoillayerlevel(borehole_left, 2, -40)

    borehole_right = g_i.borehole(xmax)
    g_i.setsoillayerlevel(borehole_right, 0, 0)
    g_i.setsoillayerlevel(borehole_right, 1, -18)
    g_i.setsoillayerlevel(borehole_right, 2, -40)

    # assign materials, top - down
    g_i.Soils[0].Material = g_i.Loam
    g_i.Soils[1].Material = g_i.Sand
    
    
    
def main():
    

    ## 01. Start a new project
    s_i.new()
    projecttitle = 'Pile length determination for storm load'
    g_i.Project.setproperties("Title", projecttitle,
                              "UnitForce", "kN",
                              "UnitLength", "m",
                              "UnitTime", "day",
                              "ModelType", "Plane strain",
                              "ElementType", "15-Noded")
    Filter_Plaxis_Parameters(g_i)
    

main()