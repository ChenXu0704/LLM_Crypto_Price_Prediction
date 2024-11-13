from omegaconf import DictConfig, OmegaConf
import hydra
import pandas as pd
import os 
from preprocessing.price import price_preprocessing
from preprocessing.post import post_preprocessing
from reddit_post_scrape import reddit_post_scrape
from preprocessing.merge import merge_post_price
from Dataloader.dataloader import dataloader
from training.training import training
def main() -> None:
    config = OmegaConf.load("./config.yaml")
    crypto_list = config.crypto_list
    crypto_data_dir = config.data.crypto_price.data_dir
    crypto_data_format = config.data.crypto_price.indata_format
    crypto_data_replace = config.data.crypto_price.replace_pattern
    main_dir = os.getcwd()
    scrape_helper = config.data.reddit_post.scrape_method
    for crypto in crypto_list:
        crypto_file = main_dir + crypto_data_dir + crypto_data_format
        crypto_file = crypto_file.replace(crypto_data_replace, crypto)
        price_preprocessing.crypto_price_preprocessing(crypto_file)
    if scrape_helper == 'pushshift':
        reddit_post_scrape.scrape_with_pushshift()
    elif scrape_helper == 'selenium':
        reddit_post_scrape.scrape_with_selenium()
    else:
        print("Please chosse from 'pushshift' and 'selenium' from scrape_method in config file")
        #exit()
        
    post_preprocessing.post_preprocessing()
    
    data = merge_post_price.merge()
    
    train_loader, valid_loader = dataloader(data)
    training(train_loader, valid_loader)
if __name__ == "__main__":
    print("Running main()...")
    main()