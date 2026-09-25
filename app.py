import re
from pathlib import Path
import country_converter as coco
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests


# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="Music Festival Investment Dashboard",
    page_icon="🎵",
    layout="wide"
)


# ============================================================
# 1. LOAD DATA
# Function Name: load_data
# Parameter: path
# Return Value: dataframe
# ============================================================

@st.cache_data
def load_data(path):
    dataset = pd.read_csv(path)
    return dataset


# ============================================================
# 2. CHECK MISSING VALUES
# Function Name: check_missing
# Parameter: dataframe
# Return Value: table showing missing values
# ============================================================

def check_missing(dataframe):

    missing = dataframe.isnull().sum().reset_index()

    missing.columns = [
        "Column",
        "Missing Values"
    ]

    return missing


# ============================================================
# 3. SUMMARY STATISTICS
# Function Name: data_stats
# Parameter: dataframe
# Return Value: mean, sd, min, max, etc.
# ============================================================

def data_stats(dataframe):

    numeric_data = dataframe.select_dtypes(
        include=np.number
    )

    statistics = numeric_data.describe().T

    return statistics[
        [
            "count",
            "mean",
            "std",
            "min",
            "25%",
            "50%",
            "75%",
            "max"
        ]
    ]


# ============================================================
# 4. GROUP BY
# Function Name: group_by
# Parameters: dataframe, column1, column2
# Return Value: relationship between two categorical variables
# ============================================================

def group_by(dataframe, column1, column2):

    result = pd.crosstab(
        dataframe[column1],
        dataframe[column2]
    )

    return result


# ============================================================
# 5. PLOT DISTRIBUTION
# Function Name: plot_histogram
# Parameters: dataframe, column_name, bins, title
# Return Value: histogram
# ============================================================

def plot_histogram(
    dataframe,
    column_name,
    bins,
    title
):

    fig, ax = plt.subplots()

    ax.hist(
        dataframe[column_name].dropna(),
        bins=bins,
        edgecolor="black"
    )

    ax.set_title(title)
    ax.set_xlabel(column_name)
    ax.set_ylabel("Frequency")

    return fig


# ============================================================
# 6. PRINT RESULTS
# Function Name: print_results
# Parameter: result
# Return Value: displays result in Streamlit
# ============================================================

def print_results(result):

    st.dataframe(
        result,
        use_container_width=True
    )


# ============================================================
# GET CURRENT EXCHANGE RATES
# ============================================================

@st.cache_data(ttl=86400)
def get_fx_rates():

    url = "https://open.er-api.com/v6/latest/USD"

    response = requests.get(
        url,
        timeout=10
    )

    response.raise_for_status()

    result = response.json()

    if result.get("result") != "success":
        raise ValueError(
            "Exchange-rate service did not return successfully."
        )

    rates = result["rates"]

    update_time = result[
        "time_last_update_utc"
    ]

    return rates, update_time


# ============================================================
# EXTRACT CURRENCY FROM ECONOMIC IMPACT
# ============================================================

def extract_currency(value):

    if pd.isna(value):
        return np.nan

    value = str(value).strip()

    if value == "":
        return np.nan

    # Currency symbols
    if value.startswith("-€") or value.startswith("€"):
        return "EUR"

    if value.startswith("-£") or value.startswith("£"):
        return "GBP"

    if value.startswith("-AU$") or value.startswith("AU$"):
        return "AUD"

    if value.startswith("-$") or value.startswith("$"):
        return "USD"

    # Currency codes such as USD, CAD, JPY, MXN, KRW, etc.
    match = re.match(
        r"-?([A-Z]{3})\b",
        value
    )

    if match:
        return match.group(1)

    return np.nan


# ============================================================
# EXTRACT ECONOMIC IMPACT NUMBER
# ============================================================

def extract_local_amount(value):

    if pd.isna(value):
        return np.nan

    value = str(value).strip()

    if value == "":
        return np.nan

    # Check if value is negative
    sign = -1 if value.startswith("-") else 1

    number_match = re.search(
        r"\d+(?:\.\d+)?",
        value.replace(",", "")
    )

    if not number_match:
        return np.nan

    amount = float(
        number_match.group()
    )

    amount = amount * sign

    # Handle million / billion
    if "billion" in value.lower():

        amount = amount * 1_000_000_000

    elif "million" in value.lower():

        amount = amount * 1_000_000

    return amount


# ============================================================
# CLEAN DATA
# ============================================================

@st.cache_data(ttl=86400)
def clean_data(dataframe):

    df = dataframe.copy()

    # --------------------------------------------------------
    # CLEAN COLUMN NAMES
    # --------------------------------------------------------

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )


    # --------------------------------------------------------
    # REMOVE OLD PARTIALLY-CLEANED CURRENCY COLUMNS
    # We rebuild these correctly below.
    # --------------------------------------------------------

    df = df.drop(
        columns=[
            "economic_impact_currency",
            "economic_impact_amount",
            "attendance_category"
        ],
        errors="ignore"
    )


    # --------------------------------------------------------
    # RENAME COLUMNS FOR EASIER USE
    # --------------------------------------------------------

    rename_columns = {

        "location":
            "Location",

        "attendance_numbers":
            "Attendance_Numbers",

        "age":
            "Age",

        "visitor_demographics":
            "Visitor_Demographics",

        "economic_impact":
            "Economic_Impact",

        "music_genre":
            "Music_Genre",

        "festival_name":
            "Festival_Name",

        "minimum_age":
            "Minimum_Age",

        "maximum_age":
            "Maximum_Age",

        "average_age":
            "Average_Age",

        "region":
            "Region"
    }

    df = df.rename(
        columns=rename_columns
    )


    # ========================================================
    # LOCATION CLEANING
    # ========================================================

    df["Location"] = (
        df["Location"]
        .astype("string")
        .str.strip()
    )

    location_corrections = {

        "UAE":
            "United Arab Emirates",

        "UK":
            "United Kingdom",

        "USA":
            "United States",

        "USSA":
            "United States",

        "SPAIN":
            "Spain",

        "NETHERLAND":
            "Netherlands",

        "Pokand":
            "Poland",

        "Thialand":
            "Thailand",

        "Vietnsm":
            "Vietnam",

        "MMalta":
            "Malta",

        "Aerbaijan":
            "Azerbaijan",

        "Tajjikistan":
            "Tajikistan",

        "Bagladesh":
            "Bangladesh",

        "PAPUA NEW GUINEA":
            "Papua New Guinea",

        "Bruneii":
            "Brunei",

        "NICARAGUA":
            "Nicaragua",

        "Saint Luciia":
            "Saint Lucia",

        "Aurba":
            "Aruba"
    }

    df["Location"] = (
        df["Location"]
        .replace(location_corrections)
    )


    # ========================================================
    # ATTENDANCE CLEANING
    # ========================================================

    df["Attendance_Numbers"] = pd.to_numeric(
        df["Attendance_Numbers"],
        errors="coerce"
    )

    # Remove obvious incorrect values.
    #
    # Less than 1,000 is treated as an invalid entry
    # for this dataset.
    #
    # More than 2 million is treated as an obvious
    # data-entry error.

    invalid_attendance = (
        (df["Attendance_Numbers"] < 1_000)
        |
        (df["Attendance_Numbers"] > 2_000_000)
    )

    df.loc[
        invalid_attendance,
        "Attendance_Numbers"
    ] = np.nan


    # ========================================================
    # MUSIC GENRE CLEANING
    # ========================================================

    df["Music_Genre"] = (
        df["Music_Genre"]
        .astype("string")
        .str.strip()
    )

    genre_corrections = {

        "Inie/Rock":
            "Indie/Rock",

        "ondie/Pop":
            "Indie/Pop",

        "Pop/ock":
            "Pop/Rock",

        "Pop/Folkk":
            "Pop/Folk",

        "Rock/Flok":
            "Rock/Folk",

        "Rocck/Folk":
            "Rock/Folk",

        "Folk/aJzz":
            "Folk/Jazz"
    }

    df["Music_Genre"] = (
        df["Music_Genre"]
        .replace(genre_corrections)
    )


    # ========================================================
    # REGION CLEANING
    # Create geographic region from country
    # ========================================================

    countries = (
        df["Location"]
        .fillna("")
        .tolist()
    )

    regions = coco.convert(
        names=countries,
        to="continent"
    )

    df["Region"] = regions

    df["Region"] = df["Region"].replace(
        ["not found", ""],
        np.nan
    )


    # ========================================================
    # ECONOMIC IMPACT
    #
    # Rebuild currency + amount from original economic impact.
    # ========================================================

    df[
        "Economic_Impact_Currency"
    ] = df[
        "Economic_Impact"
    ].apply(
        extract_currency
    )


    df[
        "Economic_Impact_Local_Amount"
    ] = df[
        "Economic_Impact"
    ].apply(
        extract_local_amount
    )


    # --------------------------------------------------------
    # GET CURRENT EXCHANGE RATES
    # --------------------------------------------------------

    rates, fx_date = get_fx_rates()


    # --------------------------------------------------------
    # CONVERT EACH ECONOMIC IMPACT TO USD
    # --------------------------------------------------------

    def convert_to_usd(row):

        currency = row[
            "Economic_Impact_Currency"
        ]

        local_amount = row[
            "Economic_Impact_Local_Amount"
        ]

        if pd.isna(currency):

            return np.nan

        if pd.isna(local_amount):

            return np.nan

        currency_rate = rates.get(
            currency
        )

        if currency_rate is None:

            return np.nan

        # Exchange-rate table uses USD as its base.
        #
        # Example:
        # 1 USD = 0.88 EUR
        #
        # Therefore:
        # EUR amount / 0.88 = USD amount

        usd_amount = (
            local_amount
            /
            currency_rate
        )

        return usd_amount


    df[
        "Economic_Impact_USD"
    ] = df.apply(
        convert_to_usd,
        axis=1
    )


    # --------------------------------------------------------
    # REMOVE INVALID ECONOMIC VALUES
    # --------------------------------------------------------

    # Negative economic impacts in this dataset
    # are treated as invalid for investment comparison.

    df.loc[
        df["Economic_Impact_USD"] <= 0,
        "Economic_Impact_USD"
    ] = np.nan


    # Remove obvious massive data-entry errors.

    df.loc[
        df["Economic_Impact_USD"]
        > 2_000_000_000,
        "Economic_Impact_USD"
    ] = np.nan


    # --------------------------------------------------------
    # USD IN MILLIONS
    # Easier for dashboard charts
    # --------------------------------------------------------

    df[
        "Economic_Impact_USD_Millions"
    ] = (
        df[
            "Economic_Impact_USD"
        ]
        /
        1_000_000
    )


    # ========================================================
    # ATTENDANCE CATEGORY
    # ========================================================

    df[
        "Attendance_Category"
    ] = pd.cut(

        df[
            "Attendance_Numbers"
        ],

        bins=[
            0,
            50_000,
            150_000,
            300_000,
            float("inf")
        ],

        labels=[
            "Small (<50K)",
            "Medium (50K–150K)",
            "Large (150K–300K)",
            "Very Large (300K+)"
        ]
    )


    return df, fx_date


# ============================================================
# FIND DATASET
# ============================================================

# This lets the app work with either filename.

possible_files = [

    Path(
        "data/music_festivals_2024_clean.csv"
    ),

    Path(
        "data/festival_data.csv"
    )
]


data_path = None


for file_path in possible_files:

    if file_path.exists():

        data_path = file_path

        break


if data_path is None:

    st.error(
        "Dataset not found. Put "
        "'music_festivals_2024_clean.csv' "
        "or 'festival_data.csv' inside the data folder."
    )

    st.stop()


# ============================================================
# LOAD RAW DATA
# ============================================================

raw_data = load_data(
    data_path
)


# ============================================================
# CLEAN DATA
# ============================================================

try:

    data, fx_date = clean_data(
        raw_data
    )

except requests.RequestException:

    st.error(
        "The app could not retrieve exchange rates. "
        "Check your internet connection and refresh the app."
    )

    st.stop()


# ============================================================
# APP TITLE
# ============================================================

st.title(
    "🎵 Music Festival Investment Dashboard"
)

st.write(
    """
    This dashboard helps festival organizers, tourism agencies,
    event planners, investors, and analysts explore music
    festival markets using attendance, music genre, location,
    audience information, and economic impact.
    """
)


# ============================================================
# BUSINESS QUESTION
# ============================================================

st.subheader(
    "Business Question"
)

st.write(
    """
    **What regions and music genres may offer attractive
    opportunities for festival investment?**
    """
)

st.write(
    """
    Users can compare festival attendance and economic impact
    across regions, countries, and music genres to identify
    patterns that may support investment and planning decisions.
    """
)


# ============================================================
# SIDEBAR
# INTERACTIVE CONTROLS
# ============================================================

st.sidebar.header(
    "Dashboard Filters"
)


# ------------------------------------------------------------
# CONTROL 1: REGION
# ------------------------------------------------------------

regions = sorted(
    data[
        "Region"
    ]
    .dropna()
    .unique()
)

selected_regions = st.sidebar.multiselect(
    "Select Region",
    regions
)


# ------------------------------------------------------------
# CONTROL 2: COUNTRY
# ------------------------------------------------------------

countries = sorted(
    data[
        "Location"
    ]
    .dropna()
    .unique()
)

selected_countries = st.sidebar.multiselect(
    "Select Country",
    countries
)


# ------------------------------------------------------------
# CONTROL 3: MUSIC GENRE
# ------------------------------------------------------------

genres = sorted(
    data[
        "Music_Genre"
    ]
    .dropna()
    .unique()
)

selected_genres = st.sidebar.multiselect(
    "Select Music Genre",
    genres
)


# ------------------------------------------------------------
# CONTROL 4: ATTENDANCE SLIDER
# ------------------------------------------------------------

attendance_values = data[
    "Attendance_Numbers"
].dropna()


minimum_attendance = int(
    attendance_values.min()
)

maximum_attendance = int(
    attendance_values.max()
)


attendance_range = st.sidebar.slider(
    "Attendance Range",
    min_value=minimum_attendance,
    max_value=maximum_attendance,
    value=(
        minimum_attendance,
        maximum_attendance
    )
)


# ------------------------------------------------------------
# CONTROL 5: SHOW DATA
# ------------------------------------------------------------

show_data = st.sidebar.checkbox(
    "Show Cleaned Dataset"
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_data = data.copy()


if selected_regions:

    filtered_data = filtered_data[
        filtered_data[
            "Region"
        ].isin(
            selected_regions
        )
    ]


if selected_countries:

    filtered_data = filtered_data[
        filtered_data[
            "Location"
        ].isin(
            selected_countries
        )
    ]


if selected_genres:

    filtered_data = filtered_data[
        filtered_data[
            "Music_Genre"
        ].isin(
            selected_genres
        )
    ]


filtered_data = filtered_data[

    filtered_data[
        "Attendance_Numbers"
    ].between(

        attendance_range[0],
        attendance_range[1]

    )

    |

    filtered_data[
        "Attendance_Numbers"
    ].isna()

]


if filtered_data.empty:

    st.warning(
        "No festivals match the selected filters."
    )

    st.stop()


# ============================================================
# SUMMARY METRICS
# ============================================================

st.subheader(
    "Festival Market Overview"
)


col1, col2, col3, col4 = st.columns(4)


# Number of festivals

col1.metric(
    "Festival Records",
    len(filtered_data)
)


# Average attendance

average_attendance = filtered_data[
    "Attendance_Numbers"
].mean()


if pd.notna(
    average_attendance
):

    attendance_display = (
        f"{average_attendance:,.0f}"
    )

else:

    attendance_display = "N/A"


col2.metric(
    "Average Attendance",
    attendance_display
)


# Average economic impact

average_impact = filtered_data[
    "Economic_Impact_USD_Millions"
].mean()


if pd.notna(
    average_impact
):

    impact_display = (
        f"${average_impact:,.1f}M"
    )

else:

    impact_display = "N/A"


col3.metric(
    "Average Economic Impact",
    impact_display
)


# Number of countries

country_count = filtered_data[
    "Location"
].nunique()


col4.metric(
    "Countries",
    country_count
)


# ============================================================
# VISUALIZATION 1
# TOP COUNTRIES BY AVERAGE ATTENDANCE
# ============================================================

st.subheader(
    "1. Average Festival Attendance by Country"
)


country_attendance = (

    filtered_data
    .groupby(
        "Location"
    )[
        "Attendance_Numbers"
    ]
    .mean()
    .dropna()
    .nlargest(10)
    .sort_values(
        ascending=True
    )

)


fig1, ax1 = plt.subplots()


country_attendance.plot(
    kind="barh",
    ax=ax1
)


ax1.set_title(
    "Top 10 Countries by Average Festival Attendance"
)

ax1.set_xlabel(
    "Average Attendance"
)

ax1.set_ylabel(
    "Country"
)


st.pyplot(
    fig1
)


# ============================================================
# VISUALIZATION 2
# MUSIC GENRES BY ECONOMIC IMPACT
# ============================================================

st.subheader(
    "2. Music Genres by Average Economic Impact"
)


genre_impact = (

    filtered_data
    .groupby(
        "Music_Genre"
    )[
        "Economic_Impact_USD_Millions"
    ]
    .mean()
    .dropna()
    .nlargest(10)
    .sort_values(
        ascending=True
    )

)


fig2, ax2 = plt.subplots()


genre_impact.plot(
    kind="barh",
    ax=ax2
)


ax2.set_title(
    "Top 10 Genres by Average Economic Impact"
)

ax2.set_xlabel(
    "Average Economic Impact (USD Millions)"
)

ax2.set_ylabel(
    "Music Genre"
)


st.pyplot(
    fig2
)


# ============================================================
# VISUALIZATION 3
# HISTOGRAM
# ============================================================

st.subheader(
    "3. Festival Attendance Distribution"
)


fig3 = plot_histogram(

    filtered_data,

    "Attendance_Numbers",

    15,

    "Distribution of Festival Attendance"
)


st.pyplot(
    fig3
)


# ============================================================
# REGION + GENRE INVESTMENT COMPARISON
# ============================================================

st.subheader(
    "Region and Genre Comparison"
)


comparison = (

    filtered_data

    .groupby(
        [
            "Region",
            "Music_Genre"
        ]
    )

    .agg(

        Festival_Count=(
            "Region",
            "size"
        ),

        Average_Attendance=(
            "Attendance_Numbers",
            "mean"
        ),

        Average_Economic_Impact_USD_Millions=(
            "Economic_Impact_USD_Millions",
            "mean"
        )

    )

    .reset_index()

)


comparison = comparison.sort_values(

    by=[
        "Average_Economic_Impact_USD_Millions",
        "Average_Attendance"
    ],

    ascending=[
        False,
        False
    ]

)


st.dataframe(
    comparison,
    use_container_width=True
)


# ============================================================
# OPTIONAL CLEANED DATA
# ============================================================

if show_data:

    st.subheader(
        "Cleaned Festival Dataset"
    )

    print_results(
        filtered_data
    )


# ============================================================
# DATA QUALITY CHECK
# ============================================================

with st.expander(
    "Data Quality Check"
):

    st.write(
        "**Total Records:**",
        len(data)
    )


    st.write(
        "**Missing Locations:**",
        data[
            "Location"
        ].isna().sum()
    )


    st.write(
        "**Missing / Invalid Attendance Values:**",
        data[
            "Attendance_Numbers"
        ].isna().sum()
    )


    original_economic_values = data[
        "Economic_Impact"
    ].notna().sum()


    converted_economic_values = data[
        "Economic_Impact_USD"
    ].notna().sum()


    st.write(
        "**Economic Impact Values Provided:**",
        original_economic_values
    )


    st.write(
        "**Valid Economic Impact Values Converted to USD:**",
        converted_economic_values
    )


    st.write(
        "**Exchange Rates Last Updated:**",
        fx_date
    )


    # Find values that had an original economic impact
    # but did not make it into the final USD analysis.

    unconverted = data[

        data[
            "Economic_Impact"
        ].notna()

        &

        data[
            "Economic_Impact_USD"
        ].isna()

    ][
        [
            "Festival_Name",
            "Economic_Impact",
            "Economic_Impact_Currency"
        ]
    ]


    st.write(
        "**Excluded or Unconverted Economic Impact Rows:**"
    )


    if unconverted.empty:

        st.success(
            "All provided economic impact values were successfully converted."
        )

    else:

        st.dataframe(
            unconverted,
            use_container_width=True
        )


# ============================================================
# MISSING VALUES
# ============================================================

with st.expander(
    "Missing Values"
):

    print_results(
        check_missing(
            data
        )
    )


# ============================================================
# SUMMARY STATISTICS
# ============================================================

with st.expander(
    "Summary Statistics"
):

    print_results(
        data_stats(
            data
        )
    )


# ============================================================
# GROUP BY TABLE
# ============================================================

with st.expander(
    "Region × Music Genre Table"
):

    print_results(

        group_by(
            data,
            "Region",
            "Music_Genre"
        )

    )


# ============================================================
# FOOTNOTE
# ============================================================

st.caption(
    """
    Economic-impact values are standardized to USD using
    current exchange rates. Missing values and obvious
    data-entry errors are excluded from numeric calculations
    rather than replaced with invented values.
    """
)