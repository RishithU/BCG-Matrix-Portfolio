import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

# Function to classify products and suggest strategies
def classify_product(market_share, growth_rate):
    if growth_rate > 0.5:
        if market_share >= 0.5:
            return "Stars", "Invest heavily to maintain position."
        else:
            return "Question Marks", "Evaluate potential and invest selectively."
    else:
        if market_share >= 0.5:
            return "Cash Cows", "Milk profits to fund other products."
        else:
            return "Dogs", "Consider divesting or repositioning."

# Function to plot the BCG Matrix
def plot_bcg(data):
    global original_xlim, original_ylim, fig, ax, canvas
    x, y, categories, sizes, products = [], [], [], [], []
    for product, values in data.items():
        x.append(values["market_share"])
        y.append(values["growth_rate"])
        category, strategy = classify_product(values["market_share"], values["growth_rate"])
        categories.append(category)
        products.append((product, strategy))
        sizes.append(values["market_share"] * values["growth_rate"] * 10000)

    # Create a new window for the BCG Matrix
    matrix_window = tk.Toplevel(root)
    matrix_window.title("BCG Matrix")
    matrix_window.geometry("900x700")
    matrix_window.minsize(800, 600)

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = {"Stars": "green", "Cash Cows": "blue", "Question Marks": "orange", "Dogs": "red"}
    ax.scatter(x, y, color=[colors[cat] for cat in categories], s=sizes, alpha=0.6)

    # Set axis limits and labels
    original_xlim, original_ylim = (0, 1), (0, 1)
    ax.set_xlim(original_xlim)
    ax.set_ylim(original_ylim)
    ax.axhline(y=0.5, color='gray', linestyle='--')
    ax.axvline(x=0.5, color='gray', linestyle='--')
    ax.set_xlabel("Relative Market Share", fontsize=14, fontweight="bold")
    ax.set_ylabel("Market Growth Rate", fontsize=14, fontweight="bold")
    ax.set_title("BCG Matrix", fontsize=16, fontweight="bold")

    # Add quadrant labels
    ax.text(0.75, 0.75, "Stars", fontsize=12, color="green", ha='center', fontweight="bold")
    ax.text(0.25, 0.75, "Question Marks", fontsize=12, color="orange", ha='center', fontweight="bold")
    ax.text(0.75, 0.25, "Cash Cows", fontsize=12, color="blue", ha='center', fontweight="bold")
    ax.text(0.25, 0.25, "Dogs", fontsize=12, color="red", ha='center', fontweight="bold")

    # Create legend
    legend_elements = [plt.scatter([], [], color=color, s=100, label=label, alpha=0.6)
                       for label, color in colors.items()]
    ax.legend(handles=legend_elements, title="Categories", loc="best")

    # Embed the plot in Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=matrix_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Hover strategy display label
    strategy_label = tk.Label(matrix_window, text="", font=("Helvetica", 12, "bold"), bg="#e0f7fa",
                              borderwidth=2, relief="groove", padx=10, pady=10)
    strategy_label.place_forget()

    # Update strategy label on hover
    def update_strategy(event):
        if event.inaxes == ax:
            for i, (product, strategy) in enumerate(products):
                if (x[i] - 0.05 < event.xdata < x[i] + 0.05) and (y[i] - 0.05 < event.ydata < y[i] + 0.05):
                    strategy_label.config(text=f"{product}: {strategy}")
                    current_font_size = 12 + int(root.winfo_width() / 100)
                    strategy_label.config(font=("Helvetica", current_font_size, "bold"))
                    label_x, label_y = min(event.x + 50, 700), max(event.y - 20, 20)
                    strategy_label.place(x=label_x, y=label_y)
                    return
        strategy_label.place_forget()

    fig.canvas.mpl_connect('motion_notify_event', update_strategy)

    # Zoom and Reset Buttons
    def zoom_in():
        xlim, ylim = ax.get_xlim(), ax.get_ylim()
        ax.set_xlim([x * 0.9 for x in xlim])
        ax.set_ylim([y * 0.9 for y in ylim])
        canvas.draw()

    def zoom_out():
        xlim, ylim = ax.get_xlim(), ax.get_ylim()
        ax.set_xlim([x * 1.1 for x in xlim])
        ax.set_ylim([y * 1.1 for y in ylim])
        canvas.draw()

    def reset_view():
        ax.set_xlim(original_xlim)
        ax.set_ylim(original_ylim)
        canvas.draw()

    # Save plot as JPEG or PDF
    def save_plot():
        file_path = filedialog.asksaveasfilename(defaultextension=".jpeg",
                                                 filetypes=[("JPEG files", "*.jpeg"), ("PDF files", "*.pdf")])
        if file_path:
            try:
                fig.savefig(file_path)
                messagebox.showinfo("Export", f"BCG Matrix successfully saved as {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to save file:\n{e}")

    # Button Frame
    button_frame = tk.Frame(matrix_window)
    button_frame.pack(side=tk.BOTTOM, fill=tk.X)
    tk.Button(button_frame, text="Zoom In", command=zoom_in, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(button_frame, text="Zoom Out", command=zoom_out, font=("Helvetica", 12, "bold"), bg="#F44336", fg="white").pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(button_frame, text="Reset View", command=reset_view, font=("Helvetica", 12, "bold"), bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(button_frame, text="Export", command=save_plot, font=("Helvetica", 12, "bold"), bg="#FF9800", fg="white").pack(side=tk.LEFT, padx=5, pady=5)

# CSV file dialog
def open_file():
    file_path = filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV files", "*.csv")])
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

# CSV reading and plotting function
def read_and_plot():
    file_path = file_entry.get()
    if file_path:
        try:
            df = pd.read_csv(file_path, index_col='Product')
            if not {'market_share', 'growth_rate'}.issubset(df.columns):
                raise ValueError("CSV must contain 'market_share' and 'growth_rate' columns.")
            data = df[["market_share", "growth_rate"]].to_dict("index")
            plot_bcg(data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read or process the file:\n{e}")
    else:
        messagebox.showwarning("Warning", "Please select a CSV file first.")

# Main window setup
root = tk.Tk()
root.title("BCG Matrix Plotter")
root.geometry("700x500")
root.resizable(True, True)

main_frame = tk.Frame(root, bg="#f0f0f0")
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

tk.Label(main_frame, text="Welcome to the BCG Matrix Plotter", font=("Helvetica", 16, "bold"), bg="#f0f0f0").pack(pady=10)
file_frame = tk.Frame(main_frame, bg="#f0f0f0")
file_frame.pack(pady=10, fill=tk.X)

file_entry = tk.Entry(file_frame, width=50, font=("Helvetica", 12, "bold"))
file_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
tk.Button(file_frame, text="Browse", command=open_file, font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="white").pack(side=tk.LEFT)

tk.Button(main_frame, text="Generate BCG Matrix", command=read_and_plot, font=("Helvetica", 12, "bold"), bg="#2196F3", fg="white").pack(pady=20)
root.mainloop()
