from settings import *
from support import draw_bar
import csv
import numpy as np
import tkinter as tk
import pandas as pd
import seaborn as sns
import tkinter.ttk as ttk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class DataCollector:
    def __init__(self, file_name):
        self.index = 0
        self.data = {}
        self.row = ['Entity', 'Side', 'Deal to', 'Action', 'Action-Type', 'Action-Element', 'Damage Dealt', 'Damage Recive', 'Current-Health', 'Current-Mana', 'Mana Useage']

    def collect_data(self, data_dict):
        self.data[self.index] = data_dict
        self.index += 1

    def save_data(self):       
        with open(f'scripts/game_data/battle.csv', mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=",")
            csv_writer.writerow(self.row)

            data_line = []
            for index, line in self.data.items():
                for header in self.row:
                    data_line.append(line[header])
                csv_writer.writerow(data_line)
                data_line.clear()

    def read_data(self):
        with open(f'scripts/game_data/battle.csv', mode='w', newline='') as csv_file:
            csv_reader = csv_reader(csv_file, delimiter=",")


class DataTkin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter")
        self.geometry("600x600")
        self.df = pd.read_csv('scripts/game_data/battle.csv')
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Select Graph", font=("Arial", 14, "bold")).pack(pady=10)

        self.combo = ttk.Combobox(self, state="readonly")
        self.combo['values'] = (
            'Boxplot',
            'Scatter Plot',
            'Table',
            'Barplot',
            'Line Plot'
        )

        self.combo.pack(pady=5)
        self.combo.bind('<<ComboboxSelected>>', self.update_plot)

        ttk.Button(self, text="Quit", command=self.destroy).pack(pady=5)

        self.fig = Figure(figsize=(9, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(expand=True, fill='both')

    def update_plot(self, event):
            selection = self.combo.get()
            self.ax.clear()

            if selection == 'Boxplot':
                data = self.df[['Damage Dealt']]
                sns.boxplot(y=data['Damage Dealt'], ax=self.ax)
                self.ax.set_yticks(range(0, 3000, 150))
                self.ax.set_ylabel('Damage Dealt')
                self.ax.set_title('Average damage dealt')

            elif selection == 'Scatter Plot':
                data = self.df[['Mana Useage']].head(51)
                self.ax.scatter(data.index, data['Mana Useage'])
                self.ax.set_xticks(range(0, 51, 1))
                self.ax.set_yticks(range(0, 200, 20))
                self.ax.set_ylabel('Mana Useage')
                self.ax.set_title('Mana Useage')

            elif selection == 'Table':
                self.ax.axis('off')
                counts = self.df['Action'].value_counts()
                table = self.ax.table(
                    cellText=[[k, v] for k, v in counts.items()],
                    colLabels=['Moves', 'Count'],
                    loc='center',
                    cellLoc='center'
                )
                table.auto_set_font_size(False)
                table.set_fontsize(12)
                table.scale(1.2, 1.2)
                self.ax.set_title("Skills Count", fontsize=14)

            elif selection == 'Barplot':
                data = self.df[['Damage Dealt']].head(50)
                data.index = range(1, 51)
                sns.barplot(x=data.index, y='Damage Dealt', data=data, ax=self.ax)
                self.ax.set_ylabel('Damage Dealt')
                self.ax.set_xlabel('Turn(s)')
                self.ax.set_title('Damage Dealt / Turn')
                self.ax.tick_params(axis='x', rotation=45)

            elif selection == 'Line Plot':
                data = self.df[['Current-Health']].head(51)
                self.ax.plot(data.index, data['Current-Health'], marker='.', linestyle='-', color='b')
                self.ax.set_yticks(range(0, 24000, 1500))
                self.ax.set_ylabel('Current Health')
                self.ax.set_xticks(range(0, 51, 5))
                self.ax.set_xlabel('Turn(s)')
                self.ax.set_title('Player Current Health')
                self.ax.grid(axis='y', linestyle='--')

            self.canvas.draw()

# app = DataTkin()
# app.mainloop()
