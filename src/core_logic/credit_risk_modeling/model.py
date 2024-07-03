import torch
import torch.nn as nn
import torch.optim as optim
from src.data_manager import DataManager

class DNN(nn.Module):
    """Prototypes a deep neural network (DNN) architecture for credit risk modeling."""

    def __init__(self, model_name: str, file_path: str, sheet_name: str = None) -> None:
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

        # Determine the input size based on the number of features
        self.input_size = len(self.data.columns) - 1  # Assuming the last column is the target variable

        # (Add your data preprocessing steps here - very important!)
        #  - Handle missing values
        #  - Feature scaling 
        #  - Split data into train/validation/test sets
        #  - Convert data to PyTorch tensors

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

    def train_model(self, train_loader, epochs=10, learning_rate=0.001):
        """Trains the DNN model."""
        criterion = nn.BCELoss()  # Binary Cross Entropy Loss
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)

        for epoch in range(epochs):
            for i, (inputs, labels) in enumerate(train_loader):
                inputs, labels = inputs.to(self.device), labels.to(self.device)

                # Forward pass
                outputs = self.model(inputs)
                loss = criterion(outputs, labels.unsqueeze(1).float())  # Unsqueeze for shape compatibility

                # Backward pass and optimization
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')

    # ... (Add methods for evaluation, prediction, saving/loading the model, etc.) 