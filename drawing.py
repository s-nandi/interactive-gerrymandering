import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pgraph import PGraph
from networkx import draw_spectral
from itertools import cycle
from voting_reader import Party


def get_fig_axes(pgraph, figsize = (8, 8)):
    """ Draws precinct boundaries and returns the created fig/axes """
    fig, ax = plt.subplots(figsize = figsize)
    for index in pgraph:
        face = pgraph.nodes[index]['points']
        polygon = face + [face[0]]
        x, y = zip(*polygon)
        ax.plot(x, y, color = 'black')
    return fig, ax


def get_axes(pgraph, figsize = (8, 8)):
    _, ax = get_fig_axes(pgraph, figsize)
    return ax

def show():
    plt.show()

def draw_connectivity(pgraph):
    draw_spectral(pgraph)
    plt.show()
    
def color_subset(pgraph,
                 subset,
                 ax,
                 color = 'blue',
                 alpha = 1.0):
    """ 
    Draws the given precinct graph and fills in subset of precincts provided
    
    Parameters:
    subset -- iterable of indices that indicate the subset of precincts chosen
    """
    for index in subset:
        face = pgraph.nodes[index]['points']
        polygon = face + [face[0]]
        x, y = zip(*polygon)
        ax.fill(x, y, color = color, alpha = alpha)
        pgraph.nodes[index]['color'] = color

def color_subsets(pgraph,
                  subsets,
                  ax,
                  colors = ['blue'],
                  alpha = 1.0):
    """ 
    Draws the given precinct graph and fills in subset of precincts provided
    
    Parameters:
    subsets -- iterable of iterable of indices that indicate the subsets of precincts chosen
    colors - list of colors that will be cycled through when coloring each subset
    """
    for subset, color in zip(subsets, cycle(colors)):
        color_subset(pgraph, subset, ax, color, alpha)
        
def color_by_votes(pgraph, ax):
    colors = {Party.dem : 'blue', Party.rep : 'red'}
    for index in pgraph.nodes:
        votes = pgraph.nodes[index]['tallied_votes']
        color = colors[Party.dem] if votes[Party.dem] > votes[Party.rep] else colors[Party.rep]
        winning_votes = max(votes[Party.dem], votes[Party.rep])
        losing_votes = min(votes[Party.dem], votes[Party.rep])
        winning_proportion = (winning_votes) / (winning_votes + losing_votes)
        color_subset(pgraph, [index], ax, color, alpha = winning_proportion)
        
def draw_convex_hull(pgraph, subset, ax, color = 'green', width = 5.0):
    hull = PGraph.calculate_subset_convex_hull(pgraph, subset)
    hull = hull + [hull[0]]
    x, y = zip(*hull)
    ax.plot(x, y, color = color, linewidth = width)    
    
def draw_enclosing_circle(pgraph, subset, ax, color = 'purple', width = 5.0):
    center, radius = PGraph.calculate_subset_circumcircle(pgraph, subset)
    circle = mpatches.Circle(center, radius, linewidth = width, fill = False, color = color)
    ax.add_artist(circle)
