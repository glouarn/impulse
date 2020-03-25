from openalea.mtg import *
from openalea.mtg import algo

from openalea.mtg import turtle as turt
from openalea.mtg.plantframe import color
import openalea.plantgl.all as pgl


"""
apex:
- radius
- hexose
- length
"""

def apex_init(apex):
    nid = apex
    nid.length = 0.
    nid.radius = 0.1
    nid.hexose = 0.
    nid.dist_to_ramif = 0.
    nid.time_burst = 0.
    nid.order = 0
    nid.radius_max = 0.1

# Parameters
LengthSegment = 1.
DistanceRamif = 2
Delay = 3

def apex_development(apex, dt, dl, sugar):

    new_apex = []
    apex.dist_to_ramif += dl

    if apex.time_burst > 0:
        apex.time_burst -= dt
        new_apex.append(apex)
        return new_apex

    if apex.dist_to_ramif >= DistanceRamif:
        ramif = apex.add_child(edge_type='+', label='Apex',
                             length=0.,
                             radius = apex.radius*0.7,
                             time_burst=Delay,
                             dist_to_ramif = 0.,
                             order=apex.order+1)
        new_apex.append(ramif)
        apex.dist_to_ramif = 0.
    else:
        apex.dist_to_ramif += dl

    if apex.length < LengthSegment+dl:
        apex.length += dl
    else:
        length = apex.length
        apex.length = LengthSegment
        apex.label = 'Segment'

        apex = apex.add_child(edge_type='<', label='Apex',
                             length=length+dl-LengthSegment,
                             radius = apex.radius,
                             time_burst=0.,
                             dist_to_ramif = apex.dist_to_ramif,
                             order = apex.order)
    new_apex.append(apex)
    return new_apex


def mtg_root(radius = 0.1):
    g = MTG()
    root = g.add_component(g.root, label='Apex')
    nid = g.node(root)
    apex_init(nid)
    return g


class Simulate(object):

    def __init__(self, g):
        """ Simulate on MTG. """
        self.g = g
        self._apex = [g.node(v) for v in g.vertices_iter(scale=1) if g.label(v)=='Apex']


    def step(self, dt=1., dl = 0.1):
        g = self.g
        apices = list(self._apex)
        self._apex = []
        sugar = 0.5
        for apex in apices:
            new_apices = apex_development(apex, dt=dt, dl=dl, sugar=sugar)
            self._apex.extend(new_apices)


def get_root_visitor():
    def root_visitor(g, v, turtle):
        angles = [90,45]+[30]*20

        rad = g.property('radius')
        n = g.node(v)
        radius = rad.get(v,0.01)
        order = g.order(v)
        length = 1.

        if g.edge_type(v) == '+':
            angle = angles[order]
            turtle.down(angle)

        turtle.setId(v)
        turtle.setWidth(radius)
        for c in n.children():
            if c.edge_type() == '+':
                turtle.rollL(130)

        turtle.F(length)

        # define the color property
        #n.color = random.random()
    return root_visitor

def plot(g, prop_cmap='radius', cmap='jet', lognorm=False):
    """
    Exemple:

        >>> from openalea.plantgl.all import *
        >>> s = plot()
        >>> shapes = dict( (x.getId(), x.geometry) for x in s)
        >>> Viewer.display(s)
    """
    visitor = get_root_visitor()

    turtle = turt.PglTurtle()
    turtle.down(180)
    scene = turt.TurtleFrame(g, visitor=visitor, turtle=turtle, gc=False)

    # Compute color from radius
    color.colormap(g,prop_cmap, cmap=cmap, lognorm=lognorm)

    shapes = dict((sh.getId(),sh) for sh in scene)

    colors = g.property('color')
    for vid in colors:
        if vid in shapes:
            shapes[vid].appearance = pgl.Material(colors[vid])
    scene = pgl.Scene(list(shapes.values()))
    return scene


