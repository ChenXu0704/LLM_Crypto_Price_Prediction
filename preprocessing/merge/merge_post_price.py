import pandas as pd
from datetime import datetime, timedelta
from omegaconf import OmegaConf
import os
config = OmegaConf.load("./config.yaml")
crypto_list = config.crypto_list


def merge():
  replace_pattern = config.data.crypto_price.replace_pattern
  indata_dir_price = config.data.crypto_price.data_dir
  indata_dir_crypt = config.text_encoding.data_dir
  features = ["embed_%d" %i for i in range(768)]
  features.extend(['Date', 'diff','pre_day']) 
  df_merge = []
  for crypto in crypto_list:
    indata_price = config.data.crypto_price.indata_format.replace(replace_pattern, crypto)
    indata_crypt = config.text_encoding.output_format.replace(replace_pattern, crypto)
    indata_price = '.' + indata_dir_price + indata_price
    indata_crypt = indata_dir_crypt + indata_crypt
    if os.path.exists(indata_price) is False or os.path.exists(indata_crypt) is False:
      continue
    output_dir = config.data.data_merge.outdata_dir
    output_name = config.data.data_merge.outdata_format.replace(replace_pattern, crypto)
    data_price = pd.read_csv(indata_price)
    data_crypt = pd.read_csv(indata_crypt)
    data_price['pre_day'] = data_price['Date'].apply(prev_date)
    data_price = data_price[['Date', 'diff','pre_day']]
    data_merge = pd.merge(data_crypt, data_price, left_on='day',right_on='pre_day',how='right')
    data_merge.to_csv(output_dir + output_name, index=False)
    df_merge.append(data_merge)
  return pd.concat(df_merge, ignore_index=True)

def prev_date(date_str):
  date_obj = datetime.strptime(date_str, '%Y-%m-%d')
  # Get the day after by adding one day to the date
  day_after = date_obj + timedelta(days=-1)
  # Convert the result back to a string in the same format
  day_after_str = day_after.strftime('%Y-%m-%d')
  return day_after_str
  

