#!/usr/bin/env python

import argparse
import rioxarray as rxr
import geopandas as gpd
from matplotlib import pyplot
from os import listdir
import re
import contextily as cx
from matplotlib.patches import Patch
from datetime import datetime, timedelta
from pathlib import Path
#import locale
#locale.setlocale(locale.LC_TIME, 'de_CH')

COLS = ['#d5fe7d', '#ffff54', '#f19e38', '#ea3423', '#75140c']
FILE_DIR = "//10.73.85.247/sam-prod/wald/archiv-fwi/sfms-current/"
INPUT_DIR = "G:/Wald/Ablage/BAY/ignis_maps/data/"
OUTPUT_DIR = "G:/Wald/Ablage/BAY/ignis_maps/output/"
ALPHA = 0.5


def main():
    parser = argparse.ArgumentParser(
        description="Script that generates beautiful FWI maps from CMD"
    )
    parser.add_argument("--startDate", required=True, type=str)
    parser.add_argument("--endDate", required=True, type=str)
    args = parser.parse_args()

    print('loading dependencies...')

    sdate = datetime.strptime(args.startDate, '%Y%m%d')
    edate = datetime.strptime(args.endDate, '%Y%m%d')

    dateArray = [(sdate + timedelta(days=i)).strftime('%Y%m%d') for i in range((edate - sdate).days + 1)]
    
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    files = listdir(FILE_DIR)

    print('generating maps... please wait...')

    limits = gpd.read_file(INPUT_DIR + 'limites_cantonales/swissBOUNDARIES3D_1_5_TLM_KANTONSGEBIET.shp', engine='pyogrio').to_crs(epsg=2056)
    waldbrand = gpd.read_file(INPUT_DIR + 'limites_waldbrand/gefahren-waldbrand_warnung_2056.geojson').to_crs(epsg=2056)

    for file in files:
        if not file.startswith('.') and file.endswith('.tif'):
            parts = re.findall(r'\D+|\d+', file)
            if parts[1] in dateArray:
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
                if parts[0] not in ['sdms', 'gfmc', 'ffmc', 'sdmc', 'bui', 'dmc', 'dc', 'isi', 'fwi', 'dsr']:
                    continue
                
                dataarray = rxr.open_rasterio(FILE_DIR + file).isel(band=0)
                dataarray = dataarray.where(dataarray != dataarray._FillValue)
                color_dict = {
                    '<= ' + str(levs[0]): COLS[0],
                    str(levs[0]) + ' - ' + str(levs[1]): COLS[1],
                    str(levs[1]) + ' - ' + str(levs[2]): COLS[2],
                    str(levs[2]) + ' - ' + str(levs[3]): COLS[3],
                    '> ' + str(levs[3]): COLS[4]
                    }
                
                fig, ax = pyplot.subplots(nrows=1, ncols=1, sharex=True, sharey=True, figsize=(14, 7), frameon=False)
                dataarray.plot(ax=ax, add_colorbar=False, levels=levs, colors=COLS, alpha=ALPHA)
                waldbrand.plot(ax=ax, facecolor="none", edgecolor="k", linewidth=.7)
                #cx.add_basemap(ax, crs=limits.crs.to_string(), source=cx.providers.SwissFederalGeoportal.NationalMapGrey)
                ax.set_title('')
                ax.annotate(parts[0].upper() + ' - ' + datetime.strptime(parts[1], '%Y%m%d').strftime('%a %d %b %Y'), xy=(.024, .965),
                            xycoords='axes fraction', verticalalignment='top', fontsize="x-large",
                            bbox={'facecolor':'white', 'edgecolor':'0.6', 'pad':10})
                ax.set_axis_off()
                custom_points = [Patch(edgecolor='k', facecolor=color, alpha=ALPHA) for color in color_dict.values()]
                leg_points = ax.legend(custom_points, color_dict.keys(), loc='upper left', bbox_to_anchor=(.0052, .92), fancybox = False)
                ax.add_artist(leg_points)
                fig.tight_layout()
                fig.savefig(OUTPUT_DIR + parts[0].upper() + parts[1] + '.png', dpi=100, bbox_inches='tight')
                pyplot.close(fig)


if __name__ == "__main__":
    main()
