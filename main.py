import os, re, time, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
import textwrap
from deep_translator import GoogleTranslator

# Rozmiar A6 przy 300 DPI
W, H = int(148/25.4*300), int(105/25.4*300)

def nazwa_pliku(s):
    s = re.sub(r'[\\/*?:"<>|]', "", s)
    s = s.strip().replace(" ", "_")
    return s[:25] if s else "etykieta"

class TlumaczA6PLEN:
    def __init__(self, r):
        self.r = r
        self.r.title("Generator Etykiet A6 (PL / EN)")
        
        lbl_info = tk.Label(r, text="Etykiety A6: Polski + Angielski", font=("Arial", 11, "bold"))
        lbl_info.pack(pady=(10, 0))

        self.t = tk.Text(r, height=10, width=50)
        self.t.pack(pady=10, padx=10)
        
        self.btn = tk.Button(r, text="GENERUJ ETYKIETY (PL / EN)", command=self.go, bg="green", fg="white", font=("Arial", 10, "bold"))
        self.btn.pack(pady=5)
        
        self.p = ttk.Progressbar(r, length=300, mode='determinate')
        self.p.pack(pady=10)

    def pobierz_czcionke(self, font_size):
        sciezki_czcionek = [
            "arialbd.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
            "C:\\Windows\\Fonts\\arial.ttf"
        ]
        for path in sciezki_czcionek:
            try:
                return ImageFont.truetype(path, font_size)
            except Exception:
                continue
        return ImageFont.load_default()

    def rysuj_sekcje_auto(self, draw, tekst, y_range):
        font_size = 85
        fnt = self.pobierz_czcionke(font_size)

        max_w = W - 300
        char_w = draw.textbbox((0, 0), "W", font=fnt)[2]
        limit = max(1, int(max_w // char_w))
        
        linie = textwrap.wrap(tekst.upper(), width=limit)
        
        if len(linie) > 3:
            font_size = 60
            fnt = self.pobierz_czcionke(font_size)
            limit = max(1, int(max_w // (char_w * 0.7)))
            linie = textwrap.wrap(tekst.upper(), width=limit)

        y_s, y_e = y_range
        line_spacing = 15
        bbox_sample = draw.textbbox((0, 0), "Ay", font=fnt)
        h_single = bbox_sample[3] - bbox_sample[1]
        total_h = (h_single * len(linie)) + (line_spacing * (len(linie) - 1))
        
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
            
        folder_sciezka = filedialog.askdirectory(title="Wybierz folder do zapisu etykiet")
        if not folder_sciezka: 
            return
        
        self.p["value"] = 0
        self.p["maximum"] = len(dane)
        
        translator = GoogleTranslator(source='pl', target='en')
        sukcesy = 0

        for i, pl in enumerate(dane, 1):
            en = None
            # Próba tłumaczenia z bezpiecznym powtarzaniem w razie limitu
            for proba in range(3):
                try:
                    en = translator.translate(pl)
                    break
                except Exception:
                    time.sleep(1.5) # Czekaj 1.5 s przed kolejną próbą

            if not en:
                messagebox.showerror("Błąd limitu", f"Google zablokowało zapytanie dla: '{pl}'. Odczekaj chwilę i spróbuj ponownie.")
                continue

            try:
                img = Image.new("RGB", (W, H), "white")
                draw = ImageDraw.Draw(img)
                h2 = H // 2
                
                self.rysuj_sekcje_auto(draw, en, (0, h2))
                self.rysuj_sekcje_auto(draw, pl, (h2, H))
                
                draw.line([(80, h2), (W - 80, h2)], fill="black", width=6)
                draw.rectangle([20, 20, W - 20, H - 20], outline="black", width=10)
                
                nazwa = f"{i:03d}_{nazwa_pliku(pl)}.png"
                sciezka_pliku = os.path.join(folder_sciezka, nazwa)
                
                img.save(sciezka_pliku, "PNG", dpi=(300, 300))
                sukcesy += 1
            except Exception as e:
                print(f"Błąd tworzenia obrazu dla {pl}: {e}")
            
            self.p["value"] = i
            self.r.update()
            time.sleep(0.5) # Odstęp 0.5 sekundy między etykietami, aby uniknąć blokady
            
        if sukcesy > 0:
            messagebox.showinfo("Sukces!", f"Pomyślnie wygenerowano {sukcesy} etykiet w folderze:\n{folder_sciezka}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("450x380")
    TlumaczA6PLEN(root)
    root.mainloop()
