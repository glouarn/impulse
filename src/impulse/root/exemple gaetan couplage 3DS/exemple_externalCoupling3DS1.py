#exemple GL couplage externe L-py (archisimple)-3DS avec 1 L-system

import os
from openalea.lpy import *

# import du sol 3ds + test
from soil3ds import soil_moduleN as solN
from soil3ds.test.test_init_soil import init_sol_test

# import de l'interface sol impulse
import impulse.soil.soil as soil_interface
import IOxls



# intitialisation modele sol
## creation d'un objet sol 3ds par defaut (S) - definit avant le modele de plante car sert a instancier la grille
pattern8 = [[-50.,-50.], [50.,50.]]#[[-15.,-15.], [15.,15.]]#cm
S = init_sol_test(pattern8, dz=5., size=[10,10,30]) #en cm / nb voxel
stateEV = [0.,0.,0.]
#print (S.ftsw_t)

# lecture meteo
#variables meteto pour bilan hydrique
nb_jours=100
dTT=10
TTdays = range(1,nb_jours*dTT,dTT) # TT des changements de jour auquel faire le calcul de bilan hydrique / Sol
Rain = [0.]*nb_jours
Irrig = [0.]*nb_jours
epsi = [0.9999]*nb_jours #efficience d'interceptio plante ; 1: voit que effet transpi
Et0 = [0.1]*nb_jours #ETP (mm)


# intitialisation modele plante
path_lsys1 = '..\ArchiSimple GL2_coupled_mm.lpy'#os.path.join(path_, 'ArchiSimple GL2_coupled_mm.lpy')

# On cree un L-système avec parametres plante et grille de sol interface
lsystem1R = Lsystem(path_lsys1)
ongletP = 'sevanskij'#'timbale'#'leo'#'canto'#'formica'#'giga'#'canto'#'kayanne'#
lsystem1R.ParamP = IOxls.read_plant_param(lsystem1R.path_plante, ongletP)
lsystem1R.carto = [[0.,0.,0.]] #cm
#offre en C
lsystem1R.OffrC = [0.0003]*100 #offre journaliere en C
#grid
properties_3ds = ['asw_t', 'tsw_t', 'Corg', 'Norg', 'm_NO3', 'm_NH4', 'm_soil_vol', 'm_Tsol', 'm_DA', 'ftsw_t']
lsystem1R.mysoil = lsystem1R.initSoilInterface_from3DS(S, properties_3ds)
lsystem1R.external_coupling = 1 #option pour desactiver couplage interne a 3DS


#test run couplage externe
NBSTEPS = 300

# Initialisations des lstring (ici lecture des axiome)
Lstring1R = lsystem1R.axiom

#Loop exerte avec 1 L-system
for i in range(NBSTEPS):
    # derive d'1 step chaque l-system
    Lstring1R = lsystem1R.derive(Lstring1R,1)#derive sur un pas de temps
    Lscene1R = lsystem1R.sceneInterpretation(Lstring1R)

    j = lsystem1R.Which_idjour(TTdays, i, 1)  # id jour
    # fait step water balance pas tous les degres jours: uniquement 1 fois par jour (TT indiques dans TTdays)
    if i in TTdays: #si TT celui d'un passage de jour
        ls_roots = [lsystem1R.soil3D2s3DSprop(lsystem1R.mysoil, S, 'root_length')]
        ls_transp, evapo_tot, ls_drainage, stateEV,  ls_m_transpi, m_evap, ls_ftsw = S.stepWBmc(Et0[j], ls_roots, [epsi[j]], Rain[j], Irrig[j], stateEV)
        print ('tp water balance externe:', i, ls_ftsw)

    # mise a zero compteur racine et a jour
    lsystem1R.mysoil.add_property('root_length', 0)
    #reinjecte resultats bilan hydrique
    lsystem1R.mysoil.set_3ds_properties(S, properties_3ds)




