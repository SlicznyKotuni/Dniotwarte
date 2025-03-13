import tkinter as tk
from tkinter import messagebox, Checkbutton, IntVar, Frame, Scrollbar
import csv
import random
import math
import time
import winsound  # Dla efektów dźwiękowych (tylko Windows)
import os
from PIL import Image, ImageTk  # Do obsługi obrazów

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz - Koło Fortuny")
        
        # Pobierz rozmiar ekranu
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        
        # Ustaw rozmiar okna na 90% ekranu
        self.window_width = int(self.screen_width * 0.9)
        self.window_height = int(self.screen_height * 0.9)
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        
        self.root.configure(bg="#2c3e50")  # Ciemniejsze tło, bardziej eleganckie

        self.pytania = self.wczytaj_pytania('pytania.csv')
        self.kategorie = list(set(p['Category'] for p in self.pytania))
        
        # Dodaj licznik odpowiedzi
        self.correct_answers = 0
        self.total_answers = 0
        
        # Załaduj ikony dla kategorii
        self.ikony = self.zaladuj_ikony()
        
        # Główny kontener
        self.main_frame = tk.Frame(root, bg="#2c3e50")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Lewa kolumna na legendę
        self.left_frame = tk.Frame(self.main_frame, bg="#34495e", width=int(self.window_width * 0.25))
        self.left_frame.pack(side="left", fill="y", padx=5, pady=5)
        self.left_frame.pack_propagate(False)  # Zapobiegaj zmniejszaniu rozmiaru
        
        # Tytuł legendy
        self.legend_title = tk.Label(self.left_frame, text="LEGENDA", font=("Arial", 16, "bold"),
                                     bg="#34495e", fg="white")
        self.legend_title.pack(pady=5)
        
        # Kontener na elementy legendy z możliwością przewijania
        self.legend_canvas = tk.Canvas(self.left_frame, bg="#34495e", highlightthickness=0)
        self.legend_canvas.pack(side="left", fill="both", expand=True)
        
        # Scrollbar dla legendy
        self.legend_scrollbar = Scrollbar(self.left_frame, orient="vertical", command=self.legend_canvas.yview)
        self.legend_scrollbar.pack(side="right", fill="y")
        self.legend_canvas.configure(yscrollcommand=self.legend_scrollbar.set)
        
        # Ramka wewnątrz canvas dla elementów legendy
        self.legend_container = tk.Frame(self.legend_canvas, bg="#34495e")
        self.legend_canvas.create_window((0, 0), window=self.legend_container, anchor="nw")
        
        # Prawa kolumna na koło i pytania
        self.right_frame = tk.Frame(self.main_frame, bg="#2c3e50")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Określ rozmiar koła - bardziej kompaktowy
        self.wheel_size = min(int(self.window_width * 0.4), int(self.window_height * 0.4))
        
        # Ramka na koło
        self.wheel_frame = tk.Frame(self.right_frame, bg="#2c3e50")
        self.wheel_frame.pack(fill="x", pady=5)
        
        # Canvas na koło
        self.canvas = tk.Canvas(self.wheel_frame, width=self.wheel_size, height=self.wheel_size, 
                               bg="#34495e", highlightthickness=2, highlightbackground="#f39c12")
        self.canvas.pack(pady=5)
        
        # Ramka na licznik odpowiedzi
        self.counter_frame = tk.Frame(self.right_frame, bg="#2c3e50")
        self.counter_frame.pack(fill="x", pady=5)
        
        # Etykieta licznika
        self.counter_label = tk.Label(self.counter_frame, 
                                    text="Poprawne odpowiedzi: 0/0 (0%)", 
                                    font=("Arial", 14, "bold"),
                                    bg="#2c3e50", fg="#ecf0f1")
        self.counter_label.pack(pady=5)
        
        # Przycisk z efektem hover
        self.spin_btn = tk.Button(self.wheel_frame, text="Zakręć kołem!", command=self.spin_wheel, 
                                 font=("Arial", 12, "bold"), bg="#3498db", fg="white", 
                                 relief="raised", bd=3, activebackground="#2980b9")
        self.spin_btn.pack(pady=5)
        self.spin_btn.bind("<Enter>", lambda e: self.spin_btn.config(bg="#2980b9"))
        self.spin_btn.bind("<Leave>", lambda e: self.spin_btn.config(bg="#3498db"))
        
        # Ramka na pytania z możliwością przewijania
        self.question_outer_frame = tk.Frame(self.right_frame, bg="#2c3e50")
        self.question_outer_frame.pack(fill="both", expand=True, pady=5)
        
        # Canvas dla przewijania pytań i odpowiedzi
        self.question_canvas = tk.Canvas(self.question_outer_frame, bg="#2c3e50", highlightthickness=0)
        self.question_canvas.pack(side="left", fill="both", expand=True)
        
        # Scrollbar dla pytań
        self.question_scrollbar = Scrollbar(self.question_outer_frame, orient="vertical", command=self.question_canvas.yview)
        self.question_scrollbar.pack(side="right", fill="y")
        self.question_canvas.configure(yscrollcommand=self.question_scrollbar.set)
        
        # Ramka wewnątrz canvas dla pytań i odpowiedzi
        self.question_frame = tk.Frame(self.question_canvas, bg="#2c3e50")
        self.question_canvas.create_window((0, 0), window=self.question_frame, anchor="nw", width=self.question_canvas.winfo_width())
        
        # Etykieta pytania z animowanym tłem
        self.label_pytanie = tk.Label(self.question_frame, text="", font=("Arial", 14, "bold"), 
                                     wraplength=int(self.window_width * 0.6), justify="center",
                                     bg="#ecf0f1", fg="#2c3e50", relief="groove", bd=2)
        self.label_pytanie.pack(pady=10, fill="x", padx=10)
        
        # Ramka na odpowiedzi
        self.odp_frame = tk.Frame(self.question_frame, bg="#2c3e50")
        self.odp_frame.pack(fill="x", pady=5, padx=10)
        
        # Zmienne dla checkboxów (dla obsługi wielu odpowiedzi)
        self.odp_vars = []
        self.odp_checks = []
        
        # Przycisk sprawdzania odpowiedzi z efektem hover - zmniejszony i przeniesiony
        self.check_btn = tk.Button(self.question_frame, text="Sprawdź odpowiedź", command=self.check_answer, 
                                  state='disabled', font=("Arial", 12, "bold"), bg="#e74c3c", fg="white", 
                                  relief="raised", bd=3, activebackground="#c0392b", padx=10, pady=5)
        self.check_btn.pack(pady=10)
        self.check_btn.bind("<Enter>", lambda e: self.check_btn.config(bg="#c0392b"))
        self.check_btn.bind("<Leave>", lambda e: self.check_btn.config(bg="#e74c3c"))
        
        self.aktualne_pytanie = None
        self.utworz_legende()
        self.rysuj_kolo()
        
        # Konfiguracja przewijania
        self.legend_container.bind("<Configure>", lambda e: self.legend_canvas.configure(scrollregion=self.legend_canvas.bbox("all")))
        self.question_frame.bind("<Configure>", self.configure_question_scroll)
        
        # Obsługa zmiany rozmiaru okna
        self.root.bind("<Configure>", self.on_resize)

    def configure_question_scroll(self, event):
        # Aktualizuj region przewijania i szerokość okna
        self.question_canvas.configure(scrollregion=self.question_canvas.bbox("all"))
        self.question_canvas.itemconfig(self.question_canvas.find_withtag("all")[0], width=self.question_canvas.winfo_width())

    def on_resize(self, event):
        # Aktualizuj rozmiary tylko gdy okno się zmienia
        if event.widget == self.root and (self.window_width != event.width or self.window_height != event.height):
            self.window_width = event.width
            self.window_height = event.height
            
            # Aktualizuj rozmiar koła - mniejszy dla lepszego dopasowania
            new_wheel_size = min(int(self.window_width * 0.35), int(self.window_height * 0.35))
            self.canvas.config(width=new_wheel_size, height=new_wheel_size)
            self.wheel_size = new_wheel_size
            
            # Aktualizuj szerokość lewej ramki
            self.left_frame.config(width=int(self.window_width * 0.2))
            
            # Aktualizuj zawijanie tekstu pytania
            self.label_pytanie.config(wraplength=int(self.window_width * 0.6))
            
            # Aktualizuj szerokość okna pytania w canvasie
            self.question_canvas.itemconfig(self.question_canvas.find_withtag("all")[0], width=self.question_canvas.winfo_width())
            
            # Przerysuj koło i legendę
            self.rysuj_kolo()
            self.utworz_legende()

    def zaladuj_ikony(self):
        ikony = {}
        assets_dir = "assets"
        
        # Sprawdź czy katalog istnieje
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir)
            print(f"Utworzono katalog {assets_dir}. Umieść w nim ikony dla kategorii.")
            return ikony
            
        # Mapowanie kategorii na nazwy plików ikon - poprawione
        ikona_mapping = {
            "lsk": "computer.png",
            "aso": "security.png",
            "Oprogramowanie": "software.png",
            "Sieci_komputerowe": "network.png",
            "Linux": "linux.png",
            "Informatyka": "informatics.png",
            "Strony internetowe": "web.png",
            "Urządzenia techniki komputerowe": "hardware.png",
            "Sieci komputerowe": "network.png",
            "Urządzenia techniki komputerowej": "hardware.png"
        }
        
        # Załaduj ikony dla każdej kategorii
        for kategoria, nazwa_pliku in ikona_mapping.items():
            sciezka_pliku = os.path.join(assets_dir, nazwa_pliku)
            if os.path.exists(sciezka_pliku):
                try:
                    ikona = Image.open(sciezka_pliku)
                    ikony[kategoria] = ikona
                except Exception as e:
                    print(f"Błąd ładowania ikony {nazwa_pliku}: {e}")
            else:
                print(f"Brak pliku ikony: {sciezka_pliku}")
                
        return ikony

    def utworz_legende(self):
        # Wyczyść istniejące elementy legendy
        for widget in self.legend_container.winfo_children():
            widget.destroy()
            
        # Określ rozmiar ikon w legendzie - mniejsze ikony
        icon_size = int(min(self.window_width * 0.03, 32))
        
        # Dodaj elementy legendy dla każdej kategorii
        for i, kategoria in enumerate(self.kategorie):
            # Ramka na jeden element legendy
            item_frame = tk.Frame(self.legend_container, bg="#34495e")
            item_frame.pack(fill="x", pady=3, padx=3, anchor="w")
            
            # Ikona kategorii (jeśli dostępna)
            if kategoria in self.ikony:
                # Przeskaluj ikonę
                resized_icon = self.ikony[kategoria].resize((icon_size, icon_size), Image.LANCZOS)
                photo = ImageTk.PhotoImage(resized_icon)
                
                # Zachowaj referencję do zdjęcia (inaczej garbage collector ją usunie)
                item_frame.photo = photo
                
                # Etykieta z ikoną
                icon_label = tk.Label(item_frame, image=photo, bg="#34495e")
                icon_label.pack(side="left", padx=3)
            else:
                # Kolorowy kwadrat jako zamiennik ikony
                colors = ["#FF6B6B", "#4ECDC4", "#FFD166", "#06D6A0", "#118AB2", "#073B4C"]
                color = colors[i % len(colors)]
                icon_label = tk.Label(item_frame, bg=color, width=2, height=1)
                icon_label.pack(side="left", padx=3, ipadx=icon_size//6, ipady=icon_size//6)
            
            # Nazwa kategorii - mniejsza czcionka
            name_label = tk.Label(item_frame, text=kategoria, font=("Arial", 10), 
                                 bg="#34495e", fg="white", anchor="w")
            name_label.pack(side="left", padx=5, fill="x", expand=True)

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
        center_x = self.wheel_size / 2
        center_y = self.wheel_size / 2
        radius = self.wheel_size * 0.4  # Promień koła
        
        # Nowe, bardziej przyjazne kolory dla koła
        colors = [
            "#FF6B6B", "#4ECDC4", "#FFD166", "#06D6A0", 
            "#118AB2", "#073B4C", "#F72585", "#7209B7", 
            "#3A86FF", "#8338EC", "#FB5607", "#FFBE0B"
        ]
        
        # Rysowanie koła
        for i, kat in enumerate(self.kategorie):
            start_angle = i * kat_angle
            color = colors[i % len(colors)] if i != highlight_idx else "#E63946"
            self.canvas.create_arc(center_x - radius, center_y - radius,
                                  center_x + radius, center_y + radius,
                                  start=start_angle, extent=kat_angle,
                                  fill=color, outline="white", width=2)
            
            # Umieść ikonę zamiast tekstu
            angle_rad = math.radians(start_angle + kat_angle / 2)
            icon_distance = radius * 0.7  # Ikona bliżej środka dla lepszej widoczności
            icon_x = center_x + icon_distance * math.cos(angle_rad)
            icon_y = center_y + icon_distance * math.sin(angle_rad)
            
            # Rozmiar ikony - mniejsze dla lepszego dopasowania
            icon_size = int(self.wheel_size * 0.08)
            
            if kat in self.ikony:
                # Przeskaluj ikonę
                resized_icon = self.ikony[kat].resize((icon_size, icon_size), Image.LANCZOS)
                photo = ImageTk.PhotoImage(resized_icon)
                
                # Zachowaj referencję do zdjęcia
                if not hasattr(self.canvas, 'photos'):
                    self.canvas.photos = [photo]
                else:
                    self.canvas.photos.append(photo)
                
                # Utwórz obrazek na canvasie
                self.canvas.create_image(icon_x, icon_y, image=photo)
            else:
                # Narysuj symbol jako zamiennik ikony
                symbol_size = icon_size / 2
                self.canvas.create_oval(icon_x - symbol_size, icon_y - symbol_size,
                                      icon_x + symbol_size, icon_y + symbol_size,
                                      fill="white", outline="black")
                self.canvas.create_text(icon_x, icon_y, text=str(i+1), font=("Arial", int(symbol_size/2)))

        # Dodanie środka koła
        center_size = self.wheel_size * 0.05
        self.canvas.create_oval(center_x - center_size, center_y - center_size,
                               center_x + center_size, center_y + center_size,
                               fill="#ecf0f1", outline="white")
        
        # Dodanie strzałki wskazującej wybraną kategorię - mniejsza i lepiej widoczna
        arrow_size = self.wheel_size * 0.08
        self.canvas.create_polygon(
            center_x + radius + arrow_size/3, center_y - arrow_size/2,
            center_x + radius + arrow_size/3, center_y + arrow_size/2,
            center_x + radius + arrow_size, center_y,
            fill="#FF1E56", outline="white", width=2
        )

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
        if not pytania_kat:
            messagebox.showinfo("Informacja", f"Brak pytań w kategorii {self.wybrana_kategoria}")
            self.reset_quiz()
            return
            
        self.aktualne_pytanie = random.choice(pytania_kat)
        self.label_pytanie.config(text=self.aktualne_pytanie['Question Text'], bg="#ecf0f1")

        # Czyszczenie poprzednich odpowiedzi
        for widget in self.odp_frame.winfo_children():
            widget.destroy()
        
        self.odp_vars = []
        self.odp_checks = []
        
        # Sprawdzenie czy pytanie ma wiele odpowiedzi
        ma_wiele_odp = "," in self.aktualne_pytanie.get('Correct Answer', '')
        
        # Tworzenie nowych widgetów odpowiedzi
        for idx in range(5):
            opcja = self.aktualne_pytanie.get(f'Option {idx+1}', '')
            if opcja.strip():
                # Kontener dla checkboxa/radiobutton i etykiety
                option_frame = tk.Frame(self.odp_frame, bg="#34495e")
                option_frame.pack(fill="x", pady=2)
                
                if ma_wiele_odp:
                    # Checkbox dla wielu odpowiedzi
                    var = IntVar()
                    self.odp_vars.append(var)
                    
                    # Poprawiony checkbox z możliwością odznaczania
                    cb = Checkbutton(option_frame, variable=var, bg="#34495e", 
                                    activebackground="#2980b9", selectcolor="#2980b9",
                                    onvalue=1, offvalue=0)
                    cb.pack(side="left", padx=5)
                    
                    # Dodaj etykietę, która po kliknięciu przełącza checkbox
                    label = tk.Label(option_frame, text=opcja, font=("Arial", 12),
                                    bg="#34495e", fg="#ecf0f1", anchor="w")
                    label.pack(side="left", fill="x", expand=True, padx=5)
                    
                    # Obsługa kliknięcia na etykietę
                    label.bind("<Button-1>", lambda event, v=var: v.set(1 if v.get() == 0 else 0))
                    
                    self.odp_checks.append(cb)
                else:
                    # Radiobutton dla pojedynczej odpowiedzi
                    if idx == 0:
                        self.odp_var = tk.StringVar()
                    
                    # Poprawiony radiobutton z możliwością odznaczania
                    rb = tk.Radiobutton(option_frame, variable=self.odp_var, value=str(idx+1), 
                                      bg="#34495e", activebackground="#2980b9", selectcolor="#2980b9",
                                      indicatoron=1)  # Pokazuj wskaźnik (kółko)
                    rb.pack(side="left", padx=5)
                    
                    # Dodaj etykietę, która po kliknięciu przełącza radiobutton
                    label = tk.Label(option_frame, text=opcja, font=("Arial", 12),
                                    bg="#34495e", fg="#ecf0f1", anchor="w")
                    label.pack(side="left", fill="x", expand=True, padx=5)
                    
                    # Obsługa kliknięcia na etykietę
                    label.bind("<Button-1>", lambda event, val=str(idx+1), v=self.odp_var: 
                              v.set("" if v.get() == val else val))

        self.check_btn.config(state='normal')
        
        # Upewnij się, że pytanie jest widoczne (przewiń do góry)
        self.question_canvas.yview_moveto(0)
        
        # Aktualizuj region przewijania
        self.question_frame.update_idletasks()
        self.question_canvas.configure(scrollregion=self.question_canvas.bbox("all"))

    def check_answer(self):
        ma_wiele_odp = "," in self.aktualne_pytanie.get('Correct Answer', '')
        odpowiedz_poprawna = False
        
        if ma_wiele_odp:
            # Sprawdzenie wielu odpowiedzi
            wybrane = [str(i+1) for i, var in enumerate(self.odp_vars) if var.get() == 1]
            if not wybrane:
                messagebox.showwarning("Brak odpowiedzi", "Proszę zaznaczyć co najmniej jedną odpowiedź!")
                return
                
            poprawne_odp = self.aktualne_pytanie['Correct Answer'].split(',')
            
            # Sprawdzenie czy wszystkie poprawne odpowiedzi zostały wybrane i żadna niepoprawna
            wszystkie_poprawne = all(odp in wybrane for odp in poprawne_odp)
            zadna_niepoprawna = all(odp in poprawne_odp for odp in wybrane)
            
            if wszystkie_poprawne and zadna_niepoprawna:
                odpowiedz_poprawna = True
                messagebox.showinfo("Wynik", "Poprawna odpowiedź! ✔️")
                self.label_pytanie.config(bg='lightgreen')
                try:
                    winsound.Beep(1000, 200)  # Dźwięk sukcesu
                except:
                    pass
            else:
                poprawne_teksty = []
                for i in poprawne_odp:
                    try:
                        poprawne_teksty.append(self.aktualne_pytanie[f'Option {int(i)}'])
                    except:
                        continue
                
                poprawne_wyswietl = ', '.join(poprawne_teksty)
                messagebox.showerror("Wynik", f"Zła odpowiedź! ❌ Poprawne odpowiedzi to: {poprawne_wyswietl}")
                self.label_pytanie.config(bg='#e74c3c')
                try:
                    winsound.Beep(300, 200)  # Dźwięk błędu
                except:
                    pass
        else:
            # Sprawdzenie pojedynczej odpowiedzi
            try:
                wybrana = self.odp_var.get()
                if not wybrana:
                    messagebox.showwarning("Brak odpowiedzi", "Proszę zaznaczyć odpowiedź!")
                    return
                    
                poprawne_odp = self.aktualne_pytanie['Correct Answer'].split(',')
                if wybrana in poprawne_odp:
                    odpowiedz_poprawna = True
                    messagebox.showinfo("Wynik", "Poprawna odpowiedź! ✔️")
                    self.label_pytanie.config(bg='lightgreen')
                    try:
                        winsound.Beep(1000, 200)  # Dźwięk sukcesu
                    except:
                        pass
                else:
                    poprawne_teksty = []
                    for i in poprawne_odp:
                        try:
                            poprawne_teksty.append(self.aktualne_pytanie[f'Option {int(i)}'])
                        except:
                            continue
                    
                    poprawne_wyswietl = ', '.join(poprawne_teksty)
                    messagebox.showerror("Wynik", f"Zła odpowiedź! ❌ Poprawna odpowiedź to: {poprawne_wyswietl}")
                    self.label_pytanie.config(bg='#e74c3c')
                    try:
                        winsound.Beep(300, 200)  # Dźwięk błędu
                    except:
                        pass
            except:
                messagebox.showwarning("Błąd", "Wystąpił problem przy sprawdzaniu odpowiedzi!")
                return

        # Aktualizuj licznik odpowiedzi
        self.total_answers += 1
        if odpowiedz_poprawna:
            self.correct_answers += 1
        
        # Oblicz procent poprawnych odpowiedzi
        procent = 0 if self.total_answers == 0 else int((self.correct_answers / self.total_answers) * 100)
        
        # Aktualizuj etykietę licznika
        self.counter_label.config(text=f"Poprawne odpowiedzi: {self.correct_answers}/{self.total_answers} ({procent}%)")
        
        self.root.after(2000, self.reset_quiz)

    def reset_quiz(self):
        self.label_pytanie.config(text="", bg="#ecf0f1")
        for widget in self.odp_frame.winfo_children():
            widget.destroy()
        self.check_btn.config(state='disabled')
        self.spin_btn.config(state='normal')
        self.rysuj_kolo()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()