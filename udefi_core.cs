using System;
using System.Management;
using System.Text;

class UdefiCore {
    static void Main() {
        Console.OutputEncoding = Encoding.UTF8;
        Console.WriteLine("=== ГЛУБОКИЙ РЕНТГЕН UDEFI (C# HYBRID ENGINE) ===\n");

        try {
            using (var searcher = new ManagementObjectSearcher("SELECT Manufacturer, Product FROM Win32_BaseBoard")) {
                foreach (ManagementObject obj in searcher.Get()) {
                    Console.WriteLine("• Платформа / Плата : " + obj["Manufacturer"] + " (" + obj["Product"] + ")");
                }
            }
        } catch { Console.WriteLine("• Платформа / Плата : Не определено"); }

        try {
            using (var searcher = new ManagementObjectSearcher("SELECT Name FROM Win32_Processor")) {
                foreach (ManagementObject obj in searcher.Get()) {
                    string cpu = obj["Name"].ToString().Trim();
                    string verdict = (cpu.Contains("HQ") || cpu.Contains("MQ") || cpu.Contains("H ") || cpu.Contains("M "))
                        ? "[+] МОЩНЫЙ ПРОЦЕССОР (полноценный чип)"
                        : (cpu.Contains("U") ? "[!] ЭНЕРГОСБЕРЕГАЮЩИЙ ЧИП (U-серия)" : "[i] Стандартный процессор");
                    Console.WriteLine("• Процессор         : " + cpu);
                    Console.WriteLine("  Вердикт           : " + verdict);
                }
            }
        } catch { Console.WriteLine("• Процессор         : Не определено"); }

        try {
            using (var searcher = new ManagementObjectSearcher("SELECT Name, ConfigManagerErrorCode FROM Win32_VideoController")) {
                foreach (ManagementObject obj in searcher.Get()) {
                    string name = obj["Name"].ToString();
                    int code = Convert.ToInt32(obj["ConfigManagerErrorCode"]);
                    string status = code == 0 ? "-> [OK] Работает чисто" : (code == 43 ? "-> [!!!] КОД 43 (ВОЗМОЖЕН ОТВАЛ ЧИПА!)" : "-> [!] Ошибка код " + code);
                    Console.WriteLine("• Видеоадаптер      : " + name + " " + status);
                }
            }
        } catch { Console.WriteLine("• Видеоадаптер      : Не определено"); }

        try {
            using (var searcher = new ManagementObjectSearcher("SELECT TotalPhysicalMemory FROM Win32_ComputerSystem")) {
                foreach (ManagementObject obj in searcher.Get()) {
                    double gb = Math.Round(Convert.ToDouble(obj["TotalPhysicalMemory"]) / (1024 * 1024 * 1024));
                    Console.WriteLine("• Оперативная память: " + gb + " ГБ");
                }
            }
        } catch { Console.WriteLine("• Оперативная память: Не определено"); }

        try {
            using (var searcher = new ManagementObjectSearcher(@"root\WMI", "SELECT CurrentTemperature FROM MSAcpi_ThermalZoneTemperature")) {
                foreach (ManagementObject obj in searcher.Get()) {
                    double tempC = Math.Round((Convert.ToDouble(obj["CurrentTemperature"]) / 10.0) - 273.15, 1);
                    Console.WriteLine("• Температура зоны  : " + tempC + " °C" + (tempC > 80 ? " [!] ГОРЯЧО!" : " [OK]"));
                    break;
                }
            }
        } catch { Console.WriteLine("• Температура зоны  : Датчик закрыт BIOS"); }
    }
}
