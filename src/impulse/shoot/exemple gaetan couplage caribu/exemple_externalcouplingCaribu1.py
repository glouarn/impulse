#exemple GL couplage externe L-py-Caribu avec 1 L-system

import os
from openalea.lpy import *

#Imports caribu
from alinea.caribu.CaribuScene import CaribuScene
#from alinea.caribu.caributriangleset import CaribuTriangleSet #pas utile
#from alinea.caribu.plantgl_adaptor import scene_to_cscene #pas utile
from openalea.plantgl.all import *



# Chemin d'accès aux modèles de plante
path_lsys1 = 'Exo 10 - Axis2_ombre_light_caribu_carbon.lpy'#os.path.join(path_, 'Exo 10 - Axis2_ombre_light_caribu_carbon.lpy')

# On cree un L-système avec parametres et positions differents
lsystem1 = Lsystem(path_lsys1)
lsystem1.Lpetiole = 0.9
lsystem1.carto = [[0.,0.,0.]] #[[5.,5.,0.]]  #cm
lsystem1.external_coupling = 1 #option pour desactiver couplage interne a caribu dans le l-system



#test de run independant
#lsystem1.derive()
#l-system plante avec derive et voit rien avec animate

#test run couplage externe

NBSTEPS = 300

# Initialisations des lstring (ici lecture des axiome)
Lstring1 = lsystem1.axiom

#Loop exerte avec 1 L-system
for i in range(NBSTEPS):
    # derive d'1 step chaque l-system
    Lstring1 = lsystem1.derive(Lstring1,1)#derive sur un pas de temps
    Lscene1 = lsystem1.sceneInterpretation(Lstring1)

    # run caribu
    cc_scene = CaribuScene(scene=Lscene1)
    raw, aggregated_out = cc_scene.run(direct=True, infinite=False)

    # mise a jour variable plante
    Lstring1, cumlight = lsystem1.updateLight_Lsyst(Lstring1, aggregated_out)
    # Carbon assimilation and allocation
    dMS = lsystem1.CarbonAssimilation(cumlight, lsystem1.IncomingLight, lsystem1.RUE, Soilsurf=1.)
    lsystem1.MS += dMS
    lsystem1.dMSRoot = dMS * lsystem1.AllocRoot
    print(i,cumlight, lsystem1.MS, lsystem1.dMSRoot)



#tourne bien, meme sortie quand interne decranche, coherente pour different points de depart de la plante

