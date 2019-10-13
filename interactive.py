from pgraph import PGraph
from path_generator import get_paths
from drawing import *

county_name = 'Cumberland'
G = PGraph.from_data(*get_paths(county_name))

def handler(G, ax):
    partition_color = 'purple'
    def onclick(event):
        if event.key == 'd':
            active_precincts = filter(G.nodes.keys, 
                                 lambda ind: G.nodes[ind]['color'] == partition_color)
            d_votes, r_votes = PGraph.calculate_votes(G, active_precincts)
            if d_votes < r_votes:
                print("Republicans won this partition")
            else:
                print("Democrats won this partition")
            eg = PGraph.calculate_efficiency_gap(G, active_precincts)
            print("The efficiency gap was:", eg)
            iq = PGraph.calculate_isoperimetric_quotient(G, active_precincts)
            print("The isoperimetric quotient was:", iq)
        else:
            x, y = event.xdata, event.ydata
            index = PGraph.node_containing(G, (x, y))
            if index == -1:
                print("Out of bounds")
                return
            current_color = G.nodes[index]['color']
            next_color = { 'white' : 'purple',
                           'purple' : 'white',
                         }[current_color]
            print("Coloring", index, next_color)
            color_subset(G, [index], ax, next_color)
            print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
                  ('double' if event.dblclick else 'single', event.button,
                   event.x, event.y, event.xdata, event.ydata))
    return onclick

fig, ax = get_fig_axes(G, (8, 8))
fig.canvas.mpl_connect('button_press_event', handler(G, ax))

while True:
    fig.canvas.draw()
    fig.canvas.flush_events()
