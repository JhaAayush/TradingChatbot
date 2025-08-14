import pandas as pd
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

CSV_PATH = "companies_sentiment.csv"

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

            # Build dynamic reply
            response_parts = []
            if positive:
                response_parts.append(f"🟢 You can consider investing in: {', '.join(positive)}.")
            if negative:
                response_parts.append(f"🔴 You should avoid investing in: {', '.join(negative)}.")

            if not response_parts:
                response = "I couldn't find any sentiment data in my records."
            else:
                response = " ".join(response_parts)

            dispatcher.utter_message(text=response)

        except Exception as e:
            dispatcher.utter_message(text=f"Error fetching stock advice: {str(e)}")
        
        return []
