#Widget blijft in principe hetzelfde, dus vanuit GUI wordt gelezen:
B_schot_1 = str(self.M_Widget_1_1_4.text())  # input lezen van gui - breedte
L_schot_1 = str(self.M_Widget_1_1_6.text())  # lengte
D_schot_1 = str(self.M_Widget_1_1_8.text())  # dikte
G_schot_1 = str(self.M_Widget_1_1_10.text())  # volume gewicht
Schot_1 = [float(B_schot_1), float(L_schot_1), float(D_schot_1), float(G_schot_1)]

n_schot = int(self.M_Widget_1_1_1.currentText())  # aantal lagen (1 of 2)





#=============================================== KOP 3 veranderingen =================================================
#voorgestelde functie in KOP3:
#voor STAAL modeleren we als plate object
def create_plates_staal(g_i, JSON_file, name, location, Model_mode):

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



#nog voorgestelde functie KOP 3

def create_volume_hout():
    #iets in het kader als:
    g_i.borehole_main = g_i.borehole(0)  #maar eigenlijk moet hij worden toegevoegd aan de borehole

    g_i.soillayer(0)  # creert een grondlaag
    g_i.setsoillayerlevel(g_i.borehole_main, number, upper_boundary)  # creert een laaglevel



# create_plates wordt aangeroepen met:
# create_plates(g_i=g_i, JSON_file=JSON_file, name=name, location=location, Model_mode=Model_mode)


#==================================================== KOP 2 veranderingen =============================================

#Huidige functie in KOP2 : moet op de schop

#wordt aangeroepen in: Calc_Bep_Stemp

#parameters:
# - Q =Q_kraan [kN]
# - mv = maaiveld
# - gws = grondwaterstand
# - Schot_1= [ breedte, lengte, dikte, volumegewicht] van schotten laag 1
# - Schot_2= [ breedte, lengte, dikte, volumegewicht] van schotten laag 2
# - n_schot= aantal lagen schotten (1 of 2)
# - Case_nr= bepaalt berekening type

# - gamma_per: op basis van risico factor RC, wordt uit tabel bel_factors gehaald
# - gamma_kraan: same


#BEREKENING SCHOTTEN BELASTING
    # berekening op basis van geselecteerde parameters in bovenstaande functie.
    """ Berekenening van belastingen, spreiding en funderingsniveaus bij toepassing van schotten """

"Dit is functie nummer 1 "
"Case 0: no enhancement (initial phase)"
def Calc_Bep_Stemp(self, W, L, Q, mv, gws):
    # Q is Q_kraan, de kraanbelasting
    self.Plaxis_Input = []
    q_rep_plaxis = Q / (W * L)  # druk op de ondergrond van de belasting. Dat is gewicht/oppervlakte  #bruikbaarheidsgrenstoestand
    # gamma_kraan, is afgeleid van de risico factor berekening, dus afhankelijk van RC 1, 2 etc
    q_d_plaxis = Q * self.gamma_kraan / (W * L)  # uiterste grenstoestand
    W_plaxis = min(W, L)  # width
    L_plaxis = max(W, L)  # length
    fund_plaxis = mv  # aangrijppunt, dit moet misschien ook nog veranderd worden
    gws_plaxis = gws  # grondwaterstand
    D_plaxis = 0
    Gv_plaxis = "n.v.t."

    Case_nr = 1000000  # initieel case_nr, er wordt hier later bij opgeteld om cases te onderscheiden
    Case_0 = [Case_nr, q_rep_plaxis, q_d_plaxis, W_plaxis, L_plaxis, gws_plaxis, fund_plaxis, D_plaxis, Gv_plaxis]
    self.Plaxis_Input.append(Case_0)   #"ALTIJD wordt deze case berekend"

"Deze functie returns de plaxis_input lijst met case 1"

"Dit is functie nummer 2 "
"Case 1 tm 4: schotten"
"Case 5: Soil enhancement (zonder schotten)"
"Case 6: Horizontal Geogrids"
def select_situation(self):

    #hier moet nog iets komen van, schotten STAAL VS HOUT
    #if STAAL:
        # ga naar functie die parameters voor plates bepaalt
        # parameters:
        # ('MaterialName', 'example_platemat'), ('IsIsotropic', True), ('Gref', G), ('d', d), ('nu', nu), ('EA', EA), ('EA2', EA), ('EI', EI)
    #if HOUT:
        # ga naar functie die parameters voor volume element bepaalt: dit kan calc_bep_schot zijn
        # parameters:
        # zelfde als voor soils

    #kan me voorstellen als staal een plate is dat wordt toegevoegd, dat in een aparte array moet worden geladen in JSON file
    # input_plaxis voor alle soils
    # input_plaxis_plate voor eventuele plate
    # KOP 3 moet dan checken: is er een plate in de list? zo ja, voeg die dan toe.

    Case_nr = 1000000  # initieel case_nr, er wordt hier later bij opgeteld om cases te onderscheiden

    """ Schotten sectie 1"""  # bepaal breedte, lengte, dikte, volume van matten
    # lees schotten informatie

    if self.M_Widget_1_1_2.isChecked():   "Include situation A with dragline mats"
        Case_nr_1 = Case_nr + 100000
        B_schot_1 = str(self.M_Widget_1_1_4.text())  # input lezen van gui - breedte
        L_schot_1 = str(self.M_Widget_1_1_6.text())  # lengte
        D_schot_1 = str(self.M_Widget_1_1_8.text())  # dikte
        G_schot_1 = str(self.M_Widget_1_1_10.text())  # volume gewicht

        Schot_1 = [float(B_schot_1), float(L_schot_1), float(D_schot_1), float(G_schot_1)]

        n_schot = int(self.M_Widget_1_1_1.currentText())  # aantal lagen (1 of 2)

    if n_schot == 2:  "option for two mats"
        B_schot_2 = str(self.M_Widget_1_2_4.text())
        L_schot_2 = str(self.M_Widget_1_2_6.text())
        D_schot_2 = str(self.M_Widget_1_2_8.text())
        G_schot_2 = str(self.M_Widget_1_2_10.text())
        Schot_2 = [float(B_schot_2), float(L_schot_2), float(D_schot_2), float(G_schot_2)]

    else:
        Schot_2 = []

    #NOTE: case_nr wordt alleen maar gegeven en dan weer teruggestuurd
    #if type=='hout':
        # case_1=self.calc_houten_schot(Q, mv, gws, Schot_1, Schot_2, n_schot, Case_nr=Case_nr_1)
    #if type=='staal':
        # case_1=self.calc_stalen_schot(Q, mv, gws, Schot_1, Schot_2, n_schot, Case_nr=Case_nr_1)
    Case_1=self.Calc_Bep_Schot(Q, mv, gws, Schot_1, Schot_2, n_schot, Case_nr=Case_nr_1)  # run schotten berekening!
    self.Plaxis_Input.append(Case_1)

    #Case = [Case_nr, q_rep_plaxis, q_d_plaxis, W_plaxis, L_plaxis, gws_plaxis, fund_plaxis, D_plaxis, Gv_plaxis]
    """ Schotten sectie 2"""
    if self.M_Widget_2_1_2.isChecked():   "Include situation B with dragline mats'"
        Case_nr_2 = Case_nr + 200000
        B_schot_1 = str(self.M_Widget_2_1_4.text())
        L_schot_1 = str(self.M_Widget_2_1_6.text())
        D_schot_1 = str(self.M_Widget_2_1_8.text())
        G_schot_1 = str(self.M_Widget_2_1_10.text())

        Schot_1 = [float(B_schot_1), float(L_schot_1), float(D_schot_1), float(G_schot_1)]

        n_schot = int(self.M_Widget_2_1_1.currentText())

    if n_schot == 2:   "option for two mats"
        B_schot_2 = str(self.M_Widget_2_2_4.text())
        L_schot_2 = str(self.M_Widget_2_2_6.text())
        D_schot_2 = str(self.M_Widget_2_2_8.text())
        G_schot_2 = str(self.M_Widget_2_2_10.text())
        Schot_2 = [float(B_schot_2), float(L_schot_2), float(D_schot_2), float(G_schot_2)]
    else:
        Schot_2 = []

        Case_2=self.Calc_Bep_Schot(Q, mv, gws, Schot_1, Schot_2, n_schot, Case_nr=Case_nr_2)
        self.Plaxis_Input.append(Case_2)

    """ Schotten sectie 3"""
    if self.M_Widget_3_1_2.isChecked():     "Include situation C with dragline mats'"
        Case_nr_3 = Case_nr + 300000
        B_schot_1 = str(self.M_Widget_3_1_4.text())
        L_schot_1 = str(self.M_Widget_3_1_6.text())
        D_schot_1 = str(self.M_Widget_3_1_8.text())
        G_schot_1 = str(self.M_Widget_3_1_10.text())
        Schot_1 = [float(B_schot_1), float(L_schot_1), float(D_schot_1), float(G_schot_1)]

        n_schot = int(self.M_Widget_3_1_1.currentText())

    if n_schot == 2:   "option for two mats"
        B_schot_2 = str(self.M_Widget_3_2_4.text())
        L_schot_2 = str(self.M_Widget_3_2_6.text())
        D_schot_2 = str(self.M_Widget_3_2_8.text())
        G_schot_2 = str(self.M_Widget_3_2_10.text())
        Schot_2 = [float(B_schot_2), float(L_schot_2), float(D_schot_2), float(G_schot_2)]
    else:
        Schot_2 = []

        Case_3=self.Calc_Bep_Schot(Q, mv, gws, Schot_1, Schot_2, n_schot, Case_nr=Case_nr_3)
        self.Plaxis_Input.append(Case_3)

    """ Schotten sectie 4"""  # laatste 'normale' selectie
    if self.M_Widget_4_1_2.isChecked():         "Include situation C with dragline mats'"
        Case_nr_4 = Case_nr + 400000
        B_schot_1 = str(self.M_Widget_4_1_4.text())
        L_schot_1 = str(self.M_Widget_4_1_6.text())
        D_schot_1 = str(self.M_Widget_4_1_8.text())
        G_schot_1 = str(self.M_Widget_4_1_10.text())
        Schot_1 = [float(B_schot_1), float(L_schot_1), float(D_schot_1), float(G_schot_1)]

     n_schot = int(self.M_Widget_4_1_1.currentText())

    if n_schot == 2:    "option for two mats"
        B_schot_2 = str(self.M_Widget_4_2_4.text())
        L_schot_2 = str(self.M_Widget_4_2_6.text())
        D_schot_2 = str(self.M_Widget_4_2_8.text())
        G_schot_2 = str(self.M_Widget_4_2_10.text())
        Schot_2 = [float(B_schot_2), float(L_schot_2), float(D_schot_2), float(G_schot_2)]
    else:
        Schot_2 = []

        Case_4=self.Calc_Bep_Schot(Q, mv, gws, Schot_1, Schot_2, n_schot, Case_nr=Case_nr_4)
        self.Plaxis_Input.append(Case_4)


        """Sectie 5: Grondverbetering zonder geotextielen (en zonder schotten) (GZG)"""
    if self.Widget3_2_3_1.isChecked():      "Include situation with Soil Enhancement"
        Case_nr_5 = []
        D_fund_g = []   # max diepte grondverbetering, meerdere kunnen worden geselecteerd!
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

        #Case 5 wordt in de functie toegevoegd aan Plaxis_Input!
        self.Calc_Combi_GZG(Q, mv, gws, Case = Case_0, Case_nr = Case_nr_5, D_fund = D_fund_g)


        """Sectie 6: Grondverbetering met horizontale geogrids (en zonder schotten) (GMG)"""
    if self.Widget3_2_4_1.isChecked():  "Ïnclude situation with horizontal Geogrids"
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
        # Case 6 wordt in de functie toegevoegd aan Plaxis_Input!
        self.Calc_Combi_GMG(Q, mv, gws, Spreiding , Gv , Case=Case_0, D_fund=D_fund_grid, Case_nr = Case_nr_6)

        """Sectie 7: Grondverbetering met geocellen (en zonder schotten)(GMG)"""
    if self.Widget3_2_5_1.isChecked():  "Include situation with Geocells"
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

"Dit is functie nummer 2 "

def Calc_Bep_Schot(self, mv, gws, Schot_1, Schot_2, n_schot, Case_nr):  #wordt dit één functie voor hout?

        #opties voor als er één laag schotten is
        if n_schot == 1:
            #bruikbaarheidsgrenstoestand
            BGT_schot = Schot_1[2]*Schot_1[1]*Schot_1[0]*Schot_1[3]*9.81/1000 #schot_1 bevat breedte [0], lengte[1], dikte[2], dus dit is volume *9,81 is Belasting
            #uiterste grenstoestand
            UGT_schot = BGT_schot*self.gamma_per
            #hier werd belasting samen genomen met kraan belasting, dat is niet de bedoeling!

            q_rep_plaxis = (BGT_schot) / (Schot_1[0] * Schot_1[1])   #bruikbaarheidsgrenstoestand
            #want schot_1[0] = lengte, schot_1[1] =  breedte

            q_d_plaxis = (UGT_schot) / (Schot_1[0] * Schot_1[1])

            W_plaxis = min(Schot_1[0],Schot_1[1])  #Bepaal korte en lange kant
            L_plaxis = max(Schot_1[0],Schot_1[1])

            fund_plaxis = mv
            gws_plaxis = gws
            D_plaxis = 0
            Gv_plaxis = "n.v.t."

            #wat heb je nodig om het plate element te maken? functie nu nog ingericht voor volume

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

            # q_rep_plaxis = (Q+BGT_schot)/(max(Schot_1[0],Schot_2[0])*max(Schot_1[1],Schot_2[1]))
            q_rep_plaxis = (BGT_schot)/(max(Schot_1[0],Schot_2[0])*max(Schot_1[1],Schot_2[1]))
            # q_d_plaxis = (Q*self.gamma_kraan + UGT_schot)/(max(Schot_1[0],Schot_2[0])*max(Schot_1[1],Schot_2[1]))
            q_d_plaxis = (Q * self.gamma_kraan + UGT_schot) / (max(Schot_1[0], Schot_2[0]) * max(Schot_1[1], Schot_2[1]))

            W_plaxis = min(Schot_1[0],Schot_1[1])
            L_plaxis = max(Schot_1[0],Schot_1[1])
            fund_plaxis = mv
            gws_plaxis = gws
            D_plaxis = 0
            Gv_plaxis = "n.v.t"

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

            Case = [Case_nr, q_rep_plaxis, q_d_plaxis, W_plaxis, L_plaxis, gws_plaxis, fund_plaxis, D_plaxis, Gv_plaxis]

        return Case

""" Berekening van belastingen, spreiding en funderingsnvieaus bij toepassing van grondverbetering zonder geotextiel """
def Calc_Combi_GZG(self, Q, mv, gws, Case, Case_nr, D_fund):
    for i in range(len(D_fund)): #dit is een loop over verschillende D_funds
        Case_GZG = Case.copy()
        Case_GZG[0] = Case_nr[i]
        #Case_3[4] = gws kan verwijderd worden
        Case_GZG[7] = D_fund[i] #Dikte van grondverbetering
        Case_GZG[8] = str(self.Widget3_2_3_5.currentText()) #Naam van grondverbetering
        self.Plaxis_Input.append(Case_GZG)


""" Berekening van belastingen, spreiding en funderingsnvieaus bij toepassing van grondverbetering met geotextiel """
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










