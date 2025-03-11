import tkinter as tk
from tkinter import messagebox
import csv
import random
import math
import time

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz - Koło Fortuny")
        self.root.geometry("700x600")

        # Wczytaj pytania z pliku CSV
        self.pytania = self.wczytaj_pytania('pytania.csv')
        self.kategorie = list(set(p['Category'] for p in self.pytania if p['Category']))

        # Widgety GUI
        self.canvas = tk.Canvas(root, width=400, height=400, bg="white")
        self.canvas.pack(pady=20)

        self.spin_btn = tk.Button(root, text="Zakręć kołem!", command=self.spin_wheel)
        self.spin_btn.pack()

        self.label_pytanie = tk.Label(root, text="", font=("Arial", 14), wraplength=600)
        self.label_pytanie.pack(pady=10)

        self.odp_var = tk.StringVar()
        self.odp_radio = []
        for i in range(5):
            rb = tk.Radiobutton(root, text="", variable=self.odp_var, value=str(i+1), font=("Arial", 12))
            rb.pack(anchor='w')
            self.odp_radio.append(rb)

        self.check_btn = tk.Button(root, text="Sprawdź odpowiedź", command=self.check_answer, state='disabled')
        self.check_btn.pack(pady=10)

        self.aktualne_pytanie = None
        self.wybrana_kategoria = None
        self.rysuj_kolo()

    def wczytaj_pytania(self, filename):
        pytania = []
        try:
            with open(filename, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=',')
                for row in reader:
                    # Obsługa brakujących danych i konwersja odpowiedzi
                    if row['Question Text'] and row['Category']:
                        row['Correct Answer'] = row['Correct Answer'].split(',')  # Lista poprawnych odpowiedzi
                        pytania.append(row)
        except FileNotFoundError:
            messagebox.showerror("Błąd", f"Nie znaleziono pliku {filename}.")
        return pytania

    def rysuj_kolo(self, highlight_idx=None):
        self.canvas.delete("all")
        liczba_kat = len(self.kategorie)
        kat_angle = 360 / liczba_kat
        center = 200, 200
        radius = 150

        for i, kat in enumerate(self.kategorie):
            start_angle = i * kat_angle
            color = "lightblue" if i != highlight_idx else "orange"
            self.canvas.create_arc(center[0]-radius, center[1]-radius,
                                   center[0]+radius, center[1]+radius,
                                   start=start_angle, extent=kat_angle,
                                   fill=color, outline="black")
            angle_rad = math.radians(start_angle + kat_angle / 2)
            x = center[0] + (radius - 60) * math.cos(angle_rad)
            y = center[1] + (radius - 60) * math.sin(angle_rad)
            self.canvas.create_text(x, y, text=kat, font=("Arial", 10, "bold"))

    def spin_wheel(self):
        self.spin_btn.config(state='disabled')
        los = random.randint(20, 40)
        for i in range(los):
            self.rysuj_kolo(highlight_idx=i % len(self.kategorie))
            self.canvas.update()
            time.sleep(0.05 + i * 0.01)
        self.wybrana_kategoria = self.kategorie[(los - 1) % len(self.kategorie)]
        self.pokaz_pytanie()

    def pokaz_pytanie(self):
        pytania_kat = [p for p in self.pytania if p['Category'] == self.wybrana_kategoria]
        if not pytania_kat:
            messagebox.showwarning("Brak pytań", f"Brak pytań dla kategorii: {self.wybrana_kategoria}")
            self.reset_quiz()
            return

        self.aktualne_pytanie = random.choice(pytania_kat)
        self.label_pytanie.config(text=self.aktualne_pytanie['Question Text'])

        for idx, rb in enumerate(self.odp_radio):
            opcja = self.aktualne_pytanie.get(f'Option {idx+1}', '').strip()
            if opcja:
                rb.config(text=opcja, state='normal')
            else:
                rb.config(text="", state='disabled')

        self.odp_var.set(None)
        self.check_btn.config(state='normal')

    def check_answer(self):
        wybrana = self.odp_var.get()
        if not wybrana:
            messagebox.showwarning("Brak odpowiedzi", "Proszę zaznaczyć odpowiedź!")
            return

        poprawne_odp = self.aktualne_pytanie['Correct Answer']
        if wybrana in poprawne_odp:
            messagebox.showinfo("Wynik", "Poprawna odpowiedź! ✔️")
            self.label_pytanie.config(bg='lightgreen')
        else:
            poprawne_teksty = [self.aktualne_pytanie[f'Option {int(i)}'] for i in poprawne_odp]
            poprawne_wyswietl = ', '.join(poprawne_teksty)
            messagebox.showerror("Wynik", f"Zła odpowiedź! ❌ Poprawna odpowiedź to: {poprawne_wyswietl}")
            self.label_pytanie.config(bg='red')

        self.root.after(2000, self.reset_quiz)

    def reset_quiz(self):
        self.label_pytanie.config(text="", bg=self.root.cget('bg'))
        for rb in self.odp_radio:
            rb.config(text="", state='normal')
        self.check_btn.config(state='disabled')
        self.spin_btn.config(state='normal')

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()