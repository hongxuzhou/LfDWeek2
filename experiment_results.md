| Experiment | Model Architecture | Hyperparameters | Dev Set Accuracy | Notes |
|------------|---------------------|------------------|-------------------|-------|
| Baseline   | Single Dense Layer  | LR: 0.0005, Activation: softmax, Loss: MSE, Optimizer: SGD, Epochs: 10, Batch Size: 32 | 31.6% | Initial performance, room for improvement |
|---|---|---|---|---|
| default test template | Two Layers | Hidden layer: 64, Dropout: 0, Learning Rate 0.0005 Activation: softmax Optimizer: SGD, Batch Size: 32, Epochs: 10, Loss Function: MSE | 75.8% | Default model looks good! |