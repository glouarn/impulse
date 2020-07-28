#exemple GL couplage externe L-py-Caribu-3DS avec 2 l-systems en intercation

import os
from openalea.lpy import *

#Imports caribu
from alinea.caribu.CaribuScene import CaribuScene
#from alinea.caribu.caributriangleset import CaribuTriangleSet #pas utile
#from alinea.caribu.plantgl_adaptor import scene_to_cscene #pas utile
from openalea.plantgl.all import *

# import du sol 3ds + test
from soil3ds import soil_moduleN as solN
from soil3ds.test.test_init_soil import init_sol_test

# import de l'interface sol impulse
import impulse.soil.soil as soil_interface
import IOxls




def get_lstringIDshapes(Lscene1, Lscene2, Lstring1, Lstring2):
    """ (J Lombard)"""
    Id_Shapes1 = []  # Listes vides qui contiendront les identifiants des objets composant la Lscene, ces identifiants sont propres a chaque scene et sont conserves lors de la fusion des deux scenes
    Id_Shapes2 = []
    # recuperer les IDshape de chaque element de chaque Lscene et les sauvegarder !!!
    # !! seulement les elements de la lstring avec une interpretation geometrique !!!
    for num in range(len(Lscene1)):
        # spaheID contient 'ShapeID'+'numero position element dans la chaine (demare a 0 et va longueur chaine, mais a tous les elements meme ceux pas interpretes)'+'une serie de chiffre??'
        ShapeID = Lscene1[num].name
        #print(ShapeID)
        ShapeID_splitted = str.split(ShapeID, '_')
        Id_Shapes1.append(int(ShapeID_splitted[1]))
    #print('Et hop !', Id_Shapes1)

    DecalLongueurString = len(Lstring1)  # Nombre de IDshapes dans la scene 1, utilise pour decale nombre dans lstring 2
    for num in range(len(Lscene2)):
        # modifie nom pour eviter doublons dans le deuxieme l-systems
        ShapeID = Lscene2[num].name  # On récupère
        # print(ShapeID)
        ShapeID_splitted = str.split(ShapeID, '_')  # On splite
        Nummodule = ShapeID_splitted[1]
        Id_Shapes2.append(int(ShapeID_splitted[1]) + DecalLongueurString)  # On enregistre la  position du module +la longueur de la scène 1 pour éviter lesID doublons

        # Mise a jour de l'ID de module dans la scene
        newID = int(ShapeID_splitted[1]) + DecalLongueurString  # Le nouvel ID du module
        NewShapeID = ShapeID.replace(Nummodule, str(newID))  # Est insere dans le IDshape de la scene
        Lscene2[num].name = NewShapeID  # On met a jour son nom
        Lscene2[num].id = newID  # Et son ID -> Indispensable pour que Caribu comprenne et calcule correctement

    #print('Et hopla !', Id_Shapes2)
    return Lscene1, Lscene2, Lstring1, Lstring2, Id_Shapes1, Id_Shapes2


def Split_outkeys(aggregated_out, Id_Shapes1, Id_Shapes2, decal):
    aggregated1 = {'default_band': {'Eabs': {}, 'Ei': {}, 'area': {}}}
    aggregated2 = {'default_band': {'Eabs': {}, 'Ei': {}, 'area': {}}}
    for key in aggregated_out['default_band'].keys():
        for ID in aggregated_out['default_band'][key].keys():
            if ID in Id_Shapes1:
                aggregated1['default_band'][key][ID] = aggregated_out['default_band'][key][ID]
            if ID in Id_Shapes2:
                newID = ID-decal #remet les ID d'origine avant fusion des scenes
                aggregated2['default_band'][key][newID] = aggregated_out['default_band'][key][ID]

    return aggregated1, aggregated2


def calc_epsi(ls_cumlight, surfsolref=1., I0=1.):
    ls_epsi= []
    for cumlight in ls_cumlight:
        ls_epsi.append(cumlight/(surfsolref*I0))
    return ls_epsi


# intitialisation modele sol
## creation d'un objet sol 3ds par defaut (S) - definit avant le modele de plante car sert a instancier la grille
pattern8 = [[-50.,-50.], [50.,50.]]#[[-15.,-15.], [15.,15.]]#cm
Lsol = max((pattern8[1][0]-pattern8[0][0])/100., (pattern8[1][1]-pattern8[0][1])/100.)#m
largsol = min((pattern8[1][0]-pattern8[0][0])/100., (pattern8[1][1]-pattern8[0][1])/100.)#m
surfsolref = Lsol*largsol #m2

dz= 5.
S = init_sol_test(pattern8, dz=dz, size=[10,10,30]) #en cm / nb voxel
stateEV = [0.,0.,0.]
properties_3ds = ['asw_t', 'tsw_t', 'Corg', 'Norg', 'm_NO3', 'm_NH4', 'm_soil_vol', 'm_Tsol', 'm_DA', 'ftsw_t']
#print (S.ftsw_t)


# lecture meteo
#variables meteto pour bilan hydrique
nb_jours=100
dTT=10
TTdays = range(1,nb_jours*dTT,dTT) # TT des changements de jour auquel faire le calcul de bilan hydrique / Sol
Rain = [10.]*nb_jours
Irrig = [0.]*nb_jours
epsi = [0.9999]*nb_jours #efficience d'interceptio plante ; 1: voit que effet transpi
Et0 = [0.1]*nb_jours #ETP (mm)
IncomingLight = 0.00001#0.001#MJ.m-2-degredays-1 (jour cumulant 10 degres days)


carto1 = [[0.,0.,0.]] #cm
carto2 = [[5.,5.,0.]] #cm


# Chemin d'acces aux modeles de plante aerien
path_lsys1 = r'C:\devel\impulse\src\impulse\shoot\exemple gaetan couplage caribu\Exo 10 - Axis2_ombre_light_caribu_carbon.lpy'#os.path.join(path_, 'Exo 10 - Axis2_ombre_light_caribu_carbon.lpy')

# On cree deux L-système avec parametres et positions differents
lsystem1 = Lsystem(path_lsys1)
lsystem1.Lpetiole = 0.9
lsystem1.carto = carto1#[[0.,0.,0.]] #cm
lsystem1.external_coupling = 1 #option pour desactiver couplage interne a caribu


lsystem2 = Lsystem(path_lsys1)
lsystem2.Lpetiole = 1.8
lsystem2.carto = carto2#[[5.,5.,0.]] #cm
lsystem2.external_coupling = 1 #option pour desactiver couplage interne a caribu


# intitialisation modele plante racine
path_lsys1R = '..\ArchiSimple GL2_coupled_mm.lpy'#os.path.join(path_, 'ArchiSimple GL2_coupled_mm.lpy')

# On cree deux L-systeme avec parametres plante et grille de sol interface
lsystem1R = Lsystem(path_lsys1R)
ongletP1 = 'sevanskij'#'timbale'#'leo'#'canto'#'formica'#'giga'#'canto'#'kayanne'#
lsystem1R.ParamP = IOxls.read_plant_param(lsystem1R.path_plante, ongletP1)
lsystem1R.carto = carto1#[[0.,0.,0.]] #cm
#offre en C
lsystem1R.OffrC = [0.0003]*100 #offre journaliere en C
#grid
lsystem1R.mysoil = lsystem1R.initSoilInterface_from3DS(S, properties_3ds)
lsystem1R.external_coupling = 1 #option pour desactiver couplage interne a 3DS
lsystem1R.PLOT_PROPERTY = -1#'root_length'#

lsystem2R = Lsystem(path_lsys1R)
ongletP2 = 'sevanskij'#'timbale'#'leo'#'canto'#'formica'#'giga'#'canto'#'kayanne'#
lsystem2R.ParamP = IOxls.read_plant_param(lsystem2R.path_plante, ongletP2)
lsystem2R.carto = carto2#[[0.,0.,0.]] #cm
#offre en C
lsystem2R.OffrC = [0.0003]*100 #offre journaliere en C
#grid
lsystem2R.mysoil = lsystem2R.initSoilInterface_from3DS(S, properties_3ds)
lsystem2R.external_coupling = 1 #option pour desactiver couplage interne a 3DS
lsystem2R.PLOT_PROPERTY = -1#'root_length'#



#test run couplage externe

NBSTEPS = 300

# Initialisations des lstring (ici lecture des axiome)
Lstring1 = lsystem1.axiom
Lstring2 = lsystem2.axiom
Lstring1R = lsystem1R.axiom
Lstring2R = lsystem2R.axiom


#Loop externe avec 2x2 L-systems + couplage 2 modeles d'environnement
for i in range(NBSTEPS):
    #######
    # Parties aeriennes et lumiere (caribu)
    #######

    # derive d'1 step chaque l-system aerien
    Lstring1 = lsystem1.derive(Lstring1,1)#derive sur un pas de temps
    Lscene1 = lsystem1.sceneInterpretation(Lstring1)

    Lstring2 = lsystem2.derive(Lstring2, 1)  # derive sur un pas de temps
    Lscene2 = lsystem2.sceneInterpretation(Lstring2)

    # Mise a jour des IDShapes compatibles entre les deux L-systems et creation de la scene commune
    Lscene1, Lscene2, Lstring1, Lstring2, Id_Shapes1, Id_Shapes2 = get_lstringIDshapes(Lscene1, Lscene2, Lstring1, Lstring2)
    Lscene_coupled = Lscene1 + Lscene2
    #print('Et hop !', Id_Shapes1)
    #print('Et hopla !', Id_Shapes2)

    # run caribu
    Pattern = (pattern8[0][0], pattern8[0][1], pattern8[1][0], pattern8[1][1]) #pattern8 untilise pour definir le sol
    cc_scene = CaribuScene(scene=Lscene_coupled,  pattern=Pattern, scene_unit='cm')  #ciel vertical + pattern
    raw, aggregated_out = cc_scene.run(direct=True, infinite=True)

    #cc_scene = CaribuScene(scene=Lscene_coupled)
    #raw, aggregated_out = cc_scene.run(direct=True, infinite=False)

    #  mise a jour variable plante dans chaque l-system
    aggregated1, aggregated2 = Split_outkeys(aggregated_out, Id_Shapes1, Id_Shapes2, decal=len(Lstring1))
    Lstring1, cumlight1 = lsystem1.updateLight_Lsyst(Lstring1, aggregated1)
    Lstring2, cumlight2 = lsystem2.updateLight_Lsyst(Lstring2, aggregated2)

    print(cumlight1, cumlight2)

    # Carbon assimilation and allocation
    dMS1 = lsystem1.CarbonAssimilation(cumlight1, IncomingLight, lsystem1.RUE, Soilsurf=1.)
    dMS2 = lsystem2.CarbonAssimilation(cumlight2, IncomingLight, lsystem2.RUE, Soilsurf=1.)
    lsystem1.MS += dMS1
    lsystem2.MS += dMS2
    OffrCR1 = dMS1 * lsystem1.AllocRoot
    OffrCR2 = dMS2 * lsystem2.AllocRoot
    lsystem1.dMSRoot = OffrCR1
    lsystem2.dMSRoot = OffrCR2

    #print(i,cumlight1, lsystem1.MS, lsystem1.dMSRoot, cumlight2)

    #######
    # Racines et Sol (3DS)
    #######
    # MAJ des L-system racines avec alloc C
    lsystem1R.OffrC = [OffrCR1]*nb_jours
    lsystem2R.OffrC = [OffrCR2]*nb_jours
    print('Offc', OffrCR1, OffrCR2, lsystem1R.P_SC, lsystem2R.P_SC)

    #MAJ espi
    #ls_epsi = [0.9999/2., 0.9999/2.] #* nb_jours #a reprendre
    ls_epsi = calc_epsi([cumlight1, cumlight2], surfsolref, I0=1.)#calcul sur ciel normalise

    # derive d'1 step chaque l-system
    Lstring1R = lsystem1R.derive(Lstring1R,1)#derive sur un pas de temps
    Lscene1R = lsystem1R.sceneInterpretation(Lstring1R)
    Lstring2R = lsystem2R.derive(Lstring2R,1)#derive sur un pas de temps
    Lscene2R = lsystem2R.sceneInterpretation(Lstring2R)


    j = lsystem1R.Which_idjour(TTdays, i, 1)  # id jour
    # fait step water balance pas tous les degres jours: uniquement 1 fois par jour (TT indiques dans TTdays)
    if i in TTdays: #si TT celui d'un passage de jour
        r1 = lsystem1R.soil3D2s3DSprop(lsystem1R.mysoil, S, 'root_length')
        r2 =lsystem2R.soil3D2s3DSprop(lsystem2R.mysoil, S, 'root_length')
        ls_roots = [r1, r2]
        print('ls_roots', r1.sum(), r2.sum(),r1.shape,r2.shape)
        ls_transp, evapo_tot, ls_drainage, stateEV,  ls_m_transpi, m_evap, ls_ftsw = S.stepWBmc(Et0[j], ls_roots, ls_epsi, Rain[j], Irrig[j], stateEV)
        print ('tp water balance externe:', i, ls_ftsw)

    # mise a zero compteur racine et a jour
    lsystem1R.mysoil.add_property('root_length', 0)
    lsystem2R.mysoil.add_property('root_length', 0)
    #reinjecte resultats bilan hydrique etat de sol
    lsystem1R.mysoil.set_3ds_properties(S, properties_3ds)
    lsystem2R.mysoil.set_3ds_properties(S, properties_3ds)
    #a faire: reinjecter FSTW et etats plantes


#couplage des deux l-systeme pour bilan hydrique fait plus planter
#+ espi mis a jour
# mais ls_ftsw reste a nan... a creuser



#sauvegarde scene complete
sceneall = Lscene1#+Lscene1R#+Lscene2+Lscene2R
sceneall.save(r'C:\Users\Glouarn\Desktop\testcoupling.geom') #sauvegarde pour visu externe
#scene pas lue dans le viewer a cause de pb d'id color?
sceneall = Lscene1R#+Lscene1#+Lscene2+Lscene2R
sceneall.save(r'C:\Users\Glouarn\Desktop\testcoupling2.geom')
sceneall = Lscene2#+Lscene1R#+Lscene2+Lscene2R
sceneall.save(r'C:\Users\Glouarn\Desktop\testcoupling3.geom')
sceneall = Lscene2R#+Lscene1R#+Lscene2+Lscene2R
sceneall.save(r'C:\Users\Glouarn\Desktop\testcoupling4.geom')

#les charger dans ipyton apres %gui qt5
#visu avec sol fait planter??

# pb de x10 dans taille des racines? non -> semble tige/feuilles qui ont taille max petite...
# meme avec un facteur 10 les racines ne sont tjrs pas limitee par C
#pb d'unite ds surface feuille/area??

#pas encore de bouclage de FTSW (car pas de reponse FSTW ds le l-system test)