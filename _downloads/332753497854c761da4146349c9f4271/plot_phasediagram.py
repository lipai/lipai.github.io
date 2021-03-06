# coding: utf-8
"""

plot phase diagram and 
==============================

This is just a test
"""
# In[ ]:

from pymatgen import MPRester, Composition, Element
from pymatgen.io.vasp.outputs import Vasprun
from pymatgen.entries.compatibility import MaterialsProjectCompatibility
from pymatgen.phasediagram.maker import PhaseDiagram
from pymatgen.phasediagram.analyzer import PDAnalyzer
from pymatgen.phasediagram.plotter import PDPlotter
from pymatgen.util.plotting_utils import get_publication_quality_plot
import json
import re
import palettable
import matplotlib as mpl

v = Vasprun("./vasprun.xml")
#entry = v.get_computed_entry(inc_structure=True)
entry = v.get_computed_entry()

m = MPRester("g8u7XE1HNSpaI2c3")
entries = m.get_entries_in_chemsys(["Li", "O","Br"]) # pass in a list of elements in your material

#compatibility = MaterialsProjectCompatibility()
#entry = compatibility.process_entry(entry)
#allentries = compatibility.process_entries([entry] + entries)
#comp = MaterialsProjectCompatibility()
#entry = comp.process_entry(entry)
#all_entries = comp.process_entries(entries + [entry])
#allentries = entries
allentries = [entry] + entries

pd = PhaseDiagram(allentries)
#plotter = PDPlotter(pd,)
plotter = PDPlotter(pd,show_unstable=True)

plotter.write_image("Figure_2.svg", image_format="svg", label_stable=True,
                    label_unstable=True, ordering=None,
                    energy_colormap=None, process_attributes=False)

#plotter.show()
# I suppose you need the energy above hull for your material
pda = PDAnalyzer(pd)
print "Energy above hull is %.2f eV/atom" % pda.get_e_above_hull(entry)
analyzer = PDAnalyzer(pd)
ehull = analyzer.get_e_above_hull(entry)
print("The energy above hull of * is %.3f eV/atom." % ehull)

li_entries = [e for e in allentries if e.composition.reduced_formula == "Li"]
uli0 = min(li_entries, key=lambda e: e.energy_per_atom).energy_per_atom

el_profile = analyzer.get_element_profile(Element("Li"), entry.composition)
for i, d in enumerate(el_profile):
    voltage = -(d["chempot"] - uli0)
    print("Voltage: %s V" % voltage)
    print(d["reaction"])
    print("")
    
# plot 
# Some matplotlib settings to improve the look of the plot.
mpl.rcParams['axes.linewidth']=3
mpl.rcParams['lines.markeredgewidth']=4
mpl.rcParams['lines.linewidth']=3
mpl.rcParams['lines.markersize']=15
mpl.rcParams['xtick.major.width']=3
mpl.rcParams['xtick.major.size']=8
mpl.rcParams['xtick.minor.width']=3
mpl.rcParams['xtick.minor.size']=4
mpl.rcParams['ytick.major.width']=3
mpl.rcParams['ytick.major.size']=8
mpl.rcParams['ytick.minor.width']=3
mpl.rcParams['ytick.minor.size']=4

# Plot of Li uptake per formula unit (f.u.) of Li6PS5Cl against voltage vs Li/Li+.
colors = palettable.colorbrewer.qualitative.Set1_9.mpl_colors
plt = get_publication_quality_plot(14, 8)

for i, d in enumerate(el_profile):
    v = - (d["chempot"] - uli0)
    if i != 0:
        plt.plot([x2, x2], [y1, 100*d["evolution"]/32 ], 'k', linewidth=3)
    x1 = v
    y1 =100* d["evolution"] /32
    if i != len(el_profile) - 1:
        x2 = - (el_profile[i + 1]["chempot"] - uli0)
    else:
        x2 = 5.0
        
    if i in [0, 4, 5, 7]:
        products = [re.sub(r"(\d+)", r"$_{\1}$", p.reduced_formula)                     
                    for p in d["reaction"].products if p.reduced_formula != "Li"]

        plt.annotate(", ".join(products), xy=(v + 0.5, y1 + 7), 
                     fontsize=30, color=colors[0])
        
        plt.plot([x1, x2], [y1, y1], color=colors[0], linewidth=5)
    else:
        plt.plot([x1, x2], [y1, y1], 'k', linewidth=3)  
plt.xlim((0, 4.0))
plt.ylim((-100,40))
plt.xlabel("Voltage vs Li/Li$^+$ (V)")
plt.ylabel("Li uptake (%)")
plt.gca().get_xaxis().set_tick_params(direction='out')
plt.gca().get_yaxis().set_tick_params(direction='out')
plt.gca().xaxis.set_ticks_position('bottom')
plt.gca().yaxis.set_ticks_position('left')
plt.tight_layout()
#plt.savefig('Figure_V.png')
plt.show()
