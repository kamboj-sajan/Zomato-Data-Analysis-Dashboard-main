"""
Build the cleaned dataset used by the dashboard from the raw Zomato Bangalore export.

Raw data: "Zomato Bangalore Restaurants" (Kaggle, himanshupoddar/zomato-bangalore-restaurants),
file zomato.csv (~574 MB, 51,717 rows). Not committed — download it, then run:

    python scripts/prepare_data.py path/to/zomato.csv

The raw file has one row per *listing*: the same restaurant repeats under several
browse categories (Delivery, Dine-out, ...) and zones. This script collapses it to
one row per restaurant (name + address) and parses rating and cost into numbers.
"""
import sys
from pathlib import Path

import pandas as pd

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "zomato_bangalore_clean.csv"

# Heavy free-text columns (reviews, menus) aren't used by the dashboard
USE_COLS = ['name', 'address', 'online_order', 'book_table', 'rate', 'votes', 'location',
            'rest_type', 'cuisines', 'approx_cost(for two people)', 'listed_in(type)']


def fix_mojibake(text):
    """Undo repeated UTF-8 -> Latin-1 mis-decoding in the scrape, e.g. "CafÃÂ©" -> "Café"."""
    for _ in range(10):
        try:
            fixed = text.encode('latin-1').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
        if fixed == text:
            break
        text = fixed
    # Leftover Windows-1252 punctuation such as \x92 -> ’
    try:
        return text.encode('latin-1').decode('cp1252')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


def main(raw_path):
    df = pd.read_csv(raw_path, usecols=USE_COLS)

    # Repair before de-duplicating: the same name appears with different levels of corruption
    for col in ['name', 'address']:
        df[col] = df[col].map(fix_mojibake).str.strip()

    # "4.1/5" / "3.9 /5" -> 4.1 ; "NEW" and "-" (not yet rated) -> NaN
    df['rate'] = pd.to_numeric(df['rate'].str.replace('/5', '').str.strip(), errors='coerce')
    # "1,200" -> 1200
    df['approx_cost(for two people)'] = pd.to_numeric(
        df['approx_cost(for two people)'].str.replace(',', ''), errors='coerce')

    # Remember every browse category a restaurant is listed under before collapsing
    listed_in = (df.groupby(['name', 'address'])['listed_in(type)']
                   .agg(lambda s: '|'.join(sorted(s.unique()))))

    # One row per restaurant; where scrapes disagree, keep the one with the most votes
    df = (df.sort_values('votes', ascending=False)
            .drop_duplicates(['name', 'address'])
            .drop(columns='listed_in(type)')
            .join(listed_in, on=['name', 'address']))

    # Primary format, e.g. "Cafe, Casual Dining" -> "Cafe"
    df['primary_type'] = df['rest_type'].str.split(',').str[0].str.strip()
    df['cuisines'] = df['cuisines'].str.strip()

    # The dashboard analyses rated restaurants with a known location and price
    df = df.dropna(subset=['rate', 'location', 'primary_type', 'approx_cost(for two people)'])

    df = df.rename(columns={'approx_cost(for two people)': 'cost_for_two',
                            'listed_in(type)': 'listed_in'})
    df['cost_for_two'] = df['cost_for_two'].astype(int)
    df = df[['name', 'location', 'primary_type', 'rest_type', 'cuisines', 'online_order',
             'book_table', 'rate', 'votes', 'cost_for_two', 'listed_in', 'address']]
    df = df.sort_values(['location', 'name']).reset_index(drop=True)

    OUT_PATH.parent.mkdir(exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(df):,} restaurants to {OUT_PATH}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/prepare_data.py path/to/zomato.csv")
    main(sys.argv[1])
