import geopandas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import laspy
from shapely.geometry import box, Polygon, MultiPolygon, GeometryCollection
import uuid
import scipy.stats
import seaborn as sns

def katana(geometry, threshold, count=0):
    """Split a Polygon into two parts across it's shortest dimension"""

    bounds = geometry.bounds

    width = bounds[2] - bounds[0]

    height = bounds[3] - bounds[1]

    if max(width, height) <= threshold or count == 250:

        # either the polygon is smaller than the threshold, or the maximum

        # number of recursions has been reached

        return [geometry]

    if height >= width:

        # split left to right

        a = box(bounds[0], bounds[1], bounds[2], bounds[1] + height / 2)

        b = box(bounds[0], bounds[1] + height / 2, bounds[2], bounds[3])

    else:

        # split top to bottom

        a = box(bounds[0], bounds[1], bounds[0] + width / 2, bounds[3])

        b = box(bounds[0] + width / 2, bounds[1], bounds[2], bounds[3])

    result = []

    for d in (
        a,
        b,
    ):

        c = geometry.intersection(d)

        if not isinstance(c, GeometryCollection):

            c = [c]

        for e in c:

            if isinstance(e, (Polygon, MultiPolygon)):

                result.extend(katana(e, threshold, count + 1))

    if count > 0:
        return result

    # convert multipart into singlepart

    final_result = []

    for g in result:

        if isinstance(g, MultiPolygon):

            final_result.extend(g)

        else:

            final_result.append(g)

    return final_result

inventory_plot_location: geopandas.GeoDataFrame = geopandas.read_file(
    "C:/Users/joaov/Documents/UFMG/TCC/Dataset/DUC_A01_2016_PLOTLOCATION/duc_a01_2016_plotlocation.shx",
)

inventory: pd.DataFrame = pd.read_csv(
    "C:/Users/joaov/Documents/UFMG/TCC/Dataset/DUC_A01_2016_inventory.csv",
    encoding="ISO-8859-1",
)

geo_inventory_dataset: geopandas.GeoDataFrame = geopandas.GeoDataFrame(
    inventory,
    geometry=geopandas.points_from_xy(
        inventory["UTM.Easting"], inventory["UTM.Northing"]
    ),
    crs="EPSG:32720",
)

inventory_splits: geopandas.GeoDataFrame = inventory_plot_location.groupby(
    "plot_ID"
).apply(lambda dataframe: katana(dataframe.geometry.iloc[0], 50, 0))

inventory_splits = inventory_splits.explode()

inventory_plot_location: geopandas.GeoDataFrame = inventory_plot_location.join(
    inventory_splits.rename("splits"), on="plot_ID"
)

inventory_plot_location["uuid"] = [
    str(uuid.uuid4()) for _ in range(len(inventory_plot_location.index))
]