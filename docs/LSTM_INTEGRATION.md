# LSTM Neural Network Integration

## Overview

The AI Retail Intelligence Platform now includes LSTM (Long Short-Term Memory) neural networks for advanced time series forecasting. This implementation provides GPU-accelerated training, model checkpointing, early stopping, and seamless integration with the existing forecasting engine.

## Features

### 1. GPU Acceleration Support
- **CUDA Support**: Automatically detects and uses NVIDIA GPUs when available
- **Apple Silicon Support**: Leverages Metal Performance Shaders (MPS) on M1/M2/M3 Macs
- **CPU Fallback**: Gracefully falls back to CPU when GPU is not available
- **Automatic Device Selection**: No manual configuration required

### 2. Configurable Architecture
- **Sequence Length**: Adjustable lookback window (default: 30 time steps)
- **Hidden Size**: Configurable number of hidden units (default: 64)
- **Number of Layers**: Stackable LSTM layers (default: 2)
- **Dropout Rate**: Regularization to prevent overfitting (default: 0.2)

### 3. Training Features
- **Early Stopping**: Prevents overfitting with configurable patience (default: 10 epochs)
- **Model Checkpointing**: Automatically saves best model during training
- **Validation Split**: Automatic train/validation split (default: 80/20)
- **Training History**: Tracks loss metrics across epochs
- **Batch Processing**: Efficient mini-batch training (default: 16)

### 4. Data Preprocessing
- **Sequence Generation**: Automatic creation of LSTM input sequences
- **Normalization**: Z-score normalization for stable training
- **Denormalization**: Automatic conversion back to original scale
- **Data Validation**: Checks for sufficient data before training

### 5. Prediction Capabilities
- **Multi-step Forecasting**: Generate predictions for any horizon
- **Confidence Intervals**: Statistical uncertainty estimates
- **Iterative Prediction**: Uses previous predictions for future steps

## Installation

### Requirements

The LSTM forecaster requires PyTorch. It's already included in `requirements.txt`:

```bash
torch>=2.0.0
```

### Verify Installation

```python
from src.forecasting_model import PriceForecastingEngine

engine = PriceForecastingEngine()
models = engine.get_available_models()

if 'lstm' in models:
    print("✓ LSTM model is available!")
else:
    print("❌ LSTM model not available. Install PyTorch.")
```

## Usage

### Basic Usage

```python
from src.forecasting_model import PriceForecastingEngine
from src.data_loader import DataLoader

# Initialize engine
engine = PriceForecastingEngine()

# Load data
data_loader = DataLoader()
gold_data = data_loader.load_gold_prices('data/gold_prices.csv')

# Train LSTM model
engine.train_model(
    data=gold_data,
    target_column='close',
    model_name='lstm',
    symbol='GOLD'
)

# Make predictions
forecast = engine.predict_prices(
    symbol='GOLD',
    horizon=30,
    model_name='lstm'
)

print(f"Predictions: {forecast.predicted_prices}")
print(f"Confidence Intervals: {forecast.confidence_intervals}")
```

### Advanced Configuration

```python
from src.lstm_forecaster import LSTMForecaster

# Create custom LSTM forecaster
lstm = LSTMForecaster(
    sequence_length=60,      # Longer lookback window
    hidden_size=128,         # More hidden units
    num_layers=3,            # Deeper network
    dropout=0.3,             # Higher dropout
    learning_rate=0.0005,    # Lower learning rate
    batch_size=32,           # Larger batches
    epochs=200,              # More training epochs
    early_stopping_patience=15
)

# Train on data
training_info = lstm.fit(gold_data, target_column='close')

print(f"Training completed in {training_info['epochs_trained']} epochs")
print(f"Best validation loss: {training_info['best_val_loss']:.6f}")

# Make predictions
predictions, confidence_intervals = lstm.predict(horizon=30)
```

### Model Evaluation

```python
# Evaluate on test data
test_data = gold_data.tail(100)

metrics = engine.evaluate_model(
    test_data=test_data,
    symbol='GOLD',
    target_column='close',
    model_name='lstm'
)

print(f"MAE: {metrics['mae']:.2f}")
print(f"RMSE: {metrics['rmse']:.2f}")
print(f"R²: {metrics['r2']:.4f}")
print(f"MAPE: {metrics['mape']:.2f}%")
```

### Model Persistence

```python
# Models are automatically saved during training
engine.train_model(data=gold_data, model_name='lstm', symbol='GOLD')

# Load saved model
engine2 = PriceForecastingEngine()
forecast = engine2.predict_prices(symbol='GOLD', model_name='lstm')
# Model is automatically loaded from checkpoint
```

## Architecture

### LSTM Network Structure

```
Input Layer (sequence_length, 1)
    ↓
LSTM Layer 1 (hidden_size units)
    ↓
Dropout (dropout rate)
    ↓
LSTM Layer 2 (hidden_size units)
    ↓
Dropout (dropout rate)
    ↓
Fully Connected Layer
    ↓
Output (1 value)
```

### Data Flow

1. **Input**: Historical price data (pandas DataFrame)
2. **Normalization**: Z-score normalization
3. **Sequence Creation**: Sliding window approach
4. **Training**: Mini-batch gradient descent with Adam optimizer
5. **Validation**: Separate validation set for early stopping
6. **Checkpointing**: Save best model based on validation loss
7. **Prediction**: Iterative multi-step forecasting
8. **Denormalization**: Convert predictions back to original scale

## Performance Considerations

### Data Requirements

- **Minimum Data**: At least `sequence_length + 50` records
- **Recommended**: 200+ records for better performance
- **Optimal**: 500+ records for production use

### Training Time

Training time depends on:
- Dataset size
- Number of epochs
- Hardware (GPU vs CPU)
- Model complexity (layers, hidden size)

**Typical Training Times** (on Apple M1):
- 90 records, 50 epochs: ~30 seconds
- 500 records, 100 epochs: ~2 minutes
- 2000 records, 200 epochs: ~10 minutes

### GPU Acceleration

**Speed Improvements**:
- CUDA GPU: 5-10x faster than CPU
- Apple Silicon (MPS): 3-5x faster than CPU
- Larger datasets benefit more from GPU acceleration

## Model Checkpoints

Checkpoints are saved in: `models/lstm_checkpoints/`

**Checkpoint Contents**:
- Model state (weights and biases)
- Scaler parameters (mean, std)
- Training history
- Model configuration
- Last sequences for prediction

**Checkpoint Files**:
- `{SYMBOL}_lstm_model.pt`: Final trained model
- `best_model.pt`: Best model during training (temporary)

## Troubleshooting

### Issue: "Insufficient data for training"

**Solution**: Ensure you have at least `sequence_length + 50` records. Reduce `sequence_length` if needed:

```python
from src.forecasting_model import LSTMModel

lstm = LSTMModel(sequence_length=20)  # Reduced from default 30
```

### Issue: "PyTorch not available"

**Solution**: Install PyTorch:

```bash
# For CPU only
pip install torch

# For CUDA (NVIDIA GPU)
pip install torch --index-url https://download.pytorch.org/whl/cu118

# For Apple Silicon
pip install torch  # MPS support included by default
```

### Issue: Training is too slow

**Solutions**:
1. Reduce number of epochs
2. Reduce batch size
3. Use GPU acceleration
4. Reduce model complexity (fewer layers, smaller hidden size)

### Issue: Poor prediction accuracy

**Solutions**:
1. Increase training data
2. Increase sequence length
3. Add more LSTM layers
4. Increase hidden size
5. Train for more epochs
6. Adjust learning rate

## API Integration

The LSTM model is fully integrated with the existing API:

```bash
# Train LSTM model
curl -X POST "http://localhost:8000/api/v1/forecast/gold" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "lstm",
    "horizon": 30,
    "train": true
  }'

# Get predictions
curl -X POST "http://localhost:8000/api/v1/forecast/gold" \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "lstm",
    "horizon": 30
  }'
```

## Comparison with Other Models

| Feature | Moving Average | Random Forest | LSTM |
|---------|---------------|---------------|------|
| Training Speed | Fast | Medium | Slow |
| Prediction Accuracy | Low | Medium | High |
| Data Requirements | Low | Medium | High |
| GPU Acceleration | No | No | Yes |
| Handles Seasonality | No | Limited | Yes |
| Handles Trends | Limited | Yes | Yes |
| Handles Non-linearity | No | Yes | Yes |

## Best Practices

1. **Data Preparation**
   - Ensure data is sorted by date
   - Remove or handle missing values
   - Use sufficient historical data

2. **Model Configuration**
   - Start with default parameters
   - Adjust based on dataset size
   - Monitor validation loss

3. **Training**
   - Use early stopping to prevent overfitting
   - Monitor training/validation loss gap
   - Save checkpoints regularly

4. **Evaluation**
   - Use separate test set
   - Compare with baseline models
   - Validate on recent data

5. **Production Deployment**
   - Use GPU for faster inference
   - Cache predictions when possible
   - Monitor model performance
   - Retrain periodically with new data

## References

- **Requirements**: 19.1, 19.3, 19.6
- **Design Document**: Phase 2 Advanced ML Models Integration
- **Source Code**: `src/lstm_forecaster.py`, `src/forecasting_model.py`
- **Test Script**: `test_lstm_integration.py`

## Future Enhancements

Planned improvements for LSTM forecasting:

1. **Attention Mechanisms**: Add attention layers for better long-term dependencies
2. **Bidirectional LSTM**: Process sequences in both directions
3. **Multi-variate Support**: Use multiple features (volume, technical indicators)
4. **Ensemble Methods**: Combine LSTM with other models
5. **Hyperparameter Tuning**: Automatic optimization of model parameters
6. **Transfer Learning**: Pre-trained models for faster convergence
