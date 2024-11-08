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
def get_change(entry):
    if entry['Close'] >= entry['Open']:
        return 1
    return 0

def crypto_price_preprocessing(path):
    data = pd.read_csv(path)
    data_name = path.split('/')[-1]
    if 'diff' in data.columns:
         print(f"{data_name} has been processed. Continue...")
         return
    print(f"Processing {data_name}...")
    data['Date'] = data['Date'].apply(convert_date)
    data['prev_date'] = data['Date'].apply(prev_date)
    data['Open'] = data['Open'].apply(lambda x : float(x.split("$")[1]))
    data['Close'] = data['Close'].apply(lambda x : float(x.split("$")[1]))
    data['diff'] = data.apply(get_change, axis=1)
    data.to_csv(path, index=False)
    print(f"Done...")
