# Music Festival Investment Dashboard

## BAN 601 Final Project

This project is an interactive Streamlit dashboard designed to help festival organizers, tourism agencies, event planners, investors, and analysts explore music festival markets across different countries and regions.

## Business Problem

Music festival organizers and investors need to decide which markets and music genres may provide attractive opportunities before committing resources to an event.

Festival opportunities can vary based on attendance, music genre, location, audience demographics, and economic impact.

The dashboard allows users to explore these factors and compare festival markets to support more informed planning and investment decisions.

## Business Question

**What regions and music genres may offer attractive opportunities for festival investment?**

The dashboard helps users explore questions such as:

- Which countries and regions have strong festival attendance?
- Which music genres are associated with higher economic impact?
- How do festival characteristics differ across locations and genres?
- Which combinations of region and music genre may deserve further consideration?

## Dataset

The project uses the **European and International Music Festivals 2024** dataset.

The dataset contains festival information including:

- Festival name
- Country/location
- Region
- Attendance
- Audience age
- Visitor demographics
- Music genre
- Economic impact

The dataset required cleaning because it included missing values, spelling inconsistencies, invalid attendance values, multiple currencies, and extreme data-entry errors.

Economic-impact values are standardized to U.S. dollars for comparison.

## Dashboard Features

The Streamlit dashboard includes:

- Region filter
- Country filter
- Music genre filter
- Attendance range slider
- Cleaned dataset display option
- Summary business metrics
- Average attendance by country visualization
- Economic impact by music genre visualization
- Festival attendance distribution
- Region and genre comparison table
- Missing-value analysis
- Summary statistics
- Data quality verification

## Python Functions

The project includes six main programming functions:

1. `load_data()` – loads the festival dataset
2. `check_missing()` – identifies missing values
3. `data_stats()` – generates summary statistics
4. `group_by()` – compares categorical variables
5. `plot_histogram()` – creates a distribution visualization
6. `print_results()` – displays results in the Streamlit application

## How to Run the App

Install the required packages:

```bash
pip install -r requirements.txt