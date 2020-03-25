import openalea.plantgl.all  as pgl
import numpy as np
import random


class Grid3D(pgl.Grid3Indexing):
    def __init__(self, voxelsize = (1,1,1), origin = (0,0,0), upper = (10,10,10), default_value = 0):
        self.origin = origin
        self.voxelsize = voxelsize
        self.upper = upper
        pgl.Grid3Indexing.__init__(self, voxelsize, origin, upper)
        self.init_value()
        
    def init_value(self):
        self.values = np.ones(self.size()) * default_value

    def getValueAt(self, pos):
        cid = self.cellIdFromPoint(pos)
        return (self.hvalues[cid],self.vvalues[cid])

    def setValueAt(self, pos, value):
        self.values[self.cellIdFromPoint(pos)] = value

    def __contains__(self,pos):
        return pgl.BoundingBox(self.getLowerCorner(),self.getUpperCorner()-(1e-5,1e-5,1e-5)).contains(pos)
    
    def get27Neighbors(self,idx):
        import itertools
        result = []
        for i,j,k in itertools.product((-1,0,1),(-1,0,1),(-1,0,1)):
           nidx = (idx[0]+i,idx[1]+j,idx[2]+k)
           if i == j == k == 0 : continue
           for i,v in enumerate(nidx):
             if v < 0 or v >= self.getGridSize()[i]:
               continue
           result.append(nidx)
        return result
    
    def __getitem__(self,cid):
        return self.values[cid]

class AniResistanceGrid(Grid3D):
    def __init__(self, voxelsize = (1,1,1), origin = (0,0,0), upper = (10,10,10), layer = 300):
        self.layer = layer
        Grid3D.__init__(self, voxelsize , origin , upper )
        self.maxvalue = 0.5
    
    def init_value(self):
        # 300 mm uniform 0 - 0.2
        # en dessous uniform V : 0. - 0.2 ; H : 0.3 - 0.5
        print('init')
        self.vvalues = np.ones(self.size())* 0.2 #np.random.uniform(0,0.2,self.size())
        self.hvalues = np.ones(0.5,self.size())
        # self.hvalues = np.random.uniform(0.3,0.5,self.size())
        import itertools as it
        deb = [self.origin[i]+self.voxelsize[i]/2. for i in range(3)]
        deb[2] = -self.layer+self.voxelsize[i]/2.
        print(deb)
        print(self.upper)
        for vx,vy,vz in it.product(*[np.arange(deb[i],self.upper[i],self.voxelsize[i]) for i in range(3)]):
            ncid = self.cellIdFromPoint([vx,vy,vz])
            self.hvalues[ncid] = random.uniform(0.,0.2)
       
    def representation(self):
       mat = pgl.Material('mblue',(0,0,200),transparency=0.8)
       mat2 = pgl.Material('mred',(200,0,0),transparency=0.8)
       if not self.maxvalue: self.maxvalue = max(self.values)
       if self.maxvalue <= 0: return pgl.Scene()
       sc = pgl.Scene()
       for i, v in enumerate(self.hvalues):
           size = 0.1
           sc += pgl.Shape(pgl.Translated(self.getVoxelCenterFromId(i),pgl.Box(self.getVoxelSize()*size)),mat.interpolate(mat2,v/self.maxvalue),i)
       return sc

def nbgs(idx):
    ref = list(idx)
    res = []
    dim = grid.dimensions()
    for d in range(3):
      if ref[d] > 0 : 
        lres = list(ref)
        lres[d] -= 1
        res.append(lres)
      if ref[d] < dim[d]-1 : 
        lres = list(ref)
        lres[d] += 1
        res.append(lres)
    return res
