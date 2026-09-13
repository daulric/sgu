from functools import reduce
from glob import glob
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch import Tensor
from diagram import Diagram
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, confusion_matrix

torch.manual_seed(1)

file_paths = glob("data/*.csv")
max_samples = None
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

if max_samples and max_samples > 0:
    merged_df.head(max_samples)

student_names = merged_df["Student"].tolist()
features_df = merged_df.drop(columns=["Student", "Position"], errors="ignore")
features_df = features_df.apply(pd.to_numeric, errors="coerce").fillna(0)

valid_means = features_df.replace(0, pd.NA).mean(axis=1, skipna=True).fillna(0)

features_normalized = (features_df - features_df.mean()) / (features_df.std() + 1e-8)
y_labels = (valid_means >= 50.0).astype(float).values

# data splitting
x_train, x_test, y_train, y_test = train_test_split(
    features_normalized.values, 
    y_labels, 
    test_size=0.2, 
    random_state=1
)

x_train_t = torch.tensor(x_train, dtype=torch.float32)
y_train_t = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
x_test_t = torch.tensor(x_test, dtype=torch.float32)
y_test_t = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)

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

# epoch is the amount of times the training is looped
epochs = 100
train_losses = [] # stores loss items during the epoch training
model.train()

for epoch in range(1, epochs + 1):
    optimizer.zero_grad()
    predictions = model(x_train_t)
    loss = criterion(predictions, y_train_t)
    loss.backward()
    optimizer.step()
    train_losses.append(loss.item())

model.eval()
with torch.no_grad():
    output = model(x_tensor)

print(f"Hidden Layers Amount: {len(hidden_layers)}")
for idx, layer_size in enumerate(hidden_layers):
    print(f"Hidden Layer {idx + 1} Size: {layer_size}")

class_scores = []
keep_score = 0

for name, pred in zip(student_names, output):
    probability = torch.sigmoid(pred)
    class_scores.append((probability.item() * 100))
    pass_or_fail = (probability >= 0.5).int()
    print(f"Student: {name:<16} | Model Output: {pred.item():.4f} | Probability: {(probability.item() * 100):.4f}% | {'Pass' if pass_or_fail.item() == 1 else 'Fail'}")


for s in class_scores:
    keep_score += s

class_passing_confidence = keep_score / len(class_scores) # getting the model confidence score on the class passing rate
print(f"Class Passing Confidence: {round(class_passing_confidence)}%")

with torch.no_grad():
    test_outputs = model(x_test_t)
    test_probs = torch.sigmoid(test_outputs)
    y_pred_binary = (test_probs >= 0.5).int().numpy()

acc = accuracy_score(y_test, y_pred_binary)
prec = precision_score(y_test, y_pred_binary, zero_division=0)
cm = confusion_matrix(y_test, y_pred_binary)

# logging precision and accuracy
print("--- TEST SET EVALUATION METRICS ---")
print(f"Accuracy:  {acc * 100:.2f}%")
print(f"Precision: {prec:.4f}")
print("Confusion Matrix:\n", cm)

# diagram for network layer diagram
d = Diagram(model, x_tensor, student_names)
d.plot_diagram()
d.render_network_diagram(num_students)
d.plot_performance_graph(epochs, train_losses)