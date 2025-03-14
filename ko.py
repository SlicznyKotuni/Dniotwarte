import tkinter as tk
from tkinter import ttk, messagebox
import csv
import random
import os
from PIL import Image, ImageTk
import time

# Stałe kolorystyczne – możesz je zmieniać według własnego gustu
BG_COLOR = "#f0f0f0"
LEGEND_BG = "#d0e1f9"
HIGHLIGHT_COLOR = "#a0c4ff"
QUESTION_BG = "#ffffff"
CORRECT_COLOR = "#a0e7a0"
WRONG_COLOR   = "#f7a8a8"

# Czas animacji koła (w milisekundach)
SPIN_DURATION = 3000
SPIN_INTERVAL = 50

class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Quiz - Losowanie Kategorii")
        self.geometry("900x600")
        self.configure(bg=BG_COLOR)

        # Słowniki z pytaniami: klucz = nazwa kategorii; wartość = lista pytań
        self.questions_by_category = {}
        self.categories = []  # lista kategorii
        self.load_questions("pytania.csv")

        # Liczniki odpowiedzi poprawnych i błędnych
        self.correct_count = 0
        self.wrong_count = 0

        # Aktualnie wybrane pytanie i zmienne dotyczące pytania
        self.current_question = None
        self.current_category = None
        self.answer_vars = {}  # słownik: klucz = numer opcji, wartość = IntVar

        # Załaduj obrazek koła
        self.wheel_image_orig = None
        if os.path.exists("wheel.png"):
            self.wheel_image_orig = Image.open("wheel.png").resize((150, 150), Image.ANTIALIAS)
        else:
            # Jeżeli nie ma obrazka, tworzymy prosty placeholder
            self.wheel_image_orig = Image.new("RGBA", (150, 150), color="grey")
        self.wheel_image = ImageTk.PhotoImage(self.wheel_image_orig)
        self.wheel_angle = 0  # aktualny kąt koła

        # Panel główny (dzielimy na legendę z kategorii i okno pytania)
        self.setup_ui()

        # Rozpoczęcie pierwszej rundy
        self.after(500, self.start_round)

    def load_questions(self, csv_file):
        """Wczytanie pytań z pliku CSV."""
        try:
            with open(csv_file, newline='', encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)  # pomin nagłówek
                for row in reader:
                    # Spodziewamy się 11 kolumn:
                    # 0: Question Text, 1: Question Type, 2-6: Opcje, 
                    # 7: Correct Answer, 8: Time in seconds, 9: Image Link, 10: Category
                    if len(row) < 11:
                        continue

                    question_text = row[0].strip()
                    question_type = row[1].strip()
                    # Zbierz opcje – zachowujemy ich oryginalny indeks (od 0 do 4)
                    options = []
                    for idx, opt in enumerate(row[2:7]):
                        if opt.strip() != "":
                            options.append( (idx, opt.strip()) )  
                    # Poprawne odpowiedzi – zakładamy, że są oddzielone średnikiem, numerowane od 1
                    correct_answers = [int(x.strip())-1 for x in row[7].split(';') if x.strip().isdigit()]
                    # Czas – domyślnie 20 sekund, jeśli nie podano inaczej
                    try:
                        time_seconds = int(row[8].strip())
                    except:
                        time_seconds = 20
                    # Link do obrazka – jeśli pusty, None
                    image_link = row[9].strip() if row[9].strip() != "" else None

                    # Kategoria
                    category = row[10].strip()

                    # Utwórz słownik pytania
                    question = {
                        "text": question_text,
                        "type": question_type,
                        "options": options,
                        "correct": correct_answers,
                        "time": time_seconds,
                        "image": image_link,
                        "category": category
                    }
                    # Dodaj pytanie do słownika według kategorii
                    if category not in self.questions_by_category:
                        self.questions_by_category[category] = []
                    self.questions_by_category[category].append(question)
                    
            # Lista kategorii
            self.categories = list(self.questions_by_category.keys())
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wczytać pliku CSV: {e}")
            self.destroy()

    def setup_ui(self):
        """Budowanie interfejsu aplikacji."""
        # Główny kontener
        self.main_frame = tk.Frame(self, bg=BG_COLOR)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Lewy panel – legenda kategorii
        self.legend_frame = tk.Frame(self.main_frame, bg=LEGEND_BG, bd=2, relief=tk.RIDGE)
        self.legend_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,10))
        legend_title = tk.Label(self.legend_frame, text="Kategorie", bg=LEGEND_BG, font=("Arial", 14, "bold"))
        legend_title.pack(pady=10)

        self.category_labels = {}  # klucz: nazwa kategorii, wartość: ramka z ikoną i etykietą
        for cat in self.categories:
            item_frame = tk.Frame(self.legend_frame, bg=LEGEND_BG, bd=1, relief=tk.SOLID, padx=5, pady=5)
            item_frame.pack(padx=5, pady=5, fill=tk.X)

            # Załaduj ikonę – zakładamy, że plik ma nazwę <kategoria>.png
            icon = None
            icon_path = f"{cat}.png"
            if os.path.exists(icon_path):
                try:
                    im = Image.open(icon_path).resize((30, 30), Image.ANTIALIAS)
                    icon = ImageTk.PhotoImage(im)
                except Exception as e:
                    icon = None
            # Przechowujemy obrazek, żeby nie został zgarbowany przez GC:
            item_frame.icon = icon

            if icon is not None:
                lbl_icon = tk.Label(item_frame, image=icon, bg=LEGEND_BG)
                lbl_icon.pack(side=tk.LEFT, padx=5)
            lbl_cat = tk.Label(item_frame, text=cat, bg=LEGEND_BG, font=("Arial", 12))
            lbl_cat.pack(side=tk.LEFT, padx=5)
            self.category_labels[cat] = item_frame

        # Prawy panel – główne okno quizu
        self.quiz_frame = tk.Frame(self.main_frame, bg=QUESTION_BG, bd=2, relief=tk.RIDGE)
        self.quiz_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Na górze panel z kołem losującym oraz licznikami
        top_frame = tk.Frame(self.quiz_frame, bg=QUESTION_BG)
        top_frame.pack(fill=tk.X, pady=5)

        # Obrazek koła losującego
        self.wheel_label = tk.Label(top_frame, image=self.wheel_image, bg=QUESTION_BG)
        self.wheel_label.pack(side=tk.LEFT, padx=10)

        # Liczniki odpowiedzi
        self.score_label = tk.Label(top_frame, text="Poprawne: 0    Błędne: 0", bg=QUESTION_BG, font=("Arial", 14))
        self.score_label.pack(side=tk.LEFT, padx=20)

        # Ramka z pytaniem (tekst, obrazek, opcje, przyciski)
        self.content_frame = tk.Frame(self.quiz_frame, bg=QUESTION_BG)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.question_label = tk.Label(self.content_frame, text="", wraplength=500, justify=tk.LEFT,
                                       bg=QUESTION_BG, font=("Arial", 16))
        self.question_label.pack(pady=10, anchor=tk.W)

        # Miejsce na dodatkowy obrazek z pytania (jeśli jest)
        self.img_label = tk.Label(self.content_frame, bg=QUESTION_BG)
        self.img_label.pack(pady=5)

        # Ramka na opcje odpowiedzi
        self.options_frame = tk.Frame(self.content_frame, bg=QUESTION_BG)
        self.options_frame.pack(pady=10, anchor=tk.W)

        # Przycisk "Sprawdź"
        self.submit_button = ttk.Button(self.content_frame, text="Sprawdź odpowiedź", command=self.check_answer)
        self.submit_button.pack(pady=10)

        # Timer – jeśli pytanie ma limit czasu
        self.timer_label = tk.Label(self.content_frame, text="", bg=QUESTION_BG, font=("Arial", 14))
        self.timer_label.pack(pady=5)

    def start_round(self):
        """Rozpoczęcie rundy: animacja koła i losowanie kategorii oraz pytania."""
        self.reset_question_area()
        self.animate_wheel(start_time=time.time())
        
    def animate_wheel(self, start_time):
        """Animacja obracającego się koła przez SPIN_DURATION milisekund."""
        elapsed = (time.time() - start_time)*1000
        if elapsed < SPIN_DURATION:
            self.wheel_angle = (self.wheel_angle + 15) % 360
            rotated = self.wheel_image_orig.rotate(self.wheel_angle)
            self.wheel_image = ImageTk.PhotoImage(rotated)
            self.wheel_label.configure(image=self.wheel_image)
            self.after(SPIN_INTERVAL, self.animate_wheel, start_time)
        else:
            # Po zakończeniu animacji losujemy kategorię
            self.choose_category_and_question()

    def choose_category_and_question(self):
        """Losowanie kategorii, podświetlenie jej w legendzie, wybór pytania i prezentacja."""
        self.current_category = random.choice(self.categories)
        # Podświetl kategorię w legendzie – najpierw zresetuj wszystkie
        for cat, frame in self.category_labels.items():
            frame.configure(bg=LEGEND_BG)
            for child in frame.winfo_children():
                child.configure(bg=LEGEND_BG)
        # Podświetl wylosowaną kategorię
        cat_frame = self.category_labels.get(self.current_category)
        if cat_frame:
            cat_frame.configure(bg=HIGHLIGHT_COLOR)
            for child in cat_frame.winfo_children():
                child.configure(bg=HIGHLIGHT_COLOR)
        # Wybierz losowe pytanie z wybranej kategorii
        self.current_question = random.choice(self.questions_by_category[self.current_category])
        self.present_question()

    def reset_question_area(self):
        """Czyszczenie obszaru pytania przed prezentacją nowego pytania."""
        self.question_label.configure(text="")
        self.timer_label.configure(text="")
        self.img_label.configure(image='')
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        self.answer_vars = {}
        self.submit_button.config(state=tk.NORMAL)

    def present_question(self):
        """Prezentacja pytania i opcji odpowiedzi."""
        self.reset_question_area()
        q = self.current_question
        self.question_label.configure(text=q["text"])
        # Jeśli pytanie ma dołączony obrazek, próbujemy go załadować
        if q["image"]:
            if os.path.exists(q["image"]):
                try:
                    img = Image.open(q["image"]).resize((300,200), Image.ANTIALIAS)
                    img_tk = ImageTk.PhotoImage(img)
                    self.img_label.image = img_tk
                    self.img_label.configure(image=img_tk)
                except Exception as e:
                    print("Błąd ładowania obrazka pytania:", e)
            else:
                print(f"Obrazek {q['image']} nie został znaleziony.")
        # Utwórz przyciski wyboru (Checkbutton) – ponieważ pytanie typu "Multiple Choice" ma możliwość wyboru wielu opcji
        for idx, option_text in q["options"]:
            var = tk.IntVar()
            chk = tk.Checkbutton(self.options_frame, text=option_text, variable=var, bg=QUESTION_BG,
                                 font=("Arial", 14), anchor="w", wraplength=500)
            chk.pack(anchor="w", pady=2)
            self.answer_vars[idx] = var

        # Ustaw timer jeśli określono czas (w sekundach)
        self.time_left = q["time"]
        if self.time_left > 0:
            self.update_timer()

    def update_timer(self):
        """Odświeżanie licznika czasu i sprawdzenie, czy upłynął limit."""
        if self.time_left > 0:
            self.timer_label.configure(text=f"Czas: {self.time_left} s")
            self.time_left -= 1
            self.timer_job = self.after(1000, self.update_timer)
        else:
            self.timer_label.configure(text="Koniec czasu!")
            self.check_answer(timeout=True)

    def check_answer(self, timeout=False):
        """Sprawdzenie zaznaczonych odpowiedzi."""
        # Jeżeli licznik czasu działa – zatrzymaj go
        if hasattr(self, "timer_job"):
            self.after_cancel(self.timer_job)
        self.submit_button.config(state=tk.DISABLED)
        q = self.current_question
        # Pobierz indeksy zaznaczonych opcji
        selected = [i for i, v in self.answer_vars.items() if v.get() == 1]
        # Porównaj z prawidłową listą opcji
        if set(selected) == set(q["correct"]) and selected != []:
            # Poprawna odpowiedź
            self.correct_count += 1
            self.content_frame.configure(bg=CORRECT_COLOR)
            self.question_label.configure(bg=CORRECT_COLOR)
            self.timer_label.configure(bg=CORRECT_COLOR)
        else:
            # Odpowiedź błędna
            self.wrong_count += 1
            self.content_frame.configure(bg=WRONG_COLOR)
            self.question_label.configure(bg=WRONG_COLOR)
            self.timer_label.configure(bg=WRONG_COLOR)
        # Uaktualnij licznik wyników
        self.score_label.configure(text=f"Poprawne: {self.correct_count}    Błędne: {self.wrong_count}")
        # Po 2 sekundach powróć do kolejnej rundy
        self.after(2000, self.prepare_next_round)

    def prepare_next_round(self):
        """Reset ustawień po rundzie i przygotowanie kolejnego pytania."""
        # Resetujemy tło w obszarze pytania
        self.content_frame.configure(bg=QUESTION_BG)
        self.question_label.configure(bg=QUESTION_BG)
        self.timer_label.configure(bg=QUESTION_BG)
        self.start_round()

if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()