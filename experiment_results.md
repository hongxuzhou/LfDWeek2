| Experiment | Model Architecture | Hyperparameters | Dev Set Accuracy | Notes |
|------------|---------------------|------------------|-------------------|-------|
| Baseline   | Single Dense Layer  | LR: 0.0005, Activation: softmax, Loss: MSE, Optimizer: SGD, Epochs: 10, Batch Size: 32 | 31.6% | Initial performance, room for improvement |
||||||
| default test template | Two Layers | Hidden layer: 64, Dropout: 0, Learning Rate 0.0005, Activation: softmax, Optimizer: SGD, Batch Size: 32, Epochs: 10, Loss Function: MSE | 75.8% | Default model looks good! |
||||||
| Dropout added | Two layers | Hidden layer: 32(down), Dropout: 0.2, Learning Rate: 0.0005, Activation: softmax, Optimizer: SGD, Batch Size 32, Epochs: 30, Loss Function: MSE | 47.2% | The issue of overfitting is addressed, at the cost of overall performance. Consider lower DP, and increase LR, change the optimizer from SGD to Adam|
||||||
| Round 3 | Two layers | Hidden layers: 64/32, Dropout 0.1, Learning Rate: 0.001, Batch Size: 32, Epochs: 30, Optimizer: Adam | 77.8% | Generally looks good, early stopping triggered. 
||||||
| Round 4 | Two layers | Hidden layers: 64/32, Dropout 0.15, Learning Rate: 0.0005, Batch Size: 64, Epochs: 30, Optimizer: Adam| 77.4%| HA! Overall performance decreases for a bit. Early stopping triggered at Epoch 12. For next round, more units will be added, and will try a different optimiser.| 
||||||
| Round 5 | Two layers | Hidden layers: 128/64, Dropout: 0.15, Learning Rate: 0,00075, Batch Size: 64, Epochs: 30, Optimiser: RMSprop (also tried adam, dropped the performance to 77%)| 77.8% | Same with Round 3, guess it is the best I can do. Early stopping triggered at Epoch 8|