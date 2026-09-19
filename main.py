import os, re, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
import textwrap
from deep_translator import GoogleTranslator

# Rozmiar A6 przy 300 DPI
W, H = int(148/25.4*300), int(105/25.4*300)

def nazwa_pliku(s):
    s = re.sub(r'[\\/*?:"<>|]', "", s)
    return s.strip().replace(" ", "_")[:30]

class TlumaczA6PLEN:
    def __init__(self, r):
        self.r = r
        self.r.title("Generator Etykiet A6 (PL / EN)")
        
        # Nagłówek
        lbl_info = tk.Label(r, text="Etykiety A6: Polski + Angielski", font=("Arial", 11, "bold"))
        lbl_info.pack(pady=(10, 0))

        # Pole tekstowe do wklejania haseł
        self.t = tk.Text(r, height=10, width=50)
        self.t.pack(pady=10, padx=10)
        
        # Przycisk generowania
        self.btn = tk.Button(r, text="GENERUJ ETYKIETY (PL / EN)", command=self.go, bg="green", fg="white", font=("Arial", 10, "bold"))
        self.btn.pack(pady=5)
        
        # Pasek postępu
        self.p = ttk.Progressbar(r, length=300, mode='determinate')
        self.p.pack(pady=10)

    def rysuj_sekcje_auto(self, draw, tekst, y_range):
        font_size = 85
        try:
            fnt = ImageFont.truetype("arialbd.ttf", font_size)
        except:
            fnt = ImageFont.load_default()

        max_w = W - 300
        
        char_w = draw.textbbox((0,0), "W", font=fnt)[2]
        limit = max(1, int(max_w // char_w))
        
        linie = textwrap.wrap(tekst.upper(), width=limit)
        
        if len(linie) > 3:
            font_size = 65
            try: fnt = ImageFont.truetype("arialbd.ttf", font_size)
            except: fnt = ImageFont.load_default()
            limit = max(1, int(max_w // (char_w * 0.7)))
            linie = textwrap.wrap(tekst.upper(), width=limit)

        y_s, y_e = y_range
        line_spacing = 15
        bbox_sample = draw.textbbox((0,0), "Ay", font=fnt)
        h_single = bbox_sample[3] - bbox_sample[1]
        total_h = (h_single * len(linie)) + (line_spacing * (len(linie)-1))
        
        curr_y = y_s + (y_e - y_s - total_h) // 2

        for l in linie:
            b = draw.textbbox((0, 0), l, font=fnt)
            tw = b[2] - b[0]
            draw.text(((W - tw) // 2, curr_y), l, fill="black", font=fnt)
            curr_y += h_single + line_spacing

    def go(self):
        dane = [d.strip() for d in self.t.get("1.0", "end").split('\n') if d.strip()]
        if not dane: 
            messagebox.showwarning("Brak tekstu", "Wpisz co najmniej jedno słowo lub frazę!")
            return
            
        f = filedialog.askdirectory()
        if not f: return
        
        cel = os.path.join(f, "ETYKIETY_PL_EN")
        os.makedirs(cel, exist_ok=True)
        self.p["maximum"] = len(dane)
        
        # Tłumacz z Polskiego na Angielski
        translator = GoogleTranslator(source='pl', target='en')

        for i, pl in enumerate(dane, 1):
            try:
                en = translator.translate(pl)
                
                img = Image.new("RGB", (W, H), "white")
                draw = ImageDraw.Draw(img)
                h2 = H // 2
                
                # Rysowanie 2 sekcji: Angielski na górze, Polski na dole
                self.rysuj_sekcje_auto(draw, en, (0, h2))
                self.rysuj_sekcje_auto(draw, pl, (h2, H))
                
                # Środkowa linia podziału i ramka zewnętrzna
                draw.line([(80, h2), (W-80, h2)], fill="black", width=6)
                draw.rectangle([20, 20, W-20, H-20], outline="black", width=10)
                
                img.save(os.path.join(cel, f"{i:03d}_{nazwa_pliku(pl)}.png"), dpi=(300, 300))
            except Exception as e:
                print(f"Błąd dla {pl}: {e}")
            
            self.p["value"] = i
            self.r.update()
            
        messagebox.showinfo("OK", "Gotowe! Sprawdź folder ETYKIETY_PL_EN.")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("450x380")
    TlumaczA6PLEN(root)
    root.mainloop()
