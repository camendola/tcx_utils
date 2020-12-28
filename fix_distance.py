import pandas as pd
import numpy as np
import modules.convert as convert
import matplotlib.pyplot as plt

def haversine(lat1, lon1, lat2, lon2):
    #from https://stackoverflow.com/a/40453439
    earth_radius = 6371000 # average in m
    lat1, lon1, lat2, lon2 = map(np.radians,[lat1,lon1,lat2,lon2])
    a = np.sin((lat2-lat1)/2.0)**2 + \
        np.cos(lat1) * np.cos(lat2) * np.sin((lon2-lon1)/2.0)**2
    
    return earth_radius * 2 * np.arcsin(np.sqrt(a))


log = convert.tcx_to_pd("../Downloads/36545800822.tcx") 	
df = log.dataframe.reset_index()

df['distance_per_second'] = \
    haversine(df["Position.Latitude"].shift(), df["Position.Longitude"].shift(),
                 df.loc[1:, "Position.Latitude"], df.loc[1:, "Position.Longitude"])

df['fixed_distance'] = df['distance_per_second'].cumsum()

#df[["DistanceMeters", "fixed_distance"]].plot()
#plt.show()
#input()

df = df.fillna(0)
df = df.reset_index().set_index(["Lap","Time"])
print (df)
log.dataframe["DistanceMeters"] = df["fixed_distance"]

log.update_tcx()
log.tcx.write(log.tcx_path.replace(".tcx", "_fixed.tcx"), pretty_print=True)
