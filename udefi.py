import webview
import subprocess
import webbrowser
import tempfile
import ctypes
import shutil
import re
import sys
import os
from PIL import Image, ImageDraw

def resource_path(rel_path):
    base = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base, rel_path)

def get_cur_wp():
    buf = ctypes.create_unicode_buffer(512)
    ctypes.windll.user32.SystemParametersInfoW(115, 512, buf, 0)
    return buf.value

def get_screen_size():
    try:
        ctypes.windll.user32.SetProcessDPIAware()
        w = ctypes.windll.user32.GetSystemMetrics(0)
        h = ctypes.windll.user32.GetSystemMetrics(1)
        return (w, h) if (w > 640 and h > 480) else (1920, 1080)
    except Exception:
        return (1920, 1080)

class Api:
    def __init__(self):
        self.backup = os.path.abspath("backup_original_wallpaper.jpg")

    def _save_backup(self):
        cur = get_cur_wp()
        if cur and os.path.exists(cur) and not os.path.exists(self.backup):
            shutil.copy2(cur, self.backup)

    def open_portal(self, target):
        if target == "site":
            webbrowser.open("https://adderly.top")
        elif target == "youtube":
            webbrowser.open("https://youtube.com")

    def open_tool(self, tool):
        local_bins = {
            "cpuz": resource_path(os.path.join("tools", "cpuz.exe")),
            "gpuz": resource_path(os.path.join("tools", "gpuz.exe")),
            "cdi": resource_path(os.path.join("tools", "cdi.exe"))
        }
        urls = {
            "cpuz": "https://cpuid.com",
            "gpuz": "https://techpowerup.com",
            "cdi": "https://crystalmark.info",
            "furmark": "https://geeks3d.com"
        }
        bin_path = local_bins.get(tool)
        if bin_path and os.path.exists(bin_path) and os.path.getsize(bin_path) > 100000:
            subprocess.Popen([bin_path], shell=True)
        elif tool in urls:
            webbrowser.open(urls[tool])

    def system_boost(self):
        try:
            subprocess.run("powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            tmp = tempfile.gettempdir()
            cleaned = 0
            for item in os.listdir(tmp):
                p = os.path.join(tmp, item)
                try:
                    if os.path.isfile(p):
                        os.remove(p)
                        cleaned += 1
                except Exception:
                    pass
            return f"[BOOST] Включена высокая производительность! Удалено временных файлов: {cleaned}"
        except Exception as e:
            return f"[!] Ошибка буста: {e}"

    def gen_wp(self, theme):
        w, h = get_screen_size()
        img = Image.new("RGB", (w, h), "#080808")
        draw = ImageDraw.Draw(img)
        cols = {
            "orange": [(110, 35, 0), (190, 75, 0), (255, 109, 0)],
            "red":    [(90, 0, 10), (160, 0, 20), (213, 0, 0)],
            "black":  [(25, 25, 25), (45, 45, 45), (80, 80, 80)]
        }
        c1, c2, c3 = cols.get(theme, cols["orange"])

        draw.ellipse([int(w*0.34), int(-h*0.14), int(w*1.12), int(h*1.15)], fill=c1)
        draw.ellipse([int(w*0.44), int(-h*0.04), int(w*1.04), int(h*1.02)], fill=c2)
        draw.ellipse([int(w*0.54), int(h*0.05), int(w*0.96), int(h*0.88)], fill=c3)

        wave1 = [(0, int(h*0.60)), (int(w*0.31), int(h*0.39)), (int(w*0.68), int(h*0.76)), (w, int(h*0.48)), (w, h), (0, h)]
        wave2 = [(0, int(h*0.76)), (int(w*0.39), int(h*0.57)), (int(w*0.75), int(h*0.87)), (w, int(h*0.67)), (w, h), (0, h)]
        draw.polygon(wave1, fill="#0B0B0B")
        draw.polygon(wave2, fill="#050505")

        out = os.path.abspath(f"udefi_wp_{theme}_{w}x{h}.png")
        img.save(out)
        self._save_backup()
        ctypes.windll.user32.SystemParametersInfoW(20, 0, out, 3)
        return f"[OK] Обои ({w}x{h}, {theme.upper()}) сгенерированы под твой экран!"

    def pick_wp(self):
        res = window.create_file_dialog(webview.OPEN_DIALOG, file_types=('Изображения (*.jpg;*.png;*.bmp)',))
        if res:
            self._save_backup()
            ctypes.windll.user32.SystemParametersInfoW(20, 0, res[0], 3)
            return f"[OK] Установлены обои: {os.path.basename(res[0])}"
        return ""

    def restore_wp(self):
        if os.path.exists(self.backup):
            ctypes.windll.user32.SystemParametersInfoW(20, 0, self.backup, 3)
            return "[OK] Родные заводские обои возвращены из бэкапа!"
        return "[!] Бэкап пока пуст."

    def sync_win(self, theme):
        cols = {"orange": 0x00006DFF, "red": 0x000000D5, "black": 0x00333333}
        c = cols.get(theme, 0x00006DFF)
        cmd = f'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\DWM" -Name "AccentColor" -Value {c}; Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" -Name "ColorPrevalence" -Value 1'
        subprocess.run(f'powershell -NoProfile -Command "{cmd}"', shell=True, stderr=subprocess.DEVNULL)
        return "[OK] Акцентный цвет окон Windows синхронизирован!"

    def run_csharp_scan(self):
        core = resource_path("udefi_core.exe")
        if not os.path.exists(core):
            return "[!] Модуль udefi_core.exe не найден."
        out = subprocess.check_output([core], creationflags=0x08000000).decode("utf-8", errors="ignore")
        return out

    def corp_cmd(self, code):
        if code == "battery":
            rep = os.path.abspath("bat_rep.html")
            subprocess.run(f'powercfg /batteryreport /output "{rep}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(rep):
                with open(rep, "r", encoding="utf-8", errors="ignore") as f:
                    html = f.read()
                os.remove(rep)
                caps = re.findall(r"(\d[\d\s,]+)\s*mWh", html)
                if len(caps) >= 2:
                    d = int(re.sub(r"\D", "", caps[0]))
                    cur = int(re.sub(r"\D", "", caps[1]))
                    wear = max(0, min(100, round((1 - (cur / d)) * 100)))
                    return f"=== ТЕСТ АКБ (ДЛЯ КОРПОРАТИВНЫХ) ===\n• Заводская ёмкость: {d} mWh\n• Текущая ёмкость  : {cur} mWh\n• Износ батареи    : {wear}%"
            return "[!] Контроллер батареи не найден (возможно, АКБ снята)."

        tips = {
            "hp": "HP Pavilion / Envy:\n• Положи родной фон в corporate_themes/hp.jpg\n• Звук: Beats Audio | Вход в UEFI: Esc -> F10",
            "asus": "ASUS ROG / N-Series:\n• Положи родной фон в corporate_themes/asus.jpg\n• Звук: SonicMaster | Вход в UEFI: F2",
            "lenovo": "Lenovo IdeaPad / ThinkPad:\n• Положи родной фон в corporate_themes/lenovo.jpg\n• Софт: Lenovo Vantage | Вход в UEFI: F2 / Novo",
            "msi": "MSI Gaming:\n• Положи родной фон в corporate_themes/msi.jpg\n• Охлаждение: Cooler Boost | Вход в UEFI: Del",
            "acer": "Acer Aspire / Predator:\n• Положи родной фон в corporate_themes/acer.jpg\n• Звук: Dolby Home Theater | Вход в UEFI: F2"
        }
        wp = os.path.abspath(os.path.join("corporate_themes", f"{code}.jpg"))
        if os.path.exists(wp):
            self._save_backup()
            ctypes.windll.user32.SystemParametersInfoW(20, 0, wp, 3)
            return f"[OK] Заводские обои установлены!\n\n{tips.get(code, '')}"
        return f"[i] Файл corporate_themes/{code}.jpg не найден.\n\n{tips.get(code, '')}"

if __name__ == "__main__":
    api = Api()
    window = webview.create_window("UDEFI // All-in-One v0.2.2-beta", resource_path("ui.html"), js_api=api, width=780, height=550, resizable=False)
    webview.start()
