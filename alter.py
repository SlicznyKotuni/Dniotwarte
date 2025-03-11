import tkinter as tk
from tkinter import ttk
import pandas as pd
import random
import time

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz")
        self.kategorie = []
        self.pytanie = None
        self.odpowiedzi = []
        self.poprawna = None
        self.wynik = None
        self.csv_file = 'pytania.csv'
        self.dane = pd.read_csv(self.csv_file, sep=',')
        
        self.koło = tk.Canvas(self.root, width=200, height=200)
        self.koło.pack()
        self.koło.create_oval(50, 50, 150, 150)
        self.kategorie = self.dane['Category'].unique()
        self.spin_button = tk.Button(self.root, text="Spin", command=self.spin)
        self.spin_button.pack()
        
        self.pytanie_label = tk.Label(self.root, text="")
        self.pytanie_label.pack()
        
        self.odpowiedz_var = tk.StringVar()
        self.odpowiedzi_radios = []
        for i in range(5):  # Do 5 opcji
            radio = tk.Radiobutton(self.root, text="", variable=self.odpowiedz_var, value=f"Option {i+1}")
            radio.pack(anchor=tk.W)
            self.odpowiedzi_radios.append(radio)
        
        self.zatwierdz_button = tk.Button(self.root, text="Zatwierdź", command=self.zatwierdz, state=tk.DISABLED)
        self.zatwierdz_button.pack()
        
        self.wynik_label = tk.Label(self.root, text="", fg="black")
        self.wynik_label.pack()
        
    def spin(self):
        self.spin_button.config(state=tk.DISABLED)
        self.koło.delete("all")
        self.koło.create_oval(50, 50, 150, 150)
        self.kategoria = random.choice(self.kategorie)
        self.koło.create_text(100, 100, text=self.kategoria)
        self.root.update()
        time.sleep(2)  # Symulacja losowania
        self.pobierz_pytanie()
        
    def pobierz_pytanie(self):
        self.pytanie = self.dane[self.dane['Category'] == self.kategoria].sample(n=1)
        self.pytanie_text = self.pytanie['Question Text'].values[0]
        self.odpowiedzi = [self.pytanie[f'Option {i+1}'].values[0] for i in range(5)]
        self.poprawna = [int(x) - 1 for x in self.pytanie['Correct Answer'].values[0].split(',')]  # Przerobienie na indeksy
        self.pytanie_label.config(text=self.pytanie_text)
        for i, radio in enumerate(self.odpowiedzi_radios):
            if i < len(self.odpowiedzi):
                radio.config(text=self.odpowiedzi[i], state=tk.NORMAL)
            else:
                radio.config(text="", state=tk.DISABLED)
        self.zatwierdz_button.config(state=tk.NORMAL)
        
    def zatwierdz(self):
        if int(self.odpowiedz_var.get()[-1]) - 1 in self.poprawna:
            self.wynik = True
            self.wynik_label.config(text="Poprawna odpowiedź!", fg="green")
        else:
            self.wynik = False
            self.wynik_label.config(text=f"Niepoprawna odpowiedź. Poprawne odpowiedzi to {[x+1 for x in self.poprawna]}.", fg="red")
        self.spin_button.config(state=tk.NORMAL)
        self.root.after(2000, self.resetuj)
        
    def resetuj(self):
        self.pytanie_label.config(text="")
        self.wynik_label.config(text="", fg="black")
        self.odpowiedz_var.set("")
        for radio in self.odpowiedzi_radios:
            radio.config(text="", state=tk.NORMAL)
        self.zatwierdz_button.config(state=tk.DISABLED)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()