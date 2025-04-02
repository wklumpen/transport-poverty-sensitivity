import os

import pandas as pd
import traccess as tr

WEEK_OF = "20240304"
TODS = ["WEDAM", "WEDPM", "SATAM"]
REGIONS = ["BOS", "CHI", "LA", "NYC", "PHL", "SFO", "WAS"]
PACKAGED_FOLDER = "/home/willem/Documents/Project/TED/data/packaged"
REGION_FOLDER = "/home/willem/Documents/Project/TED/data/region"
SUPPLY_FIELD = "C000"
ACCESS_COLUMN = "C000_c45"

PERCENT_RANGES = range(1, 101, 1)
dfs = []

poverty_lines = {
    "region": [],
    "tod": [],
    "p": [],
    "value": [],
}

for region in REGIONS:
    print(region)
    supply_df = pd.read_csv(
        os.path.join(REGION_FOLDER, region, "supply", "supply.csv"), dtype={"BG20": str}
    )
    total_supply = supply_df[SUPPLY_FIELD].sum()
    supply = tr.Supply(supply_df, id_column="BG20")
    demo = tr.Demographic.from_csv(
        os.path.join(REGION_FOLDER, region, "demographics.csv"),
        id_column="BG20",
        dtype={"BG20": str},
    )
    print(f"  Total supply of {SUPPLY_FIELD}:", total_supply)
    for tod in TODS:
        print(f" {tod}")
        score_file = os.path.join(
            PACKAGED_FOLDER, region, "scores", f"acs_{region}_{WEEK_OF}_{tod}.csv"
        )
        scores = pd.read_csv(score_file, dtype={"BG20": str})
        print("  Minimum % of total:", 100 * scores[ACCESS_COLUMN].min() / total_supply)
        print("  Maximum % of total:", 100 * scores[ACCESS_COLUMN].max() / total_supply)
        access = tr.Access(scores, id_column="BG20")
        for p in PERCENT_RANGES:
            poverty_line = (p / 100.0) * total_supply

            poverty_lines["region"].append(region)
            poverty_lines["tod"].append(tod)
            poverty_lines["p"].append(p)
            poverty_lines["value"].append(poverty_line)

            print("    Poverty line:", poverty_line)
            ec = tr.EquityComputer(access, demo)
            df = ec.fgt_poverty(
                ACCESS_COLUMN, poverty_line=poverty_line, alpha=0
            ).to_frame()
            df = df.reset_index()
            df.columns = ["group", "fgt0"]

            fgt1 = ec.fgt_poverty(
                ACCESS_COLUMN, poverty_line=poverty_line, alpha=1
            ).to_frame()
            fgt1 = fgt1.reset_index()
            fgt1.columns = ["group", "fgt1"]

            fgt2 = ec.fgt_poverty(
                ACCESS_COLUMN, poverty_line=poverty_line, alpha=2
            ).to_frame()
            fgt2 = fgt2.reset_index()
            fgt2.columns = ["group", "fgt2"]

            df = pd.merge(df, fgt1, on="group")
            df = pd.merge(df, fgt2, on="group")

            df["region"] = region
            df["tod"] = tod
            df["p"] = p
            dfs.append(df)

out = pd.concat(dfs, axis="index")
out.to_csv("../data/fraction.csv", index=False)

poverty_df = pd.DataFrame(poverty_lines)
poverty_df.to_csv("../data/fraction_lines.csv", index=False)
