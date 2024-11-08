import requests, json, csv 
import pandas as pd
from datetime import datetime
import time
import traceback
from omegaconf import DictConfig, OmegaConf
from selenium import webdriver
from bs4 import BeautifulSoup
import os

def scrape_with_pushshift():
  # Read the configuration file
  config = OmegaConf.load("./config.yaml")
  # Target cryptos for scraping
  crypto_list = config.crypto_list
  # Define the starting date and end date for data scraping using pushshift 
  start_date = config.data.reddit_post.pushshift.start_date
  end_date = config.data.reddit_post.pushshift.end_date
  start_time = datetime.strptime(start_date, "%m/%d/%Y")
  end_time = datetime.strptime(end_date, "%m/%d/%Y")
  # Output name
  outdata_format = config.data.reddit_post.pushshift.outdata_format
  replace_pattern = config.data.reddit_post.replace_pattern
  # merge the result to output file?
  merge = config.data.reddit_post.pushshift.merge
  # Reedit account information for scraping
  reddit_client_id = config.data.reddit_post.pushshift.reddit_client_id
  reddit_client_secret = config.data.reddit_post.pushshift.reddit_client_secret
  # Target username or thread_id for scraping
  username = config.data.reddit_post.pushshift.username
  thread_id = config.data.reddit_post.pushshift.thread_id
  # Data encode
  convert_thread_id_to_base_ten = True
  # url related information
  filter_string = None
  url_template = "https://api.pushshift.io/reddit/submission/search?limit=1000&{}&before="
  #output_dir = config.data.outdata_dir
  output = f"{config.data.reddit_post.outdata_dir}{outdata_format}"
  print("testing scrape_with_pushshift.py")
  print(output)
  for crypto in crypto_list:
    output = outdata_format.replace(replace_pattern, crypto)
    filters = []
    filters.append(subreddit={crypto})
    if username:
      filters.append(f"author={username}")
    if thread_id:
      if convert_thread_id_to_base_ten:
        filters.append(f"link_id={int(thread_id), 36}")
      else:
        filters.append(f"link_id=t3_{thread_id}")
    filter_string = '&'.join(filters)
  data_download(output, url_template.format(filter_string), start_time, end_time, merge, config)

# Download the data from pushshift endpoint
def data_download(output, url_base, start_datetime, end_datetime, merge, config):
  print(f"Saving to {output}")
  count = 0
  handle = open(output, 'w', encoding='UTF-8', newline='')
  writer = csv.writer(handle)
  previous_epoch = int(start_datetime.timestamp())
  break_out = False
  index = 1
  columns = config.data.reddit_post.columns
  if merge == False:
    writer.writerow(columns)
  while True:
    new_url = url_base + str(previous_epoch)
    s = requests.Session()
    s.headers['User-Agent'] =  "user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    s.headers['accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    json_text = requests.get(new_url)
    time.sleep(3.5) 
    try:
      json_data = json_text.json()
    except json.decoder.JSONDecodeError:
      time.sleep(2)
      continue
    if 'data' not in json_data:
      break 
    objects = json_data['data']
    if len(objects) == 0:
      break
    for object in objects:
        previous_epoch = object['created_utc'] - 1
        if end_datetime is not None and datetime.utcfromtimestamp(previous_epoch) < end_datetime:
            break_out = True
            break
        count += 1
        try:
            write_csv_line(writer, object, index, columns)
            index += 1
        except Exception as err:
            print(f"Couldn't print object: https://www.reddit.com{object['permalink']}")
            print(traceback.format_exc())
    if break_out:
        break
    
# Write each post info to output file
#['index', 'id', 'day', 'title', 'author_fullname', 'url', 'score']
def write_csv_line(writer, obj, i, columns):
    output_list = [None for i in range(len(columns))]
    output_list[0] = i
    if 'id' in columns:
      index = columns.find('id')
      output_list[index] = obj['id']
    if 'day' in columns:
      index = columns.find('day')
      output_list[index] = datetime.fromtimestamp(obj['created_utc']).strftime("%Y-%m-%d")
    if 'title' in columns:
      index = columns.find('title')
      output_list[index] = obj['body']
    if 'author_fullname' in columns:
      index = columns.find('author_fullname')
      try:
          output_list[index] = f"u/{obj['author_fullname']}"
      except:
          output_list[index] = "u/[deleted]"
    if 'url' in columns:
      index = columns.find('url')
      output_list[index] = f"https://www.reddit.com{obj['permalink']}"
    if 'score' in columns:
      output_list[index] = obj['score']
    writer.writerow(output_list)

def scrape_with_selenium():
  # Read the configuration file
  config = OmegaConf.load("./config.yaml")
  # Target cryptos for scraping
  crypto_list = config.crypto_list