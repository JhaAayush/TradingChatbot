import requests
import pandas as pd
import spacy
from textblob import TextBlob
import os
from collections import defaultdict

API_URL = "https://newsapi.org/v2/top-headlines?category=business&apiKey=d3ac6eee157a42e4abda6f20c5aa9e89"
CSV_PATH = "companies_sentiment.csv"

nlp = spacy.load("en_core_web_sm")

EXCLUDE = {"news", "yahoo", "cnbc", "cnn", "bbc", "bloomberg", "times", "journal", "reuters", "hollywood", "abp"}

def fetch_headlines(api_url=API_URL):
    print("Fetching news data...")
    response = requests.get(api_url)
    data = response.json()
    return [a['title'] for a in data.get("articles", []) if a.get('title')]

def extract_organizations(text):
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ == "ORG"]

def get_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    else:
        return "Neutral"

def main():
    headlines = fetch_headlines()
    records = []

    for headline in headlines:
        orgs = extract_organizations(headline)
        sent = get_sentiment(headline)
        for org in orgs:
            org_l = org.strip().lower()
            if org_l not in EXCLUDE and 2 < len(org) < 40:
                records.append({
                    "Company": org.strip(),
                    "Sentiment": sent,
                    "Headline": headline
                })

    # Keep only latest entry per company (drop duplicates, keep last)
    df = pd.DataFrame(records)
    if not df.empty:
        df = df.drop_duplicates(["Company"], keep='last')
        if os.path.exists(CSV_PATH):
            old = pd.read_csv(CSV_PATH)
            combined = pd.concat([old, df]).drop_duplicates(["Company"], keep='last')
        else:
            combined = df
        combined.to_csv(CSV_PATH, index=False)
        print(f"Updated {CSV_PATH} with {len(df)} companies from latest news.")
    else:
        print("No companies found in today's headlines.")

if __name__ == "__main__":
    main()
