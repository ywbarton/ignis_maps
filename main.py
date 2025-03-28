import rioxarray as rxr
import geopandas as gpd
from matplotlib import pyplot
from os import listdir
import re
import numpy as np
import contextily as cx
from matplotlib.patches import Patch
from datetime import datetime
import locale
locale.setlocale(locale.LC_TIME, 'de_CH')

files = listdir('data/input/')
size = str(len(files))
init = 0
a = 0.5

for file in files:
    if not file.startswith('.'):
        init = init + 1
        print(str(init) + '/' + size)
        parts = re.findall(r'\D+|\d+', file)
        cols = ['#d5fe7d', '#ffff54', '#f19e38', '#ea3423', '#75140c']
        if parts[0] == 'sdmc':
            levs = [32, 50, 65, 93]
        if parts[0] == 'gfmc':
            levs = [75, 81, 87, 92]
        if parts[0] == 'ffmc':
            levs = [80, 85, 90, 92]
        if parts[0] == 'sdmc':
            levs = [32, 50, 65, 93]
        if parts[0] == 'bui':
            levs = [20, 30, 40, 60]
        if parts[0] == 'dmc':
            levs = [20, 30, 40, 60]
        if parts[0] == 'dc':
            levs = [200, 300, 500, 600]
        if parts[0] == 'isi':
            levs = [5, 10, 20, 30]
        if parts[0] == 'fwi':
            levs = [5, 20, 30, 40]
        if parts[0] == 'dsr':
            levs = [.47, 5.46, 11.2, 18.63]
        if parts[0] == 'bui_trend':
            continue
        if parts[0] == 'ffmc_trend':
            continue
        if parts[0] == 'fwi_trend':
            continue
        
        dataarray = rxr.open_rasterio('data/input/' + file).isel(band=0)
        limits = gpd.read_file('data/limites_cantonales/swissBOUNDARIES3D_1_5_TLM_KANTONSGEBIET.shp').to_crs(epsg=2056)
        dataarray = dataarray.where(dataarray != dataarray._FillValue)
        waldbrand = gpd.read_file('data/limites_waldbrand/gefahren-waldbrand_warnung_2056.geojson').to_crs(epsg=2056)

        color_dict = {
            '<= ' + str(levs[0]): cols[0],
            str(levs[0]) + ' - ' + str(levs[1]): cols[1],
            str(levs[1]) + ' - ' + str(levs[2]): cols[2],
            str(levs[2]) + ' - ' + str(levs[3]): cols[3],
            '> ' + str(levs[3]): cols[4]
            }

        fig, ax = pyplot.subplots(nrows=1, ncols=1, sharex=True, sharey=True, figsize=(14, 7), frameon=False)
        dataarray.plot(ax=ax, add_colorbar=False, levels=levs, colors=cols, alpha=a)
        waldbrand.plot(ax=ax, facecolor="none", edgecolor="k", linewidth=.7)
        cx.add_basemap(ax, crs=limits.crs.to_string(), source=cx.providers.SwissFederalGeoportal.NationalMapGrey)
        ax.set_title('')
        ax.annotate(parts[0].upper() + ' - ' + datetime.strptime(parts[1], '%Y%m%d').strftime('%a %d %b %Y'), xy=(.024, .965),
                    xycoords='axes fraction', verticalalignment='top', fontsize="x-large",
                    bbox={'facecolor':'white', 'edgecolor':'0.6', 'pad':10})
        ax.set_axis_off()
        custom_points = [Patch(edgecolor='k', facecolor=color, alpha=a) for color in color_dict.values()]
        leg_points = ax.legend(custom_points, color_dict.keys(), loc='upper left', bbox_to_anchor=(.0052, .92), fancybox = False)
        ax.add_artist(leg_points)
        fig.tight_layout()
        fig.savefig('output/' + parts[0].upper() + parts[1] + '.png', dpi=100, bbox_inches='tight')
        pyplot.close(fig)