from omegaconf import DictConfig, OmegaConf
import hydra
import pandas as pd
from preprocessing.price import price_preprocessing
import os 
def main() -> None:
    config = OmegaConf.load("./config.yaml")
    crypto_list = config.crypto_list
    crypto_data_dir = config.data.crypto_price.data_dir
    crypto_data_format = config.data.crypto_price.indata_format
    crypto_data_replace = config.data.crypto_price.replace_pattern
    main_dir = os.getcwd()
    for crypto in crypto_list:
        crypto_file = main_dir + crypto_data_dir + crypto_data_format
        crypto_file = crypto_file.replace(crypto_data_replace, crypto)
        price_preprocessing.crypto_price_preprocessing(crypto_file)
        
        break

        

if __name__ == "__main__":
    print("Running main()...")
    main()