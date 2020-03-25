import openalea.mtg as mtg
import openalea.plantgl.all as pgl
from openalea.mtg import turtle as turt
from openalea.mtg.plantframe import color
from .root_mtg import plot


# scene=plot(g)
# Viewer.display(scene)

#liste des parametres
init1 = 100
init2 = 30

#creation de la struture MTG initiale
#
g = mtg.MTG()

#noeud principal de la plante avec pool de concentration
root =  g.add_component(g.root, label ='systracinaire')
nid = g.node(root)
nid.C1 = init1
nid.radius = 0.02

#rajout de l'apex connecte au root
apex = g.add_child(root, label='A',edge_type='<')
nid_apex = g.node(apex)
nid_apex.C2 = init2
nid_apex.radius = 0.01
nid_apex.length = 2
nid_apex.cumulatedlength = 2
nid_apex.thr = 0.02

STEPS = 30
dt = 1
kv = 20
kz = 15
sgl = 20 # segment_length
ibd = 50
hierc = 0.75
rir =0.9*0.001


for tps in range(STEPS):
    for vtx in g.VtxList():
        if g.label(vtx)=='A':
            nid_apex = g.node(vtx)
            #vitesse d'allongement segment
            if nid_apex.radius<nid_apex.thr:
                nid_apex.radius += rir*nid_apex.C2
            else:
                v = (nid_apex.radius*2)*nid_apex.C2*kv*1/kz #kv constante de vitesse
                dl = v*dt
                nid_apex.length += dl
                nid_apex.cumulatedlength += dl

                print(tps,nid_apex.length)

                if nid_apex.length > sgl:
                    nid_apex.label='S'
                    nid_s1 = nid_apex
                    _length = nid_apex.length
                    _cl = nid_apex.cumulatedlength
                    nid_s1.length = sgl
                    nid_apex = nid_s1.add_child(label='A', edge_type='<')

                    nid_apex.length = _length - sgl

                    nid_apex.C2 = init2
                    nid_apex.radius = nid_s1.radius
                    nid_apex.length = 2
                    nid_apex.cumulatedlength = _cl
                    nid_apex.thr = nid_s1.thr


                    if nid_apex.cumulatedlength > ibd:
                        nid_apexB = nid_s1.add_child(label='A', edge_type='+')
                        nid_apexB.C2 = nid_apex.C2
                        nid_apexB.radius = 0.
                        nid_apexB.length = 0.
                        nid_apexB.cumulatedlength = 2
                        nid_apexB.thr = nid_apex.radius*hierc



