import os
import numpy as np
import torch
import torchvision.transforms as transforms
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader, random_split


class LoadData:
    """Download, split and shuffle dataset into train, validate, test and pool"""

    def __init__(self, val_size: int = 100):
        self.train_size = 1000
        self.val_size = val_size
        self.pool_size = 5712 - self.train_size - self.val_size
        self.cancer_train, self.cancer_test = self.download_dataset()
        (
            self.X_train_All,
            self.y_train_All,
            self.X_val,
            self.y_val,
            self.X_pool,
            self.y_pool,
            self.X_test,
            self.y_test,
        ) = self.split_and_load_dataset()
        self.X_init, self.y_init = self.preprocess_training_data()

    def tensor_to_np(self, tensor_data: torch.Tensor) -> np.ndarray:
        """Since Skorch doesn not support dtype of torch.Tensor, we will modify
        the dtype to numpy.ndarray

        Attribute:
            tensor_data: Data of class type=torch.Tensor
        """
        np_data = tensor_data.detach().numpy()
        return np_data

    def download_dataset(self):
        """Load Cancer dataset for training and test set."""
        transform = transforms.Compose(
            [transforms.Resize((64, 64)), transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
        )
        cancer_train = ImageFolder("dataset/Training", transform=transform)
        cancer_test = ImageFolder("dataset/Testing", transform=transform)
        return cancer_train, cancer_test

    def split_and_load_dataset(self):
        """Split all training datatset into train, validate, pool sets and load them accordingly."""
        train_set, val_set, pool_set = random_split(
            self.cancer_train, [self.train_size, self.val_size, self.pool_size]
        )
        train_loader = DataLoader(
            dataset=train_set, batch_size=self.train_size, shuffle=True
        )
        val_loader = DataLoader(dataset=val_set, batch_size=self.val_size, shuffle=True)
        pool_loader = DataLoader(
            dataset=pool_set, batch_size=self.pool_size, shuffle=True
        )
        test_loader = DataLoader(
            dataset=self.cancer_test, batch_size=1311, shuffle=True
        )
        X_train_All, y_train_All = next(iter(train_loader))
        X_val, y_val = next(iter(val_loader))
        X_pool, y_pool = next(iter(pool_loader))
        X_test, y_test = next(iter(test_loader))
        return X_train_All, y_train_All, X_val, y_val, X_pool, y_pool, X_test, y_test

    def preprocess_training_data(self):
        """Setup a random but balanced initial training set of 20 data points

        Attributes:
            X_train_All: X input of training set,
            y_train_All: y input of training set
        """
        initial_idx = np.array([], dtype=np.int)
        for i in range(4):
            idx = np.random.choice(
                np.where(self.y_train_All == i)[0], size=2, replace=False
            )
            initial_idx = np.concatenate((initial_idx, idx))
        X_init = self.X_train_All[initial_idx]
        y_init = self.y_train_All[initial_idx]
        print(f"Initial training data points: {X_init.shape[0]}")
        print(f"Data distribution for each class: {np.bincount(y_init)}")
        return X_init, y_init

    def load_all(self):
        """Load all data"""
        return (
            self.tensor_to_np(self.X_init),
            self.tensor_to_np(self.y_init),
            self.tensor_to_np(self.X_val),
            self.tensor_to_np(self.y_val),
            self.tensor_to_np(self.X_pool),
            self.tensor_to_np(self.y_pool),
            self.tensor_to_np(self.X_test),
            self.tensor_to_np(self.y_test),
        )
