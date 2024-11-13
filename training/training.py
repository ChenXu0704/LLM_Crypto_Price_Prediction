from omegaconf import OmegaConf
import torch.optim as optim
from torch import nn 
import torch 
from models.NeuralNetworkForPricePrediction import NeuralNetworkForPricePrediction 
import numpy as np
from sklearn.metrics import confusion_matrix
import copy 

config = OmegaConf.load("./config.yaml")
def training(train_loader, valid_loader):
  hidden_layer = config.model.hidden_layer
  loss_name = config.training.loss
  opt = config.training.opt
  num_epochs = config.training.epochs
  lr = config.training.lr
  model = NeuralNetworkForPricePrediction(hidden_layer)
  best_model = None
  if opt == 'Adam':
    optimizer = optim.Adam(model.parameters(), lr=lr)
  else:
    optimizer = optim.Adam(model.parameters(), lr=lr)
  if loss_name == 'BCE':
    criterion = nn.BCELoss()
  else:
    criterion = nn.BCELoss()
  train_loss = []
  valid_loss = []
  valid_val = []
  true_val = []
  train_val = []
  train_true = []
  valid_best = []
  cm = None
  for epoch in range(num_epochs):
      model.train()
      running_loss = 0.0
      for inputs, labels in train_loader:
          optimizer.zero_grad()
          outputs = model(inputs)
          #print(outputs, labels)
          loss = criterion(outputs, labels)
          loss.backward()
          optimizer.step()
          running_loss += loss.item()*inputs.size(0)
          if epoch == num_epochs - 1:
              train_val.extend(outputs.tolist())
              train_true.extend(labels.tolist())
      epoch_loss = running_loss / len(train_loader.dataset)
      train_loss.append(epoch_loss)
      
      val_loss = 0.0
      best_acc = -1
      
      with torch.no_grad():
          predict_val = []
          valid_val = []
          for inputs_val, targets_val in valid_loader:
              outputs_val = model(inputs_val)
              if epoch == 0:
                  true_val.extend(targets_val.tolist())
              val_loss += criterion(outputs_val, targets_val).item() * inputs_val.size(0)
              predict_val.extend(outputs_val.tolist())
              #print(outputs_val, targets_val)
          val_loss = val_loss / len(valid_loader.dataset)
          
          valid_val.extend(predict_val)
          # Example predicted probabilities and true labels
          predicted_probabilities = np.array(valid_val)  # Example predicted probabilities
          #print(predicted_probabilities)
          threshold = 0.5  # Example threshold for converting probabilities to class labels
          true_labels = np.array(true_val)  # Example true labels

          # Convert probabilities to class labels based on threshold
          predicted_labels = (predicted_probabilities >= threshold).astype(int)

          # Calculate confusion matrix
          cm = confusion_matrix(true_labels, predicted_labels)
          if (cm[0,0] + cm[1, 1]) / (cm[0,1] + cm[1, 0] + cm[0,0] + cm[1, 1]) > best_acc:
              best_acc = (cm[0,0] + cm[1, 1]) / (cm[0,1] + cm[1, 0] + cm[0,0] + cm[1, 1])
              valid_best = []
              valid_best.extend(valid_val)
              best_model = copy.deepcopy(model)
          valid_loss.append(val_loss)
      
      if epoch % 10 == 9:
          print(f'Epoch [{epoch+1}/{num_epochs}], Training Loss: {epoch_loss:.4f}, Validation Loss: {val_loss:.4f}')
  print(cm)
  output_path = config.training.outpath + "model_loss_" + loss_name + "_opt_" + opt + "_epo_" + str(num_epochs) + "_lr_" + str(lr)
  torch.save(best_model, output_path)
 