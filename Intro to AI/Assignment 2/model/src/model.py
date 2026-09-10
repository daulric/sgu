from functools import reduce
from glob import glob
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch import Tensor
import matplotlib.pyplot as plt
import numpy as np
import diagram

from diagram import Diagram

torch.manual_seed(1)

file_paths = glob("data/*.csv")

class SimpleNN(nn.Module):
    def __init__(self, input_size, hidden_sizes: list[int], output_size) -> None:
        super(SimpleNN, self).__init__()

        layers = []
        in_dim = input_size

        for h_dim in hidden_sizes:
            layers.append(nn.Linear(in_dim, h_dim))
            layers.append(nn.ReLU())
            in_dim = h_dim

        layers.append(nn.Linear(in_dim, output_size))
        self.network = nn.Sequential(*layers)

    def forward(self, x: Tensor) -> Tensor:
        return self.network(x)

def chooseHiddenLayers(num_samples, input_dim): # this selects how many layers thats needed
    first_width = max(4, min(64, num_samples * 2, input_dim))

    if num_samples < 20:
        depth = 1
    elif num_samples < 60:
        depth = 2
    elif num_samples < 150:
        depth = 3
    else:
        depth = 4

    layers = [first_width]
    width = first_width
    for _ in range(depth - 1):
        width = max(4, width // 2)
        layers.append(width)

    return layers

def load_report(path, idx):
    raw = pd.read_csv(path, header=None)
    subject_row = raw.iloc[9].ffill()
    field_row = raw.iloc[10]

    columns = []

    for subj, field in zip(subject_row, field_row):
        field = str(field).strip()

        if field == "Student":
            columns.append("Student")
        elif field == "Position":
            columns.append("Position")
        elif field == "Year Average":
            columns.append(f"Year Average_{idx+1}")
        else:
            columns.append(f"{str(subj).strip()}_{field}_{idx+1}")
    
    df = raw.iloc[11:].copy()
    df.columns = columns
    df["Student"] = df["Student"].astype(str).str.strip()
    df = df.dropna(subset=["Student"])
    df = df.drop(columns=["Position"], errors="ignore")
    return df


processed_dfs = [load_report(f, idx) for idx, f in enumerate(file_paths)]

if not processed_dfs:
    raise ValueError("No CSV files found in the 'data' directory.")

merged_df = reduce(
    lambda left, right: pd.merge(left, right, on="Student", how="outer"),
    processed_dfs
)

student_names = merged_df["Student"].tolist()
features_df = merged_df.drop(columns=["Student", "Position"], errors="ignore")
features_df = features_df.apply(pd.to_numeric, errors="coerce").fillna(0)

valid_means = features_df.replace(0, pd.NA).mean(axis=1, skipna=True).fillna(0)

features_normalized = (features_df - features_df.mean()) / (features_df.std() + 1e-8)
x_tensor: Tensor = torch.tensor(features_normalized.values, dtype=torch.float32)

y_labels = (valid_means >= 50.0).astype(float).values
y_tensor: Tensor = torch.tensor(y_labels, dtype=torch.float32).unsqueeze(1)

num_students, input_layers = x_tensor.shape
print("Tensor Shape: ",x_tensor.shape)

hidden_layers = chooseHiddenLayers(num_students, input_layers)
output_layers = 1

model = SimpleNN(input_layers, hidden_layers, output_layers)

criterion = nn.BCEWithLogitsLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

epochs = 100
model.train()

for epoch in range(1, epochs + 1):
    optimizer.zero_grad()
    predictions = model(x_tensor)
    loss = criterion(predictions, y_tensor)
    loss.backward()
    optimizer.step()

model.eval()
with torch.no_grad():
    output = model(x_tensor)

print(f"Hidden Layers Amount: {len(hidden_layers)}")
for idx, layer_size in enumerate(hidden_layers):
    print(f"Hidden Layer {idx + 1} Size: {layer_size}")

for name, pred in zip(student_names, output):
    probability = torch.sigmoid(pred)
    pass_or_fail = (probability >= 0.5).int()
    print(f"Student: {name:<16} | Model Output: {pred.item():.4f} | Probability: {(probability.item() * 100):.4f}% | {'Pass' if pass_or_fail.item() == 1 else 'Fail'}")

d = Diagram(model, x_tensor, student_names)

d.plot_diagram()
d.render_network_diagram(num_students)