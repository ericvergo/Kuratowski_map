import math
import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Global variables
sliders = []
labels = []
arcs = []
point_history = []
points = []
colors = ["black", "red", "green", "blue"]
delta_one = delta_two = delta_three = 0
delta_one_label = delta_two_label = delta_three_label = None
canvas = None
circle_center_x = circle_center_y = circle_radius = 0
ax = None
canvas_3d = None


def render():  # Main function to render the GUI
    global delta_one, delta_two, delta_three
    update_deltas()
    draw_arcs()
    draw_points()
    update_3d_plot(delta_one, delta_two, delta_three)


def update_deltas():  # Calculate and update delta values based on slider positions
    global delta_one, delta_two, delta_three, delta_one_label, delta_two_label, delta_three_label, labels

    black_angle = sliders[0].get()
    green_angle = sliders[1].get()
    blue_angle = sliders[2].get()
    purple_angle = sliders[3].get()

    delta_one = min((green_angle - black_angle) % (2 * math.pi), (black_angle - green_angle) % (2 * math.pi))
    delta_two = min((blue_angle - black_angle) % (2 * math.pi), (black_angle - blue_angle) % (2 * math.pi))
    delta_three = min((purple_angle - black_angle) % (2 * math.pi), (black_angle - purple_angle) % (2 * math.pi))

    delta_one_label.config(text=f"Delta {colors[1]}: {delta_one:.2f}")
    delta_two_label.config(text=f"Delta {colors[2]}: {delta_two:.2f}")
    delta_three_label.config(text=f"Delta {colors[3]}: {delta_three:.2f}")

    for i in range(1, 4):
        labels[i].config(text=f"{colors[i]}: {sliders[i].get():.2f}")


def draw_arcs():  # Draw arcs on the canvas based on slider positions.
    global arcs, canvas

    # Clear existing arcs
    for arc in arcs:
        canvas.delete(arc)
    arcs.clear()

    black_angle = float(sliders[0].get())
    to_draw = []

    # Prepare arcs to draw
    for i in range(1, 4):
        color_angle = float(sliders[i].get())
        diff = (color_angle - black_angle) % (2 * math.pi)

        if diff > math.pi:
            start_angle = black_angle
            extent = -(2 * math.pi - diff)
        else:
            start_angle = black_angle
            extent = diff

        start_angle_deg = math.degrees(start_angle)
        extent_deg = math.degrees(extent)
        to_draw.append((start_angle_deg, extent_deg, i, abs(extent_deg)))

    # Sort arcs by size, decreasing
    to_draw.sort(key=lambda x: x[3], reverse=True)

    # Draw the arcs
    for arc_data in to_draw:
        arc = canvas.create_arc(
            circle_center_x - circle_radius,
            circle_center_y - circle_radius,
            circle_center_x + circle_radius,
            circle_center_y + circle_radius,
            start=arc_data[0],
            extent=arc_data[1],
            outline=colors[arc_data[2]],
            style=tk.ARC,
            width=5
        )
        arcs.append(arc)


def draw_points():  # Draw points on the canvas based on slider positions.
    global circle_center_x, circle_center_y, circle_radius, points, sliders, canvas

    # Clear existing points
    for point in points:
        canvas.delete(point)
    points.clear()

    # Draw new points
    for i in range(4):
        angle = sliders[i].get()
        x = circle_center_x + circle_radius * math.cos(angle)
        y = circle_center_y - circle_radius * math.sin(angle)
        point = canvas.create_oval(x - 9, y - 9, x + 9, y + 9, fill=colors[i], outline='black')
        points.append(point)


def update_3d_plot(x, y, z):  # Update the 3D plot with new delta values.
    global ax, canvas_3d, point_history

    ax.clear()
    ax.set_xlim([0, math.pi])
    ax.set_ylim([0, math.pi])
    ax.set_zlim([0, math.pi])
    ax.set_xlabel(f'Delta {colors[1]}')
    ax.set_ylabel(f'Delta {colors[2]}')
    ax.set_zlabel(f'Delta {colors[3]}')

    # Plot the history of points
    if point_history:
        history_array = np.array(point_history)
        ax.scatter(history_array[:, 0], history_array[:, 1], history_array[:, 2], color='black', s=1, alpha=0.5)

    # Add the new point to the history
    point_history.append((x, y, z))

    # Plot the current point and lines
    ax.plot([0, x], [0, 0], [0, 0], color=colors[1])
    ax.plot([x, x], [0, y], [0, 0], color=colors[2])
    ax.plot([x, x], [y, y], [0, z], color=colors[3])
    ax.scatter(x, y, z, color='black', s=25)

    plt.tight_layout()
    canvas_3d.draw()


def cycle_black():
    """Cycle the black slider through all positions and update the plot."""
    green_angle = sliders[1].get()
    blue_angle = sliders[2].get()
    purple_angle = sliders[3].get()

    black_angles = np.linspace(0, 2 * math.pi, 1000)

    for black_angle in black_angles:
        delta_green = min((green_angle - black_angle) % (2 * math.pi), (black_angle - green_angle) % (2 * math.pi))
        delta_blue = min((blue_angle - black_angle) % (2 * math.pi), (black_angle - blue_angle) % (2 * math.pi))
        delta_purple = min((purple_angle - black_angle) % (2 * math.pi), (black_angle - purple_angle) % (2 * math.pi))
        point_history.append((delta_green, delta_blue, delta_purple))

    render()


def reset_path():
    """Clear the point history and reset the 3D plot."""
    global point_history
    point_history.clear()
    render()


def create_gui():  # Create the main GUI elements
    global root, sliders, labels, canvas, delta_one_label, delta_two_label, delta_three_label, ax, canvas_3d

    root.title("Kuratowski Map")
    root.geometry("1000x750")

    # Left frame for sliders and buttons
    left_frame = ttk.Frame(root, padding="10")
    left_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))

    for i in range(4):
        frame = ttk.Frame(left_frame, padding="5")
        frame.grid(row=i, column=0, sticky=(tk.W, tk.E))

        slider = ttk.Scale(frame, from_=0, to=2 * math.pi, length=300, orient="horizontal",
                           command=lambda num=i: render(), value=(i/ 2) * math.pi)
        slider.grid(column=1, row=0)
        sliders.append(slider)

        label = ttk.Label(frame, text=f"{colors[i]}: 0.00")
        label.grid(column=2, row=0)
        labels.append(label)

    # Button frame
    button_frame = ttk.Frame(left_frame, padding="5")
    button_frame.grid(row=4, column=0, pady=10)

    reset_button = ttk.Button(button_frame, text="Reset Path", command=reset_path)
    reset_button.grid(row=0, column=0, padx=5)

    cycle_black_button = ttk.Button(button_frame, text="Cycle Black", command=cycle_black)
    cycle_black_button.grid(row=0, column=1, padx=5)

    # Right frame for canvas, delta values, and 3D plot
    right_frame = ttk.Frame(root, padding="10")
    right_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.W, tk.E))

    # Canvas setup
    canvas_size = 300
    canvas = tk.Canvas(right_frame, width=canvas_size, height=canvas_size, bg="white")
    canvas.grid(row=0, column=0, columnspan=3)

    # Draw circle
    global circle_center_x, circle_center_y, circle_radius
    circle_center_x = circle_center_y = canvas_size // 2
    circle_radius = 100
    canvas.create_oval(circle_center_x - circle_radius, circle_center_y - circle_radius,
                       circle_center_x + circle_radius, circle_center_y + circle_radius,
                       outline="black", width=2)

    # Labels for delta values
    delta_one_label = ttk.Label(right_frame, text=f"Delta {colors[1]}: 0.00")
    delta_one_label.grid(row=1, column=0, pady=5)

    delta_two_label = ttk.Label(right_frame, text=f"Delta {colors[2]}: 0.00")
    delta_two_label.grid(row=1, column=1, pady=5)

    delta_three_label = ttk.Label(right_frame, text=f"Delta {colors[3]}: 0.00")
    delta_three_label.grid(row=1, column=2, pady=5)

    # 3D plot setup
    fig = plt.Figure(figsize=(5, 5), dpi=100)
    ax = fig.add_subplot(111, projection='3d')
    canvas_3d = FigureCanvasTkAgg(fig, master=right_frame)
    canvas_3d.draw()
    canvas_3d.get_tk_widget().grid(row=2, column=0, columnspan=3, pady=10)

    render()


if __name__ == "__main__":
    root = tk.Tk()
    create_gui()
    root.mainloop()
