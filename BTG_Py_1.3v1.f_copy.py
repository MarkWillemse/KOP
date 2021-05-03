import math
from plxscripting.easy import *
import pandas as pd
import os
import io
import numpy as np
import easygui
import math
import csv
from matplotlib import pyplot as plt
import numpy as np
import random
from matplotlib.ticker import FormatStrFormatter


#DIT SCRIPT WORDT GEOPEND IN PLAXIS

## 00. setup Remote Scripting server for PLAXIS Input

password = 'x6NrX~$s^S+vAL!G'

s_i, g_i = new_server('localhost', 10000, password=password)


#onderstaande functie opent de JSON files gebouwd in script 2
def Open_json(s_i, g_i):
    #01 Read created JSON files and convert them to a dataframe
    print('#01')
    location = easygui.diropenbox("Select which JSON files you want to calculate in Plaxis V20")
    file = open(location + str("\\") + "results.txt", "w")
    file.write("Results of the calculations of JSON files at" + str(location))
    file.close()

    create_csv(location=location)

    for Plx_file in os.listdir(location):
        ## 02. Start a new project for every json file in the directory
        
        s_i.new()
        
        if Plx_file.endswith(".json"):
            print('#02')
            projecttitle = Plx_file[:-5]
            Plx_file = str(location + str("\\") + Plx_file)
            Plx_file_df = pd.read_json(Plx_file)   #convert JSON to pandas dataframe!
            
            print(projecttitle)
           
            
            g_i.Project.setproperties("Title", projecttitle,
                                      "UnitForce", "kN",
                                      "UnitLength", "m",
                                      "UnitTime", "day",
                                      "ModelType", "Plane strain",
                                      "ElementType", "15-Noded")
            try:
                create_materials(g_i, Plx_file_df, projecttitle, location=location)   # aangeroepen functie staat er onder
            except:
                pass
    
    Plot_results(location=location)
    exit()

def create_materials(g_i, JSON_file, name, location):
    ## 03. Create material datasets for the phases
    print('#03')

    #haal parameters uit de JSON file
    #variations_mode=welke type variatie: grondverbetering of niet
    g_i, Plx_Materials, no_SoilLayers, Variations_mode = assign_variables(g_i=g_i,Data=JSON_file)  #aangeroepen functie staat hier onder

    #create boreholes from JSON file
    Create_Boreholes(Amount_of_Soil_Layers=no_SoilLayers, JSON_file=JSON_file, g_i=g_i, List_Soillayers=Plx_Materials, name=name, location=location, Model_mode=Variations_mode)
     
def assign_variables(g_i, Data):
    #04 Function to extract parameters from the JSON file and save them as a Plaxis Soil File
    print('#04')

    #Data is the JSON file!
    no_SoilLayers = len(Data) #every row is one soil layer I guess
    Plx_Materials = []
    
    for SoilLayer in range(no_SoilLayers):


        #PLAN VAN AANPAK: maak 2 soil profiles hier?? of zelfs 3??
        # Als houten schotten dan een extra laag bovenop, of zelfs 2.

        #dus op einde: append houten schot (of misschien wel als eerste, afhankelijk van volgorde laden)
        
        Plx_Materials.append(SoilLayer)
        #Omdat Soil_Level_nr begint bij 0, maar de eerste datarij met materialen in SoilData met 1, moeten we er 1 optellen

        #lees alle parameters per soillayer uit JSON file
        Material_name = Data.loc[SoilLayer, "Soil type\n[-]"]

        #voor hout, material_name='houten schotten'

        Cohesion = Data.loc[SoilLayer, "Cohesion\n[kPa]"]
       
        Conusfactor = Data.loc[SoilLayer, "Conusfactor\n[-]"]
        Delta = Data.loc[SoilLayer, "Delta\n[]"]
        E50ref = Data.loc[SoilLayer,"E'50ref\n[kPa]"]
        Eoed = Data.loc[SoilLayer,"Eoed\n[kPa]"]
        EurRef = Data.loc[SoilLayer,"EurRef\n[kPa]"]
        GWL = Data.loc[SoilLayer,"GWL\n[m]"]
        Initial_ssm = Data.loc[SoilLayer,"Initial shear\nstrain modulus\n[kPa]"]
        Friction_angle = Data.loc[SoilLayer,"Internal friction\nangle"]
        
        Lower_Soil_Boundary = Data.loc[SoilLayer,"Lower soil boundary\n[m]"]
        #Normalised_conus_resistance = Data.loc[SoilLayer,"Normalised\nconus resistance\n[Mpa]"]
        OCR = Data.loc[SoilLayer,"OCR\n[-]"]
        POP = Data.loc[SoilLayer,"POP\n[-]"]
        Power = Data.loc[SoilLayer,"Power\n[-]"]
        Rinter = Data.loc[SoilLayer,"RInter\n[-]"]
        Shear_strain = Data.loc[SoilLayer,"Shear strain\n[-]"]
        #Undrained_shear_strenght = Data.loc[SoilLayer,"Undrained\nshear strenght\n[kPa]"]
        ydry = Data.loc[SoilLayer,"ydry\n[kN/m^3]"]
        ysaturated = Data.loc[SoilLayer,"ysaturated\n[kN/m^3]"]
        Drainage_Type = Data.loc[SoilLayer,"DrainageType\n[-]"]
        Thickness = Data.loc[SoilLayer,"Thickness\n[m]"]
        Lower_Soil_Boundary = Data.loc[SoilLayer,"Lower soil boundary\n[m]"]
        Upper_soil_boundary = Data.loc[SoilLayer,"Upper soil boundary\n[m]"]
        Z = Data.loc[SoilLayer,"Z, relative to\nNAP\n[m]"]
        Thickness_Soil_Enhancement = Data.loc[SoilLayer, "Thickness Soil\nEnhancement [m]"]
        Enhancement_Type = Data.loc[SoilLayer, "Soil type\nenhancement"]


        Area_W = Data.loc[SoilLayer, "Area Width\n[m]"]             #komt dit uit de excel file?
        Area_L = Data.loc[SoilLayer, "Area Length\n[m]"]
        q_rep = Data.loc[SoilLayer, "q_rep\n[kN/m]"]  #waarom is q_rep kN/m en niet kN/m2??
        q_d = Data.loc[SoilLayer, "q_d\n[kN/m]"]


        if q_d == 'not used in this model':
            Variations_mode = True
        else:
            Variations_mode = False #this means that we are doing variations with Loads instead of Parameters

        G0ref = 4*EurRef/(2*(1+0.2)) #calculate ground model parameters
        KOnc = 1-np.sin(Friction_angle*np.pi/180)
        
        #Gamma07 = (1/(9*G0ref))*(2*Cohesion*(1+np.cos(2*Friction_angle*np.pi/180))+100*(1+KOnc)*np.sin(2*Friction_angle*np.pi/180))
        Soil_params = [("MaterialName", Material_name),
                   ("SoilModel", 4),
                   ("POP",POP),
                   ("OCR", OCR),
                   ("gammaUnsat", ydry),
                   ("gammaSat", ysaturated),
                   ("cref", Cohesion),
                   ("E50ref", E50ref),
                   ("Eoedref",Eoed ),
                   ("Eurref", EurRef),
                   ("K0NC", KOnc),
                   ("gamma07", Shear_strain),
                   ("G0ref", G0ref),
                   ("phi", Friction_angle),
                   ("Rinter",Rinter),
                   ('DrainageType', Drainage_Type),
                   ("powerm", Power)]
        #Soilname = g_i.soilmat(*Soil_params)



        Plx_Materials[SoilLayer] = g_i.soilmat(*Soil_params)
        try:
            Plx_Materials[SoilLayer].DefaultValuesAdvanced = True
        except:
            pass
        print('#04 Finished')
    return g_i, Plx_Materials, no_SoilLayers, Variations_mode

   

def Create_Boreholes(Amount_of_Soil_Layers, JSON_file, g_i, List_Soillayers, name, location, Model_mode):
    ## 05. Create boreholes and assign materials to them
    print('#05')
    Materials = List_Soillayers

    xmin = -30
    xmax = 30

    ymax = JSON_file.loc[0,"Upper soil boundary\n[m]"]
    ymin = JSON_file.loc[Amount_of_Soil_Layers-1, "Lower soil boundary\n[m]"]
    
    g_i.SoilContour.initializerectangular(xmin, ymin, xmax, ymax)
    g_i.borehole_main = g_i.borehole(0)
    
    Extra_layer = True
    if Model_mode == False:  # input of model_mode is variation_mode, which means: if false we do variations with loads instead of parameters

        SoilEnh_Thickness = float(JSON_file.loc[0, "Thickness Soil\nEnhancement [m]"])
        New_border = ymax - SoilEnh_Thickness
        
    
        for number in range(Amount_of_Soil_Layers):     #Function to determine if we have an fictive extra layer. This is needed when for example the first layer is 2.0m, but the enhancement is 1.5m. Than we need a 1.5m layer and 0.5m layer.
            Level = JSON_file.loc[number,"Upper soil boundary\n[m]"]

            if Level == New_border:
                Extra_layer = False
    Borders = []

    
    if Extra_layer == True and Model_mode == False:  #Deze functie als er grondverbetering is met een extra laag
        print('Extra Layer')
        if SoilEnh_Thickness > 0:
            boolean_stop = False
            
            
            for number in range(Amount_of_Soil_Layers):
                Level = JSON_file.loc[number,"Upper soil boundary\n[m]"]
        
                if New_border > Level and boolean_stop == False:
                    g_i.Soil_to_split = number 
                    boolean_stop = True
                    print(g_i.Soil_to_split)
                    print('Soil to split')
                    
                Borders.append(Level)

            Borders.append(New_border)
            Borders.sort()
            Borders.reverse()
            g_i.Borders = Borders

            for number in range(len(Borders)):
                g_i.soillayer(0)  # creert een grondlaag
                g_i.setsoillayerlevel(g_i.borehole_main, number, Borders[number])  # creert een laaglevel
            g_i.soillayer(0)
            g_i.setsoillayerlevel(g_i.borehole_main, (Amount_of_Soil_Layers + 1), ymin) #Zet de laatste laaglijn erin
            
            bool_split = False
            
            
            for number in range(len(Borders)): # Deze functie geeft 1 materiaal aan 2 grondlagen, als er een extra splitsing in zit
                if number == g_i.Soil_to_split:
                    bool_split = True
                
                if bool_split == False:
                    try:
                        g_i.Soils[number].Material = Materials[number]
                    except:
                        easygui.msgbox('Plaxis cannot accept the parameters you gave in, and changed some of them. This happend in the following material (others may follow):\n\n' +  str(Materials[number].MaterialName) + '\n\nin the following file :\n' + name + '\nPlease check this file afterwards', 'Error in creating a material')
                        pass
                
                    
                elif bool_split == True:
                    g_i.Soils[number].Material = Materials[number-1] # aanpassing JHo
                    #g_i.Soils[number].Material = Materials[number+1]
                    bool_split == False
                    
        
           
    else:      #Deze functie wanneer geen grondverbetering of grondverbetering zonder extra laag is
        
        # Loop door de data van de grondprofielen, zet de bovenste grenzen van de lagen en maak de lagen aan.
        for number in range(Amount_of_Soil_Layers):
            g_i.soillayer(0)  # creert een grondlaag
            g_i.setsoillayerlevel(g_i.borehole_main, number, JSON_file.loc[number,"Upper soil boundary\n[m]"])  # creert een laaglevel
            Borders.append(float(JSON_file.loc[number,"Upper soil boundary\n[m]"]))

    
    # Nu plaatsen we de laatste laag-lijn
        g_i.setsoillayerlevel(g_i.borehole_main, (Amount_of_Soil_Layers), ymin)

        for number in range(Amount_of_Soil_Layers):
            g_i.Soils[number].Material = Materials[number]
            
            
        
        Borders.sort()
        Borders.reverse()
        g_i.Borders = Borders
    
    print('set head')
    try:
        g_i.borehole_main.Head = float(JSON_file.loc[0,"GWL\n[m]"])
    except:
        pass
        
    create_crane_load(g_i=g_i, JSON_file=JSON_file, name=name, location=location, Model_mode=Model_mode)
        

    #haal crane load uit JSON file

    #note: extra input (bij script verandering) vereist ook extra functie hier waarschijnlijk!
def create_crane_load(g_i, JSON_file, name, location, Model_mode):
    ## 06. Create crane loads for the different phases
    print('#06')
    # Crane Load:
    # we will set the load values in staged construction
    Area_W = float(JSON_file.loc[0, "Area Width\n[m]"])
    Area_L = float(JSON_file.loc[0, "Area Length\n[m]"])
    
    if Area_W > Area_L:
        Area_L_Copy = Area_L
        Area_L = Area_W
        Area_W = Area_L_Copy

    #deze worden op een andere plek wel gebruikt
    q_rep = float(JSON_file.loc[0, "q_rep\n[kN/m]"])
    # Load = q_rep
    #
    # q_load_crane = Load/Area_W

    y_coordinate_load = JSON_file.loc[0,"Z, relative to\nNAP\n[m]"]


    g_i.lineload(-(Area_W/2), y_coordinate_load,
                 (Area_W/2), y_coordinate_load)

    try:
        g_i.LineLoads[-1].Name = "Craneload q_rep"
    except:
        pass
    #bouw mesh nadat loads zijn toegevoegd
    generate_mesh(g_i, JSON_file=JSON_file, Model_mode=Model_mode, name=name, location=location)

#voorgestelde functie:
def create_plates(g_i, JSON_file, name, location, Model_mode):

#HIER NOG KIJKEN WAT PLAATS VINDT IN KOP2 EN WAT IN KOP3

    #dimension plate comes from JSON_file
    Area_W_plate = float(JSON_file.loc[0, "Area Width\n[m]"])       #Geef locatie in JSON file
    Area_L_plate = float(JSON_file.loc[0, "Area Length\n[m]"])      #Geef locatie in JSON file
    if Area_W_plate > Area_L_plate:
        Area_L_Copy = Area_L_plate
        Area_L_plate = Area_W_plate
        Area_W_plate = Area_L_Copy

    q_rep = float(JSON_file.loc[0, "q_rep\n[kN/m]"])                #Geef locatie in JSON file:representatieve load
    Load = q_rep

    q_load_plate = Load / Area_W_plate

    y_coordinate_load = JSON_file.loc[0, "Z, relative to\nNAP\n[m]"] #Geef locatie in JSON file

    #define line coordinates
    line_plate=g_i.line((0,0),(0,1))[-1]   #[-1] defines Line Object

    #required parameters
    EA = 4700000           # [kN/m]
    EI = 20450             # [kN m2/m]
    nu = 0.3

    # derived parameters
    d = math.sqrt(12 * EI / EA)     # [m]
    E = EA / d
    G = E / (2 * (1 + nu))

    #collect plate material
    plate_params = (('MaterialName', 'example_platemat'), ('IsIsotropic', True),
                    ('Gref', G), ('d', d), ('nu', nu),
                    ('EA', EA), ('EA2', EA), ('EI', EI))  #set up list with parameters for function
    plate_mat = g_i.platemat(*plate_params)

    #set plate
    g_i.setmaterial(line_plate.Plate, plate_mat)


# create_plates wordt aangeroepen met:
# create_plates(g_i=g_i, JSON_file=JSON_file, name=name, location=location, Model_mode=Model_mode)

#dit is de functie die de mesh instellingen geeft
def generate_mesh(g_i, JSON_file, Model_mode, name, location):
    ## 07. generate the mesh
    print('#07')
  
    g_i.gotomesh()
   
    #g_i.refine(g_i.Raft)
    # generate a fine mesh:
    g_i.mesh(0.04002)
 
    setup_phases(g_i, JSON_file=JSON_file, Model_mode=Model_mode, name=name, location=location)
    
    # optional
    # g_i.viewmesh()

#voeg bodem verbetering toe als nodig
def Create_enhancement(g_i, JSON_file, location):
    
    #This function creates a new Soil Layer which is the soil enhancement
    
    Enhancement_Type = JSON_file.loc[0, "Soil type\nenhancement"]
    Data = pd.read_csv(location + str("\\") + "SoilTypes_PLAXIS.csv")
   
    
    if Enhancement_Type in g_i.dumpmaterials():
        print('Inside')
    else:
        print('Not inside')
    
    
    for SoilType in range(len(Data)):
        if str((Data.iat[SoilType, 0])) == Enhancement_Type:
            ydry = Data.iat[SoilType,1]
            ysaturated = Data.iat[SoilType,2]
            Friction_angle = Data.iat[SoilType,4]
            Delta = Data.iat[SoilType, 5]
            Cohesion = Data.iat[SoilType,6]
            #Normalised_conus_resistance = Data.iat[SoilType,7]
            Conusfactor = Data.iat[SoilType,9]
            Eoed = Data.iat[SoilType,10]
            E50ref = Data.iat[SoilType,11]
            EurRef = Data.iat[SoilType,12]
            Power = Data.iat[SoilType,13]
            Rinter = Data.iat[SoilType,14]
            Initial_ssm = Data.iat[SoilType,15]
            Shear_strain = Data.iat[SoilType,16]
            OCR = Data.iat[SoilType,17]
            POP = Data.iat[SoilType,18]
            Drainage_type = Data.iat[SoilType,19]
            #Undrained_shear_strenght = Data.iat[SoilType,7]


            
            G0ref = 4*EurRef/(2*(1+0.2))
            KOnc = 1-np.sin(Friction_angle*np.pi/180)
            #Gamma07 = (1/(9*G0ref))*(2*Cohesion*(1+np.cos(2*Friction_angle*np.pi/180))+100*(1+KOnc)*np.sin(2*Friction_angle*np.pi/180))
            Soil_params = [("MaterialName", Enhancement_Type),
                       ("SoilModel", 4),
                       ("POP",POP),
                       ("OCR", OCR),
                       ("gammaUnsat", ydry),
                       ("gammaSat", ysaturated),
                       ("cref", Cohesion),
                       ("E50ref", E50ref),
                       ("Eoedref",Eoed ),
                       ("Eurref", EurRef),
                       ("K0NC", KOnc),
                       ("gamma07", Shear_strain),
                       ("G0ref", G0ref),
                       ("phi", Friction_angle),
                       ("Rinter",Rinter),
                       ('DrainageType', Drainage_type),
                       ("powerm", Power)]

            NewSoil =  g_i.soilmat(*Soil_params)
            
            return NewSoil
    
    
def Initiate_NextPhases(g_i, JSON_file, location, Model_mode, phase):
    
    if Model_mode == False:    #dit is de parameter die wel of niet bodemverbetering aangeeft!
        SoilEnh_Thickness = float(JSON_file.loc[0, "Thickness Soil\nEnhancement [m]"])
   
    
        if SoilEnh_Thickness > 0:

            ymax = float(JSON_file.loc[0,"Upper soil boundary\n[m]"])
            New_border = float(ymax - SoilEnh_Thickness)
            
            for nr_Borders in range(int(len(g_i.Borders))):
           
                
                if float(g_i.Borders[nr_Borders]) <= New_border:
                   
                    Difference = int(len(g_i.Borders)) - int(len(JSON_file))
                   
                    if g_i.Borders[nr_Borders] == New_border:
                        if Difference == 0:

                            #hier wordt de bodemverbetering functie aangeroepen
                            NewSoil = Create_enhancement(g_i=g_i, JSON_file=JSON_file, location=location)
                            counter = 0
                            for soillayer in g_i.Borders:
                                if soillayer == New_border:
                                    break
                                else:
                                    counter +=1
                            for _ in range(counter):
                                g_i.Soils[_].Material[phase] = NewSoil
                            try:
                                Plx_Materials[0].DefaultValuesAdvanced = True
                            except:
                                pass
                               
                        if Difference > 0:
                            
                            NewSoil = Create_enhancement(g_i=g_i, JSON_file=JSON_file, location=location)

                            print(g_i.Soil_to_split)
                            for Soil in range(int(g_i.Soil_to_split)):
                                g_i.Soils[int(Soil)].Material[phase] = NewSoil
                                try:
                                    Plx_Materials[Soil].DefaultValuesAdvanced = True
                                except:
                                    pass
                        
                    #break 


def setup_phases(g_i, JSON_file, Model_mode, name, location):
    g_i.gotostages()
    ## 08. initial phase: K0 value
    print('#08A')
    #g_i.deactivate(g_i.Plates, g_i.InitialPhase)
   
   
    g_i.deactivate(g_i.LineLoads, g_i.InitialPhase)  #set situation for initial phase, without lineLoads
    q_rep = float(JSON_file.loc[0, "q_rep\n[kN/m]"])

    ## 08.1 foundation phase
    print('#08B')

    g_i.FoundationPhase = g_i.phase(g_i.InitialPhase)
    g_i.setcurrentphase(g_i.FoundationPhase)
    g_i.FoundationPhase.Identification = "Foundation"
    g_i.FoundationPhase.Deform.IgnoreUndrainedBehaviour = True
    #hieronder wordt eventuele bodemverbetering toegevoegd:
    Initiate_NextPhases(g_i=g_i, JSON_file=JSON_file, location=location, Model_mode=Model_mode, phase=g_i.FoundationPhase)


    ## 09 phase_1: Crane load qrep
    print('#09')
 
    g_i.CraneLoadPhase1 = g_i.phase(g_i.FoundationPhase)
    g_i.setcurrentphase(g_i.CraneLoadPhase1)
    g_i.CraneLoadPhase1.Identification = "Crane load q_rep"
    g_i.CraneLoadPhase1.Deform.ResetDisplacementsToZero = True
    # g_i.CraneLoadPhase1.Deform.UseDefaultIterationParams = False                                        #Tijdelijk ingesteld voor CASE
    # g_i.CraneLoadPhase1.Deform.MaxSteps = 75                                                       #Tijdelijk ingesteld voor CASE
   
    for lineload in g_i.Lineloads[:]:
        lineload.activate(g_i.CraneLoadPhase1)
        lineload.q_start[g_i.CraneLoadPhase1] = q_rep
        
    #Initiate_NextPhases(g_i=g_i, JSON_file=JSON_file, location=location, Model_mode=Model_mode, phase=g_i.CranePhase1)   #This function is being called to make the change from the initial phase to other phases
    
    g_i.SafetyPhase1 = g_i.phase(g_i.CraneLoadPhase1)
    g_i.setcurrentphase(g_i.SafetyPhase1)
    g_i.SafetyPhase1.DeformCalcType = "Safety"
    # g_i.SafetyPhase1.Deform.UseDefaultIterationParams = False
    # g_i.SafetyPhase1.Deform.MaxSteps = 75                                                               #Tijdelijk ingesteld voor CASE
    g_i.SafetyPhase1.Identification = "Safety calculation Crane load q_rep"
   
    if Model_mode == False: #this means that we are doing variations with Loads instead of Parameters !!!
        q_d = float(JSON_file.loc[0, "q_d\n[kN/m]"])
        ## 10. phase_2: Crane load qdesign
        print('#10')
        g_i.CraneLoadPhase2 = g_i.phase(g_i.FoundationPhase)
        g_i.setcurrentphase(g_i.CraneLoadPhase2)
        g_i.CraneLoadPhase2.Identification = "Crane load q_design"
        g_i.CraneLoadPhase2.Deform.ResetDisplacementsToZero = True
        # g_i.CraneLoadPhase2.Deform.UseDefaultIterationParams = False                                        #Tijdelijk ingesteld voor CASE
        # g_i.CraneLoadPhase2.Deform.MaxSteps = 75                                                       #Tijdelijk ingesteld voor CASE
        for lineload in g_i.Lineloads[:]:
            lineload.activate(g_i.CraneLoadPhase2)
            lineload.q_start[g_i.CraneLoadPhase2] = q_d
        #Initiate_NextPhases(g_i=g_i, JSON_file=JSON_file, location=location, Model_mode=Model_mode, phase=g_i.CranePhase2)
            
        g_i.SafetyPhase2 = g_i.phase(g_i.CraneLoadPhase2)
        g_i.setcurrentphase(g_i.SafetyPhase2)
        g_i.SafetyPhase2.DeformCalcType = "Safety"
        # g_i.SafetyPhase2.Deform.UseDefaultIterationParams = False
        # g_i.SafetyPhase2.Deform.MaxSteps = 75                                                           #Tijdelijk ingesteld voor CASE
        g_i.SafetyPhase2.Identification = "Safety calculation Crane load q_design"
            
    calculate(g_i, name=name, location=location, Model_mode=Model_mode, JSON_file=JSON_file)

def calculate(g_i, name, location, Model_mode, JSON_file):
    ## 11. calculate the model
    filename = (name + '.p2dx')
    filename_todelete = str(location + str("\\") + filename)
    if os.path.exists(filename_todelete):
        os.remove(filename_todelete)
    g_i.save(filename_todelete)
    print('#11')
    g_i.calculate()

    retrieve_results(g_i, name=name, location=location, Model_mode=Model_mode, JSON_file=JSON_file)#, width, floors * floor_height, pile_length)

def outputphase(g_o, inputphase):
    outputphase = get_equivalent(inputphase, g_o)
    return outputphase

def get_result(phase, JSON_file):#, width, height):
    Area_W = float(JSON_file.loc[0, "Area Width\n[m]"])
    outputport = g_i.view(phase)
    s_o, g_o = new_server('localhost', outputport, password=password)
    phase_o = outputphase(g_o, phase)

    y_displ = (JSON_file.loc[0, "Upper soil boundary\n[m]"] ) 

    uy_l = float(g_o.getsingleresult(phase_o,g_o.ResultTypes.Soil.Uy,-Area_W/2,y_displ))
    uy_c = float(g_o.getsingleresult(phase_o,g_o.ResultTypes.Soil.Uy,0,y_displ))
    uy_r = float(g_o.getsingleresult(phase_o,g_o.ResultTypes.Soil.Uy,Area_W/2,y_displ))

    settlement = min(uy_l, uy_c, uy_r)
    print("Phase: {}".format(phase_o.Identification.value))
    print("\tSettlement: {} m [{} mm]".format(settlement,round(settlement*1000, 1)))
    s_o.close()

    return settlement, uy_c, uy_r, uy_l

def retrieve_results(g_i, name, location, Model_mode, JSON_file):#, width, height, pile_length):
    ## 12. First save the model
    print('#12')

    filename = (name + '.p2dx')
    filename_todelete = str(location + str("\\") + filename)
    if os.path.exists(filename_todelete):
        os.remove(filename_todelete)
    g_i.save(filename_todelete)
    

    
    ## 13. Collect results
    print('#13')
    ## 13.01 retrieve results
    
    u1_ph1, uy_c_ph1, uy_r_ph1, uy_l_ph1 = get_result(g_i.CraneLoadPhase1, JSON_file=JSON_file)

    
    u1_ph1 = u1_ph1*1000 #to convert to mm
    uy_c_ph1 = uy_c_ph1*1000
    uy_r_ph1 = uy_r_ph1*1000
    uy_l_ph1 = uy_l_ph1*1000
 
    

    
    if Model_mode == False and g_i.Phase_1.CalculationResult == 1:
        u1_ph2, uy_c_ph2, uy_r_ph2, uy_l_ph2 = get_result(g_i.CraneLoadPhase2, JSON_file=JSON_file)
        u1_ph2 = u1_ph2*1000 #to convert to mm
        uy_c_ph2 = uy_c_ph2*1000
        uy_r_ph2 = uy_r_ph2*1000
        uy_l_ph2 = uy_l_ph2*1000
        
    if g_i.CraneLoadPhase1.CalculationResult == 0:
        Ph1_melding = 'Not finished'
    elif g_i.CraneLoadPhase1.CalculationResult == 1:
        Ph1_melding = 'Calculation OK'
    elif g_i.CraneLoadPhase1.CalculationResult == 2:
        Ph1_melding = 'Calculation failed! Low settlements may be caused by soil failure'
    
    if g_i.SafetyPhase1.CalculationResult == 0:
        S1_melding = 'Not finished'
    elif g_i.SafetyPhase1.CalculationResult == 1:
        S1_melding = 'Calculation OK'
    elif g_i.SafetyPhase1.CalculationResult == 2:
        S1_melding = 'Calculation failed'   

    ## 13.02 write results 

    file_object = open(location + str("\\") + "results.txt", "a")
    file_object.write("\n\n!!!NEW SET OF RESULTS!!!\n\nSummary for crane hard stand nr:" + name)

    file_object.write("\n Phase 1, status = " + Ph1_melding)
    file_object.write("\n Settlements calculated at ground level")
    file_object.write("\nSettlement: Phase_1 for construction: u_y = {:.1f} mm".format(u1_ph1))
    file_object.write("\nSettlement: Phase_1 for construction: u_ycenter = {:.1f} mm".format(uy_c_ph1))
    file_object.write("\nSettlement: Phase_1 for construction: u_yleft = {:.1f} mm".format(uy_l_ph1))
    file_object.write("\nSettlement: Phase_1 for construction: u_yright = {:.1f} mm".format(uy_r_ph1))
    file_object.write("\n\n Phase 1 Safety Calculation (250 steps), status = " + S1_melding)
    Phase_1 = [u1_ph1 ,uy_c_ph1, uy_l_ph1, uy_r_ph1]
  
    if Model_mode == False and g_i.Phase_1.CalculationResult == 1:
        if g_i.CraneLoadPhase2 == 0:
            Ph2_melding = 'Not finished'
        elif g_i.CraneLoadPhase2.CalculationResult == 1:
            Ph2_melding = 'Calculation OK'
        elif g_i.CraneLoadPhase2.CalculationResult == 2:
            Ph2_melding = 'Calculation failed! Low settlements may be caused by soil failure '
        
        if g_i.SafetyPhase2.CalculationResult == 0:
            S2_melding = 'Not finished'
        elif g_i.SafetyPhase2.CalculationResult == 1:
            S2_melding = 'Calculation OK'
        elif g_i.SafetyPhase2.CalculationResult == 2:
            S2_melding = 'Calculation failed' 
    
        file_object.write("\n Phase 2 , status = " + Ph2_melding)
        file_object.write("\n Settlements calculated at 20cm below ground level")
        file_object.write("\nSettlement: Phase_2 for construction: u_y = {:.1f} mm".format(u1_ph2))
        file_object.write("\nSettlement: Phase_2 for construction: u_ycenter = {:.1f} mm".format(uy_c_ph2))
        file_object.write("\nSettlement: Phase_2 for construction: u_yleft = {:.1f} mm".format(uy_l_ph2))
        file_object.write("\nSettlement: Phase_2 for construction: u_yright = {:.1f} mm".format(uy_r_ph2))
        file_object.write("\n\n Phase 2 Safety Calculation (250 steps), status = " + S2_melding)
        Phase_2 = [u1_ph2,uy_c_ph2, uy_l_ph2, uy_r_ph2]
        
    else: 
        Phase_2 = [0, 0, 0,0]


    Create_PlotData(Phase_1=Phase_1, Phase_2=Phase_2 ,name=name, location=location)

def create_csv(location):

    with open(location + str("\\")+ 'Plot_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['names', 'Uy center phase1 [mm]', 'Uy side phase1 [mm]', 'Uy center phase2 [mm]', 'Uy side phase2 [mm]' ])
        file.close()

    

def Create_PlotData(Phase_1, Phase_2, name, location):
    
    u_ycenter_ph1 = Phase_1[1]
    u_yleft_ph1 = Phase_1[2]
    u_ycenter_ph2 = Phase_2[1]    
    u_yleft_ph2 = Phase_2[2]

    with open(location + str("\\")+ 'Plot_data.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([name,u_ycenter_ph1, u_yleft_ph1, u_ycenter_ph2, u_yleft_ph2])

def Plot_results(location):
    plt.style.use('seaborn')
    plt.figure(figsize=(19.20,10.80))

    data = pd.read_csv(location + str("\\")+ 'Plot_data.csv')
    data.replace(0, np.nan, inplace=True)
    names = data['names']
    u_c1 = data['Uy center phase1 [mm]']
    u_s1 = data['Uy side phase1 [mm]']
    u_c2 = data['Uy center phase2 [mm]']
    u_s2 = data['Uy side phase2 [mm]']
    
    plt.scatter(names, u_s1, c='black', edgecolor='black', linewidth=1, alpha=1)#, s=100), #c=categories_list)
    plt.scatter(names, u_c1, c='green', edgecolor='green', linewidth=1, alpha=0.5,s=100, marker='s')#, s=100), #c=categories_list)
    plt.scatter(names, u_s2, c='red', edgecolor='red', linewidth=1, alpha=1)#, #c=categories_list)
    plt.scatter(names, u_c2, c='orange', edgecolor='orange', linewidth=1, alpha=0.5, s=100,marker='s')#, s=100)#, c=categories_list)

    plt.title('Settlement for different solutions')
    plt.xlabel('Type of solution')
    plt.ylabel('Settlement (mm)')
    plt.xticks(rotation=45)
    

    
    
    
    plt.legend(bbox_to_anchor=(0., 1.08, 1., .108), loc='lower left',ncol=4, mode="expand", borderaxespad=0.)

    plt.savefig(location + str("\\")+ 'Results_plotted.png', bbox_inches = "tight")
    print('Calculation finished. Report and visual results have been put in the direction folder.')
 
    


Open_json(s_i, g_i)

    



