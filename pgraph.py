from geometry import make_oriented, \
                     perimeter_area, \
                     convex_hull, \
                     convex_hull_perimeter_area, \
                     circumcircle_center_radius
from math import pi, isclose, sqrt
from networkx import Graph
from os.path import join
from parsing import read_population, \
                    read_shapes, \
                    read_adj_list, \
                    read_border_lengths, \
                    read_areas, \
                    read_perimeters
from typing import NamedTuple
from voting_reader import read_votes, read_precinct_prefixes, calculate_votes, total_votes, wasted_votes, Party

def construct_graph(path, weights = []):
    """reads the adjacency list and construct the base graph"""
    G = Graph()
    adj_list = read_adj_list(path)
    G.add_nodes_from(set(adj_list.keys()) - set([-1]))
    for n in G.nodes:
        G.nodes[n]['boundary'] = False
    for n, adj in adj_list.items():
        if n == -1:
            continue
        for v in adj:
            if v == -1:
                G.nodes[n]['boundary'] = True
                continue
            G.add_edge(n, v, border_length = weights[n][v])
    return G

class subset_data(NamedTuple):
        area : float = 0.0
        perimeter : float = 0.0
        convex_hull_area : float = 0.0
        convex_hull_perimeter : float = 0.0
        circumcircle_area : float = 0.0
        circumcircle_circumference : float = 0.0
        area_of_circle_with_same_perimeter : float = 0.0
        perimeter_of_circle_with_same_area : float = 0.0

class PGraph(Graph):
    @staticmethod
    def from_data(precinct_name, precinct_folder, data_path, shape_path, election_path, debug = False):
        area_path = join(data_path, "%s_AREAS.txt" % precinct_folder)
        neighbors_path = join(data_path, "%s_NEIGHBORS.txt" % precinct_folder)
        pop_path = join(data_path, "%s_POPULATION.txt" % precinct_folder)
        border_path = join(data_path, "%s_BORDERLENGTHS.txt" % precinct_folder)
        area_path = join(data_path, "%s_AREAS.txt" % precinct_folder)
        
        shapes = read_shapes(shape_path)
        num_precincts = len(shapes)
        
        border_perimeters = read_border_lengths(num_precincts, border_path)
        G = construct_graph(neighbors_path, border_perimeters)
        
        pops = read_population(pop_path)
        areas = read_areas(area_path)
        perimeters = read_perimeters(border_path)
        for index in range(num_precincts):
            G.nodes[index]['population'] = pops[index]
            G.nodes[index]['area'] = areas[index]
            G.nodes[index]['perimeter'] = perimeters[index]
            
        voting_data = read_votes(election_path, precinct_name)
        voting_prefixes = read_precinct_prefixes(shape_path)
        for index in G.nodes:
            G.nodes[index]['voting'] = voting_data[voting_prefixes[index]]
            G.nodes[index]['tallied_votes'] = calculate_votes(G.nodes[index]['voting'])
            G.nodes[index]['total_votes'] = total_votes(G.nodes[index]['tallied_votes']) 
            G.nodes[index]['wasted_votes'] = wasted_votes(G.nodes[index]['tallied_votes']) 
        for index, points in shapes.items():
            oriented = make_oriented(points)
            G.nodes[index]['points'] = oriented
            
            ch_perimeter, ch_area = convex_hull_perimeter_area(points)
            G.nodes[index]['ch_perimeter'] = ch_perimeter
            G.nodes[index]['ch_area'] = ch_area
            
            center, radius = circumcircle_center_radius(points)
            G.nodes[index]['enclosing_circle_circumference'] = 2 * pi * radius
            G.nodes[index]['enclosing_circle_area'] = pi * radius * radius
            G.nodes[index]['enclosing_circle_center'] = center
            
            if debug:
                assert(len(oriented) == len(points))
                assert(isclose(perimeter_area(oriented)[0], perimeter_area(points)[0]))
                assert(isclose(perimeter_area(oriented)[1], perimeter_area(points)[1]))
                assert(isclose(circumcircle_center_radius(oriented)[0][0], circumcircle_center_radius(points)[0][0]))
                assert(isclose(circumcircle_center_radius(oriented)[0][1], circumcircle_center_radius(points)[0][1]))
                assert(isclose(circumcircle_center_radius(oriented)[1], circumcircle_center_radius(points)[1]))
        return G
    
    @staticmethod
    def _calculate_subset_perimeter(G, 
                                    subset_indices, 
                                    is_neighbor = None):
        if not is_neighbor:
            is_neighbor = lambda i, j: i in G.neighbors(j)
        perimeter = 0.0
        for index in subset_indices:
            perimeter += G.nodes[index]['perimeter']
        for index in subset_indices:
            for index2 in subset_indices:
                if index != index2 and is_neighbor(index, index2):
                    perimeter -= G[index][index2]['border_length']
        return perimeter
    
    @staticmethod
    def _calculate_subset_area(G, subset_indices):
        area = 0.0
        for index in subset_indices:
            area += G.nodes[index]['area']
        return area
    
    @staticmethod
    def _calculate_subset_point_set(G, subset_indices):
        point_set = []
        for index in subset_indices:
            point_set.extend(G.nodes[index]['points'])
        return point_set
    
    @staticmethod
    def _calculate_subset_convex_hull_and_enclosing_circle(G, subset_indices):
        points = PGraph._calculate_subset_point_set(G, subset_indices)
        ch_perimeter, ch_area = convex_hull_perimeter_area(points)
        _, circumcircle_radius = circumcircle_center_radius(points)
        circumcircle_area = pi * circumcircle_radius * circumcircle_radius
        circumcircle_circumference = 2 * pi * circumcircle_radius
        return ch_area, ch_perimeter, circumcircle_area, circumcircle_circumference
        
    @staticmethod
    def _calculate_area_of_circle_with_same_perimeter(perimeter):
        radius = perimeter / 2 * pi
        return pi * radius * radius
    
    @staticmethod
    def _calculate_perimeter_of_circle_with_same_area(area):
        radius = sqrt(area / pi)
        return 2 * pi * radius
    
    @staticmethod
    def calculate_subset_data(G, subset_indices):  
        area = PGraph._calculate_subset_area(G, subset_indices)
        perimeter = PGraph._calculate_subset_perimeter(G, subset_indices)
        ch_perimeter, ch_area, circumcircle_circumference, circumcircle_area = \
            PGraph._calculate_subset_convex_hull_and_enclosing_circle(G, subset_indices)
        area_of_circle_with_same_perimeter = \
            PGraph._calculate_area_of_circle_with_same_perimeter(perimeter)
        perimeter_of_circle_with_same_area = \
            PGraph._calculate_perimeter_of_circle_with_same_area(area)
        
        data = subset_data(perimeter = perimeter,
                           area = area,
                           convex_hull_area = ch_area,
                           convex_hull_perimeter = ch_perimeter,
                           circumcircle_area = circumcircle_area,
                           circumcircle_circumference = circumcircle_circumference,
                           area_of_circle_with_same_perimeter = area_of_circle_with_same_perimeter,
                           perimeter_of_circle_with_same_area = perimeter_of_circle_with_same_area)
        return data
    
    @staticmethod
    def calculate_subset_circumcircle(G, subset_indices):
        points = PGraph._calculate_subset_point_set(G, subset_indices)
        center, radius = circumcircle_center_radius(points)
        return center, radius
    
    @staticmethod
    def calculate_subset_convex_hull(G, subset_indices):
        points = PGraph._calculate_subset_point_set(G, subset_indices)
        ch = convex_hull(points)
        return ch
    
    @staticmethod
    def calculate_efficiency_gap(G, subset_indices):
        wasted = dict()
        total = 0
        for index in subset_indices:
            for party, votes in G.nodes[index]['wasted_votes'].items():
                wasted[party] = wasted.get(party, 0) + votes
                total += votes
        return abs(wasted[Party.dem] - wasted[Party.rep]) / total
    
    @staticmethod
    def calculate_isoperimetric_quotient(G, subset_indices):
        data = PGraph.calculate_subset_data(G, subset_indices)
        return data.area / data.area_of_circle_with_same_perimeter
        
        
        
            