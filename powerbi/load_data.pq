// Power Query (M) — loads the cleaned dataset straight from this GitHub repo.
// Power BI Desktop: Home > Transform data > New Source > Blank Query > Advanced Editor, paste this,
// then rename the query to "Restaurants".
// Working offline? Replace the Web.Contents(...) call with File.Contents("C:\path\to\zomato_bangalore_clean.csv").
let
    Source = Csv.Document(
        Web.Contents("https://raw.githubusercontent.com/kamboj-sajan/Zomato-Data-Analysis-Dashboard-main/main/data/zomato_bangalore_clean.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(
        Promoted,
        {
            {"name", type text}, {"location", type text}, {"primary_type", type text},
            {"rest_type", type text}, {"cuisines", type text}, {"online_order", type text},
            {"book_table", type text}, {"rate", type number}, {"votes", Int64.Type},
            {"cost_for_two", Int64.Type}, {"listed_in", type text}, {"address", type text}
        },
        "en-US"
    ),
    // Same price bands as the Streamlit dashboard
    WithBand = Table.AddColumn(
        Typed, "Price Band",
        each if [cost_for_two] <= 300 then "≤ ₹300"
            else if [cost_for_two] <= 500 then "₹301–500"
            else if [cost_for_two] <= 800 then "₹501–800"
            else if [cost_for_two] <= 1500 then "₹801–1,500"
            else "> ₹1,500",
        type text
    ),
    // Used with "Sort by column" so the bands plot cheapest -> most expensive
    WithBandOrder = Table.AddColumn(
        WithBand, "Price Band Order",
        each if [cost_for_two] <= 300 then 1
            else if [cost_for_two] <= 500 then 2
            else if [cost_for_two] <= 800 then 3
            else if [cost_for_two] <= 1500 then 4
            else 5,
        Int64.Type
    )
in
    WithBandOrder
