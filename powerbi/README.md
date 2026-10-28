# Power BI version: "Does price buy a better rating?"

This folder rebuilds the top of the Streamlit dashboard as a single Power BI report page.
The page has filters, four KPI cards, and the two charts behind insights 1 and 2 in the
main README.

| File | What it is |
|---|---|
| [`load_data.pq`](load_data.pq) | Power Query script. Loads the cleaned CSV from this repo and adds a price-band column. |
| [`measures.dax`](measures.dax) | The five DAX measures the page uses. |
| [`theme.json`](theme.json) | Report theme with the same colours as the Streamlit app. |

There are two ways to build it:

- **Power BI Desktop** is free but runs on Windows only. See
  [Build in Power BI Desktop](#build-in-power-bi-desktop).
- **Power BI on the web** works in any browser, including on a Mac. You need a work or
  school account, because Microsoft doesn't accept personal emails like Gmail. See
  [Build in Power BI on the web](#build-in-power-bi-on-the-web).

## Build in Power BI Desktop

This takes about 15 minutes.

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

## Build in Power BI on the web

This takes about 20 minutes. The web editor can do everything this page needs, but some
menus are in different places from Desktop.

**1. Load the data**
- Sign in at [app.powerbi.com](https://app.powerbi.com) with your work or school account.
- Choose **Create → Get data**. This opens Power Query in the browser.
- The easiest way in is **Blank query**: paste the whole of `load_data.pq` and continue.
  This also adds the price-band columns.
- If Blank query isn't offered, choose **Text/CSV** and enter this URL as the file path:
  `https://raw.githubusercontent.com/kamboj-sajan/Zomato-Data-Analysis-Dashboard-main/main/data/zomato_bangalore_clean.csv`
- If you're asked how to sign in to the data source, choose **Anonymous**.
- Name the query **`Restaurants`**.
- At the last step, choose **Create a semantic model only**. This opens the model editor.

**2. Switch to editing mode**
- The model opens in Viewing mode. Use the toggle at the top right to switch to **Editing**.
- From here, changes save automatically and there is no undo. Version history can restore
  an earlier state.

**3. Add the price-band columns (only if you used Text/CSV)**
- Select the `Restaurants` table and choose **New column**.
- Add `Price Band`, then `Price Band Order`, from the bottom of `measures.dax`.

**4. Sort the price bands in order**
- Select the **Price Band** column.
- In the **Properties** pane, set **Sort by column** to **Price Band Order**.

**5. Add the measures**
- Click the `Restaurants` table name, not a measure inside it, and choose **New measure**.
  The formula bar should start with `Measure =`. If it shows a different formula, you're
  editing an existing measure, and pasting over it causes a "circular dependency" error.
- Add the measures from `measures.dax` one at a time, and set each one's format in the
  **Properties** pane.

**6. Build the page**
- Choose **New report**. The report editor opens in a new tab.
- Build the same layout as step 5 of the Desktop guide.
- If the Restaurant Count card shows "9K", put `Restaurant Count Label` from `measures.dax`
  on the card instead. It shows the full number, 9,359.
- The theme is optional. If **View → Themes → Browse for themes** isn't there, colour the
  table-booking chart by hand in **Format → Columns → Colors**: `Yes` = `#2A78D6`,
  `No` = `#EB6834`.
- **Save** the report.

**If a button is greyed out:** some organisations switch off model editing on the web.
Hover over the button to see the reason. If your school or employer has turned it off, use
Power BI Desktop on a Windows PC instead.

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

- **Desktop:** save the file as `powerbi/zomato_overview.pbix` and commit it.
- **Web:** the report is saved in your Power BI workspace, not in this repo. Export it with
  **File → Export → PDF**, or take a screenshot, and commit that as
  `powerbi/zomato_overview.png`.

Either way, add a screenshot of the page to the main README so visitors without Power BI
can see it.
