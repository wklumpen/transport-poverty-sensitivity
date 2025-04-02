import os

import altair as alt
import geopandas as gpd
import pandas as pd

REGIONS = ["WAS", "BOS", "CHI", "LA", "PHL", "SFO"]
# REGIONS = ["WAS"]
REGION_MAP = {
    "WAS": "Washington, DC",
    "BOS": "Boston",
    "CHI": "Chicago",
    "LA": "Los Angeles",
    "NYC": "New York City",
    "PHL": "Philadelphia",
    "SFO": "San Francisco Bay Area",
}

BASE_GEODATA_PATH = "/home/willem/Documents/Project/TED/data/packaged"
BASE_SENSITIVTY_PATH = (
    "/home/willem/Documents/Project/Transport Poverty Sensitivity/data"
)
WEEK_OF = "20240304"
TOD = "WEDAM"
LAYER_TITLE = "March 3, 2024, 7-9am"

layer_name = f"{WEEK_OF}_{TOD}"


fraction_lines = pd.read_csv(os.path.join(BASE_SENSITIVTY_PATH, "fraction_lines.csv"))
fraction_p_values = [1, 6, 11, 16, 21, 26, 31]

auto_lines = pd.read_csv(os.path.join(BASE_SENSITIVTY_PATH, "auto_lines.csv"))
auto_p_values = [1, 6, 11, 16, 21, 26, 31]

percentile_lines = pd.read_csv(
    os.path.join(BASE_SENSITIVTY_PATH, "percentile_lines.csv")
)
percentile_p_values = [20, 40, 60, 80]

for region in REGIONS:
    print(f"Creating {region} fractional map")
    gdf = gpd.read_file(
        os.path.join(BASE_GEODATA_PATH, region, "gpkg", f"acs_{region}.gpkg"),
        layer=layer_name,
    ).to_crs(epsg=4326)[["C000_c45", "C000_c45_auto", "geometry"]]

    gdf["C000_c45_auto"] = gdf["C000_c45"] / gdf["C000_c45_auto"]

    transit_gdf = gpd.read_file(
        os.path.join(BASE_SENSITIVTY_PATH, "sensitivity.gpkg"),
        layer=f"{region}_transit_1",
    ).to_crs(epsg=4326)

    region_fraction_lines = fraction_lines[
        (fraction_lines.region == region) & (fraction_lines.tod == TOD)
    ][["value", "p"]].set_index("p")

    domain = [int(region_fraction_lines.loc[p].value) for p in fraction_p_values]
    domain_string = ", ".join([str(p) for p in fraction_p_values])
    # Let's load in those lines
    map = (
        alt.Chart(gdf)
        .mark_geoshape(opacity=1)
        .encode(
            alt.Color("C000_c45:Q", title="Jobs Reachable")
            .scale(domain=domain, scheme="viridis", type="threshold")
            .legend(format=",.3r"),
            # alt.Stroke("C000_c45:Q").scale(
            #     domain=domain, scheme="purples", type="threshold"
            # ),
        )
        .project(type="mercator")
    )

    transit = (
        alt.Chart(transit_gdf)
        .mark_geoshape(filled=False, stroke="white", strokeWidth=4)
        .project(type="mercator")
    )

    out = (
        (map + transit)
        .properties(
            title={
                "text": [
                    f"Fractional Disadvantage Lines in {REGION_MAP[region]}",
                ],
                "subtitle": [
                    "Distribution of jobs reachable in 45 minutes for various disadvantage lines",
                    f"Data for the week of {LAYER_TITLE}. Major transit lines are shown in white.",
                    f"Disadvantage lines are set at p = {domain_string}",
                ],
            },
            width=2000,
            height=2000,
        )
        .configure(
            font="Lato",
        )
        .configure_title(
            fontSize=80,
            subtitleFontSize=48,
            anchor="middle",
            color="#708090",
            offset=20,
            subtitlePadding=10,
        )
        .configure_legend(
            titleFontSize=68,
            titleFontWeight="bold",
            titleAnchor="middle",
            labelFontSize=48,
            labelPadding=100,
            gradientThickness=50,
            # labelAlign="right",
            orient="bottom",
            direction="horizontal",
            titleLimit=800,
            #     labelLimit=3200,
            gradientLength=2000,
            symbolSize=500,
        )
    )

    outfile = f"../maps/{region}_fractional.png"
    out.save(outfile)
    print(f"  Map written to", outfile)

    print(f"Creating {region} auto map")

    region_auto_lines = auto_lines[
        (auto_lines.region == region) & (auto_lines.tod == TOD)
    ][["value", "p"]].set_index("p")

    domain = [p / 100.0 for p in auto_p_values]
    domain_string = ", ".join([str(p) for p in auto_p_values])
    # Let's load in those lines
    map = (
        alt.Chart(gdf)
        .mark_geoshape(opacity=1)
        .encode(
            alt.Color("C000_c45_auto:Q", title="Transit/Auto Access")
            .scale(domain=domain, scheme="viridis", type="threshold")
            .legend(format=".2"),
            # alt.Stroke("C000_c45:Q").scale(
            #     domain=domain, scheme="purples", type="threshold"
            # ),
        )
        .project(type="mercator")
    )

    transit = (
        alt.Chart(transit_gdf)
        .mark_geoshape(filled=False, stroke="white", strokeWidth=4)
        .project(type="mercator")
    )

    out = (
        (map + transit)
        .properties(
            title={
                "text": [
                    f"Auto Ratio Disadvantage Lines in {REGION_MAP[region]}",
                ],
                "subtitle": [
                    "Distribution of the ratio of transt:auto jobs accessible for various disadvantage lines",
                    f"Data for the week of {LAYER_TITLE}. Major transit lines are shown in white.",
                    f"Disadvantage lines are set at p = {domain_string}",
                ],
            },
            width=2000,
            height=2000,
        )
        .configure(
            font="Lato",
        )
        .configure_title(
            fontSize=80,
            subtitleFontSize=48,
            anchor="middle",
            color="#708090",
            offset=20,
            subtitlePadding=10,
        )
        .configure_legend(
            titleFontSize=68,
            titleFontWeight="bold",
            titleAnchor="middle",
            labelFontSize=48,
            labelPadding=100,
            gradientThickness=50,
            # labelAlign="right",
            orient="bottom",
            direction="horizontal",
            titleLimit=800,
            #     labelLimit=3200,
            gradientLength=2000,
            symbolSize=500,
        )
    )

    outfile = f"../maps/{region}_auto.png"
    out.save(outfile)
    print(f"  Map written to", outfile)

    print(f"Creating {region} percentile map")

    region_percentile_lines = percentile_lines[
        (percentile_lines.region == region) & (percentile_lines.tod == TOD)
    ][["value", "p"]].set_index("p")

    domain = [int(region_percentile_lines.loc[p].value) for p in percentile_p_values]
    domain_string = ", ".join([str(p) for p in percentile_p_values])

    map = (
        alt.Chart(gdf)
        .mark_geoshape(opacity=1)
        .encode(
            alt.Color("C000_c45:Q", title="Jobs Reachable")
            .scale(domain=domain, scheme="viridis", type="threshold")
            .legend(format="s"),
            # alt.Stroke("C000_c45:Q").scale(
            #     domain=domain, scheme="purples", type="threshold"
            # ),
        )
        .project(type="mercator")
    )

    transit = (
        alt.Chart(transit_gdf)
        .mark_geoshape(filled=False, stroke="white", strokeWidth=4)
        .project(type="mercator")
    )

    out = (
        (map + transit)
        .properties(
            title={
                "text": [
                    f"Percentile Disadvantage Lines in {REGION_MAP[region]}",
                ],
                "subtitle": [
                    "Distribution of jobs accessible for various disadvantage lines set with percentiles.",
                    f"Data for the week of {LAYER_TITLE}. Major transit lines are shown in white.",
                    f"Disadvantage lines are set at p = {domain_string}",
                ],
            },
            width=2000,
            height=2000,
        )
        .configure(
            font="Lato",
        )
        .configure_title(
            fontSize=80,
            subtitleFontSize=48,
            anchor="middle",
            color="#708090",
            offset=20,
            subtitlePadding=10,
        )
        .configure_legend(
            titleFontSize=68,
            titleFontWeight="bold",
            titleAnchor="middle",
            labelFontSize=48,
            labelPadding=100,
            gradientThickness=50,
            # labelAlign="right",
            orient="bottom",
            direction="horizontal",
            titleLimit=800,
            #     labelLimit=3200,
            gradientLength=2000,
            symbolSize=500,
        )
    )

    outfile = f"../maps/{region}_percentile.png"
    out.save(outfile)
    print(f"  Map written to", outfile)
