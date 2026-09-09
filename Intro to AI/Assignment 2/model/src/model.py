import torch
import torch.nn as nn
from torch import Tensor
import pandas as pd
from glob import glob
from functools import reduce

torch.manual_seed(1)
hidden_layers = [100, 50, 25] # higher the network, the more its connected
output_layers = 1

file_paths = glob("data/*.csv")

class SimpleNN(nn.Module):
    def __init__(self, input_size, hidden_sizes: list[int], output_size) -> None:
        super(SimpleNN, self).__init__()

        layers = []
        in_dim = input_size

        for h_dim in hidden_sizes:
            layers.append(nn.Linear(in_dim, h_dim))
            in_dim = h_dim

        layers.append(nn.Linear(in_dim, output_size))
        self.network = nn.Sequential(*layers)
        

    def forward(self, x: Tensor) -> Tensor:
        return self.network(x)


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

x_tensor: Tensor = torch.tensor(features_df.values, dtype=torch.float32)

num_students, input_layers = x_tensor.shape
model = SimpleNN(input_layers, hidden_layers, output_layers)

output = model(x_tensor)

print("Model Output:", output)

for name, pred in zip(student_names, output):
    probability = torch.sigmoid(pred)
    pass_or_fail = (probability >= 0.5).int()
    print(f"Student: {name:<16} | Model Output: {pred.item():.4f} | Probability: {(probability.item() * 100):.4f}% | {'Pass' if pass_or_fail.item() == 1 else 'Fail'}")
