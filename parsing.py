import shapefile as sf

def read_areas(path):
    areas = {}
    with open(path) as fp:
        for line in fp:
            index, area = line.split('\t')
            index, area = int(index), float(area)
            areas[index] = area
    return areas

def read_population(path):
    pop = {}
    with open(path) as fp:
        for line in fp:
            parsed = list(map(int, line.split('\t')[:2]))
            i, n = parsed
            pop[i] = n
    return pop

def read_adj_list(path):
    adj_list = {}
    with open(path) as fp:
        for line in fp:
            parsed = list(map(int, line.split('\t')))
            hd, tl = parsed[0], parsed[1:]
            adj_list[hd] = tl
    return adj_list

def read_shapes(path):
    """ 
    Parses point information from a shapefile
    
    Parameters:
    path -- the base filename of the shapefile or
            the complete filename of any of the shapefile component files.
    
    
    Returns a mapping from precinct indices to a list of points
    describing that precinct
    
    The points are in the same order they were stored
    in the input shapefile
    """
    shapes = {}
    shapefile = sf.Reader(path)
    for index, shape in enumerate(shapefile.shapes()):
        shapes[index] = shape.points
    return shapes

def read_border_lengths(num_precincts, path):
    borders = [[float('inf') for _ in range(num_precincts)] for _ in range(num_precincts)]
    with open(path) as fp:
        for line in fp:
            precinct_from, precinct_to, border_length = line.split('\t')
            precinct_from, precinct_to, border_length = int(precinct_from), int(precinct_to), float(border_length)      
            borders[precinct_from][precinct_to] = border_length
    return borders

def read_perimeters(path):
    perimeters = {}
    with open(path) as fp:
        for line in fp:
            precinct_from, _, border_length = line.split('\t')
            precinct_from, border_length = int(precinct_from), float(border_length)
            perimeters[precinct_from] = perimeters.get(precinct_from, 0.0) + border_length
    return perimeters
