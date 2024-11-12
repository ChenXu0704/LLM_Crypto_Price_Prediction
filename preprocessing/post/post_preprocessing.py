from transformers import AutoTokenizer
from transformers import TFAutoModelForSequenceClassification
import numpy as np
import pandas as pd
from tqdm import tqdm 
import pickle
import re 
from omegaconf import OmegaConf
import os 

# Get global variables for the processing.
with open("./Emoji_dict.p", 'rb') as fp:
  emoji_dict = pickle.load(fp)
config = OmegaConf.load("./config.yaml")
transformer_model = config.text_encoding.model
tokenizer = AutoTokenizer.from_pretrained(transformer_model)
bert_model = TFAutoModelForSequenceClassification.from_pretrained(transformer_model)

# Using emoji dictionary to replace the emoji in the text
def convert_emojis_to_word(text):
  try:
    for emot in emoji_dict:
      text = re.sub(r'('+emot+')', "_".join(emoji_dict[emot].replace(",","").replace(":","").split()), text)
    return text
  except:
    print("convert failed ", text)
    return text

# Apply emoji replacement
def deal_with_emojis(data):
  data['emoj_replc'] = data['title'].apply(convert_emojis_to_word)
  return data

# Get the [cls] token from BERT model
def cls_bert(text):
  max_length = 400
  words = text.split(" ")
  if len(words) > max_length:
    text = " ".join(words[:max_length])
  #try:
  encoded_text = tokenizer(text, return_tensors='tf')
  output = bert_model(**encoded_text, output_hidden_states=True)
  return output.hidden_states[-1][0][0]
  # except:
  #   print(f"Failed to embed {text}")
  #   return np.zeros(768)

def get_count_each_day(data):
  data = data.copy()
  data.loc[:, 'count'] = 1
  data = data.groupby('day').agg({'count': 'sum'}).reset_index()
  return data

# Text embedding and aggregation by date
def post_preprocessing():
  crypto_list = config.crypto_list
  crypto_data_dir = config.text_encoding.data_dir
  indata_format = config.text_encoding.indata_format
  output_format = config.text_encoding.output_format
  replace_pattern = config.text_encoding.replace_pattern
  for crypto in crypto_list:
    indata_name = indata_format.replace(replace_pattern, crypto)
    if os.path.exists(crypto_data_dir+indata_name) is False:
      continue
    outdata_name = output_format.replace(replace_pattern, crypto)
    data = pd.read_csv(crypto_data_dir+indata_name)
    data = deal_with_emojis(data)
    embed = []
    for i, entry in tqdm(data.iterrows(), total=len(data)):
      embed.append(cls_bert(entry['emoj_replc']).numpy().tolist())
    embed = np.array(embed)
    new_columns_df = pd.DataFrame(embed, columns=[f'embed_{i}' for i in range(embed.shape[1])])
    data = pd.concat([data, new_columns_df], axis=1)
    keep_columns = [f'embed_{i}' for i in range(embed.shape[1])]
    keep_columns.append('day')
    data = data[keep_columns]
    data_agg = data.groupby('day').agg('mean').reset_index()
    data_count = get_count_each_day(data[['day']])
    data_agg = pd.merge(data_agg, data_count, on='day', how='left')
    
    data_agg.to_csv(crypto_data_dir+outdata_name, index=False)
    break 
