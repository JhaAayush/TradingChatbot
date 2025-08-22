import pandas as pd
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import finnhub

CSV_PATH = "companies_sentiment.csv"

API_KEY = "d2g9p29r01qq1lhu2l6gd2g9p29r01qq1lhu2l70"

class ActionStockAdvice(Action):
    def name(self) -> str:
        return "action_stock_advice"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict):

        try:
            data = pd.read_csv(CSV_PATH)

            # Get positive and negative sentiment companies
            positive = data[data['Sentiment'].str.lower() == 'positive']['Company'].tolist()
            negative = data[data['Sentiment'].str.lower() == 'negative']['Company'].tolist()
            # neutral = data[data['Sentiment'].str.lower() == 'neutral']['Company'].tolist()
            # Build dynamic reply
            response_parts = []
            if positive:
                response_parts.append(f"You can consider investing in: {', '.join(positive)}.")
            if negative:
                response_parts.append(f"And you should probably avoid investing in: {', '.join(negative)}.")
            # if neutral:
            #     response_parts.append(f"I am unsure about these companies: {', '.join(positive)}. The sentiment around them seems to be neutral.")
   

            if not response_parts:
                response = "I couldn't find any sentiment data in my records."
            else:
                response = " ".join(response_parts)

            dispatcher.utter_message(text=response)

        except Exception as e:
            dispatcher.utter_message(text=f"Error fetching stock advice: {str(e)}")
        
        return []



import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import finnhub

NEWS_API_KEY = "d3ac6eee157a42e4abda6f20c5aa9e89"
NEWS_URL_TEMPLATE = "https://newsapi.org/v2/everything?q={company_name}&apiKey=" + NEWS_API_KEY

class ActionGiveCompanyInfo(Action):
    def name(self) -> str:
        return "action_give_company_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict):

        company = tracker.get_slot("company")
        if not company:
            dispatcher.utter_message(text="Please tell me which company you're asking about.")
            return []

        finnhub_client = finnhub.Client(api_key=API_KEY)

        try:
            # --- Symbol Lookup
            results = finnhub_client.symbol_lookup(company)
            candidates = results.get('result', [])

            symbol = None
            chosen = None

            for cand in candidates:
                if company.lower() in cand['description'].lower() and cand['type'] == "Common Stock":
                    symbol = cand['symbol']
                    chosen = cand
                    break

            if not symbol:
                for cand in candidates:
                    if cand['description'].lower() == f"{company.lower()} inc" and cand['type'] == "Common Stock":
                        symbol = cand['symbol']
                        chosen = cand
                        break

            if not symbol:
                for cand in candidates:
                    if cand['type'] == "Common Stock" and cand['symbol'].isalpha() and len(cand['symbol']) <= 5:
                        symbol = cand['symbol']
                        chosen = cand
                        break

            if not symbol and candidates:
                symbol = candidates[0]['symbol']
                chosen = candidates

            if not symbol:
                dispatcher.utter_message(text=f"Sorry, could not find a suitable stock symbol for '{company}'.")
                return []

            # --- Profile Info
            profile = finnhub_client.company_profile2(symbol=symbol)
            response = (
                f"**{profile.get('name', 'N/A')} ({symbol})**\n"
                f"Industry: {profile.get('finnhubIndustry', 'N/A')}\n"
                f"Country: {profile.get('country', 'N/A')}\n"
                f"Exchange: {profile.get('exchange', 'N/A')}\n"
                f"Market Cap: ${profile.get('marketCapitalization', 'N/A'):,.0f} Million\n"
                f"Shares Outstanding: {profile.get('shareOutstanding', 'N/A'):,.0f}\n"
                f"IPO Date: {profile.get('ipo', 'N/A')}\n"
                f"Website: {profile.get('weburl', 'N/A')}\n"
                f"Contact: {profile.get('phone', 'N/A')}\n"
            )

            # --- News Headlines
            news_url = NEWS_URL_TEMPLATE.format(company_name=company)
            news_response = requests.get(news_url)
            news_data = news_response.json()
            articles = news_data.get('articles', [])

            headlines = [a['title'] for a in articles if 'title' in a][:3]  # show up to 3 headlines
            if headlines:
                response += "\nRecent News Headlines:\n"
                for i, headline in enumerate(headlines, 1):
                    response += f"{i}. {headline}\n"

            dispatcher.utter_message(text=response)

        except Exception as e:
            dispatcher.utter_message(text=f"Sorry, I couldn't fetch company data due to an error: {str(e)}.")

        return []

