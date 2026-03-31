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
file_path = r"Final data.xlsx"
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
    "Nepali": "#8C93F4",              # blue
    "Punjabi": "#F49EEB",             # red
    "Hindi": "#F4791A",               # green
    "Urdu": "#87DB8B",                # purple
    "Sinhalese": "#1E6E17",           # orange
    "Bengali": "#19D3F3",             # light blue
    "Gujarati": "#FF6692",            # pink
    "Marathi": "#97DAF5",             # light green
    "Sindhi": "#EBF561",              # light purple
    "Dhivehi": "#52FEDC",             # yellow
    "Indo-Aryan, nec": "#15157F",     # soft blue
    "Fijian Hindustani": "#382B27",   # coral
    "Konkani": "#45DD63",             # teal-green
    "Assamese": "#7F6CA3"             # lavender
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
    
state_df = pd.read_excel(r"lang_state.xlsx")
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
st.subheader("🧩 Language → State Mapping")

# -------------------------------
# LANGUAGES
# -------------------------------
languages = [
    "Bengali","Gujarati","Hindi","Konkani","Marathi","Nepali",
    "Punjabi","Sindhi","Sinhalese","Urdu","Assamese",
    "Dhivehi","Kashmiri","Oriya","Fijian Hindustani"
]

# -------------------------------
# DEFAULT MAPPING
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
    "Sinhalese": ["Sri Lanka"],
    "Assamese": ["Assam"],
    "Dhivehi": ["Maldives"],
    "Kashmiri": ["Kashmir"],
    "Oriya": ["Odisha"],
    "Fijian Hindustani": ["Fiji"]
}

# -------------------------------
# ALL STATES
# -------------------------------
all_states = [
    "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh",
    "Goa","Gujarat","Haryana","Himachal Pradesh","Jharkhand",
    "Karnataka","Kerala","Madhya Pradesh","Maharashtra","Manipur",
    "Meghalaya","Mizoram","Nagaland","Odisha","Punjab",
    "Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura",
    "Uttar Pradesh","Uttarakhand","West Bengal",
    "Kashmir","Fiji","Pakistan","Sri Lanka","Maldives"
]

# -------------------------------
# UI (MULTISELECT)
# -------------------------------
language_state_mapping = {}
cols = st.columns(3)

for i, lang in enumerate(languages):
    with cols[i % 3]:
        language_state_mapping[lang] = st.multiselect(
            f"{lang}",
            options=all_states,
            default=default_mapping.get(lang, [])
        )

# -------------------------------
# SHOW CURRENT MAPPING
# -------------------------------
mapping_display = pd.DataFrame([
    {
        "Language": lang,
        "States": ", ".join(states) if states else "—"
    }
    for lang, states in language_state_mapping.items()
])

st.markdown("### 📋 Current Mapping")
st.dataframe(mapping_display, use_container_width=True)

# -------------------------------
# CREATE EXPLODED MAPPING (FOR GRAPH)
# -------------------------------
mapping_rows = []
for lang, states in language_state_mapping.items():
    for state in states:
        mapping_rows.append({"Language": lang, "State": state})

mapping_df = pd.DataFrame(mapping_rows)

# -------------------------------
# 🔥 IMPORTANT: USE FILTERED DATA
# -------------------------------
merged = filtered.merge(mapping_df, on="Language", how="left")

# -------------------------------
# 1️⃣ CLEAN TABLE (NO DUPLICATION)
# -------------------------------
suburb_lang = (
    filtered.groupby(["Suburb", "Language"])["Count"]
    .sum()
    .reset_index()
)

suburb_lang["Indian State(s)"] = suburb_lang["Language"].apply(
    lambda x: ", ".join(language_state_mapping.get(x, []))
)

final_df = suburb_lang.rename(columns={"Count": "Population"})

st.subheader("📊 Suburb → Language → Indian State Mapping")
st.dataframe(final_df.sort_values(["Suburb","Population"], ascending=[True, False]), use_container_width=True)

# -------------------------------
# 2️⃣ STATE-LEVEL GRAPH (EXPLODED VIEW)
# -------------------------------
suburb_state = (
    merged.groupby(["Suburb", "State"])["Count"]
    .sum()
    .reset_index()
)

# 🎨 STATE COLORS SAME AS LANGUAGE
state_color_map = {}
for lang, states in language_state_mapping.items():
    for state in states:
        state_color_map[state] = color_map.get(lang, "#CCCCCC")

st.subheader("📍 Suburb → Indian State Distribution")

tab1, tab2 = st.tabs(["📊 Graph", "📋 Data"])

with tab1:
    fig = px.bar(
        suburb_state,
        x="Suburb",
        y="Count",
        color="State",
        color_discrete_map=state_color_map,
        title="Suburb-wise Indian State Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.dataframe(suburb_state, use_container_width=True)

# -------------------------------
# 3️⃣ TOP LANGUAGE + STATES PER SUBURB
# -------------------------------
top_lang_suburb = (
    filtered.groupby(["Suburb", "Language"])["Count"]
    .sum()
    .reset_index()
    .sort_values(["Suburb", "Count"], ascending=[True, False])
    .groupby("Suburb")
    .first()
    .reset_index()
)

top_lang_suburb["Indian State(s)"] = top_lang_suburb["Language"].apply(
    lambda x: ", ".join(language_state_mapping.get(x, []))
)

st.subheader("🏆 Top Language → Indian States per Suburb")
st.dataframe(top_lang_suburb, use_container_width=True)