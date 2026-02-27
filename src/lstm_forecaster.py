"""LSTM neural network implementation for time series forecasting.

This module provides LSTM-based forecasting capabilities with GPU acceleration,
model checkpointing, and early stopping for the AI Retail Intelligence Platform.
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: PyTorch not available. LSTM forecasting will not be available.")

from src.exceptions import ModelTrainingError, ForecastingError
from src.config import settings


class TimeSeriesDataset(Dataset):
    """PyTorch Dataset for time series data."""
    
    def __init__(self, sequences: np.ndarray, targets: np.ndarray):
        """Initialize dataset with sequences and targets.
        
        Args:
            sequences: Input sequences of shape (n_samples, sequence_length, n_features)
            targets: Target values of shape (n_samples,)
        """
        self.sequences = torch.FloatTensor(sequences)
        self.targets = torch.FloatTensor(targets)
    
    def __len__(self) -> int:
        return len(self.sequences)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.sequences[idx], self.targets[idx]


class LSTMNetwork(nn.Module):
    """LSTM neural network architecture for time series forecasting."""
    
    def __init__(self, input_size: int = 1, hidden_size: int = 64, 
                 num_layers: int = 2, dropout: float = 0.2, output_size: int = 1):
        """Initialize LSTM network.
        
        Args:
            input_size: Number of input features
            hidden_size: Number of hidden units in LSTM layers
            num_layers: Number of stacked LSTM layers
            dropout: Dropout rate for regularization
            output_size: Number of output values
        """
        super(LSTMNetwork, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        # Dropout layer
        self.dropout = nn.Dropout(dropout)
        
        # Fully connected output layer
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the network.
        
        Args:
            x: Input tensor of shape (batch_size, sequence_length, input_size)
            
        Returns:
            Output tensor of shape (batch_size, output_size)
        """
        # LSTM forward pass
        lstm_out, _ = self.lstm(x)
        
        # Take the output from the last time step
        last_output = lstm_out[:, -1, :]
        
        # Apply dropout
        dropped = self.dropout(last_output)
        
        # Final prediction
        output = self.fc(dropped)
        
        return output


class LSTMForecaster:
    """LSTM-based time series forecaster with GPU acceleration and checkpointing."""
    
    def __init__(self, sequence_length: int = 60, hidden_size: int = 64,
                 num_layers: int = 2, dropout: float = 0.2, 
                 learning_rate: float = 0.001, batch_size: int = 32,
                 epochs: int = 100, early_stopping_patience: int = 10,
                 checkpoint_dir: str = None):
        """Initialize LSTM forecaster.
        
        Args:
            sequence_length: Length of input sequences (lookback window)
            hidden_size: Number of hidden units in LSTM layers
            num_layers: Number of stacked LSTM layers
            dropout: Dropout rate for regularization
            learning_rate: Learning rate for optimizer
            batch_size: Batch size for training
            epochs: Maximum number of training epochs
            early_stopping_patience: Patience for early stopping
            checkpoint_dir: Directory to save model checkpoints
        """
        if not TORCH_AVAILABLE:
            raise ModelTrainingError("PyTorch is not available. Please install torch.")
        
        self.sequence_length = sequence_length
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout = dropout
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.epochs = epochs
        self.early_stopping_patience = early_stopping_patience
        
        # Setup checkpoint directory
        self.checkpoint_dir = checkpoint_dir or os.path.join(settings.model_dir, 'lstm_checkpoints')
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        # GPU acceleration support
        self.device = self._setup_device()
        
        # Model components
        self.model = None
        self.scaler_mean = None
        self.scaler_std = None
        self.is_trained = False
        self.training_history = []
        self.last_sequences = None
        
        print(f"LSTM Forecaster initialized with device: {self.device}")
    
    def _setup_device(self) -> torch.device:
        """Setup computation device (GPU if available, else CPU).
        
        Returns:
            torch.device: Device to use for computation
        """
        if torch.cuda.is_available():
            device = torch.device('cuda')
            print(f"GPU acceleration enabled: {torch.cuda.get_device_name(0)}")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = torch.device('mps')
            print("Apple Silicon GPU acceleration enabled")
        else:
            device = torch.device('cpu')
            print("Using CPU for computation")
        
        return device
    
    def _normalize_data(self, data: np.ndarray, fit: bool = False) -> np.ndarray:
        """Normalize data using z-score normalization.
        
        Args:
            data: Data to normalize
            fit: Whether to fit the scaler (True for training data)
            
        Returns:
            Normalized data
        """
        if fit:
            self.scaler_mean = np.mean(data)
            self.scaler_std = np.std(data)
        
        if self.scaler_std == 0:
            return data - self.scaler_mean
        
        return (data - self.scaler_mean) / self.scaler_std
    
    def _denormalize_data(self, data: np.ndarray) -> np.ndarray:
        """Denormalize data back to original scale.
        
        Args:
            data: Normalized data
            
        Returns:
            Denormalized data
        """
        if self.scaler_std == 0:
            return data + self.scaler_mean
        
        return (data * self.scaler_std) + self.scaler_mean
    
    def _create_sequences(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training.
        
        Args:
            data: Time series data
            
        Returns:
            Tuple of (sequences, targets)
        """
        sequences = []
        targets = []
        
        for i in range(len(data) - self.sequence_length):
            seq = data[i:i + self.sequence_length]
            target = data[i + self.sequence_length]
            sequences.append(seq)
            targets.append(target)
        
        sequences = np.array(sequences)
        targets = np.array(targets)
        
        # Reshape sequences for LSTM: (samples, sequence_length, features)
        if len(sequences.shape) == 2:
            sequences = sequences.reshape(sequences.shape[0], sequences.shape[1], 1)
        
        return sequences, targets

    def fit(self, data: pd.DataFrame, target_column: str = 'close', 
            validation_split: float = 0.2) -> Dict[str, Any]:
        """Train the LSTM model on historical data.
        
        Args:
            data: Historical price data
            target_column: Column name for target variable
            validation_split: Fraction of data to use for validation
            
        Returns:
            Training history with loss metrics
        """
        try:
            if target_column not in data.columns:
                raise ModelTrainingError(f"Target column '{target_column}' not found in data")
            
            if len(data) < self.sequence_length + 50:
                raise ModelTrainingError(
                    f"Insufficient data for training. Need at least {self.sequence_length + 50} records, got {len(data)}"
                )
            
            # Extract and normalize data
            prices = data[target_column].values
            normalized_prices = self._normalize_data(prices, fit=True)
            
            # Create sequences
            sequences, targets = self._create_sequences(normalized_prices)
            
            # Split into train and validation sets
            split_idx = int(len(sequences) * (1 - validation_split))
            train_sequences = sequences[:split_idx]
            train_targets = targets[:split_idx]
            val_sequences = sequences[split_idx:]
            val_targets = targets[split_idx:]
            
            # Create datasets and dataloaders
            train_dataset = TimeSeriesDataset(train_sequences, train_targets)
            val_dataset = TimeSeriesDataset(val_sequences, val_targets)
            
            train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
            val_loader = DataLoader(val_dataset, batch_size=self.batch_size, shuffle=False)
            
            # Initialize model
            input_size = train_sequences.shape[2]  # Number of features
            self.model = LSTMNetwork(
                input_size=input_size,
                hidden_size=self.hidden_size,
                num_layers=self.num_layers,
                dropout=self.dropout,
                output_size=1
            ).to(self.device)
            
            # Loss function and optimizer
            criterion = nn.MSELoss()
            optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
            
            # Training loop with early stopping
            best_val_loss = float('inf')
            patience_counter = 0
            self.training_history = []
            
            print(f"Training LSTM model for {self.epochs} epochs...")
            
            for epoch in range(self.epochs):
                # Training phase
                self.model.train()
                train_losses = []
                
                for batch_sequences, batch_targets in train_loader:
                    batch_sequences = batch_sequences.to(self.device)
                    batch_targets = batch_targets.to(self.device)
                    
                    # Forward pass
                    optimizer.zero_grad()
                    outputs = self.model(batch_sequences)
                    loss = criterion(outputs.squeeze(), batch_targets)
                    
                    # Backward pass
                    loss.backward()
                    optimizer.step()
                    
                    train_losses.append(loss.item())
                
                avg_train_loss = np.mean(train_losses)
                
                # Validation phase
                self.model.eval()
                val_losses = []
                
                with torch.no_grad():
                    for batch_sequences, batch_targets in val_loader:
                        batch_sequences = batch_sequences.to(self.device)
                        batch_targets = batch_targets.to(self.device)
                        
                        outputs = self.model(batch_sequences)
                        loss = criterion(outputs.squeeze(), batch_targets)
                        val_losses.append(loss.item())
                
                avg_val_loss = np.mean(val_losses)
                
                # Record history
                self.training_history.append({
                    'epoch': epoch + 1,
                    'train_loss': avg_train_loss,
                    'val_loss': avg_val_loss
                })
                
                # Print progress every 10 epochs
                if (epoch + 1) % 10 == 0:
                    print(f"Epoch {epoch + 1}/{self.epochs} - Train Loss: {avg_train_loss:.6f}, Val Loss: {avg_val_loss:.6f}")
                
                # Early stopping check
                if avg_val_loss < best_val_loss:
                    best_val_loss = avg_val_loss
                    patience_counter = 0
                    # Save best model checkpoint
                    self._save_checkpoint('best_model.pt', epoch, avg_val_loss)
                else:
                    patience_counter += 1
                
                if patience_counter >= self.early_stopping_patience:
                    print(f"Early stopping triggered at epoch {epoch + 1}")
                    break
            
            # Load best model
            self._load_checkpoint('best_model.pt')
            
            # Store last sequences for prediction
            self.last_sequences = normalized_prices[-self.sequence_length:]
            
            self.is_trained = True
            print(f"Training completed. Best validation loss: {best_val_loss:.6f}")
            
            return {
                'epochs_trained': len(self.training_history),
                'best_val_loss': best_val_loss,
                'final_train_loss': self.training_history[-1]['train_loss'],
                'training_history': self.training_history
            }
            
        except Exception as e:
            raise ModelTrainingError(f"Failed to train LSTM model: {str(e)}")
    
    def predict(self, horizon: int) -> Tuple[List[float], Dict[str, List[float]]]:
        """Generate predictions for specified horizon.
        
        Args:
            horizon: Number of time steps to predict
            
        Returns:
            Tuple of (predictions, confidence_intervals)
        """
        if not self.is_trained:
            raise ForecastingError("Model must be trained before making predictions")
        
        try:
            self.model.eval()
            predictions = []
            current_sequence = self.last_sequences.copy()
            
            with torch.no_grad():
                for _ in range(horizon):
                    # Prepare input
                    input_seq = current_sequence[-self.sequence_length:].reshape(1, self.sequence_length, 1)
                    input_tensor = torch.FloatTensor(input_seq).to(self.device)
                    
                    # Make prediction
                    output = self.model(input_tensor)
                    pred_normalized = output.cpu().numpy()[0, 0]
                    
                    # Denormalize prediction
                    pred = self._denormalize_data(np.array([pred_normalized]))[0]
                    predictions.append(float(pred))
                    
                    # Update sequence for next prediction
                    current_sequence = np.append(current_sequence, pred_normalized)
            
            # Generate confidence intervals (using historical volatility)
            # Calculate prediction uncertainty based on validation loss
            if self.training_history:
                val_loss = self.training_history[-1]['val_loss']
                uncertainty = np.sqrt(val_loss) * self.scaler_std
            else:
                uncertainty = np.std(predictions) * 0.1
            
            confidence_intervals = {
                'lower': [max(0, p - 1.96 * uncertainty) for p in predictions],
                'upper': [p + 1.96 * uncertainty for p in predictions]
            }
            
            return predictions, confidence_intervals
            
        except Exception as e:
            raise ForecastingError(f"Prediction failed: {str(e)}")
    
    def evaluate(self, test_data: pd.DataFrame, target_column: str = 'close') -> Dict[str, float]:
        """Evaluate model performance on test data.
        
        Args:
            test_data: Test dataset
            target_column: Column name for target variable
            
        Returns:
            Dictionary of evaluation metrics
        """
        if not self.is_trained:
            return {'mae': float('inf'), 'rmse': float('inf'), 'r2': -1.0, 'accuracy': 0.0}
        
        try:
            # Extract and normalize test data
            test_prices = test_data[target_column].values
            normalized_test = self._normalize_data(test_prices, fit=False)
            
            # Create sequences
            test_sequences, test_targets = self._create_sequences(normalized_test)
            
            if len(test_sequences) == 0:
                return {'mae': float('inf'), 'rmse': float('inf'), 'r2': -1.0, 'accuracy': 0.0}
            
            # Make predictions
            self.model.eval()
            predictions = []
            
            with torch.no_grad():
                for seq in test_sequences:
                    input_tensor = torch.FloatTensor(seq).unsqueeze(0).to(self.device)
                    output = self.model(input_tensor)
                    predictions.append(output.cpu().numpy()[0, 0])
            
            predictions = np.array(predictions)
            
            # Denormalize
            predictions_denorm = self._denormalize_data(predictions)
            targets_denorm = self._denormalize_data(test_targets)
            
            # Calculate metrics
            mae = float(np.mean(np.abs(targets_denorm - predictions_denorm)))
            rmse = float(np.sqrt(np.mean((targets_denorm - predictions_denorm) ** 2)))
            
            # R² score
            ss_res = np.sum((targets_denorm - predictions_denorm) ** 2)
            ss_tot = np.sum((targets_denorm - np.mean(targets_denorm)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Mean Absolute Percentage Error
            mape = float(np.mean(np.abs((targets_denorm - predictions_denorm) / targets_denorm)) * 100)
            
            return {
                'mae': mae,
                'rmse': rmse,
                'r2': float(r2),
                'mape': mape,
                'accuracy': max(0, min(1, r2))
            }
            
        except Exception as e:
            print(f"Evaluation error: {str(e)}")
            return {'mae': float('inf'), 'rmse': float('inf'), 'r2': -1.0, 'accuracy': 0.0}
    
    def _save_checkpoint(self, filename: str, epoch: int, val_loss: float):
        """Save model checkpoint.
        
        Args:
            filename: Checkpoint filename
            epoch: Current epoch number
            val_loss: Validation loss
        """
        try:
            checkpoint_path = os.path.join(self.checkpoint_dir, filename)
            
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': self.model.state_dict(),
                'val_loss': val_loss,
                'scaler_mean': self.scaler_mean,
                'scaler_std': self.scaler_std,
                'sequence_length': self.sequence_length,
                'hidden_size': self.hidden_size,
                'num_layers': self.num_layers,
                'dropout': self.dropout,
                'training_history': self.training_history,
                'last_sequences': self.last_sequences
            }
            
            torch.save(checkpoint, checkpoint_path)
            
        except Exception as e:
            print(f"Warning: Could not save checkpoint: {str(e)}")
    
    def _load_checkpoint(self, filename: str) -> bool:
        """Load model checkpoint.
        
        Args:
            filename: Checkpoint filename
            
        Returns:
            True if checkpoint loaded successfully, False otherwise
        """
        try:
            checkpoint_path = os.path.join(self.checkpoint_dir, filename)
            
            if not os.path.exists(checkpoint_path):
                return False
            
            checkpoint = torch.load(checkpoint_path, map_location=self.device)
            
            # Restore model state
            if self.model is None:
                input_size = 1
                self.model = LSTMNetwork(
                    input_size=input_size,
                    hidden_size=checkpoint['hidden_size'],
                    num_layers=checkpoint['num_layers'],
                    dropout=checkpoint['dropout'],
                    output_size=1
                ).to(self.device)
            
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.scaler_mean = checkpoint['scaler_mean']
            self.scaler_std = checkpoint['scaler_std']
            self.training_history = checkpoint.get('training_history', [])
            self.last_sequences = checkpoint.get('last_sequences')
            
            return True
            
        except Exception as e:
            print(f"Warning: Could not load checkpoint: {str(e)}")
            return False
    
    def save_model(self, symbol: str):
        """Save complete model for a specific symbol.
        
        Args:
            symbol: Symbol identifier (e.g., 'GOLD', 'SILVER')
        """
        filename = f"{symbol}_lstm_model.pt"
        if self.training_history:
            val_loss = self.training_history[-1]['val_loss']
            epoch = self.training_history[-1]['epoch']
        else:
            val_loss = 0.0
            epoch = 0
        
        self._save_checkpoint(filename, epoch, val_loss)
        print(f"Model saved: {filename}")
    
    def load_model(self, symbol: str) -> bool:
        """Load complete model for a specific symbol.
        
        Args:
            symbol: Symbol identifier (e.g., 'GOLD', 'SILVER')
            
        Returns:
            True if model loaded successfully, False otherwise
        """
        filename = f"{symbol}_lstm_model.pt"
        success = self._load_checkpoint(filename)
        
        if success:
            self.is_trained = True
            print(f"Model loaded: {filename}")
        
        return success
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model configuration and training status.
        
        Returns:
            Dictionary with model information
        """
        info = {
            'model_type': 'LSTM',
            'is_trained': self.is_trained,
            'device': str(self.device),
            'sequence_length': self.sequence_length,
            'hidden_size': self.hidden_size,
            'num_layers': self.num_layers,
            'dropout': self.dropout,
            'learning_rate': self.learning_rate,
            'batch_size': self.batch_size,
            'epochs': self.epochs,
            'early_stopping_patience': self.early_stopping_patience
        }
        
        if self.training_history:
            info['training_epochs'] = len(self.training_history)
            info['best_val_loss'] = min(h['val_loss'] for h in self.training_history)
            info['final_train_loss'] = self.training_history[-1]['train_loss']
            info['final_val_loss'] = self.training_history[-1]['val_loss']
        
        return info
