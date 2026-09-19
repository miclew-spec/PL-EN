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

class TlumaczA6:
    def __init__(self, r):
        self.r = r
        self.r.title("Generator Etykiet A6")
        
        frame_lang = tk.Frame(r)
        frame_lang.pack(pady=10, padx=10)
        
        tk.Label(frame_lang, text="Język 1:").grid(row=0, column=0, pady=2)
        self.lang1 = tk.StringVar(value="de")
        tk.Entry(frame_lang, textvariable=self.lang1, width=10).grid(row=0, column=1)
        
        tk.Label(frame_lang, text="Język 2:").grid(row=1, column=0, pady=2)
        self.lang2 = tk.StringVar(value="en")
        tk.Entry(frame_lang, textvariable=self.lang2, width=10).grid(row=1, column=1)

        self.t = tk.Text(r, height=10, width=50)
        self.t.pack(pady=10, padx=10)
        
        self.btn = tk.Button(r, text="GENERUJ ETYKIETY", command=self.go, bg="green", fg="white", font=("Arial", 10, "bold"))
        self.btn.pack(pady=10)
        
        self.p = ttk.Progressbar(r, length=300, mode='determinate')
        self.p.pack(pady=10)

    def rysuj_sekcje_auto(self, draw, tekst, y_range):
        font_size = 80
        try:
            fnt = ImageFont.truetype("arialbd.ttf", font_size)
        except:
            fnt = ImageFont.load_default()

        max_w = W - 300
        
        char_w = draw.textbbox((0,0), "W", font=fnt)[2]
        limit = max(1, int(max_w // char_w))
        
        linie = textwrap.wrap(tekst.upper(), width=limit)
        
        if len(linie) > 3:
            font_size = 60
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
        if not dane: return
        f = filedialog.askdirectory()
        if not f: return
        
        cel = os.path.join(f, "ETYKIETY")
        os.makedirs(cel, exist_ok=True)
        self.p["maximum"] = len(dane)
        
        t1 = GoogleTranslator(source='pl', target=self.lang1.get())
        t2 = GoogleTranslator(source='pl', target=self.lang2.get())

        for i, pl in enumerate(dane, 1):
            try:
                txt1 = t1.translate(pl)
                txt2 = t2.translate(pl)
                
                img = Image.new("RGB", (W, H), "white")
                draw = ImageDraw.Draw(img)
                h3 = H // 3
                
                self.rysuj_sekcje_auto(draw, txt1, (0, h3))
                self.rysuj_sekcje_auto(draw, txt2, (h3, 2*h3))
                self.rysuj_sekcje_auto(draw, pl, (2*h3, H))
                
                draw.line([(80, h3), (W-80, h3)], fill="black", width=5)
                draw.line([(80, 2*h3), (W-80, 2*h3)], fill="black", width=5)
                draw.rectangle([20, 20, W-20, H-20], outline="black", width=10)
                
                img.save(os.path.join(cel, f"{i:03d}_{nazwa_pliku(pl)}.png"), dpi=(300, 300))
            except: pass
            
            self.p["value"] = i
            self.r.update()
        messagebox.showinfo("OK", "Gotowe! Sprawdź folder ETYKIETY.")

if __name__ == "__main__":
    root = tk.Tk(); TlumaczA6(root); root.mainloop()
