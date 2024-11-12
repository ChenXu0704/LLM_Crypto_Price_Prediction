from torch.utils.data import DataLoader, TensorDataset
from omegaconf import OmegaConf
import torch 
config = OmegaConf.load("./config.yaml")
def dataloader(df):
  n_samples = df.shape[0]
  training_rate = config.data.loader.training_rate
  embd_lst = ["embed_%d" %i for i in range(768)]
  X_train = torch.tensor(df[embd_lst].iloc[0:int(n_samples*training_rate)].values, dtype=torch.float32)
  y_train = torch.tensor(df[['diff']].iloc[0:int(n_samples*training_rate)].values, dtype=torch.float32)
  X_valid = torch.tensor(df[embd_lst].iloc[int(n_samples*training_rate):].values, dtype=torch.float32)
  y_valid = torch.tensor(df[['diff']].iloc[int(n_samples*training_rate):].values, dtype=torch.float32)
  train_dataset = TensorDataset(X_train, y_train)
  train_loader = DataLoader(train_dataset, batch_size=32)
  valid_dataset = TensorDataset(X_valid, y_valid)
  valid_loader = DataLoader(valid_dataset, batch_size=32)

  return (train_loader, valid_loader)