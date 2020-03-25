#test soil impulse G Louarn v2
# couplage avec l'interface sol d'impulse - racines forcee dans une structure fixe par defaut (root)

import numpy as np

# import du sol 3ds + test
from soil3ds import soil_moduleN as solN
from soil3ds.test.test_init_soil import init_sol_test

# import de l'interface sol impulse
import impulse.soil.soil as soil_interface



########################
## exemple 1
## couplage + boucle avec uniquement transpiration plante
## (pas d'entree d'eau + pas d'evaporation du sol avec epsi=1.)
########################

nb_jours = 50#20#100
Rain = [0.]*nb_jours
Irrig = [0.]*nb_jours
epsi = [0.9999]*nb_jours #efficience d'interceptio plante ; 1: voit que effet transpi
Et0 = [0.5]*nb_jours #ETP (mm)



## creation d'un objet sol 3ds par defaut (S)
S = init_sol_test(pattern8 = [[-50.,-50.], [50.,50.]], dz=5., size=[10,10,30])
stateEV = [0.,0.,0.] #pour le calcul de l'evaporation du sol (memoire du cumul evapore depuis derniere PI)


#instancie un odjet sol 3D d'interface vide (mysoil) a partir de l'objet sol 3ds (S)
size_ = S.size[1:]+S.size[0:1] #passe z,x,y en xyz
dxyz_ = [S.dxyz[0][0], S.dxyz[1][0], S.dxyz[2][0]]
origin = S.origin
# Par default, les dimensions sont exprimes en m. Il faut les convertir en cm pour le Soil3D
dxyz_ = [v*100 for v in dxyz_]
origin = [v*100 for v in origin]


mysoil = soil_interface.Soil3D(origin, size_, dxyz_)
print(origin, size_, dxyz_)

from impulse.root.archisimple import ArchiSimpleModel

rootmodel = ArchiSimpleModel(soil=mysoil)
rootmodel.model.PLOT_PROPERTY = 'root_density'#'ftsw_t'

#def soil3D2s3DSprop(struct1, struct2, propname):
#    propvalue = np.zeros(struct2.size)
#    for i in range(struct2.size[0]):
#        propvalue[i,:,:] = struct1.m[propname][:,:,i]
#    return propvalue


def soil3D2s3DSprop(struct1, struct2, propname):
    return np.transpose(struct1.m[propname], (2,1,0) )


def s3DS2soil3D(struct1, struct2, propname):
    return struct2.add_property(propname, np.transpose(getattr(struct1,propname), (2,1,0) ))

## Boucle jounaliere
for j in range(nb_jours):

    #remplissage des valeurs de propriete de l'interface a partir du contenu de l'ojet 3ds et et d'une liste de propriete dediees
    properties_3ds = ['asw_t', 'tsw_t', 'Corg', 'Norg', 'm_NO3', 'm_NH4', 'm_soil_vol', 'm_Tsol', 'm_DA', 'ftsw_t']
    # signification des properties:
    # asw_t : quantite d'eau libre pour plante dans le voxel au temps t (mm)
    # tsw_t : quantite d'eau totale dans le voxel au temps t (mm)
    # ftsw_t : fraction d'eau ranspirable = asw_t/tsw_t
    # m_soil_vol : volume des voxels (m3)
    # m_DA : densite apparente du sol par voxel (g.cm-3)
    # m_Tsol: Temperature sol (degreC - entree actuellement forcee par meteo)
    # Corg: (kg C dans le voxel)
    # Norg: (kg N dans le voxel)
    # m_NH4: (kg N NH4 dans le voxel)
    # m_NO3: (kg N NO3 dans le voxel)


    #mysoil.m
    mysoil.set_3ds_properties(S, properties_3ds)
    #mysoil.m

    # Simulation of the root system and update of soil property 'root_density'
    rootmodel.simulate(1)

    #lecure de root_density dans l'interface sol et construction du ls_root pour 3ds
    #resh = np.reshape(mysoil.m['root_density'], S.size)#reshape z,x,y pour 3ds
    #reshape remet pas les racines dans l'ordre que je veux!!!??
    ls_roots = [soil3D2s3DSprop(mysoil, S, 'root_density')]

    #step de water balance
    ls_transp, evapo_tot, ls_drainage, stateEV,  ls_m_transpi, m_evap, ls_ftsw = S.stepWBmc(Et0[j], ls_roots, [epsi[j]], Rain[j], Irrig[j], stateEV)

    s3DS2soil3D(S, mysoil, 'ftsw_t')#en fait pas necessaire car deja fait dans .set_3ds_properties au debut de boucle

    print(j, ls_ftsw[0]) #print de la fraction d'eau disponible percue par le systeme racinaire

    rootmodel.plot()










