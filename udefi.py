import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import platform
import ctypes
import shutil
import os

def get_wmi(cmd):
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode("cp866", errors="ignore")
        lines = [line.strip() for line in out.splitlines() if line.strip()]
        return lines[1] if len(lines) > 1 else "Не определено"
    except Exception:
        return "Не определено"

def get_current_wallpaper():
    try:
        buf = ctypes.create_unicode_buffer(512)
        ctypes.windll.user32.SystemParametersInfoW(115, 512, buf, 0)
        return buf.value
    except Exception:
        return ""

class UDEFIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UDEFI // Темы, Обои и Рентген Железа v1.2")
        self.root.geometry("720x530")
        self.root.resizable(False, False)

        self.themes = {
            "orange": {"bg": "#0D0D0D", "panel": "#161616", "accent": "#FF6D00", "text": "#FFFFFF"},
            "red":    {"bg": "#0F0505", "panel": "#1C0A0A", "accent": "#D50000", "text": "#FFFFFF"},
            "black":  {"bg": "#080808", "panel": "#141414", "accent": "#E0E0E0", "text": "#FFFFFF"}
        }
        self.current_theme = "orange"
        self.active_tab = "wallpapers"
        self.selected_wp = None
        self.backup_path = os.path.abspath("backup_original_wallpaper.jpg")

        self.setup_ui()
        self.apply_theme("orange")

    def setup_ui(self):
        self.header = tk.Frame(self.root)
        self.header.pack(fill="x", padx=20, pady=(15, 5))

        self.title_lbl = tk.Label(self.header, text="UDEFI // CUSTOM EDITION", font=("Consolas", 18, "bold"))
        self.title_lbl.pack(side="left")

        self.btn_frame = tk.Frame(self.header)
        self.btn_frame.pack(side="right")

        tk.Button(self.btn_frame, text="DNS ORANGE", command=lambda: self.apply_theme("orange"),
                  bg="#FF6D00", fg="#000", font=("Consolas", 9, "bold"), relief="flat", padx=8).pack(side="left", padx=3)
        tk.Button(self.btn_frame, text="CRIMSON", command=lambda: self.apply_theme("red"),
                  bg="#D50000", fg="#FFF", font=("Consolas", 9, "bold"), relief="flat", padx=8).pack(side="left", padx=3)
        tk.Button(self.btn_frame, text="STEALTH", command=lambda: self.apply_theme("black"),
                  bg="#262626", fg="#FFF", font=("Consolas", 9, "bold"), relief="flat", padx=8).pack(side="left", padx=3)

        self.nav_frame = tk.Frame(self.root)
        self.nav_frame.pack(fill="x", padx=20, pady=8)

        self.tab_wp_btn = tk.Button(self.nav_frame, text="[ 1. НАРОДНЫЙ СТИЛЬ ]", command=lambda: self.switch_tab("wallpapers"),
                                    font=("Consolas", 10, "bold"), relief="flat", padx=10, pady=6, cursor="hand2")
        self.tab_wp_btn.pack(side="left", padx=(0, 8))

        self.tab_info_btn = tk.Button(self.nav_frame, text="[ 2. РЕНТГЕН ЖЕЛЕЗА ]", command=lambda: self.switch_tab("info"),
                                      font=("Consolas", 10, "bold"), relief="flat", padx=10, pady=6, cursor="hand2")
        self.tab_info_btn.pack(side="left", padx=(0, 8))

        self.tab_corp_btn = tk.Button(self.nav_frame, text="[ 3. ДЛЯ КОРПОРАТИВНЫХ ]", command=lambda: self.switch_tab("corp"),
                                      font=("Consolas", 10, "bold"), relief="flat", padx=10, pady=6, cursor="hand2")
        self.tab_corp_btn.pack(side="left")

        self.content = tk.Frame(self.root)
        self.content.pack(fill="both", expand=True)

        # --- ВКЛАДКА 1: НАРОДНЫЙ СТИЛЬ ---
        self.wp_frame = tk.Frame(self.content)
        self.preview_canvas = tk.Canvas(self.wp_frame, width=680, height=220, highlightthickness=1, highlightbackground="#333333")
        self.preview_canvas.pack(pady=(5, 8))
        self.draw_default_art()

        self.wp_status = tk.Label(self.wp_frame, text="Выбери кастомные обои сообщества или загрузи свою картинку", font=("Consolas", 9))
        self.wp_status.pack(pady=3)

        wp_btns = tk.Frame(self.wp_frame)
        wp_btns.pack(fill="x", padx=20, pady=8)
        self.wp_btns = wp_btns

        self.choose_btn = tk.Button(wp_btns, text="ВЫБРАТЬ ФАЙЛ ОБОЕВ...", command=self.choose_wallpaper,
                                    font=("Consolas", 10, "bold"), relief="flat", padx=12, pady=8, cursor="hand2")
        self.choose_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.apply_wp_btn = tk.Button(wp_btns, text="УСТАНОВИТЬ НА РАБОЧИЙ СТОЛ", command=self.set_wallpaper,
                                      font=("Consolas", 10, "bold"), relief="flat", padx=12, pady=8, cursor="hand2")
        self.apply_wp_btn.pack(side="left", expand=True, fill="x", padx=(6, 0))

        # --- ВКЛАДКА 2: РЕНТГЕН ЖЕЛЕЗА ---
        self.info_frame = tk.Frame(self.content)
        self.info_box = tk.Text(self.info_frame, font=("Consolas", 10), relief="flat", padx=15, pady=15, height=15, state="disabled")
        self.info_box.pack(fill="both", expand=True, padx=20, pady=10)

        self.scan_btn = tk.Button(self.info_frame, text="ЗАПУСТИТЬ ПРОВЕРКУ ЖЕЛЕЗА И ПЛАТЫ", command=self.scan_hardware,
                                  font=("Consolas", 11, "bold"), relief="flat", pady=8, cursor="hand2")
        self.scan_btn.pack(fill="x", padx=20, pady=(0, 15))

        # --- ВКЛАДКА 3: ДЛЯ КОРПОРАТИВНЫХ ---
        self.corp_frame = tk.Frame(self.content)
        self.corp_title = tk.Label(self.corp_frame,
                                   text="Зашёл с брендового ноута и хочешь заводской лоск? Не проблема, поможем!\nВыбери свой бренд ниже, чтобы подтянуть заводские обои и советы:",
                                   font=("Consolas", 10), justify="left")
        self.corp_title.pack(anchor="w", padx=20, pady=(10, 10))

        brands_grid = tk.Frame(self.corp_frame)
        brands_grid.pack(fill="x", padx=20, pady=5)
        self.brands_grid = brands_grid

        brands = [
            ("HP Pavilion / Envy (2010–2014)", "hp"),
            ("ASUS ROG / N-Series", "asus"),
            ("Lenovo IdeaPad / ThinkPad", "lenovo"),
            ("MSI Gaming / Dragon", "msi"),
            ("Acer Aspire / Predator", "acer"),
            ("ВЕРНУТЬ МОЙ БЭКАП ОБОЕВ", "restore")
        ]

        for idx, (b_name, b_code) in enumerate(brands):
            btn = tk.Button(brands_grid, text=b_name, command=lambda c=b_code, n=b_name: self.apply_corporate_brand(c, n),
                            bg="#1E1E1E", fg="#FFFFFF", font=("Consolas", 10, "bold"), relief="flat", pady=10, cursor="hand2")
            btn.grid(row=idx // 2, column=idx % 2, sticky="ew", padx=5, pady=5)
        brands_grid.columnconfigure(0, weight=1)
        brands_grid.columnconfigure(1, weight=1)

        self.corp_info = tk.Text(self.corp_frame, font=("Consolas", 9), bg="#161616", fg="#CCCCCC",
                                 relief="flat", padx=12, pady=12, height=7, state="disabled")
        self.corp_info.pack(fill="both", expand=True, padx=20, pady=(10, 15))
        self.write_corp_log("Совет: закинь родные картинки брендов в папку 'corporate_themes' (hp.jpg, asus.jpg, lenovo.jpg, msi.jpg, acer.jpg) рядом с программой — и кнопки выше будут ставить их в 1 клик!")

        self.switch_tab("wallpapers")

    def write_corp_log(self, text):
        self.corp_info.configure(state="normal")
        self.corp_info.delete("1.0", tk.END)
        self.corp_info.insert(tk.END, text)
        self.corp_info.configure(state="disabled")

    def apply_corporate_brand(self, code, name):
        if code == "restore":
            if os.path.exists(self.backup_path):
                ctypes.windll.user32.SystemParametersInfoW(20, 0, self.backup_path, 3)
                self.write_corp_log("[OK] Твои родные заводские обои из бэкапа успешно возвращены на рабочий стол!")
            else:
                self.write_corp_log("[!] Бэкап пока пуст — ты ещё не менял обои через UDEFI.")
            return

        tips = {
            "hp": "Бренд: HP (Hewlett-Packard)\n• Родные обои ищи в папке: corporate_themes/hp.jpg\n• Звук: ставь драйвер Realtek с панелью Beats Audio (для моделей 2010–2014).\n• Вход в UEFI при старте: клавиша Esc, затем F10.",
            "asus": "Бренд: ASUS (ROG / N-Series)\n• Родные обои ищи в папке: corporate_themes/asus.jpg\n• Звук: фирменная утилита ASUS SonicMaster / AudioWizard.\n• Вход в UEFI при старте: клавиша F2.",
            "lenovo": "Бренд: Lenovo (IdeaPad / ThinkPad)\n• Родные обои ищи в папке: corporate_themes/lenovo.jpg\n• Софт: Lenovo Vantage или Lenovo Energy Management (для защиты батареи).\n• Вход в UEFI при старте: клавиша F2 или кнопка Novo сбоку.",
            "msi": "Бренд: MSI Gaming\n• Родные обои ищи в папке: corporate_themes/msi.jpg\n• Охлаждение: кнопка Cooler Boost над клавиатурой или MSI Dragon Center.\n• Вход в UEFI при старте: клавиша Delete (Del).",
            "acer": "Бренд: Acer Aspire / Nitro\n• Родные обои ищи в папке: corporate_themes/acer.jpg\n• Софт: Acer Quick Access и Dolby Home Theater.\n• Вход в UEFI при старте: клавиша F2."
        }

        wp_file = os.path.abspath(os.path.join("corporate_themes", f"{code}.jpg"))
        if os.path.exists(wp_file):
            cur = get_current_wallpaper()
            if cur and os.path.exists(cur) and not os.path.exists(self.backup_path):
                shutil.copy2(cur, self.backup_path)
            ctypes.windll.user32.SystemParametersInfoW(20, 0, wp_file, 3)
            self.write_corp_log(f"[OK] Установлены заводские обои для {name}!\n\n{tips[code]}")
        else:
            self.write_corp_log(f"[i] Файл corporate_themes/{code}.jpg пока не найден, но вот памятка по твоему ноуту:\n\n{tips[code]}")

    def draw_default_art(self):
        self.preview_canvas.delete("all")
        self.preview_canvas.configure(bg="#1A0800")
        self.preview_canvas.create_oval(250, -50, 760, 290, fill="#B34700", outline="")
