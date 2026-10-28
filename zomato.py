import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Resolve files relative to this script so the app runs from any working directory
BASE_DIR = Path(__file__).parent
LOGO_PATH = BASE_DIR / "zomato1.png"
DATA_PATH = BASE_DIR / "data" / "zomato_bangalore_clean.csv"

TOP_RATED = 4.0  # a restaurant rated at or above this counts as "top rated"
PRICE_BINS = [0, 300, 500, 800, 1500, float("inf")]
PRICE_LABELS = ["≤ ₹300", "₹301–500", "₹501–800", "₹801–1,500", "> ₹1,500"]
MIN_GROUP_SIZE = 20  # hide comparison bars backed by too few restaurants

# Set page config
st.set_page_config(page_title="Zomato Bangalore Restaurant Dashboard", layout="wide")

# Series colours, validated for colour-blind separation and stepped per theme
DARK_THEME = st.context.theme.type == "dark"
BLUE, ORANGE = ("#3987e5", "#d95926") if DARK_THEME else ("#2a78d6", "#eb6834")
YES_NO_COLORS = {"Yes": BLUE, "No": ORANGE}
MUTED = "#898781"
HEATMAP_SCALE = [[0, "#e34948"], [0.5, "#383835" if DARK_THEME else "#f0efec"], [1, BLUE]]

# Apply Custom Styles
st.markdown(
    """
    <style>
        /* Smooth Fade-in Animation */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .fade {
            animation: fadeIn 1.5s;
        }
        /* Custom Font */
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Ensure analysis state persists across reruns
if "analysis_started" not in st.session_state:
    st.session_state.analysis_started = False

# Show Welcome Page ONLY if analysis has NOT started
if not st.session_state.analysis_started:
    # Logo is optional — skip it if the image isn't present
    if LOGO_PATH.exists():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(str(LOGO_PATH), width="stretch")

    st.markdown("<h1 style='text-align: center;' class='fade'>🍽 Welcome to the Zomato Bangalore Restaurant Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>🔍 Explore what drives ratings across 9,000+ Bangalore restaurants</p>", unsafe_allow_html=True)

    # Center the button properly using Streamlit columns
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🚀 Let's Analyze!", key="start_analysis"):
            st.session_state.analysis_started = True
            st.rerun()

    st.stop()  # Prevents the rest of the script from running before clicking the button


# Loading Animation with Spinner
with st.spinner("🔄 Loading Data..."):
    @st.cache_data
    def load_data():
        df = pd.read_csv(DATA_PATH)
        df["price_band"] = pd.cut(df["cost_for_two"], PRICE_BINS, labels=PRICE_LABELS)
        df["top_rated"] = df["rate"] >= TOP_RATED
        return df

    df = load_data()


def style(fig):
    """Shared chart styling: rounded bar ends, compact margins."""
    fig.update_layout(barcornerradius=4, margin=dict(t=50, l=10, r=10, b=10), legend_title_text="")
    return fig


def top_rated_share_chart(data, field, n, title):
    """Share rated TOP_RATED+ for the n most common values of `field`, busiest first."""
    grp = (data.groupby(field)
               .agg(restaurants=("rate", "size"), top_share=("top_rated", "mean"), avg_rating=("rate", "mean"))
               .nlargest(n, "restaurants")
               .reset_index())
    grp["label"] = grp[field] + " (" + grp["restaurants"].map("{:,}".format) + ")"
    fig = px.bar(grp, x="top_share", y="label", orientation="h", title=title,
                 color_discrete_sequence=[BLUE],
                 labels={"top_share": f"Rated {TOP_RATED}+", "label": "", "restaurants": "Restaurants",
                         "avg_rating": "Average rating"},
                 hover_data={"label": False, "restaurants": ":,", "avg_rating": ":.2f", "top_share": ":.0%"})
    fig.update_yaxes(categoryorder="array", categoryarray=grp["label"][::-1])
    fig.update_xaxes(tickformat=".0%")
    fig.add_vline(x=data["top_rated"].mean(), line_width=1, line_color=MUTED,
                  annotation_text="Overall", annotation_position="top")
    return style(fig)


# Sidebar Filters
st.sidebar.header("🎛 Advanced Filters")

FILTER_KEYS = ["f_areas", "f_formats", "f_rating", "f_cost", "f_online", "f_booking"]


def reset_filters():
    # Drop only the filter widgets' state so the user stays on the dashboard
    for key in FILTER_KEYS:
        st.session_state.pop(key, None)


areas = sorted(df["location"].unique())
formats = df["primary_type"].value_counts().index.tolist()  # most common first
rate_min, rate_max = float(df["rate"].min()), float(df["rate"].max())
cost_max = int(df["cost_for_two"].max())

selected_areas = st.sidebar.multiselect("🏙 Select Area", areas, key="f_areas", placeholder="All areas",
                                        help="Bangalore neighbourhood. Leave empty to include every area")
selected_formats = st.sidebar.multiselect("🍽 Select Restaurant Format", formats, key="f_formats", placeholder="All formats",
                                          help="Primary format, e.g. Quick Bites or Casual Dining. Leave empty to include every format")
rating_range = st.sidebar.slider("⭐ Select Rating Range", rate_min, rate_max, (rate_min, rate_max), step=0.1, key="f_rating",
                                 help="Set minimum and maximum rating")
cost_range = st.sidebar.slider("💰 Select Cost Range (₹ for two)", 0, cost_max, (0, cost_max), step=50, key="f_cost",
                               help="Set cost range for two people")
online_order_filter = st.sidebar.checkbox("🛒 Show Only Online Order Restaurants", key="f_online",
                                          help="Show restaurants that accept online orders")
book_table_filter = st.sidebar.checkbox("📅 Show Only Table Booking Restaurants", key="f_booking",
                                        help="Show restaurants that take table reservations")
st.sidebar.button("🔄 Reset Filters", on_click=reset_filters)
st.sidebar.caption("Data: Zomato Bangalore restaurant listings (Kaggle, scraped 2019). "
                   "One row per rated restaurant.")

# Apply Filters (an empty multiselect means "all")
mask = df["rate"].between(*rating_range) & df["cost_for_two"].between(*cost_range)
if selected_areas:
    mask &= df["location"].isin(selected_areas)
if selected_formats:
    mask &= df["primary_type"].isin(selected_formats)
if online_order_filter:
    mask &= df["online_order"] == "Yes"
if book_table_filter:
    mask &= df["book_table"] == "Yes"
df_filtered = df[mask]

st.title("🍽 Zomato Bangalore Restaurant Dashboard")

if df_filtered.empty:
    st.warning("⚠ No data found. Try adjusting filters!")
else:
    with st.expander("📊 Key Insights", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Restaurants Analyzed", f"{len(df_filtered):,}")
        c2.metric("Average Rating", f"{df_filtered['rate'].mean():.2f}")
        c3.metric(f"Rated {TOP_RATED}+", f"{df_filtered['top_rated'].mean():.0%}")
        c4.metric("Median Cost for Two", f"₹{df_filtered['cost_for_two'].median():,.0f}")

    st.subheader("💰 Does Price Buy a Better Rating?")
    by_band = (df_filtered.groupby("price_band", observed=True)
                          .agg(restaurants=("rate", "size"), top_share=("top_rated", "mean"), avg_rating=("rate", "mean"))
                          .reset_index())
    fig1 = px.bar(by_band, x="price_band", y="top_share", text="top_share",
                  title=f"Share of restaurants rated {TOP_RATED}+, by cost for two",
                  color_discrete_sequence=[BLUE],
                  labels={"price_band": "Cost for two", "top_share": f"Rated {TOP_RATED}+",
                          "restaurants": "Restaurants", "avg_rating": "Average rating"},
                  hover_data={"restaurants": ":,", "avg_rating": ":.2f", "top_share": ":.0%"})
    fig1.update_traces(texttemplate="%{text:.0%}", textposition="outside", cliponaxis=False)
    fig1.update_yaxes(tickformat=".0%")
    st.plotly_chart(style(fig1), width="stretch")

    st.subheader("🛒 Online Ordering & Table Booking")
    service_cols = st.columns(2)
    for col, (field, label) in zip(service_cols, {"online_order": "Online ordering", "book_table": "Table booking"}.items()):
        grp = (df_filtered.groupby(["price_band", field], observed=True)
                          .agg(restaurants=("rate", "size"), top_share=("top_rated", "mean"))
                          .reset_index())
        grp = grp[grp["restaurants"] >= MIN_GROUP_SIZE]
        if grp.empty:
            col.info(f"Not enough restaurants to compare {label.lower()}.")
            continue
        fig = px.bar(grp, x="price_band", y="top_share", color=field, barmode="group",
                     title=f"{label}: share rated {TOP_RATED}+, by cost for two",
                     color_discrete_map=YES_NO_COLORS,
                     category_orders={field: ["Yes", "No"], "price_band": PRICE_LABELS},
                     labels={"price_band": "Cost for two", "top_share": f"Rated {TOP_RATED}+",
                             "restaurants": "Restaurants", field: label},
                     hover_data={"restaurants": ":,", "top_share": ":.0%"})
        fig.update_yaxes(tickformat=".0%")
        fig.update_layout(bargroupgap=0.08)
        col.plotly_chart(style(fig), width="stretch")
    st.caption(f"Bars backed by fewer than {MIN_GROUP_SIZE} restaurants are hidden.")

    scatter_col, heatmap_col = st.columns([2, 1])
    with scatter_col:
        st.subheader("📈 Cost vs. Rating")
        fig4 = px.scatter(df_filtered, x="cost_for_two", y="rate", color="book_table", log_x=True, opacity=0.5,
                          title="Each dot is a restaurant",
                          color_discrete_map=YES_NO_COLORS,
                          # Draw the larger "No" group first so table-booking restaurants stay visible on top
                          category_orders={"book_table": ["No", "Yes"]},
                          hover_name="name",
                          hover_data={"location": True, "primary_type": True, "votes": ":,", "book_table": False},
                          labels={"cost_for_two": "Cost for two (₹, log scale)", "rate": "Rating",
                                  "book_table": "Table booking", "location": "Area", "primary_type": "Format",
                                  "votes": "Votes"})
        fig4.update_traces(marker=dict(size=8))
        fig4.update_xaxes(tickvals=[50, 100, 200, 500, 1000, 2000, 5000], tickprefix="₹", tickformat=",")
        st.plotly_chart(style(fig4), width="stretch")
    with heatmap_col:
        st.subheader("🔥 Correlation Heatmap")
        heatmap_data = (df_filtered[["rate", "cost_for_two", "votes"]]
                        .rename(columns={"rate": "Rating", "cost_for_two": "Cost for two", "votes": "Votes"})
                        .corr(method="spearman"))
        fig_hm = px.imshow(heatmap_data, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale=HEATMAP_SCALE,
                           title="Rank (Spearman) correlation")
        fig_hm.update_layout(coloraxis_showscale=False)  # every cell is labelled, so the scale bar is redundant
        st.plotly_chart(style(fig_hm), width="stretch")

    format_col, area_col = st.columns(2)
    with format_col:
        st.subheader("🍩 Restaurant Formats")
        st.plotly_chart(top_rated_share_chart(df_filtered, "primary_type", 10,
                                              f"Share rated {TOP_RATED}+ in the 10 most common formats"),
                        width="stretch")
    with area_col:
        st.subheader("🏙 Busiest Areas")
        st.plotly_chart(top_rated_share_chart(df_filtered, "location", 15,
                                              f"Share rated {TOP_RATED}+ in the 15 busiest areas"),
                        width="stretch")

    st.subheader("📋 Top 10 Restaurants by Rating")
    top_restaurants = (df_filtered.sort_values(by=["rate", "votes"], ascending=[False, False]).head(10)
                       [["name", "location", "primary_type", "cuisines", "rate", "votes", "cost_for_two"]])
    st.dataframe(top_restaurants, hide_index=True, width="stretch",
                 column_config={"name": "Restaurant", "location": "Area", "primary_type": "Format",
                                "cuisines": st.column_config.TextColumn("Cuisines", width="medium"), "rate": st.column_config.NumberColumn("Rating", format="%.1f"),
                                "votes": st.column_config.NumberColumn("Votes", format="localized"),
                                "cost_for_two": st.column_config.NumberColumn("Cost for Two (₹)", format="localized")})
