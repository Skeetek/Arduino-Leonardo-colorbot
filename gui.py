import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import datetime  # Pro práci s datem
import os
import hashlib
from keyauth import api

class LicenseAuth:
    def __init__(self):
        self.app_name = "ColorVant"
        self.owner_id = "PTCLv3Qp0x"
        self.secret = "f5b846a054f471471de5da09e5c360f747ca254d3173a08ef7bcf2a980563055"
        self.version = "1.0"

    def get_checksum(self, filename):
        md5_hash = hashlib.md5()
        with open(filename, "rb") as file:
            while chunk := file.read(8192):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    def check_license(self, key):
        try:
            keyauthapp = api(
                name=self.app_name,
                ownerid=self.owner_id,
                secret=self.secret,
                version=self.version,
                hash_to_check=self.get_checksum("main.py")
            )
            keyauthapp.license(key)
            if keyauthapp.check():
                return True, keyauthapp.user_data.expires
            else:
                return False, None
        except Exception as e:
            return False, None

class ColrVantApp:
    def __init__(self, master):
        self.master = master
        self.master.title("ColorVant | Key verify")
        self.master.iconbitmap("valo.ico")  # Přidání ikony
        self.master.configure(bg='black')  # Černé pozadí
        self.license_auth = LicenseAuth()

        # Získání rozměrů obrazovky
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()

        # Výpočet polohy na střed obrazovky
        x_position = (screen_width - 740) // 2
        y_position = (screen_height - 330) // 2

        # Nastavení polohy na střed obrazovky
        self.master.geometry('740x330+{}+{}'.format(x_position, y_position))  # Nastavení rozměrů

        # Změna barvy horní lišty okna podle systémového tématu
        self.master.attributes("-topmost", True)
        self.master.attributes("-topmost", False)

        # Vítejte zpráva
        self.welcome_label = tk.Label(master, text="Welcome to ColorVant", bg='black', fg='red', font=('Arial', 40, 'bold'))
        self.welcome_label.pack()
        self.welcome_label.pack(pady=(0, 50)) 
        
        # Popisek pro pole s klíčem
        self.key_label = tk.Label(master, text="Please enter your key:", bg='black', fg='white')
        self.key_label.pack()
        # Vstup pro klíč s červenými okraji, šedým pozadím, bílým textem, zvětšením a zaoblenými okraji
        self.key_entry = tk.Entry(master, bg='black', fg='white', bd=8, relief=tk.SOLID, font=('Arial', 14), highlightbackground='white', highlightcolor='red', highlightthickness=3)
        self.key_entry.pack(pady=(0, 50))  # Mezera pod vstupem pro klíč
        
        # Tlačítko pro ověření klíče
        self.verify_button = tk.Button(master, text="Verify Key", command=self.verify_key, font=('Arial', 12), bg='red', fg='white', bd=5, relief=tk.RAISED)
        self.verify_button.pack()

        # Malý bílý text a odkaz na web na spodní hraně okna
        self.footer_label = tk.Label(master, text="GUI v. A2.0 by", bg='black', fg='white', font=('Arial', 8), anchor=tk.SW)
        self.footer_label.pack(side=tk.LEFT, padx=5, pady=5, anchor=tk.SW)
        
        # Přidání odkazu na web
        self.web_link = tk.Label(master, text="Václav Pisinger", bg='black', fg='white', font=('Arial', 8, 'underline'), cursor="hand2")
        self.web_link.pack(side=tk.LEFT, padx=(0, 5), pady=5, anchor=tk.SW)
        self.web_link.bind("<Button-1>", self.open_web_link)  # Otevřít web na kliknutí

    def verify_key(self):
        key = self.key_entry.get()
        success, expiry_date = self.license_auth.check_license(key)
        if success:
            expiry_date_str = datetime.datetime.fromtimestamp(int(expiry_date)).strftime('%Y-%m-%d %H:%M:%S')
            messagebox.showinfo("Success", f"Key verified successfully!\nExpiry Date: {expiry_date_str}")
            self.open_colorant_window()
            self.master.destroy()
        else:
            messagebox.showerror("Error", "Invalid key")

    def open_colorant_window(self):
        pass  # Implement opening Colorant window here

    # Otevřít web
    def open_web_link(self, event):
        import webbrowser
        webbrowser.open_new("https://vaclavpi.github.io/")

# Vytvoření hlavního okna
root = tk.Tk()
app = ColrVantApp(root)
root.mainloop()
