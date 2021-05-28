import pandas as pd

df = pd.read_csv("seatmaps.csv", delimiter=";")
df2 = df.sort_values(by=["airline_name", "aircraft_code"], key=lambda col: col.str.lower())

df2.to_csv(
    "cleaned.csv",
    sep=";",
    index=False,
    columns=[
        "airline_code",
        "aircraft_code",
        "aircraft_description",
        "airline_name",
        "layout",
        "seat_map",
        "traveler_photos",
        "seat_map_key",
        "overview",
        "seats_file",
    ],
)
