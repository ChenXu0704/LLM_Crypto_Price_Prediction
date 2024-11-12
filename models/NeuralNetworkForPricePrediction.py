import torch.nn as nn

class NeuralNetworkForPricePrediction(nn.Module):
  def __init__(self, hidden_size, num_classes = 1, dropout_prob = 0.1):
    super(NeuralNetworkForPricePrediction, self).__init__()
    self.layer1 = nn.Linear(768, hidden_size)
    self.layer2 = nn.Linear(hidden_size, num_classes)
    self.bn1 = nn.BatchNorm1d(hidden_size)
    self.relu = nn.ReLU()
    self.sig = nn.Sigmoid()
  def forward(self, x):
    #x = self.bn1(self.relu(self.layer1(x)))
    x = self.bn1(self.sig(self.layer1(x)))
    #x = self.sig(self.layer1(x))
    x = self.layer2(x)
    return self.sig(x)