import os
from typing import cast
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def plot_diagram(model: nn.Module, x_data: torch.Tensor, student_names: list[str], file_name: str = "./output/real_layer_activations.png"):
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    model.eval()

    activations = []
    layer_names = ["Input Layer"]
    x = x_data

    # Retrieve sequential container safely for typing
    network = getattr(model, 'network', model)
    layers = list(network.children())
    total_layers = len(layers)

    with torch.no_grad():
        activations.append(x.numpy())

        for idx, layer in enumerate(layers):
            x = layer(x)
            if isinstance(layer, nn.ReLU):
                activations.append(x.numpy())
                layer_names.append("Hidden Layer (ReLU)")
            elif idx == total_layers - 1:
                probs = torch.sigmoid(x).numpy()
                activations.append(probs)
                layer_names.append("Output Probabilities")

    fig, axes = plt.subplots(len(activations), 1, figsize=(10, 3 * len(activations)))

    if len(activations) == 1:
        axes = [axes]

    for idx, (act, name) in enumerate(zip(activations, layer_names)):
        ax = axes[idx]
        im = ax.imshow(act, aspect='auto', cmap='viridis')
        ax.set_title(f"{name} | Shape: {act.shape}", fontsize=11, fontweight='bold')
        ax.set_yticks(range(len(student_names)))
        ax.set_yticklabels(student_names)
        ax.set_xlabel("Neuron Index")
        fig.colorbar(im, ax=ax, orientation='vertical', pad=0.02)

    plt.tight_layout()
    plt.savefig(file_name, bbox_inches='tight')
    plt.close()

def render_network_diagram(input_dim: int, hidden_sizes: list[int], output_dim: int, filename: str = "./output/deep_neural_network.png"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Increased figure height to give room for 64 small circles
    fig, ax = plt.subplots(figsize=(12, 10), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')

    color_input = '#0066FF'     # Blue
    color_hidden = '#2AD1C8'    # Turquoise
    color_output = '#6E9CFF'    # Soft Blue

    num_hidden = len(hidden_sizes)
    
    # Cap input layer visual count to avoid drawing 915 circles (which turns black), 
    # but render exact neuron counts for hidden and output layers (64, 32, 16, 1)
    all_layer_dims = [input_dim] + list(hidden_sizes) + [output_dim]
    num_layers = len(all_layer_dims)

    x_positions = [1.5 + (7.0 / (num_layers - 1)) * i for i in range(num_layers)]

    # Titles
    ax.text(x_positions[0], 7.3, "Input layer", fontsize=13, fontweight='bold', ha='center', color='#111827')
    if num_hidden > 0:
        mid_x = (x_positions[1] + x_positions[-2]) / 2 if num_hidden > 1 else x_positions[1]
        ax.text(mid_x, 7.3, "Multiple hidden layer" if num_hidden > 1 else "Hidden layer", 
                fontsize=13, fontweight='bold', ha='center', color='#111827')
    ax.text(x_positions[-1], 7.3, "Output layer", fontsize=13, fontweight='bold', ha='center', color='#111827')

    layer_nodes = []

    # Nodes
    for idx, (dim, x) in enumerate(zip(all_layer_dims, x_positions)):
        if idx == 0:
            c = color_input
            visual_count = 10  # Sample input features
        elif idx == num_layers - 1:
            c = color_output
            visual_count = dim
        else:
            c = color_hidden
            visual_count = dim  # Renders full 64, 32, 16 neurons literally

        # Dynamic circle radius & line thickness: smaller circles for larger layers
        radius = max(0.03, min(0.22, 1.6 / visual_count))
        
        y_step = 5.8 / (visual_count + 1)
        ys = [1.0 + y_step * (i + 1) for i in range(visual_count)]
        layer_nodes.append((x, ys, radius))

        for y in ys:
            circle = patches.Circle((x, y), radius, color=c, zorder=3)
            ax.add_patch(circle)

        ax.text(x, 0.4, f"Dim: {dim}", fontsize=9, fontweight='bold', ha='center', color='#4B5563')

    # Connections / Synapses
    for i in range(len(layer_nodes) - 1):
        x1, ys1, r1 = layer_nodes[i]
        x2, ys2, r2 = layer_nodes[i+1]
        line_color = '#3B82F6' if i == 0 else ('#93C5FD' if i == len(layer_nodes)-2 else '#67E8F9')
        
        # Use thinner arrows/lines when dealing with many nodes
        line_width = 0.3 if len(ys1) * len(ys2) > 200 else 0.7

        for y1 in ys1:
            for y2 in ys2:
                arrow = patches.FancyArrowPatch(
                    (x1 + r1, y1), (x2 - r2, y2),
                    arrowstyle='->', mutation_scale=4,
                    color=line_color, lw=line_width, alpha=0.4, zorder=2
                )
                ax.add_patch(arrow)

    plt.suptitle("Deep neural network", x=0.15, y=0.95, fontsize=20, fontweight='bold', ha='left', color='#111827')
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight', dpi=300)
    plt.close()

# performance graph need here

class Diagram:
    def __init__(self, model: nn.Module, x_data: torch.Tensor, student_names: list[str]):
        self.model = model
        self.x_data = x_data
        self.student_names = student_names

    def plot_diagram(self, file_name: str = "./output/real_layer_activations.png"):
        plot_diagram(self.model, self.x_data, self.student_names, file_name)

    def render_network_diagram(self, input_dim, filename: str = "./output/deep_neural_network.png"):
        # Safely extract Linear layers across types
        network = getattr(self.model, 'network', self.model)
        linear_layers = [cast(nn.Linear, layer) for layer in network.children() if isinstance(layer, nn.Linear)]

        hidden_sizes = [layer.out_features for layer in linear_layers[:-1]]
        output_dim = linear_layers[-1].out_features

        render_network_diagram(input_dim, hidden_sizes, output_dim, filename)