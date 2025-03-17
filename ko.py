import tkinter as tk
from tkinter import ttk, messagebox
import csv
import random
import math
import os
from PIL import Image, ImageTk
import time

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz z Losowaniem Kategorii")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2E2E2E")  # Ciepły grafitowy
        self.root.minsize(800, 600)  # Minimalna wielkość okna
        
        # Konfiguracja stylu
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#2E2E2E")
        self.style.configure("TButton", background="#2E2E2E", foreground="#FF3333", font=("Arial", 12, "bold"))
        self.style.configure("TLabel", background="#2E2E2E", foreground="white")
        self.style.configure("TCheckbutton", background="#2E2E2E", foreground="white", font=("Arial", 12))
        self.style.map("TCheckbutton",
            background=[('active', '#3E3E3E')],
            foreground=[('active', '#FF3333')]
        )
        
        # Zmienne
        self.questions = []
        self.categories = []
        self.category_colors = {}
        self.category_icons = {}
        self.current_question = None
        self.correct_count = 0
        self.incorrect_count = 0
        self.spinning = False
        self.angle = 0
        self.selected_category = None
        self.category_items = []  # Elementy na kole
        self.answer_vars = []  # Dla wielokrotnego wyboru
        
        # Wczytaj pytania z CSV
        self.load_questions()
        
        # Utwórz układ interfejsu
        self.setup_layout()
        
        # Inicjalizacja koła
        self.init_wheel()
        
        # Utwórz legendę
        self.create_legend()
        
        # Wyświetlanie wyniku
        self.setup_score_display()
        
        # Ustaw obsługę zmiany rozmiaru okna
        self.root.bind("<Configure>", self.on_window_resize)

    def load_questions(self):
        try:
            with open('pytania.csv', 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader)  # Pomiń nagłówek
                
                for row in reader:
                    # Upewnij się, że mamy wystarczającą liczbę kolumn
                    if len(row) < 11:
                        print(f"Pominięto wiersz z niewystarczającą liczbą kolumn: {row}")
                        continue
                    
                    # Tylko niepuste opcje
                    options = [opt for opt in row[2:7] if opt.strip()]
                    
                    # Debugowanie
                    print(f"Wczytano pytanie: {row[0]}")
                    print(f"Opcje: {options}")
                    
                    question = {
                        "text": row[0],
                        "type": row[1],
                        "options": options,  # Tylko niepuste opcje
                        "correct": row[7].split(','),  # Poprawne odpowiedzi
                        "time": int(row[8]) if row[8] else 20,  # Domyślnie 20 sekund
                        "image": row[9] if row[9] else None,
                        "category": row[10]
                    }
                    self.questions.append(question)
                    
                    if question["category"] not in self.categories:
                        self.categories.append(question["category"])
            
            # Wyświetl podsumowanie wczytanych danych
            print(f"Wczytano {len(self.questions)} pytań w {len(self.categories)} kategoriach")
                
            # Przypisz kolory do kategorii
            colors = ["#FF3333", "#33FF33", "#3333FF", "#FFFF33", "#FF33FF", "#33FFFF", "#FF9933", "#9933FF"]
            for i, category in enumerate(self.categories):
                self.category_colors[category] = colors[i % len(colors)]
                
                # Wczytaj ikony kategorii
                icon_path = f"assets/{category}.png"
                if os.path.exists(icon_path):
                    img = Image.open(icon_path)
                    img = img.resize((40, 40), Image.LANCZOS)
                    self.category_icons[category] = ImageTk.PhotoImage(img)
                else:
                    print(f"Brak ikony dla kategorii {category}. Oczekiwano pliku: {icon_path}")
                    self.category_icons[category] = None
                    
        except FileNotFoundError:
            messagebox.showerror("Błąd", "Nie znaleziono pliku pytania.csv!")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas wczytywania pytań: {str(e)}")

    def setup_layout(self):
        # Główny układ - podział poziomy 1:4
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=4)
        self.root.rowconfigure(0, weight=1)
        
        # Główne ramki
        self.left_frame = ttk.Frame(self.root, style="TFrame")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.right_frame = ttk.Frame(self.root, style="TFrame")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Konfiguracja ramki po prawej stronie - podział pionowy 3:2
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(0, weight=3)  # Koło zajmuje więcej miejsca
        self.right_frame.rowconfigure(1, weight=2)  # Pytania zajmują mniej miejsca
        
        # Górna ramka na koło
        self.wheel_frame = ttk.Frame(self.right_frame, style="TFrame")
        self.wheel_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Dolna ramka na pytania
        self.question_frame = ttk.Frame(self.right_frame, style="TFrame")
        self.question_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Ustawienie ramki koła
        self.wheel_frame.columnconfigure(0, weight=1)
        self.wheel_frame.rowconfigure(0, weight=1)
        self.wheel_frame.rowconfigure(1, weight=0)
        
        # Płótno dla koła
        self.wheel_canvas = tk.Canvas(
            self.wheel_frame, 
            bg="#2E2E2E",
            highlightthickness=0
        )
        self.wheel_canvas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Przycisk do losowania
        self.spin_button = ttk.Button(
            self.wheel_frame, 
            text="LOSUJ KATEGORIĘ", 
            command=self.spin_wheel,
            style="TButton"
        )
        self.spin_button.grid(row=1, column=0, pady=(0, 10))
        
        # Ustawienie ramki pytań
        self.question_frame.columnconfigure(0, weight=1)
        self.question_frame.rowconfigure(0, weight=0)
        self.question_frame.rowconfigure(1, weight=1)
        self.question_frame.rowconfigure(2, weight=0)
        
        # Wyświetlanie pytania
        self.question_label = ttk.Label(
            self.question_frame, 
            text="Naciśnij przycisk aby wylosować kategorię i rozpocząć quiz!",
            wraplength=600,
            font=("Arial", 14),
            style="TLabel",
            justify="center"
        )
        self.question_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Ramka na opcje odpowiedzi ze scrollem
        self.options_container = ttk.Frame(self.question_frame, style="TFrame")
        self.options_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self.options_container.columnconfigure(0, weight=1)
        self.options_container.rowconfigure(0, weight=1)
        
        # Canvas i scrollbar dla opcji
        self.options_canvas = tk.Canvas(
            self.options_container,
            bg="#2E2E2E",
            highlightthickness=0
        )
        
        self.options_scrollbar = ttk.Scrollbar(
            self.options_container,
            orient="vertical",
            command=self.options_canvas.yview
        )
        
        self.options_frame = ttk.Frame(
            self.options_canvas, 
            style="TFrame"
        )
        
        self.options_canvas.configure(yscrollcommand=self.options_scrollbar.set)
        self.options_canvas.grid(row=0, column=0, sticky="nsew")
        self.options_scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.options_window = self.options_canvas.create_window(
            (0, 0),
            window=self.options_frame,
            anchor="nw",
            width=self.options_canvas.winfo_width()
        )
        
        # Obsługa zmiany rozmiaru dla scrollowania
        self.options_frame.bind("<Configure>", self.on_options_frame_configure)
        self.options_canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Przycisk zatwierdzania
        self.submit_button = ttk.Button(
            self.question_frame, 
            text="ZATWIERDŹ ODPOWIEDŹ", 
            command=self.check_answer,
            style="TButton"
        )
        self.submit_button.grid(row=2, column=0, pady=10)
        self.submit_button.config(state=tk.DISABLED)  # Początkowo nieaktywny

    def on_options_frame_configure(self, event):
        # Aktualizacja regionu przewijania
        self.options_canvas.configure(scrollregion=self.options_canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        # Aktualizacja szerokości okna zawartości
        self.options_canvas.itemconfig(self.options_window, width=event.width)
    
    def on_window_resize(self, event):
        # Aktualizacja przy zmianie rozmiaru okna
        if event.widget == self.root:
            # Aktualizacja wraplength dla pytania
            self.question_label.configure(wraplength=self.question_frame.winfo_width() - 40)
            # Zmiana rozmiaru koła
            self.resize_wheel()

    def resize_wheel(self):
        # Oblicz rozmiar koła tak, by mieściło się w dostępnej przestrzeni
        width = self.wheel_canvas.winfo_width()
        height = self.wheel_canvas.winfo_height()
        
        # Użyj mniejszego wymiaru, aby koło było całkowicie widoczne
        wheel_size = min(width, height) - 20
        
        if wheel_size > 100:  # Minimalny rozmiar koła
            self.wheel_center_x = width // 2
            self.wheel_center_y = height // 2
            self.wheel_radius = wheel_size // 2 - 10
            
            # Przerysuj koło
            self.draw_wheel()

    def init_wheel(self):
        # Początkowe ustawienia koła
        self.wheel_center_x = 250
        self.wheel_center_y = 250
        self.wheel_radius = 200
        self.draw_wheel()
        
        # Uruchom resize_wheel po pierwszym wyświetleniu GUI
        self.root.update()
        self.resize_wheel()

    def draw_wheel(self):
        self.wheel_canvas.delete("all")
        
        # Rysuj koło z sekcjami kategorii
        if not self.categories:
            return
            
        num_categories = len(self.categories)
        angle_per_category = 360 / num_categories
        
        self.category_items = []
        
        # Narysuj koło z segmentami
        for i, category in enumerate(self.categories):
            start_angle = self.angle + i * angle_per_category
            end_angle = start_angle + angle_per_category
            
            # Utwórz sekcję koła
            section = self.wheel_canvas.create_arc(
                self.wheel_center_x - self.wheel_radius,
                self.wheel_center_y - self.wheel_radius,
                self.wheel_center_x + self.wheel_radius,
                self.wheel_center_y + self.wheel_radius,
                start=start_angle, 
                extent=angle_per_category,
                fill=self.category_colors[category],
                outline="white",
                width=2,
                tags=f"section_{category}"
            )
            self.category_items.append(section)
            
            # Oblicz pozycję dla ikony kategorii
            mid_angle_rad = math.radians(start_angle + angle_per_category / 2)
            icon_x = self.wheel_center_x + (self.wheel_radius * 0.7) * math.cos(mid_angle_rad)
            icon_y = self.wheel_center_y + (self.wheel_radius * 0.7) * math.sin(mid_angle_rad)
            
            # Dodaj ikonę kategorii jeśli dostępna
            if self.category_icons.get(category):
                icon = self.wheel_canvas.create_image(
                    icon_x, icon_y,
                    image=self.category_icons[category],
                    tags=f"icon_{category}"
                )
                self.category_items.append(icon)
        
        # Narysuj środkowe koło
        center_radius = self.wheel_radius * 0.1
        center_circle = self.wheel_canvas.create_oval(
            self.wheel_center_x - center_radius,
            self.wheel_center_y - center_radius,
            self.wheel_center_x + center_radius,
            self.wheel_center_y + center_radius,
            fill="#2E2E2E",
            outline="white",
            width=2
        )
        
        # Narysuj wskaźnik
        pointer_size = self.wheel_radius * 0.1
        pointer = self.wheel_canvas.create_polygon(
            self.wheel_center_x, self.wheel_center_y - self.wheel_radius - pointer_size,
            self.wheel_center_x - pointer_size, self.wheel_center_y - self.wheel_radius + pointer_size,
            self.wheel_center_x + pointer_size, self.wheel_center_y - self.wheel_radius + pointer_size,
            fill="#FF3333",
            outline="white",
            width=2
        )

    def spin_wheel(self):
        if self.spinning:
            return
            
        self.spinning = True
        self.spin_button.config(state=tk.DISABLED)
        
        # Losowa liczba obrotów między 2 a 5
        rotations = random.uniform(2, 5)
        total_angle = rotations * 360
        
        # Losowe spowolnienie
        slow_down = random.uniform(0.985, 0.995)
        
        # Początkowa wysoka prędkość
        speed = 10
        
        def animate_spin():
            nonlocal speed, total_angle
            
            if total_angle > 0 and speed > 0.2:
                # Aktualizuj kąt
                self.angle = (self.angle + speed) % 360
                total_angle -= speed
                
                # Przerysuj koło
                self.draw_wheel()
                
                # Spowolnij
                speed *= slow_down
                
                # Kontynuuj animację
                self.root.after(20, animate_spin)
            else:
                # Zakończ kręcenie
                self.spinning = False
                self.spin_button.config(state=tk.NORMAL)
                
                # Określ wybraną kategorię
                category_index = int(((self.angle + 180) % 360) / (360 / len(self.categories)))
                self.selected_category = self.categories[category_index]
                
                # Zaktualizuj legendę aby podświetlić wybraną kategorię
                self.highlight_category(self.selected_category)
                
                # Wczytaj pytanie z wybranej kategorii
                self.load_question_from_category(self.selected_category)
        
        animate_spin()

    def create_legend(self):
        # Tytuł legendy
        legend_title = ttk.Label(
            self.left_frame, 
            text="KATEGORIE", 
            font=("Arial", 16, "bold"),
            style="TLabel"
        )
        legend_title.pack(pady=(0, 20))
        
        # Ramka dla kategorii - bez przewijania
        legend_frame = ttk.Frame(self.left_frame, style="TFrame")
        legend_frame.pack(fill=tk.BOTH, expand=True)
        
        # Utwórz ramkę dla każdej kategorii w legendzie
        for category in self.categories:
            category_frame = ttk.Frame(legend_frame, style="TFrame")
            category_frame.pack(fill=tk.X, pady=5)
            
            # Wskaźnik koloru
            color_indicator = tk.Canvas(
                category_frame, 
                width=20, 
                height=20, 
                bg=self.category_colors[category],
                highlightthickness=0
            )
            color_indicator.pack(side=tk.LEFT, padx=5)
            
            # Ikona jeśli dostępna
            if self.category_icons.get(category):
                icon_label = ttk.Label(category_frame, image=self.category_icons[category])
                icon_label.pack(side=tk.LEFT, padx=5)
            
            # Nazwa kategorii
            name_label = ttk.Label(
                category_frame, 
                text=category, 
                style="TLabel"
            )
            name_label.pack(side=tk.LEFT, padx=5)
            
            # Zapisz referencje do podświetlania
            category_frame.color_indicator = color_indicator
            category_frame.name_label = name_label
            setattr(self, f"legend_{category}", category_frame)

    def highlight_category(self, category):
        # Zresetuj wszystkie kategorie w legendzie
        for cat in self.categories:
            cat_frame = getattr(self, f"legend_{cat}")
            cat_frame.name_label.configure(foreground="white")
            cat_frame.configure(style="TFrame")
        
        # Podświetl wybraną kategorię
        selected_frame = getattr(self, f"legend_{category}")
        selected_frame.name_label.configure(foreground="#FF3333")  # Neonowa czerwień
        
        # Dodaj efekt podświetlenia
        self.root.update()  # Upewnij się, że UI jest zaktualizowane przed efektem błysku
        
        # Efekt błysku
        for _ in range(3):
            selected_frame.name_label.configure(foreground="#FF3333")
            self.root.update()
            time.sleep(0.2)
            selected_frame.name_label.configure(foreground="white")
            self.root.update()
            time.sleep(0.2)
        
        selected_frame.name_label.configure(foreground="#FF3333")  # Ustaw końcowy stan na podświetlony

    def setup_score_display(self):
        # Utwórz ramkę dla wyświetlania wyniku
        score_frame = ttk.Frame(self.left_frame, style="TFrame")
        score_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        # Licznik poprawnych odpowiedzi
        self.correct_label = ttk.Label(
            score_frame, 
            text="Poprawne: 0", 
            font=("Arial", 12),
            foreground="#33FF33",  # Zielony dla poprawnych
            style="TLabel"
        )
        self.correct_label.pack(pady=5)
        
        # Licznik niepoprawnych odpowiedzi
        self.incorrect_label = ttk.Label(
            score_frame, 
            text="Niepoprawne: 0", 
            font=("Arial", 12),
            foreground="#FF3333",  # Czerwony dla niepoprawnych
            style="TLabel"
        )
        self.incorrect_label.pack(pady=5)

    def update_score_display(self):
        self.correct_label.config(text=f"Poprawne: {self.correct_count}")
        self.incorrect_label.config(text=f"Niepoprawne: {self.incorrect_count}")

    def load_question_from_category(self, category):
        # Filtruj pytania według kategorii
        category_questions = [q for q in self.questions if q["category"] == category]
        
        if not category_questions:
            self.question_label.config(text=f"Brak pytań w kategorii {category}!")
            return
        
        # Wybierz losowe pytanie
        self.current_question = random.choice(category_questions)
        
        # Zaktualizuj wyświetlanie pytania
        self.question_label.config(text=self.current_question["text"], foreground="white")
        
        # Wyczyść poprzednie opcje
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        self.answer_vars = []
        
        # Sprawdź, czy są dostępne opcje odpowiedzi
        if not self.current_question["options"]:
            error_label = ttk.Label(
                self.options_frame,
                text="Błąd: Brak opcji odpowiedzi!",
                foreground="#FF3333",
                style="TLabel"
            )
            error_label.pack(pady=10)
            return
        
        # Utwórz opcje jako checkboxy (bez wraplength - przyczyna błędu)
        for i, option in enumerate(self.current_question["options"]):
            var = tk.BooleanVar()
            self.answer_vars.append(var)
            
            # Utwórz ramkę dla opcji
            option_frame = ttk.Frame(self.options_frame, style="TFrame")
            option_frame.pack(fill=tk.X, pady=5, padx=5)
            
            # Dodaj numer opcji i checkbox
            option_cb = ttk.Checkbutton(
                option_frame,
                text=f"Opcja {i+1}: {option}",
                variable=var,
                style="TCheckbutton"
            )
            option_cb.pack(side=tk.LEFT, anchor="w", padx=5)
        
        # Aktualizuj scrollregion
        self.options_frame.update_idletasks()
        self.options_canvas.configure(scrollregion=self.options_canvas.bbox("all"))
        
        # Włącz przycisk zatwierdzania
        self.submit_button.config(state=tk.NORMAL)

    def check_answer(self):
        if not self.current_question:
            return
        
        # Pobierz zaznaczone odpowiedzi (indeksy zaznaczonych opcji)
        selected_answers = [str(i+1) for i, var in enumerate(self.answer_vars) if var.get()]
        
        # Sprawdź czy zaznaczone odpowiedzi są zgodne z poprawnymi
        correct = set(selected_answers) == set(self.current_question["correct"])
        
        # Zaktualizuj wynik
        if correct:
            self.correct_count += 1
            result_text = "Poprawna odpowiedź!"
            result_color = "#33FF33"  # Zielony
        else:
            self.incorrect_count += 1
            
            # Przygotuj tekst poprawnych odpowiedzi
            correct_options = [self.current_question["options"][int(i)-1] for i in self.current_question["correct"]]
            correct_text = ", ".join(correct_options)
            
            result_text = f"Niepoprawna odpowiedź! Prawidłowe odpowiedzi: {correct_text}"
            result_color = "#FF3333"  # Czerwony
        
        # Zaktualizuj wyświetlanie wyniku
        self.update_score_display()
        
        # Pokaż wynik
        self.question_label.config(text=result_text, foreground=result_color)
        
        # Tymczasowo wyłącz przycisk zatwierdzania
        self.submit_button.config(state=tk.DISABLED)
        
        # Po opóźnieniu, zresetuj dla następnego pytania
        self.root.after(3000, self.reset_for_next_question)

    def reset_for_next_question(self):
        # Zresetuj etykietę pytania
        self.question_label.config(
            text="Naciśnij przycisk aby wylosować kolejną kategorię!",
            foreground="white"
        )
        
        # Wyczyść opcje
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        self.answer_vars = []
        
        # Włącz przycisk losowania dla następnego pytania
        self.spin_button.config(state=tk.NORMAL)
        
        # Zresetuj aktualne pytanie
        self.current_question = None

def main():
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()