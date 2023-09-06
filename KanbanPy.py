import tkinter as tk
from tkinter import ttk
import json

columns = {}
drag_data = {"widget": None}

def save_to_json():
    with open('kanban_data.json', 'w') as jsonfile:
        data = {}
        for column in columns.keys():
            data[column] = [card.cget("text") for card in columns[column]['cards']]
        json.dump(data, jsonfile)

def load_from_json():
    try:
        with open('kanban_data.json', 'r') as jsonfile:
            data = json.load(jsonfile)
            for column, cards in data.items():
                for content in cards:
                    create_card(column, content)
    except FileNotFoundError:
        pass

def create_card(column_name, content=""):
    card = tk.Label(columns[column_name]['frame'], text=content, 
                    bg='#414868', fg='#A4A6AC',  # New colors for better visibility
                    padx=10, pady=5)
    card.pack(fill='x', padx=5, pady=2)
    card.bind("<ButtonPress-1>", on_drag_start)
    card.bind("<B1-Motion>", on_drag_motion)
    card.bind("<ButtonRelease-1>", on_drag_stop)
    card.bind("<Button-3>", delete_card)
    columns[column_name]['cards'].append(card)
    save_to_json()
    return card

def delete_card(event):
    card = event.widget
    card.pack_forget()
    column_name = [col for col, details in columns.items() if card in details['cards']][0]
    columns[column_name]['cards'].remove(card)
    save_to_json()

def on_drag_start(event):
    widget = event.widget
    drag_data["widget"] = widget
    drag_data["source_column"] = [col for col, details in columns.items() if widget in details['cards']][0]

def on_drag_motion(event):
    widget = drag_data['widget']
    if widget is not None:
        x, y = widget.winfo_pointerxy()
        for column_name, column_details in columns.items():
            frame = column_details['frame']
            x1 = frame.winfo_rootx()
            x2 = x1 + frame.winfo_width()
            if x1 < x < x2:
                drag_data["target_column"] = column_name
                break

def on_drag_stop(event):
    widget = drag_data['widget']
    target_column = drag_data.get("target_column")
    source_column = drag_data.get("source_column")
    if widget is not None and target_column and source_column:
        text = widget.cget('text')
        if source_column != target_column:
            widget.pack_forget()
            columns[source_column]['cards'].remove(widget)
            create_card(target_column, text)
        save_to_json()
    drag_data["widget"] = None
    drag_data["target_column"] = None
    drag_data["source_column"] = None


def add_card(*args):  # Added *args to accommodate events
    column_name = column_to_add.get()
    content = new_card_content.get()
    create_card(column_name, content)
    new_card_content.set('')  # Clear the entry


root = tk.Tk()
root.title('Simple Kanban App')
root.configure(bg='#1A1E27')  # Setting root background color for Tokyo Nights

column_names = ['To-Do', 'Doing', 'Done']

for name in column_names:
    frame = tk.LabelFrame(root, text=name, bg='#1A1E27', fg='#A4A6AC')  # Changed ttk.LabelFrame to tk.LabelFrame
    frame.pack(side='left', fill='both', expand='yes')
    columns[name] = {'frame': frame, 'cards': []}

add_frame = ttk.Frame(root)
add_frame.pack(side='bottom', fill='x')

column_to_add = ttk.Combobox(add_frame, values=column_names)
column_to_add.grid(row=0, column=0)
column_to_add.set(column_names[0])

new_card_content = tk.StringVar()
new_card_entry = ttk.Entry(add_frame, textvariable=new_card_content)
new_card_entry.grid(row=0, column=1)
new_card_entry.bind('<Return>', add_card)

add_button = ttk.Button(add_frame, text="Add Card", command=add_card)
add_button.grid(row=0, column=2)

load_from_json()

root.protocol("WM_DELETE_WINDOW", lambda: (save_to_json(), root.destroy()))
root.mainloop()
