import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from src.data_manager import DataManager
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd

class DNN(nn.Module):
    """Prototypes a deep neural network (DNN) architecture for credit risk modeling."""

    def __init__(self, model_name: str, file_path: str, sheet_name: str = None) -> None:
        super(DNN, self).__init__()
        self.model_name = model_name
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.data = None
        self.model = None
        self.input_size = None  # To be determined after data loading
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def load_data(self):
        """Loads data from an Excel file using the DataManager."""
        data_manager = DataManager(self.file_path)
        self.data = data_manager.load_data(data_format="excel", sheet_name=self.sheet_name)

        # Data preprocessing
        # Handle missing values (for simplicity, let's fill them with the mean of each column)
        self.data = self.data.fillna(self.data.mean())

        # Feature scaling
        features = self.data.drop(columns='target')
        target = self.data['target']
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)

        # Split data into train/validation/test sets
        X_train, X_temp, y_train, y_temp = train_test_split(features_scaled, target, test_size=0.3, random_state=42)
        X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

        # Convert data to PyTorch tensors
        self.train_data = TensorDataset(torch.tensor(X_train, dtype=torch.float32),
                                        torch.tensor(y_train.values, dtype=torch.float32))
        self.val_data = TensorDataset(torch.tensor(X_val, dtype=torch.float32),
                                      torch.tensor(y_val.values, dtype=torch.float32))
        self.test_data = TensorDataset(torch.tensor(X_test, dtype=torch.float32),
                                       torch.tensor(y_test.values, dtype=torch.float32))

        # DataLoader
        self.train_loader = DataLoader(self.train_data, batch_size=64, shuffle=True)
        self.val_loader = DataLoader(self.val_data, batch_size=64, shuffle=False)
        self.test_loader = DataLoader(self.test_data, batch_size=64, shuffle=False)

        # Determine the input size based on the number of features
        self.input_size = X_train.shape[1]

    def build_model(self, hidden_size1=64, hidden_size2=32):
        """Builds a basic DNN architecture."""
        self.model = nn.Sequential(
            nn.Linear(self.input_size, hidden_size1),
            nn.ReLU(),
            nn.Linear(hidden_size1, hidden_size2),
            nn.ReLU(),
            nn.Linear(hidden_size2, 1),  # Output layer - 1 neuron for binary classification
            nn.Sigmoid()  # Sigmoid for outputting probability between 0 and 1
        ).to(self.device)

    def train_model(self, epochs=10, learning_rate=0.001):
        """Trains the DNN model."""
        criterion = nn.BCELoss()  # Binary Cross Entropy Loss
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)

        for epoch in range(epochs):
            self.model.train()
            for i, (inputs, labels) in enumerate(self.train_loader):
                inputs, labels = inputs.to(self.device), labels.to(self.device)

                # Forward pass
                outputs = self.model(inputs)
                loss = criterion(outputs, labels.unsqueeze(1).float())  # Unsqueeze for shape compatibility

                # Backward pass and optimization
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            # Print training loss
            print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')

            # Validation
            self.validate_model()

    def validate_model(self):
        """Validates the DNN model on the validation set."""
        self.model.eval()
        with torch.no_grad():
            val_loss = 0.0
            correct = 0
            total = 0
            criterion = nn.BCELoss()

            for inputs, labels in self.val_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                outputs = self.model(inputs)
                loss = criterion(outputs, labels.unsqueeze(1).float())
                val_loss += loss.item()

                predicted = (outputs > 0.5).float()
                total += labels.size(0)
                correct += (predicted.squeeze().long() == labels.long()).sum().item()

            val_loss /= len(self.val_loader)
            accuracy = 100 * correct / total
            print(f'Validation Loss: {val_loss:.4f}, Accuracy: {accuracy:.2f}%')

    def test_model(self):
        """Tests the DNN model on the test set."""
        self.model.eval()
        with torch.no_grad():
            test_loss = 0.0
            correct = 0
            total = 0
            criterion = nn.BCELoss()

            for inputs, labels in self.test_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                outputs = self.model(inputs)
                loss = criterion(outputs, labels.unsqueeze(1).float())
                test_loss += loss.item()

                predicted = (outputs > 0.5).float()
                total += labels.size(0)
                correct += (predicted.squeeze().long() == labels.long()).sum().item()

            test_loss /= len(self.test_loader)
            accuracy = 100 * correct / total
            print(f'Test Loss: {test_loss:.4f}, Accuracy: {accuracy:.2f}%')

    def save_model(self, path):
        """Saves the trained model to a file."""
        torch.save(self.model.state_dict(), path)
        print(f'Model saved to {path}')

    def load_model(self, path):
        """Loads a model from a file."""
        self.model.load_state_dict(torch.load(path))
        self.model.to(self.device)
        print(f'Model loaded from {path}')

    def predict(self, inputs):
        """Predicts the outputs for given inputs using the trained model."""
        self.model.eval()
        inputs = torch.tensor(inputs, dtype=torch.float32).to(self.device)
        with torch.no_grad():
            outputs = self.model(inputs)
        return outputs.cpu().numpy()
