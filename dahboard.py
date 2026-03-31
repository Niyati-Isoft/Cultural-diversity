import pandas as pd
import streamlit as st
import plotly.express as px
##
# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Language Dashboard", layout="wide")
from datetime import datetime
import pytz

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(layout="wide")

# -------------------------------
# GREETING
# -------------------------------
tz = pytz.timezone("Australia/Sydney")
now = datetime.now(tz)

hour = now.hour
if hour < 12:
    greeting = "Good Morning"
elif hour < 18:
    greeting = "Good Afternoon"
else:
    greeting = "Good Evening"

st.markdown(
    f"""
    <div style='text-align: center; font-size:18px; color:#6c757d;'>
    Hello, {greeting}! ({now.strftime("%a %d %b %Y, %I:%M %p — Australia/Sydney")}) 👋
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# LOGO (CENTERED)
# -------------------------------
st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    """
    <div style='text-align: center;'>
        <img src="https://b3660930.smushcdn.com/3660930/wp-content/uploads/2024/03/iSOFT-Logo-Tag-New-e1721176700423.png?lossy=2&strip=1&webp=1"
        width="220">
    </div>
    """,
    unsafe_allow_html=True
)
# -------------------------------
# LOAD DATA
# -------------------------------
file_path = r"C:\Users\NiyatiiSOFT\OneDrive - iSOFTGroup\Documents\Final data.xlsx"
df = pd.read_excel(file_path)

# -------------------------------
# CLEAN DATA
# -------------------------------
# Clean column names
df.columns = df.columns.str.strip()

# Fill merged cells (Greater column)
df["Greater"] = df["Greater"].ffill()

# Remove Total column if exists
if "Total" in df.columns:
    df = df.drop(columns=["Total"])

# -------------------------------
# TRANSFORM DATA (WIDE → LONG)
# -------------------------------
df_long = df.melt(
    id_vars=["Greater", "Suburb"],
    var_name="Language",
    value_name="Count"
)

# Remove zero values
df_long = df_long[df_long["Count"] > 0]

# -------------------------------
# SIDEBAR FILTERS (MULTI-SELECT)
# -------------------------------
st.sidebar.header("Filters")

# ---- CITY FILTER ----
city_options = ["All"] + sorted(df_long["Greater"].unique().tolist())
selected_city = st.sidebar.multiselect(
    "Select City",
    city_options,
    default=["All"]
)

# ---- SUBURB FILTER (DEPENDENT) ----
if "All" in selected_city:
    suburb_list = df_long["Suburb"].unique()
else:
    suburb_list = df_long[df_long["Greater"].isin(selected_city)]["Suburb"].unique()

suburb_options = ["All"] + sorted(suburb_list.tolist())

selected_suburb = st.sidebar.multiselect(
    "Select Suburb",
    suburb_options,
    default=["All"]
)

# ---- LANGUAGE FILTER ----
language_options = ["All"] + sorted(df_long["Language"].unique().tolist())
selected_language = st.sidebar.multiselect(
    "Select Language",
    language_options,
    default=["All"]
)


filtered = df_long.copy()

# City filter
if "All" not in selected_city:
    filtered = filtered[filtered["Greater"].isin(selected_city)]

# Suburb filter
if "All" not in selected_suburb:
    filtered = filtered[filtered["Suburb"].isin(selected_suburb)]

# Language filter
if "All" not in selected_language:
    filtered = filtered[filtered["Language"].isin(selected_language)]

# -------------------------------
# TITLE
# -------------------------------
st.title("Language → Indian State Mapping")

st.markdown(
    f"**Selected Filters →** City: `{selected_city}` | Suburb: `{selected_suburb}` | Language: `{selected_language}`"
)

# -------------------------------
# TOP 3 LANGUAGES TILE
# -------------------------------
top_lang = (
    filtered.groupby("Language")["Count"]
    .sum()
    .sort_values(ascending=False)
    .head(3)
)

col1, col2, col3 = st.columns(3)

for i, (lang, val) in enumerate(top_lang.items()):
    if i == 0:
        col1.metric("🥇 Top Language", f"{lang} ({val:,})")
    elif i == 1:
        col2.metric("🥈 Second", f"{lang} ({val:,})")
    elif i == 2:
        col3.metric("🥉 Third", f"{lang} ({val:,})")

color_map = {
    "Nepali": "#636EFA",              # blue
    "Punjabi": "#EF553B",             # red
    "Hindi": "#00CC96",               # green
    "Urdu": "#AB63FA",                # purple
    "Sinhalese": "#FFA15A",           # orange
    "Bengali": "#19D3F3",             # light blue
    "Gujarati": "#FF6692",            # pink
    "Marathi": "#B6E880",             # light green
    "Sindhi": "#FF97FF",              # light purple
    "Dhivehi": "#FECB52",             # yellow
    "Indo-Aryan, nec": "#A1A1FF",     # soft blue
    "Fijian Hindustani": "#FF8C69",   # coral
    "Konkani": "#00E396",             # teal-green
    "Assamese": "#B39DDB"             # lavender
}
# -------------------------------
# CHART 1: LANGUAGE DISTRIBUTION
# -------------------------------
lang_dist = (
    filtered.groupby("Language")["Count"]
    .sum()
    .reset_index()
    .sort_values(by="Count", ascending=False)
)

tab1, tab2 = st.tabs(["📊 Graph", "📋 Data"])

with tab1:
    fig1 = px.bar(
        lang_dist,
        x="Language",
        y="Count",
        color="Language",
        color_discrete_map=color_map,
        title="Language Distribution"
    )
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    st.dataframe(lang_dist)
# -------------------------------
# CHART 2: PIE CHART
# -------------------------------
tab1, tab2 = st.tabs(["📊 Graph", "📋 Data"])

with tab1:
    fig2 = px.pie(
        filtered,
        names="Language",
        values="Count",
        color="Language",
        color_discrete_map=color_map,
        title="Language Share"
    )
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    pie_data = (
        filtered.groupby("Language")["Count"]
        .sum()
        .reset_index()
    )
    st.dataframe(pie_data)
# -------------------------------
# CHART 3: SUBURB DRILL-DOWN
# -------------------------------
tab1, tab2 = st.tabs(["📊 Graph", "📋 Data"])

with tab1:
    fig3 = px.bar(
        filtered,
        x="Suburb",
        y="Count",
        color="Language",
        color_discrete_map=color_map,
        title="Suburb-wise Language Distribution"
    )
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    suburb_data = (
        filtered.groupby(["Suburb", "Language"])["Count"]
        .sum()
        .reset_index()
    )
    st.dataframe(suburb_data)
# -------------------------------
# CHART 4: CITY COMPARISON
# -------------------------------
city_comp = (
    filtered.groupby(["Greater", "Language"])["Count"]
    .sum()
    .reset_index()
)

city_comp = (
    filtered.groupby(["Greater", "Language"])["Count"]
    .sum()
    .reset_index()
)

tab1, tab2 = st.tabs(["📊 Graph", "📋 Data"])

with tab1:
    fig4 = px.bar(
        city_comp,
        x="Greater",
        y="Count",
        color="Language",
        color_discrete_map=color_map,
        barmode="stack",
        title="City-wise Comparison"
    )
    st.plotly_chart(fig4, use_container_width=True)

with tab2:
    st.dataframe(city_comp)
# -------------------------------
# OPTIONAL TABLE
# -------------------------------
if st.checkbox("Show Data Table"):
    st.dataframe(filtered)
    
state_df = pd.read_excel(r"C:\Users\NiyatiiSOFT\OneDrive - iSOFTGroup\Documents\lang_state.xlsx")
st.write(state_df.columns.tolist())
# Rename columns if needed
state_df.columns = state_df.columns.str.strip()

# Melt to long format
state_long = state_df.melt(
    id_vars=["State"],
    var_name="Temp",
    value_name="Language"
)

# Remove nulls
state_long = state_long.dropna()

# Clean language names
state_long["Language"] = state_long["Language"].str.replace(",", "").str.strip()

# -------------------------------
# LANGUAGE → STATE MAPPING SECTION
# -------------------------------
import streamlit as st
import pandas as pd

st.subheader("🧩 Language → State Mapping")

# -------------------------------
# 1. DEFINE LANGUAGES
# -------------------------------
languages = [
    "Bengali","Gujarati","Hindi","Konkani","Marathi","Nepali",
    "Punjabi","Sindhi","Sinhalese","Urdu","Assamese",
    "Dhivehi","Kashmiri","Oriya","Fijian Hindustani"
]

# -------------------------------
# 2. DEFAULT MAPPING (YOUR LIST)
# -------------------------------
default_mapping = {
    "Bengali": ["West Bengal", "Tripura"],
    "Gujarati": ["Gujarat"],
    "Hindi": [
        "Bihar","Chhattisgarh","Haryana","Himachal Pradesh",
        "Jharkhand","Madhya Pradesh","Rajasthan",
        "Uttar Pradesh","Uttarakhand"
    ],
    "Konkani": ["Goa"],
    "Marathi": ["Maharashtra"],
    "Nepali": ["Sikkim"],
    "Punjabi": ["Punjab"],
    "Sindhi": ["Pakistan"],
    "Urdu": ["Telangana", "Uttar Pradesh", "Bihar", "Pakistan"],
    "Sinhalese": ["Sri Lanka"],  # optional
    "Assamese": ["Assam"],
    "Dhivehi": ["Maldives"],  # optional
    "Kashmiri": ["Kashmir"],  # optional
    "Oriya": ["Odisha"],
    "Fijian Hindustani": ["Fiji"]
}

# -------------------------------
# 3. ALL STATES OPTIONS
# -------------------------------
all_states = [
    "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh",
    "Goa","Gujarat","Haryana","Himachal Pradesh","Jharkhand",
    "Karnataka","Kerala","Madhya Pradesh","Maharashtra","Manipur",
    "Meghalaya","Mizoram","Nagaland","Odisha","Punjab",
    "Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura",
    "Uttar Pradesh","Uttarakhand","West Bengal","Kashmir","Fiji","Pakistan","Sri Lanka","Maldives"
]

# -------------------------------
# 4. BUILD UI (MULTI-SELECT PER LANGUAGE)
# -------------------------------
language_state_mapping = {}

cols = st.columns(3)  # 3-column layout for clean UI

for i, lang in enumerate(languages):
    with cols[i % 3]:
        language_state_mapping[lang] = st.multiselect(
            f"{lang}",
            options=all_states,
            default=default_mapping.get(lang, [])
        )

# -------------------------------
# 5. SHOW MAPPING TABLE
# -------------------------------
st.markdown("### 📋 Current Mapping")

mapping_df = pd.DataFrame([
    {
        "Language": lang,
        "States": ", ".join(states) if states else "—"
    }
    for lang, states in language_state_mapping.items()
])

st.dataframe(mapping_df, use_container_width=True)

# -------------------------------
# 6. OPTIONAL: FILTER BY STATES
# -------------------------------
# st.sidebar.subheader("🌏 Filter by Selected States")

# selected_states = st.sidebar.multiselect(
#     "Choose States",
#     all_states
# )

# Convert selected states → languages
if selected_states:
    selected_languages_from_states = [
        lang for lang, states in language_state_mapping.items()
        if any(state in selected_states for state in states)
    ]
else:
    selected_languages_from_states = languages

# -------------------------------
# 7. FINAL FILTERED DATA (USE THIS IN YOUR MAIN DASHBOARD)
# -------------------------------
# Example: df_long should already exist in your app

try:
    filtered_by_state = df_long[
        df_long["Language"].isin(selected_languages_from_states)
    ]

except:
    st.warning("⚠️ df_long not found yet — integrate this section after your main data load.")