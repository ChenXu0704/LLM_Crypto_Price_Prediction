from datetime import datetime, timedelta
import pandas as pd

def convert_date(date_string):
    original_date = datetime.strptime(date_string, "%m/%d/%Y")
    # Format the datetime object as a string in YYYY-MM-DD format
    return original_date.strftime("%Y-%m-%d")

def prev_date(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    # Get the day after by adding one day to the date
    day_after = date_obj + timedelta(days=-1)
    # Convert the result back to a string in the same format
    day_after_str = day_after.strftime('%Y-%m-%d')
    return day_after_str

def crypto_price_preprocessing(path):
    data = pd.read_csv(path)
    if 'diff' in data.columns:
        print(f"{path} has been processed. Continue...")
        return
    print(f"Processing {path}...")
    data['Date'] = data['Date'].apply(convert_date)
    data['prev_date'] = data['Date'].apply(prev_date)
    data['Open'] = data['Open'].apply(lambda x : float(x.split("$")[1]))
    data['Close'] = data['Close'].apply(lambda x : float(x.split("$")[1]))
    data['diff'] = data['Open'] <= data['Close']
    data.to_csv(path, index=False)
    print(f"Done...")