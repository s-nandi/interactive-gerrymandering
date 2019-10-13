from nayuki_minimum_enclosing_circle import make_circle
from shapely.geometry import Polygon, MultiPoint
from shapely.geometry.polygon import orient
from math import pi

def make_oriented(polygon):
    oriented_boundary = orient(Polygon(polygon)).exterior
    return list(oriented_boundary.coords)

def perimeter_area(polygon):
    poly = Polygon(polygon)
    return poly.length, poly.area

def convex_hull(points):
    ch = MultiPoint(points).convex_hull
    return list(ch.exterior.coords)

def convex_hull_perimeter_area(points):
    ch = MultiPoint(points).convex_hull
    return ch.length, ch.area

def circumcircle_center_radius(points):
    x, y, radius = make_circle(points)
    return (x, y), radius