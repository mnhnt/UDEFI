import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import platform
import ctypes
import shutil
import traceback
import os

def get_ps(cmd):
    try:
        full_cmd = f'powershell -NoProfile -Command "{cmd}"'
        out = subprocess.check_output(full_cmd, shell=True, stderr=subprocess.DEVNULL).decode("utf-8", errors="ignore").strip()
        return out if out else "Не определено"
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
        self.root.title("UDEFI // Темы, Обои и Рентген Железа v1.3")
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

        self.info_frame = tk.Frame(self.content)
        self.info_box = tk.Text(self.info_frame, font=("Consolas", 10), relief="flat", padx=15, pady=15, height=15, state="disabled")
        self.info_box.pack(fill="both", expand=True, padx=20, pady=10)

        self.scan_btn = tk.Button(self.info_frame, text="ЗАПУСТИТЬ ПРОВЕРКУ ЖЕЛЕЗА И ПЛАТЫ", command=self.scan_hardware,
                                  font=("Consolas", 11, "bold"), relief="flat", pady=8, cursor="hand2")
        self.scan_btn.pack(fill="x", padx=20, pady=(0, 15))

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
        self.preview_canvas.create_oval(320, 10, 720, 250, fill="#FF6D00", outline="")
self.preview_canvas.create_polygon(0, 130, 220, 80, 460, 170, 680, 100, 680, 220, 0, 220, fill="#0A0A0A", smooth=True)
self.preview_canvas.create_polygon(0, 170, 280, 130, 500, 200, 680, 150, 680, 220, 0, 220, fill="#050505", smooth=True)
self.preview_canvas.create_text(610, 196, text="UDEFI // DNS", fill="#FF9E40", font=("Consolas", 12, "bold"))
self.preview_canvas.create_text(340, 40, text="ФИРМЕННЫЙ СТИЛЬ СООБЩЕСТВА (2010–2014+)", fill="#FFFFFF", font=("Consolas", 10, "bold"))
def choose_wallpaper(self):
path = filedialog.askopenfilename(
title="Выбери картинку для рабочего стола",
filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp")]
)
if path:
self.selected_wp = os.path.abspath(path)
self.wp_status.configure(text=f"Выбран файл: {os.path.basename(path)}")
def set_wallpaper(self):
if not self.selected_wp:
messagebox.showinfo("UDEFI", "Сначала выбери картинку кнопкой «Выбрать файл обоев»!")
return
try:
cur = get_current_wallpaper()
if cur and os.path.exists(cur) and not os.path.exists(self.backup_path):
shutil.copy2(cur, self.backup_path)
ctypes.windll.user32.SystemParametersInfoW(20, 0, self.selected_wp, 3)
self.wp_status.configure(text="[OK] Новые обои установлены! (Старые сохранены в бэкап)")
except Exception as e:
messagebox.showerror("Ошибка", f"Не удалось применить обои: {e}")
def switch_tab(self, tab):
self.active_tab = tab
self.wp_frame.pack_forget()
self.info_frame.pack_forget()
self.corp_frame.pack_forget()
if tab == "wallpapers":
self.wp_frame.pack(fill="both", expand=True)
elif tab == "info":
self.info_frame.pack(fill="both", expand=True)
else:
self.corp_frame.pack(fill="both", expand=True)
self.apply_theme(self.current_theme)
def apply_theme(self, name):
self.current_theme = name
t = self.themes[name]
for w in [self.root, self.header, self.btn_frame, self.nav_frame, self.content,
self.wp_frame, self.wp_btns, self.info_frame, self.corp_frame, self.brands_grid]:
w.configure(bg=t["bg"])
self.title_lbl.configure(bg=t["bg"], fg=t["accent"])
self.wp_status.configure(bg=t["bg"], fg="#AAAAAA")
self.corp_title.configure(bg=t["bg"], fg=t["text"])
self.info_box.configure(bg=t["panel"], fg=t["text"])
self.corp_info.configure(bg=t["panel"], fg="#CCCCCC")
btn_fg = "#000000" if name != "red" else "#FFFFFF"
self.choose_btn.configure(bg=t["panel"], fg=t["text"])
self.apply_wp_btn.configure(bg=t["accent"], fg=btn_fg)
self.scan_btn.configure(bg=t["accent"], fg=btn_fg)
self.tab_wp_btn.configure(bg=t["accent"] if self.active_tab == "wallpapers" else t["panel"],
fg=btn_fg if self.active_tab == "wallpapers" else t["text"])
self.tab_info_btn.configure(bg=t["accent"] if self.active_tab == "info" else t["panel"],
fg=btn_fg if self.active_tab == "info" else t["text"])
self.tab_corp_btn.configure(bg=t["accent"] if self.active_tab == "corp" else t["panel"],
fg=btn_fg if self.active_tab == "corp" else t["text"])
def scan_hardware(self):
self.info_box.configure(state="normal")
self.info_box.delete("1.0", tk.END)
self.info_box.insert(tk.END, "Сканирую железо ноутбука (подожди 2–3 секунды)...\n")
self.info_box.configure(state="disabled")
self.root.update()
board_maker = get_ps("(Get-CimInstance Win32_BaseBoard).Manufacturer")
board_prod = get_ps("(Get-CimInstance Win32_BaseBoard).Product")
cpu_name = get_ps("(Get-CimInstance Win32_Processor).Name")
gpu_name = get_ps("(Get-CimInstance Win32_VideoController).Name")
ram_bytes = get_ps("(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory")
try:
ram_gb = f"{round(int(ram_bytes) / (1024**3))} ГБ"
except Exception:
ram_gb = "Не определено"
if any(tag in cpu_name.upper() for tag in ["HQ", "MQ", "H ", "M "]):
cpu_verdict = "[+] МОЩНЫЙ ПРОЦЕССОР (полноценный чип)"
elif "U" in cpu_name.upper():
cpu_verdict = "[!] ЭНЕРГОСБЕРЕГАЮЩИЙ ЧИП (U-серия)"
else:
cpu_verdict = "[i] Стандартный процессор"
report = (
f"=== ПАСПОРТ СИСТЕМЫ UDEFI ===\n\n"
f"• Платформа / Плата : {board_maker} ({board_prod})\n"
f"• Процессор         : {cpu_name}\n"
f"  Вердикт           : {cpu_verdict}\n"
f"• Видеокарта        : {gpu_name}\n"
f"• Оперативная память: {ram_gb}\n"
f"• Система           : {platform.system()} {platform.release()}\n\n"
f"=== СОВЕТ UDEFI ===\n"
f"На вкладке 'Народный стиль' можно поставить обои сообщества,\n"
f"а на вкладке 'Для корпоративных' — вернуть заводской стиль брендов."
)
self.info_box.configure(state="normal")
self.info_box.delete("1.0", tk.END)
self.info_box.insert(tk.END, report)
self.info_box.configure(state="disabled")
if name == "main":
try:
root = tk.Tk()
app = UDEFIApp(root)
root.mainloop()
except Exception:
messagebox.showerror("Ошибка запуска UDEFI", traceback.format_exc())
