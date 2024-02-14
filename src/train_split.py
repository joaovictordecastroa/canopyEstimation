import geopandas
from shapely.geometry import Point, Polygon


class TrainSplit:
    @staticmethod
    def _get_records_in_plot_location(lidar_data: geopandas.GeoDataFrame, plot_location: geopandas.GeoDataFrame) -> any:
        # return plot_location.contains(lidar_data)
        print(plot_location.items())
        return lidar_data.assign(**{key: lidar_data.within(geom) for key, geom in plot_location.items()})
