# Power BI version: "Does price buy a better rating?"

This folder rebuilds the top of the Streamlit dashboard as a single Power BI report page.
The page has filters, four KPI cards, and the two charts behind insights 1 and 2 in the
main README.

| File | What it is |
|---|---|
| [`load_data.pq`](load_data.pq) | Power Query script. Loads the cleaned CSV from this repo and adds a price-band column. |
| [`measures.dax`](measures.dax) | The five DAX measures the page uses. |
| [`theme.json`](theme.json) | Report theme with the same colours as the Streamlit app. |

> **Requirements:** Power BI Desktop (free) runs on Windows only. On a Mac, use a Windows
> VM. Power BI on the web can also show the finished report, but it needs a work or
> school account.

## Build steps (about 15 minutes)

**1. Load the data**
- Open Power BI Desktop and choose **Home → Transform data**.
- Choose **New Source → Blank Query → Advanced Editor**, then paste the whole of `load_data.pq`.
- Rename the query to **`Restaurants`**, then choose **Close & Apply**.
- If you're asked about privacy, choose *Anonymous* access for `raw.githubusercontent.com`.

**2. Sort the price bands in order**
- In the Data view, select the **Price Band** column.
- Choose **Column tools → Sort by column → Price Band Order**.

**3. Add the measures**
- Choose **Modeling → New measure**.
- Add each measure in `measures.dax` one at a time, and set the format given in its comment.

**4. Apply the theme**
- Choose **View → Themes → Browse for themes**, then pick `theme.json`.

**5. Lay out the page.** The page is 1280 × 720 by default.

| Area | Visual | Fields |
|---|---|---|
| Top strip | Text box | Title: "Zomato Bangalore: Does Price Buy a Better Rating?" |
| Left column | 4 slicers (dropdown) | `location`, `primary_type`, `online_order`, `book_table` |
| Top row | 4 **Card** visuals | `Restaurant Count`, `Avg Rating`, `Rated 4.0+ %`, `Median Cost for Two` |
| Bottom left | **Clustered column chart** | X-axis: `Price Band` · Y-axis: `Rated 4.0+ %` · data labels on |
| Bottom right | **Clustered column chart** | X-axis: `Price Band` · Y-axis: `Rated 4.0+ %` · Legend: `book_table` |

On both charts:
- Sort the x-axis by **Price Band** ascending: choose **⋯ → Sort axis**.
- Turn off the "Sum of" auto-titles.
- Name the charts "Share rated 4.0+, by cost for two" and "…split by table booking".

## Check your numbers

With no filters applied, the visuals should match the Streamlit app exactly.

| Visual | Expected |
|---|---|
| Restaurant Count | 9,359 |
| Avg Rating | 3.63 |
| Rated 4.0+ % | 23% |
| Median Cost for Two | ₹400 |

| Price band | Rated 4.0+ (all) | With table booking | Without table booking |
|---|---|---|---|
| ≤ ₹300 | 12% | 29% ⚠ only 7 restaurants | 12% |
| ₹301–500 | 16% | 43% | 16% |
| ₹501–800 | 28% | 59% | 24% |
| ₹801–1,500 | 57% | 78% | 34% |
| > ₹1,500 | 73% | 85% | 36% |

The Streamlit app hides any bar based on fewer than 20 restaurants, so it leaves out the
≤ ₹300 table-booking bar. To do the same in Power BI, add a visual-level filter on that
chart: **Restaurant Count is greater than or equal to 20**.

## Saving

Save the file as `powerbi/zomato_overview.pbix` and commit it. A screenshot of the page in
the main README helps visitors who don't have Power BI.
