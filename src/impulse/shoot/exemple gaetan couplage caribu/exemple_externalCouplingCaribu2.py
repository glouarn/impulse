#exemple GL couplage externe L-py-Caribu avec 2 l-systems en intercation

import os
from openalea.lpy import *

#Imports caribu
from alinea.caribu.CaribuScene import CaribuScene
#from alinea.caribu.caributriangleset import CaribuTriangleSet #pas utile
#from alinea.caribu.plantgl_adaptor import scene_to_cscene #pas utile
from openalea.plantgl.all import *


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


# Chemin d'accès aux modèles de plante
path_lsys1 = 'Exo 10 - Axis2_ombre_light_caribu_carbon.lpy'#os.path.join(path_, 'Exo 10 - Axis2_ombre_light_caribu_carbon.lpy')

# On cree deux L-système avec parametres et positions differents
lsystem1 = Lsystem(path_lsys1)
lsystem1.Lpetiole = 0.9
lsystem1.carto = [[0.,0.,0.]] #cm
lsystem1.external_coupling = 1 #option pour desactiver couplage interne a caribu


lsystem2 = Lsystem(path_lsys1)
lsystem2.Lpetiole = 1.2
lsystem2.carto = [[5.,5.,0.]] #cm
lsystem2.external_coupling = 1 #option pour desactiver couplage interne a caribu

#gerer avec des nump!


#test de run independant
#lsystem1.derive()
#l-system plante avec derive et voit rien avec animate

#test run couplage externe

NBSTEPS = 300

# Initialisations des lstring (ici lecture des axiome)
Lstring1 = lsystem1.axiom
Lstring2 = lsystem2.axiom


#Loop externe avec 2 L-systems
for i in range(NBSTEPS):
    # derive d'1 step chaque l-system
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
    cc_scene = CaribuScene(scene=Lscene_coupled)
    raw, aggregated_out = cc_scene.run(direct=True, infinite=False)

    #  mise a jour variable plante dans chaque l-system
    aggregated1, aggregated2 = Split_outkeys(aggregated_out, Id_Shapes1, Id_Shapes2, decal=len(Lstring1))
    Lstring1, cumlight1 = lsystem1.updateLight_Lsyst(Lstring1, aggregated1)
    Lstring2, cumlight2 = lsystem2.updateLight_Lsyst(Lstring2, aggregated2)

    print(cumlight1, cumlight2)

    # Carbon assimilation and allocation
    dMS1 = lsystem1.CarbonAssimilation(cumlight1, lsystem1.IncomingLight, lsystem1.RUE, Soilsurf=1.)
    dMS2 = lsystem2.CarbonAssimilation(cumlight2, lsystem2.IncomingLight, lsystem2.RUE, Soilsurf=1.)
    lsystem1.MS += dMS1
    lsystem2.MS += dMS2
    lsystem1.dMSRoot = dMS1 * lsystem1.AllocRoot
    lsystem2.dMSRoot = dMS2 * lsystem2.AllocRoot

    #print(i,cumlight1, lsystem1.MS, lsystem1.dMSRoot, cumlight2)




