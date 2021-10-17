import pandas as pd
from shapely.geometry import Point
import geopandas as gpd
from geopandas import GeoDataFrame

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

import datetime
import calendar

def plot_on_ny_map(df, points=10, figsize=(12, 12), markersize=20, save=False, title='NYC data', fname='plot.png',
                   cols=['startLongitude', 'startLatitude'], colored=False, color_col=None):
    data_x = df[cols[0]][:points]
    data_y = df[cols[1]][:points]

    ny = gpd.read_file(gpd.datasets.get_path('nybb'))
    geometry = [Point(x, y) for x, y in zip(data_x, data_y)]
    crs = 'EPSG:4326'

    gdf = GeoDataFrame(df[[cols[0], cols[1]]][:points], crs=crs, geometry=geometry)

    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_title(title)
    ny.to_crs(epsg=4326).plot(ax=ax, color='lightgrey', edgecolor='black')

    if colored:
        if color_col is None:
            raise Exception("color_col arg is missing, but colored is set to True.")
            return
        gdf.plot(ax=ax, c=df[color_col], markersize=markersize)
    else:
        gdf.plot(ax=ax, markersize=markersize)

    if save:
        plt.savefig(fname)
    else:
        plt.show()

def profit(ride, consider_date_time=False):
    '''Calculate the net profit from a single ride, which is a row of the dataset'''
    initial_charge = 2.5
    # $2.5 per mile
    mile_fare = ride['drivingDistance'] * 2.5
    # $0.5 per minute (drivingTime in seconds)
    minute_fare = ride['drivingTime'] / 60 * 0.5
    # rush hour or night surcharge
    surcharge = 0.0
    if consider_date_time:
        weekend = ride['day'] == 'Saturday' | ride['day'] == 'Sunday'
        hour = ride['hour']
        if (not weekend & hour >= 16 & hour < 20):
            surcharge = 1.0
        if (hour >= 20 & hour <= 6):
            surcharge = 0.5
    return initial_charge + surcharge + np.maximum(mile_fare, minute_fare)


def filter_by_weekday_hour(df, year, month, day, hour):
    '''Return the rides on the same weekday at the same hour'''
    dayName = datetime.datetime(year, month, day).strftime('%A')
    return df.loc[(df['dayName'] == dayName) & (df['hour'] == hour)]



def predict_for_weekday_hour(year, month, day, hour):
    '''Main function for the K-Means predictor'''
    df = pd.read_csv('data/taxi_data_profits.csv')
    pd.set_option('max_columns', None)

    df = filter_by_weekday_hour(df, year, month, day, hour)
    # clean out NaN values
    df = df[df['startLatitude'].notna()]
    df = df[df['startLongitude'].notna()]
    X = df[['startLatitude', 'startLongitude']][:20000]
    print('Analyzing', len(X.index), 'rides...')

    # Find clusters with KMeans
    kmeans = KMeans(n_clusters=int(len(X.index) / 100)).fit(X)  # at least 500 rides per cluster
    labels = pd.DataFrame(kmeans.labels_, columns=['label'])
    clusters = X.join(labels)
    df_with_clusters = df.join(labels)

    # Aggregate hotspots locations and predicted profits (from each cluster)
    hotspots = pd.DataFrame({})
    df_with_clusters['profit'] = profit(df_with_clusters)

    for i in np.unique(df_with_clusters['label']):
        cluster = df_with_clusters[df_with_clusters['label'] == i]
        hotspot = cluster.mean(axis=0)
        hotspots = hotspots.append(hotspot, ignore_index=True)
    hotspots = hotspots.dropna(subset=['label'])
    hotspots = hotspots.loc[hotspots['profit'] > 2.5]  # filter out hotspots with profit = flat rate
    # print(hotspots['profit'])

    return hotspots, clusters

# hotspots, clusters = predict_for_weekday_hour(2016,10,17,18)
# print(len(hotspots.index), len(clusters.index))
# print(hotspots.head())
# plot_on_ny_map(hotspots, points=20000, colored=True, color_col='profit', markersize=30)
# plot_on_ny_map(clusters, points=20000, colored=False, color_col='label', markersize=10)