
import pandas as pd
import numpy as np
from lxml import objectify

class tcx_to_pd:
    def __init__(self, path):
        self.tcx_path  = path
        self.tcx       = self.set_tcx()
        self.activity  = self.tcx.getroot().Activities.Activity
        self.dataframe = self.set_dataframe()

    def set_tcx(self):
        tcx = objectify.parse(open(self.tcx_path))
        return tcx

    def set_dataframe(self):
        data = []
        for lap in self.activity.Lap:
            lap_start = pd.Timestamp(lap.items()[0][1])
            for track in lap.Track:
                for trackpoint in track.Trackpoint:
                    time      = pd.Timestamp(str(trackpoint.Time))
                    latitude  = np.float(trackpoint.Position.LatitudeDegrees)
                    longitude = np.float(trackpoint.Position.LongitudeDegrees)
                    altitude  = np.float(trackpoint.AltitudeMeters)
                    distance  = np.float(trackpoint.DistanceMeters)
                    hr        = np.int(trackpoint.HeartRateBpm.Value)
                    data.append({"Lap" :               lap_start,
                                 "Time":               time,
                                 "Position.Latitude" : latitude,
                                 "Position.Longitude": longitude,
                                 "AltitudeMeters":     altitude,
                                 "DistanceMeters":     distance,
     			         "HeartRateBpm.Value": hr})
        df = pd.DataFrame(data).set_index(["Lap", "Time"])
        df["HeartRateBpm.Value"] = df["HeartRateBpm.Value"].astype(int)
        return df

    def update_tcx(self):
        for lap in self.activity.Lap:
            lap_start = pd.Timestamp(lap.items()[0][1])
            lap.DistanceMeters._setText(str(self.dataframe.reset_index().set_index("Lap").loc[lap_start].DistanceMeters.values[-1]))
            for track in lap.Track:
                for trackpoint in track.Trackpoint:
                    time      = pd.Timestamp(str(trackpoint.Time))
                    this_row  = self.dataframe.loc[(lap_start,time)]
                    trackpoint.Position.LatitudeDegrees._setText(str(this_row["Position.Latitude"]))
                    trackpoint.Position.LongitudeDegrees._setText(str(this_row["Position.Longitude"]))
                    trackpoint.AltitudeMeters._setText(str(this_row["AltitudeMeters"]))
                    trackpoint.DistanceMeters._setText(str(this_row["DistanceMeters"]))
                    print(this_row["HeartRateBpm.Value"])
                    trackpoint.HeartRateBpm.Value._setText(str(this_row["HeartRateBpm.Value"].astype(int)))
        self.tcx.getroot().Activities.Activity = self.activity
        return self.tcx
