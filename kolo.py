import tkinter as tk
from tkinter import messagebox
import csv
import random
import math
import time
import winsound  # Dla efektów dźwiękowych (tylko Windows)

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz - Koło Fortuny")
        self.root.geometry("800x700")
        self.root.configure(bg="#f0f8ff")  # Tło w kolorze jasnoniebieskim

        self.pytania = self.wczytaj_pytania('pytania.csv')
        self.kategorie = list(set(p['Category'] for p in self.pytania))

        # Stylizacja canvasu
        self.canvas = tk.Canvas(root, width=400, height=400, bg="white", highlightthickness=2, highlightbackground="gold")
        self.canvas.pack(pady=20)

        # Przycisk z efektem hover
        self.spin_btn = tk.Button(root, text="Zakręć kołem!", command=self.spin_wheel, font=("Arial", 14, "bold"),
                                  bg="#32cd32", fg="white", relief="raised", bd=3, activebackground="#228b22")
        self.spin_btn.pack(pady=10)
        self.spin_btn.bind("<Enter>", lambda e: self.spin_btn.config(bg="#228b22"))
        self.spin_btn.bind("<Leave>", lambda e: self.spin_btn.config(bg="#32cd32"))

        # Etykieta pytania z animowanym tłem
        self.label_pytanie = tk.Label(root, text="", font=("Arial", 16, "bold"), wraplength=600, justify="center",
                                      bg="#e6e6fa", fg="#000080", relief="groove", bd=2)
        self.label_pytanie.pack(pady=15)

        # Odpowiedzi z efektami
        self.odp_var = tk.StringVar()
        self.odp_radio = []
        for i in range(5):
            rb = tk.Radiobutton(root, text="", variable=self.odp_var, value=str(i+1), font=("Arial", 14),
                                bg="#f0f8ff", fg="#2f4f4f", selectcolor="#add8e6", activebackground="#add8e6")
            rb.pack(anchor='w', padx=30)
            self.odp_radio.append(rb)

        # Przycisk sprawdzania odpowiedzi z efektem hover
        self.check_btn = tk.Button(root, text="Sprawdź odpowiedź", command=self.check_answer, state='disabled',
                                   font=("Arial", 14, "bold"), bg="#ff4500", fg="white", relief="raised", bd=3,
                                   activebackground="#d2691e")
        self.check_btn.pack(pady=15)
        self.check_btn.bind("<Enter>", lambda e: self.check_btn.config(bg="#d2691e"))
        self.check_btn.bind("<Leave>", lambda e: self.check_btn.config(bg="#ff4500"))

        self.aktualne_pytanie = None
        self.rysuj_kolo()

    def wczytaj_pytania(self, filename):
        pytania = []
        try:
            with open(filename, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=',')
                for row in reader:
                    if row['Question Text'].strip():
                        pytania.append(row)
        except FileNotFoundError:
            messagebox.showerror("Błąd", "Nie znaleziono pliku pytania.csv!")
            return []
        return pytania

    def rysuj_kolo(self, highlight_idx=None):
        self.canvas.delete("all")
        liczba_kat = len(self.kategorie)
        kat_angle = 360 / liczba_kat
        center = 200, 200
        radius = 150

        # Gradientowe kolory dla koła
        colors = ["#ff6347", "#ffa500", "#ffd700", "#90ee90", "#87ceeb", "#9370db"]
        for i, kat in enumerate(self.kategorie):
            start_angle = i * kat_angle
            color = colors[i % len(colors)] if i != highlight_idx else "#ff4500"
            self.canvas.create_arc(center[0] - radius, center[1] - radius,
                                   center[0] + radius, center[1] + radius,
                                   start=start_angle, extent=kat_angle,
                                   fill=color, outline="black", width=2)
            angle_rad = math.radians(start_angle + kat_angle / 2)
            x = center[0] + (radius - 60) * math.cos(angle_rad)
            y = center[1] + (radius - 60) * math.sin(angle_rad)
            self.canvas.create_text(x, y, text=kat, font=("Arial", 12, "bold"), fill="white")

        # Dodanie strzałki wskazującej wybraną kategorię
        self.canvas.create_polygon(380, 180, 380, 220, 400, 200, fill="red", outline="black")

    def spin_wheel(self):
        self.spin_btn.config(state='disabled')
        los = random.randint(30, 50)
        for i in range(los):
            self.rysuj_kolo(highlight_idx=i % len(self.kategorie))
            self.canvas.update()
            time.sleep(0.03 + i * 0.005)  # Przyspieszanie animacji
            if i % 5 == 0:  # Dźwięk podczas kręcenia (tylko Windows)
                try:
                    winsound.Beep(500 + i * 10, 50)
                except:
                    pass
        self.wybrana_kategoria = self.kategorie[(los - 1) % len(self.kategorie)]
        self.pokaz_pytanie()

    def pokaz_pytanie(self):
        pytania_kat = [p for p in self.pytania if p['Category'] == self.wybrana_kategoria]
        self.aktualne_pytanie = random.choice(pytania_kat)
        self.label_pytanie.config(text=self.aktualne_pytanie['Question Text'], bg="#e6e6fa")

        # Animacja pojawiania się pytania
        self.label_pytanie.place_forget()
        self.label_pytanie.place(relx=0.5, rely=0.5, anchor="center")
        for i in range(10):
            self.label_pytanie.place(relx=0.5, rely=0.5 - i * 0.01, anchor="center")
            self.root.update()
            time.sleep(0.02)

        for idx in range(5):
            opcja = self.aktualne_pytanie.get(f'Option {idx+1}', '')
            if opcja.strip():
                self.odp_radio[idx].config(text=opcja, state='normal')
            else:
                self.odp_radio[idx].config(text="", state='disabled')

        self.odp_var.set(None)
        self.check_btn.config(state='normal')

    def check_answer(self):
        wybrana = self.odp_var.get()
        if not wybrana:
            messagebox.showwarning("Brak odpowiedzi", "Proszę zaznaczyć odpowiedź!")
            return

        poprawne_odp = self.aktualne_pytanie['Correct Answer'].split(',')
        if wybrana in poprawne_odp:
            messagebox.showinfo("Wynik", "Poprawna odpowiedź! ✔️")
            self.label_pytanie.config(bg='lightgreen')
            try:
                winsound.Beep(1000, 200)  # Dźwięk sukcesu
            except:
                pass
        else:
            poprawne_teksty = [self.aktualne_pytanie[f'Option {int(i)}'] for i in poprawne_odp]
            poprawne_wyswietl = ', '.join(poprawne_teksty)
            messagebox.showerror("Wynik", f"Zła odpowiedź! ❌ Poprawna odpowiedź to: {poprawne_wyswietl}")
            self.label_pytanie.config(bg='red')
            try:
                winsound.Beep(300, 200)  # Dźwięk błędu
            except:
                pass

        self.root.after(2000, self.reset_quiz)

    def reset_quiz(self):
        self.label_pytanie.config(text="", bg="#e6e6fa")
        for rb in self.odp_radio:
            rb.config(text="", state='normal')
        self.check_btn.config(state='disabled')
        self.spin_btn.config(state='normal')
        self.rysuj_kolo()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()