import tkinter as tk
from tkinter import ttk, messagebox
import csv
import random
import math
import os
from PIL import Image, ImageTk
import time
import colorsys

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz z Losowaniem Kategorii")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0D0D1A")
        self.root.minsize(800, 600)

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#0D0D1A")
        self.style.configure("TButton", background="#0D0D1A", foreground="#00FFFF", font=("Arial", 12, "bold"))
        self.style.configure("TLabel", background="#0D0D1A", foreground="#E0E0FF")
        self.style.configure("TCheckbutton", background="#0D0D1A", foreground="#E0E0FF", font=("Arial", 12))
        self.style.map("TCheckbutton",
            background=[('active', '#1A1A2E')],
            foreground=[('active', '#00FFFF')]
        )

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
        self.category_items = []
        self.answer_vars = []

        self.pulse_intensity = 0
        self.pulse_direction = 1
        self.neon_glow_ids = []
        self.neon_animation_running = False

        self.load_questions()
        self.setup_layout()
        self.init_wheel()
        self.create_legend()
        self.setup_score_display()
        self.root.bind("<Configure>", self.on_window_resize)
        self.start_neon_animation()

    def load_questions(self):
        try:
            with open('pytania.csv', 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader)

                for row in reader:
                    if len(row) < 11:
                        print(f"Pominięto wiersz z niewystarczającą liczbą kolumn: {row}")
                        continue

                    options = [opt for opt in row[2:7] if opt.strip()]
                    question = {
                        "text": row[0],
                        "type": row[1],
                        "options": options,
                        "correct": row[7].split(','),
                        "time": int(row[8]) if row[8] else 20,
                        "image": row[9] if row[9] else None,
                        "category": row[10]
                    }
                    self.questions.append(question)
                    
                    if question["category"] not in self.categories:
                        self.categories.append(question["category"])

            print(f"Wczytano {len(self.questions)} pytań w {len(self.categories)} kategoriach")

            neon_colors = ["#00FFFF", "#FF00FF", "#00FF00", "#FFFF00", "#FF3399", "#33CCFF", "#FF6600", "#CC99FF"]
            for i, category in enumerate(self.categories):
                self.category_colors[category] = neon_colors[i % len(neon_colors)]
                
                icon_path = f"assets/{category}.png"
                if os.path.exists(icon_path):
                    img = Image.open(icon_path)
                    img = img.resize((50, 50), Image.LANCZOS)
                    self.category_icons[category] = ImageTk.PhotoImage(img)
                else:
                    print(f"Brak ikony dla kategorii {category}")
                    self.category_icons[category] = None

        except FileNotFoundError:
            messagebox.showerror("Błąd", "Nie znaleziono pliku pytania.csv!")
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd podczas wczytywania pytań: {str(e)}")

    def setup_layout(self):
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=4)
        self.root.rowconfigure(0, weight=1)

        self.left_frame = ttk.Frame(self.root, style="TFrame")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.right_frame = ttk.Frame(self.root, style="TFrame")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(0, weight=3)
        self.right_frame.rowconfigure(1, weight=2)

        self.wheel_frame = ttk.Frame(self.right_frame, style="TFrame")
        self.wheel_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.question_frame = ttk.Frame(self.right_frame, style="TFrame")
        self.question_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.wheel_frame.columnconfigure(0, weight=1)
        self.wheel_frame.rowconfigure(0, weight=1)
        self.wheel_frame.rowconfigure(1, weight=0)

        self.wheel_canvas = tk.Canvas(
            self.wheel_frame, 
            bg="#0D0D1A",
            highlightthickness=0
        )
        self.wheel_canvas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.spin_button = ttk.Button(
            self.wheel_frame, 
            text="LOSUJ KATEGORIĘ", 
            command=self.spin_wheel,
            style="TButton"
        )
        self.spin_button.grid(row=1, column=0, pady=(0, 10))

        self.question_label = ttk.Label(
            self.question_frame, 
            text="Naciśnij przycisk aby wylosować kategorię i rozpocząć quiz!",
            wraplength=600,
            font=("Arial", 14),
            style="TLabel",
            justify="center"
        )
        self.question_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.options_container = ttk.Frame(self.question_frame, style="TFrame")
        self.options_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.options_container.columnconfigure(0, weight=1)
        self.options_container.rowconfigure(0, weight=1)

        self.options_canvas = tk.Canvas(
            self.options_container,
            bg="#0D0D1A",
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

        self.options_frame.bind("<Configure>", self.on_options_frame_configure)
        self.options_canvas.bind("<Configure>", self.on_canvas_configure)

        self.submit_button = ttk.Button(
            self.question_frame, 
            text="ZATWIERDŹ ODPOWIEDŹ", 
            command=self.check_answer,
            style="TButton"
        )
        self.submit_button.grid(row=2, column=0, pady=10)
        self.submit_button.config(state=tk.DISABLED)

    def on_options_frame_configure(self, event):
        self.options_canvas.configure(scrollregion=self.options_canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        self.options_canvas.itemconfig(self.options_window, width=event.width)
    
    def on_window_resize(self, event):
        if event.widget == self.root:
            self.question_label.configure(wraplength=self.question_frame.winfo_width() - 40)
            self.resize_wheel()

    def resize_wheel(self):
        width = self.wheel_canvas.winfo_width()
        height = self.wheel_canvas.winfo_height()
        
        wheel_size = min(width, height) - 180
        
        if wheel_size > 100:
            self.wheel_center_x = width // 2
            self.wheel_center_y = height // 2
            self.wheel_radius = wheel_size // 2 - 10
            
            self.draw_wheel()

    def init_wheel(self):
        self.wheel_center_x = 250
        self.wheel_center_y = 250
        self.wheel_radius = 200
        self.draw_wheel()
        
        self.root.update()
        self.resize_wheel()

    def create_neon_glow(self, x1, y1, x2, y2, color, width=2, tags=None):
        glow_colors = []
        intensity = self.pulse_intensity
        
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)

        for i in range(3):
            r_adj = min(255, int(r * (0.5 + intensity * 0.5)))
            g_adj = min(255, int(g * (0.5 + intensity * 0.5)))
            b_adj = min(255, int(b * (0.5 + intensity * 0.5)))

            glow_hex = f"#{r_adj:02x}{g_adj:02x}{b_adj:02x}"
            glow_colors.append(glow_hex)
            
            intensity *= 0.7
        
        glow_ids = []
        for i in range(3):
            glow_width = width + (3-i) * 4
            
            item_tags = tags if tags else []
            if isinstance(item_tags, str):
                item_tags = [item_tags]
            item_tags.append("neon_glow")
            
            glow_id = self.wheel_canvas.create_arc(
                x1-i*3, y1-i*3, x2+i*3, y2+i*3,
                outline=glow_colors[i], width=glow_width,
                start=0, extent=359.99, style="arc",
                tags=item_tags
            )
            glow_ids.append(glow_id)
        
        return glow_ids

    def draw_wheel(self):
        self.wheel_canvas.delete("all")
        
        for r in range(self.wheel_radius, 0, -5):
            ratio = r / self.wheel_radius
            color_value = int(25 * ratio)
            color = f"#{color_value:02x}{color_value:02x}{color_value + 10:02x}"
            
            self.wheel_canvas.create_oval(
                self.wheel_center_x - r,
                self.wheel_center_y - r,
                self.wheel_center_x + r,
                self.wheel_center_y + r,
                outline=color, width=5, fill=""
            )
        
        if not self.categories:
            return
            
        num_categories = len(self.categories)
        angle_per_category = 360.0 / num_categories
        
        self.category_items = []
        self.neon_glow_ids = []

        for i, category in enumerate(self.categories):
            start_angle = self.angle + i * angle_per_category
            end_angle = start_angle + angle_per_category

            section = self.wheel_canvas.create_arc(
                self.wheel_center_x - self.wheel_radius,
                self.wheel_center_y - self.wheel_radius,
                self.wheel_center_x + self.wheel_radius,
                self.wheel_center_y + self.wheel_radius,
                start=start_angle, 
                extent=angle_per_category,
                fill="",
                outline=self.category_colors[category],
                width=2,
                tags=f"section_{category}"
            )
            self.category_items.append(section)

            glow_ids = self.create_neon_glow(
                self.wheel_center_x - self.wheel_radius,
                self.wheel_center_y - self.wheel_radius,
                self.wheel_center_x + self.wheel_radius,
                self.wheel_center_y + self.wheel_radius,
                self.category_colors[category],
                width=2,
                tags=[f"glow_{category}", f"section_{category}"]
            )
            self.neon_glow_ids.extend(glow_ids)

            mid_angle_rad = math.radians(start_angle + angle_per_category / 2)
            icon_x = self.wheel_center_x + (self.wheel_radius * 0.7) * math.cos(mid_angle_rad)
            icon_y = self.wheel_center_y + (self.wheel_radius * 0.7) * math.sin(mid_angle_rad)
            
            if self.category_icons.get(category):
                icon = self.wheel_canvas.create_image(
                    icon_x, icon_y,
                    image=self.category_icons[category],
                    tags=f"icon_{category}"
                )
                self.category_items.append(icon)

        for r in range(int(self.wheel_radius * 0.25), 0, -3):
            ratio = r / (self.wheel_radius * 0.25)
            blue_value = int(200 * ratio)
            center_color = f"#00{blue_value:02x}ff"
            
            self.wheel_canvas.create_oval(
                self.wheel_center_x - r,
                self.wheel_center_y - r,
                self.wheel_center_x + r,
                self.wheel_center_y + r,
                outline=center_color,
                width=2,
                fill=""
            )

        center_glow_ids = self.create_neon_glow(
            self.wheel_center_x - self.wheel_radius * 0.25,
            self.wheel_center_y - self.wheel_radius * 0.25,
            self.wheel_center_x + self.wheel_radius * 0.25,
            self.wheel_center_y + self.wheel_radius * 0.25,
            "#00FFFF",
            width=3,
            tags="center_glow"
        )
        self.neon_glow_ids.extend(center_glow_ids)

        pointer_line = self.wheel_canvas.create_line(
            self.wheel_center_x, self.wheel_center_y,
            self.wheel_center_x, self.wheel_center_y - self.wheel_radius,
            fill="#00FFFF",
            width=2,
            dash=(5, 3),
            tags="pointer_line"
        )
        
        pointer_glow = self.wheel_canvas.create_polygon(
            self.wheel_center_x, self.wheel_center_y - self.wheel_radius - 10,
            self.wheel_center_x - 10, self.wheel_center_y - self.wheel_radius + 10,
            self.wheel_center_x + 10, self.wheel_center_y - self.wheel_radius + 10,
            fill="",
            outline="#00FFFF",
            width=3,
            tags="pointer_glow"
        )
        self.neon_glow_ids.append(pointer_glow)

        for angle in range(0, 360, 45):
            angle_rad = math.radians(angle)
            x1 = self.wheel_center_x + (self.wheel_radius * 0.25) * math.cos(angle_rad)
            y1 = self.wheel_center_y + (self.wheel_radius * 0.25) * math.sin(angle_rad)
            x2 = self.wheel_center_x + self.wheel_radius * math.cos(angle_rad)
            y2 = self.wheel_center_y + self.wheel_radius * math.sin(angle_rad)

            self.wheel_canvas.create_line(
                x1, y1, x2, y2,
                fill="#004466",
                width=1,
                dash=(5, 3),
                tags="cyber_line"
            )

    def start_neon_animation(self):
        if not self.neon_animation_running:
            self.neon_animation_running = True
            self.animate_neon()
    
    def animate_neon(self):
        self.pulse_intensity += 0.05 * self.pulse_direction
        
        if self.pulse_intensity >= 1.0:
            self.pulse_intensity = 1.0
            self.pulse_direction = -1
        elif self.pulse_intensity <= 0.3:
            self.pulse_intensity = 0.3
            self.pulse_direction = 1

        if hasattr(self, 'wheel_canvas'):
            self.draw_wheel()
            self.root.after(50, self.animate_neon)

    def spin_wheel(self):
        if self.spinning:
            return
            
        self.spinning = True
        self.spin_button.config(state=tk.DISABLED)
        
        rotations = random.uniform(2, 5)
        total_angle = rotations * 360
        
        speed = 8
        
        trail_ids = []
        
        def animate_spin():
            nonlocal speed, total_angle, trail_ids
            
            if total_angle > 0 and speed > 0.2:
                self.angle = (self.angle + speed) % 360
                total_angle -= speed
                
                for trail_id in trail_ids:
                    self.wheel_canvas.delete(trail_id)
                trail_ids = []
                
                self.draw_wheel()
                
                speed *= 0.985 
                
                self.root.after(20, animate_spin)
            else:
                self.spinning = False
                self.spin_button.config(state=tk.NORMAL)
                
                angle_per_category = 360 / len(self.categories)
                adjusted_angle = (self.angle + angle_per_category / 2) % 360 
                category_index = int(adjusted_angle / angle_per_category) 
                self.selected_category = self.categories[category_index]

                self.highlight_category(self.selected_category)
                
                self.load_question_from_category(self.selected_category)

        animate_spin()

    def create_legend(self):
        legend_title = ttk.Label(
            self.left_frame, 
            text="KATEGORIE", 
            font=("Arial", 16, "bold"),
            foreground="#00FFFF",
            style="TLabel"
        )
        legend_title.pack(pady=(0, 20))
        
        legend_frame = ttk.Frame(self.left_frame, style="TFrame")
        legend_frame.pack(fill=tk.BOTH, expand=True)
        
        for category in self.categories:
            category_frame = ttk.Frame(legend_frame, style="TFrame")
            category_frame.pack(fill=tk.X, pady=5)
            
            color_frame = ttk.Frame(category_frame, style="TFrame")
            color_frame.pack(side=tk.LEFT, padx=5)
            
            color_canvas = tk.Canvas(
                color_frame, 
                width=25, 
                height=25, 
                bg="#0D0D1A",
                highlightthickness=1,
                highlightbackground=self.category_colors[category]
            )
            color_canvas.pack()
            
            glow_size = 15
            for i in range(3):
                size = glow_size - i*3
                color_canvas.create_oval(
                    12-size/2, 12-size/2, 
                    12+size/2, 12+size/2,
                    outline=self.category_colors[category],
                    width=2-i*0.5,
                    fill=""
                )
            
            if self.category_icons.get(category):
                icon_frame = ttk.Frame(category_frame, style="TFrame")
                icon_frame.pack(side=tk.LEFT, padx=5)
                
                icon_label = ttk.Label(icon_frame, image=self.category_icons[category])
                icon_label.pack()
            
            name_label = ttk.Label(
                category_frame, 
                text=category, 
                foreground="#E0E0FF",
                font=("Arial", 12, "bold"),
                style="TLabel"
            )
            name_label.pack(side=tk.LEFT, padx=5)
            
            category_frame.color_canvas = color_canvas
            category_frame.name_label = name_label
            setattr(self, f"legend_{category}", category_frame)

    def highlight_category(self, category):
        for cat in self.categories:
            cat_frame = getattr(self, f"legend_{cat}")
            cat_frame.name_label.configure(foreground="#E0E0FF")
        
        selected_frame = getattr(self, f"legend_{category}")
        selected_frame.name_label.configure(foreground=self.category_colors[category])
        
        self.root.update()
        
        flash_colors = ["#FFFFFF", self.category_colors[category]]
        for _ in range(5):
            for color in flash_colors:
                selected_frame.name_label.configure(foreground=color)
                selected_frame.color_canvas.configure(highlightbackground=color)
                self.root.update()
                time.sleep(0.1)
        
        selected_frame.name_label.configure(foreground=self.category_colors[category])
        selected_frame.color_canvas.configure(highlightbackground=self.category_colors[category])

    def setup_score_display(self):
        score_frame = ttk.Frame(self.left_frame, style="TFrame")
        score_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        score_title = ttk.Label(
            score_frame,
            text="WYNIKI",
            font=("Arial", 14, "bold"),
            foreground="#00FFFF",
            style="TLabel"
        )
        score_title.pack(pady=(0, 10))
        
        self.correct_label = ttk.Label(
            score_frame, 
            text="Poprawne: 0", 
            font=("Arial", 12, "bold"),
            foreground="#00FF00",
            style="TLabel"
        )
        self.correct_label.pack(pady=5)
        
        self.incorrect_label = ttk.Label(
            score_frame, 
            text="Niepoprawne: 0", 
            font=("Arial", 12, "bold"),
            foreground="#FF00FF",
            style="TLabel"
        )
        self.incorrect_label.pack(pady=5)
        
        cyber_canvas = tk.Canvas(score_frame, height=30, bg="#0D0D1A", highlightthickness=0)
        cyber_canvas.pack(fill=tk.X, pady=10)
        
        for i in range(5):
            y = 15
            cyber_canvas.create_line(0, y, cyber_canvas.winfo_reqwidth(), y, fill="#00FFFF", dash=(10, 5))

    def update_score_display(self):
        self.correct_label.config(text=f"Poprawne: {self.correct_count}")
        self.incorrect_label.config(text=f"Niepoprawne: {self.incorrect_count}")

    def load_question_from_category(self, category):
        category_questions = [q for q in self.questions if q["category"] == category]
        
        if not category_questions:
            self.question_label.config(text=f"Brak pytań w kategorii {category}!")
            return
        
        self.current_question = random.choice(category_questions)
        
        self.question_label.config(
            text=self.current_question["text"], 
            foreground="#E0E0FF",
            font=("Arial", 14, "bold")
        )
        
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        self.answer_vars = []
        
        if not self.current_question["options"]:
            error_label = ttk.Label(
                self.options_frame,
                text="Błąd: Brak opcji odpowiedzi!",
                foreground="#FF00FF",
                style="TLabel"
            )
            error_label.pack(pady=10)
            return
        
        for i, option in enumerate(self.current_question["options"]):
            var = tk.BooleanVar()
            self.answer_vars.append(var)
            
            option_frame = ttk.Frame(self.options_frame, style="TFrame")
            option_frame.pack(fill=tk.X, pady=8, padx=5)
            
            option_canvas = tk.Canvas(
                option_frame,
                bg="#0D0D1A",
                highlightthickness=1,
                highlightbackground="#00AAFF",
                height=40
            )
            option_canvas.pack(fill=tk.X, padx=5, pady=3)
            
            option_cb = ttk.Checkbutton(
                option_canvas,
                text=f"Opcja {i+1}: {option}",
                variable=var,
                style="TCheckbutton"
            )
            option_cb.place(x=10, y=8)

        self.options_frame.update_idletasks()
        self.options_canvas.configure(scrollregion=self.options_canvas.bbox("all"))
        
        self.submit_button.config(state=tk.NORMAL)

    def check_answer(self):
        if not self.current_question:
            return
        
        selected_answers = [str(i+1) for i, var in enumerate(self.answer_vars) if var.get()]
        correct = set(selected_answers) == set(self.current_question["correct"])
        
        if correct:
            self.correct_count += 1
            result_text = "Poprawna odpowiedź!"
            result_color = "#00FF00"
        else:
            self.incorrect_count += 1
            correct_options = [self.current_question["options"][int(i)-1] for i in self.current_question["correct"]]
            correct_text = ", ".join(correct_options)
            
            result_text = f"Niepoprawna odpowiedź! Prawidłowe odpowiedzi: {correct_text}"
            result_color = "#FF00FF"
        
        self.update_score_display()
        
        original_bg = self.question_frame["background"]
        
        def flash_background(count=0):
            if count < 5:
                flash_color = result_color if count % 2 == 0 else "#0D0D1A"
                self.question_frame.configure(background=flash_color)
                self.root.after(200, flash_background, count + 1)
            else:
                self.question_frame.configure(background=original_bg)
                self.root.after(1000, self.reset_for_next_question)

        flash_background()

    def reset_for_next_question(self):
        self.question_label.config(
            text="Naciśnij przycisk aby wylosować kolejną kategorię!",
            foreground="#00FFFF",
            font=("Arial", 14)
        )
        
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        self.answer_vars = []
        
        self.spin_button.config(state=tk.NORMAL)
        
        self.current_question = None

def main():
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
