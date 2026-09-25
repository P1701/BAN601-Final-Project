import re
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import country_converter as coco


# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------

st.set_page_config(
    page_title="Music Festival Investment Dashboard",
    layout="wide"
)


# --------------------------------------------------
# 1. LOAD DATA
# Function name: load_data
# Parameter: path
# Return value: dataset
# --------------------------------------------------

@st.cache_data
def load_data(path):
    dataset = pd.read_csv(path)
    return dataset


# --------------------------------------------------
# 2. CHECK MISSING VALUES
# Function name: check_missing
# Parameter: dataframe
# Return value: missing value summary
# --------------------------------------------------

def check_missing(dataframe):
    missing = dataframe.isnull().sum().reset_index()
    missing.columns = ["Column", "Missing Values"]
    return missing


# --------------------------------------------------
# 3. SUMMARY STATISTICS
# Function name: data_stats
# Parameter: dataframe
# Return value: mean, sd, min, max, etc.
# --------------------------------------------------

def data_stats(dataframe):
    numeric_data = dataframe.select_dtypes(include=np.number)

    stats = numeric_data.describe().T

    return stats[
        ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]
    ]


# --------------------------------------------------
# 4. GROUP BY
# Function name: group_by
# Parameters: dataframe, column1, column2
# Return value: relationship between categorical variables
# --------------------------------------------------

def group_by(dataframe, column1, column2):
    result = pd.crosstab(
        dataframe[column1],
        dataframe[column2]
    )

    return result


# --------------------------------------------------
# 5. PLOT DISTRIBUTION
# Function name: plot_histogram
# Parameters: dataframe, column_name, bins, title
# Return value: histogram
# --------------------------------------------------

def plot_histogram(dataframe, column_name, bins, title):

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


# --------------------------------------------------
# 6. PRINT RESULTS
# Function name: print_results
# Parameter: result
# Return value: displayed result
# --------------------------------------------------

def print_results(result):
    st.dataframe(
        result,
        use_container_width=True
    )


# --------------------------------------------------
# DATA CLEANING
# --------------------------------------------------

def clean_data(dataframe):

    df = dataframe.copy()

    # Clean column names
    df.columns = df.columns.str.strip()

    # ----------------------------------------------
    # Clean locations
    # ----------------------------------------------

    df["Location"] = df["Location"].astype("string").str.strip()

    location_corrections = {
        "UK": "United Kingdom",
        "USA": "United States",
        "USSA": "United States",
        "SPAIN": "Spain",
        "NETHERLAND": "Netherlands",
        "Pokand": "Poland",
        "Thialand": "Thailand",
        "Vietnsm": "Vietnam",
        "MMalta": "Malta",
        "Aerbaijan": "Azerbaijan",
        "Tajjikistan": "Tajikistan",
        "Bagladesh": "Bangladesh",
        "PAPUA NEW GUINEA": "Papua New Guinea",
        "Bruneii": "Brunei",
        "NICARAGUA": "Nicaragua",
        "Saint Luciia": "Saint Lucia",
        "Aurba": "Aruba",
        "UAE": "United Arab Emirates"
    }

    df["Location"] = df["Location"].replace(location_corrections)

    # ----------------------------------------------
    # Clean attendance
    # ----------------------------------------------

    df["Attendance_Numbers"] = pd.to_numeric(
        df["Attendance_Numbers"],
        errors="coerce"
    )

    # Remove clearly impossible / erroneous values
    df.loc[
        (df["Attendance_Numbers"] < 1000) |
        (df["Attendance_Numbers"] > 2000000),
        "Attendance_Numbers"
    ] = np.nan

    # ----------------------------------------------
    # Clean music genre
    # ----------------------------------------------

    df["Music_Genre"] = df["Music_Genre"].astype("string").str.strip()

    genre_corrections = {
        "Variious": "Various",
        "Varius": "Various",
        "Inie/Rock": "Indie/Rock",
        "ondie/Pop": "Indie/Pop",
        "Pop/ock": "Pop/Rock",
        "Rock/Flok": "Rock/Folk"
    }

    df["Music_Genre"] = df["Music_Genre"].replace(genre_corrections)

    # ----------------------------------------------
    # Create Region column from country
    # ----------------------------------------------

    country_list = df["Location"].fillna("").tolist()

    continents = coco.convert(
        names=country_list,
        to="continent"
    )

    df["Region"] = continents

    df["Region"] = df["Region"].replace(
        ["not found", ""],
        np.nan
    )

    # ----------------------------------------------
    # Convert Economic Impact to USD
    # Approximate conversion rates for analysis
    # ----------------------------------------------

    usd_rates = {
        "USD": 1.00,
        "GBP": 1.27,
        "EUR": 1.08,
        "DKK": 0.145,
        "CHF": 1.13,
        "AUD": 0.66,
        "MXN": 0.059,
        "PLN": 0.25,
        "CAD": 0.74,
        "SEK": 0.095,
        "NOK": 0.094,
        "JPY": 0.0067,
        "CLP": 0.0011,
        "ARS": 0.0011,
        "BRL": 0.20,
        "KRW": 0.00075,
        "NZD": 0.61,
        "ZAR": 0.054,
        "TRY": 0.031,
        "AED": 0.272,
        "RUB": 0.011,
        "CZK": 0.043,
        "COP": 0.00025,
        "THB": 0.028,
        "IDR": 0.000064,
        "MYR": 0.21,
        "PHP": 0.0176,
        "VND": 0.000041,
        "SGD": 0.74,
        "EGP": 0.020,
        "MAD": 0.10,
        "KES": 0.0076,
        "TZS": 0.00038,
        "GHS": 0.065,
        "XOF": 0.00165,
        "XAF": 0.00165,
        "UGX": 0.00027,
        "ZMW": 0.037,
        "BWP": 0.073,
        "NAD": 0.054,
        "UAH": 0.025,
        "PEN": 0.27,
        "ISK": 0.0072,
        "BYN": 0.30,
        "MDL": 0.056,
        "BAM": 0.55,
        "MKD": 0.0176,
        "AMD": 0.0026,
        "GEL": 0.37,
        "KZT": 0.0021,
        "UZS": 0.000079,
        "KGS": 0.0116,
        "TJS": 0.091,
        "TMT": 0.286,
        "MNT": 0.00029,
        "KHR": 0.000245,
        "LAK": 0.000046,
        "MMK": 0.00048,
        "BDT": 0.0085,
        "NPR": 0.0075,
        "BTN": 0.012,
        "LKR": 0.0033,
        "FJD": 0.44,
        "TOP": 0.42,
        "WST": 0.37,
        "VUV": 0.0082,
        "PGK": 0.26,
        "SBD": 0.12,
        "MVR": 0.065,
        "BND": 0.74,
        "PYG": 0.00013,
        "UYU": 0.025,
        "BOB": 0.145,
        "PAB": 1.00,
        "HNL": 0.040,
        "NIO": 0.027,
        "GTQ": 0.129,
        "BZD": 0.50,
        "BBD": 0.50,
        "JMD": 0.0064,
        "TTD": 0.147,
        "XCD": 0.370,
        "BSD": 1.00,
        "ANG": 0.559,
        "KYD": 1.20,
        "BMD": 1.00,
        "FKP": 1.27
    }

    def convert_to_usd(value):

        if pd.isna(value):
            return np.nan

        value = str(value).strip()

        if value == "":
            return np.nan

        # Determine currency
        if value.startswith("AU$"):
            currency = "AUD"

        elif value.startswith("£"):
            currency = "GBP"

        elif value.startswith("€"):
            currency = "EUR"

        else:
            match = re.match(r"([A-Z]{3})", value)

            if match:
                currency = match.group(1)

            else:
                return np.nan

        # Find numeric amount
        number_match = re.search(
            r"-?\d+(?:\.\d+)?",
            value.replace(",", "")
        )

        if not number_match:
            return np.nan

        amount = float(number_match.group())

        # Million / billion
        if "billion" in value.lower():
            amount *= 1_000_000_000

        elif "million" in value.lower():
            amount *= 1_000_000

        rate = usd_rates.get(currency)

        if rate is None:
            return np.nan

        return amount * rate

    df["Economic_Impact_USD"] = df["Economic_Impact"].apply(
        convert_to_usd
    )

    # Invalid negative values and extreme data-entry errors
    df.loc[
        (df["Economic_Impact_USD"] <= 0) |
        (df["Economic_Impact_USD"] > 2_000_000_000),
        "Economic_Impact_USD"
    ] = np.nan

    df["Economic_Impact_USD_Millions"] = (
        df["Economic_Impact_USD"] / 1_000_000
    )

    return df


# --------------------------------------------------
# LOAD + CLEAN DATA
# --------------------------------------------------

try:

    raw_data = load_data(
        "data/festival_data.csv"
    )

except FileNotFoundError:

    st.error(
        "festival_data.csv was not found. "
        "Place it inside the data folder."
    )

    st.stop()


data = clean_data(raw_data)


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🎵 Music Festival Investment Dashboard")

st.write(
    "This dashboard helps festival organizers, tourism agencies, "
    "event planners, investors, and analysts explore festival "
    "attendance, music genres, and economic impact across regions."
)

st.subheader("Business Question")

st.write(
    "What regions and music genres may offer attractive "
    "opportunities for festival investment?"
)


# --------------------------------------------------
# SIDEBAR FILTERS
# 3+ INTERACTIVE CONTROLS
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")


# Control 1 - Region

regions = sorted(
    data["Region"].dropna().unique()
)

selected_regions = st.sidebar.multiselect(
    "Select Region",
    regions
)


# Control 2 - Genre

genres = sorted(
    data["Music_Genre"].dropna().unique()
)

selected_genres = st.sidebar.multiselect(
    "Select Music Genre",
    genres
)


# Control 3 - Attendance

attendance_values = data[
    "Attendance_Numbers"
].dropna()

min_attendance = int(attendance_values.min())
max_attendance = int(attendance_values.max())

attendance_range = st.sidebar.slider(
    "Attendance Range",
    min_value=min_attendance,
    max_value=max_attendance,
    value=(min_attendance, max_attendance)
)


# Control 4

show_data = st.sidebar.checkbox(
    "Show Cleaned Dataset"
)


# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------

filtered_data = data.copy()

if selected_regions:

    filtered_data = filtered_data[
        filtered_data["Region"].isin(selected_regions)
    ]

if selected_genres:

    filtered_data = filtered_data[
        filtered_data["Music_Genre"].isin(selected_genres)
    ]

filtered_data = filtered_data[
    (
        filtered_data["Attendance_Numbers"].isna()
    )
    |
    (
        filtered_data["Attendance_Numbers"].between(
            attendance_range[0],
            attendance_range[1]
        )
    )
]


# --------------------------------------------------
# SUMMARY METRICS
# --------------------------------------------------

st.subheader("Festival Market Overview")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Festivals",
    len(filtered_data)
)

average_attendance = filtered_data[
    "Attendance_Numbers"
].mean()

col2.metric(
    "Average Attendance",
    f"{average_attendance:,.0f}"
    if pd.notna(average_attendance)
    else "N/A"
)

average_impact = filtered_data[
    "Economic_Impact_USD_Millions"
].mean()

col3.metric(
    "Average Economic Impact",
    f"${average_impact:,.1f}M"
    if pd.notna(average_impact)
    else "N/A"
)


# --------------------------------------------------
# VISUALIZATION 1
# Average Attendance by Region
# --------------------------------------------------

st.subheader("1. Average Festival Attendance by Region")

region_attendance = (
    filtered_data
    .groupby("Region")["Attendance_Numbers"]
    .mean()
    .dropna()
    .sort_values(ascending=False)
)

fig1, ax1 = plt.subplots()

region_attendance.plot(
    kind="bar",
    ax=ax1
)

ax1.set_xlabel("Region")
ax1.set_ylabel("Average Attendance")
ax1.set_title("Average Attendance by Region")

plt.xticks(rotation=45)

st.pyplot(fig1)


# --------------------------------------------------
# VISUALIZATION 2
# Economic Impact by Genre
# --------------------------------------------------

st.subheader(
    "2. Music Genres by Average Economic Impact"
)

genre_impact = (
    filtered_data
    .groupby("Music_Genre")[
        "Economic_Impact_USD_Millions"
    ]
    .mean()
    .dropna()
    .nlargest(10)
    .sort_values()
)

fig2, ax2 = plt.subplots()

genre_impact.plot(
    kind="barh",
    ax=ax2
)

ax2.set_xlabel(
    "Average Economic Impact (USD Millions)"
)

ax2.set_ylabel(
    "Music Genre"
)

ax2.set_title(
    "Top Genres by Average Economic Impact"
)

st.pyplot(fig2)


# --------------------------------------------------
# VISUALIZATION 3
# Histogram
# --------------------------------------------------

st.subheader(
    "3. Distribution of Festival Attendance"
)

fig3 = plot_histogram(
    filtered_data,
    "Attendance_Numbers",
    15,
    "Festival Attendance Distribution"
)

st.pyplot(fig3)


# --------------------------------------------------
# INVESTMENT COMPARISON TABLE
# --------------------------------------------------

st.subheader(
    "Region and Genre Comparison"
)

comparison = (
    filtered_data
    .groupby(
        ["Region", "Music_Genre"]
    )
    .agg(
        Festivals=(
            "Festival_Name",
            "count"
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
    [
        "Average_Economic_Impact_USD_Millions",
        "Average_Attendance"
    ],
    ascending=False
)

st.dataframe(
    comparison,
    use_container_width=True
)


# --------------------------------------------------
# OPTIONAL DATA DETAILS
# --------------------------------------------------

if show_data:

    st.subheader(
        "Cleaned Festival Dataset"
    )

    print_results(filtered_data)


with st.expander(
    "Missing Values"
):

    print_results(
        check_missing(data)
    )


with st.expander(
    "Summary Statistics"
):

    print_results(
        data_stats(data)
    )


with st.expander(
    "Region × Genre Table"
):

    print_results(
        group_by(
            data,
            "Region",
            "Music_Genre"
        )
    )


# --------------------------------------------------
# FOOTNOTE
# --------------------------------------------------

st.caption(
    "Economic impact values are converted to approximate USD "
    "values for comparison. Obvious invalid and extreme data-entry "
    "values are excluded from numeric calculations."
)