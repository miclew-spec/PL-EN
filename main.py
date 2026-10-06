import os, re, threading, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
import textwrap
from deep_translator import GoogleTranslator

# Rozmiar A6 przy 300 DPI
W, H = int(148 / 25.4 * 300), int(105 / 25.4 * 300)

JEZYKI = {
    "Polski": "pl",
    "Angielski": "en",
    "Niemiecki": "de",
    "Kaszubski": "csb",
    "Śląski": "szl",
    "Hiszpański": "es",
    "Francuski": "fr",
    "Włoski": "it",
    "Ukraiński": "uk",
    "Czeski": "cs"
}

def nazwa_pliku(s):
    s = re.sub(r'[\\/*?:"<>|]', "", s)
    s = s.strip().replace(" ", "_")
    return s[:25] if s else "etykieta"

class TlumaczA6Auto:
    def __init__(self, r):
        self.r = r
        self.r.title("Generator Etykiet A6 - MultiLang")
        
        lbl_info = tk.Label(r, text="Etykiety A6: Wybierz języki tłumaczenia", font=("Arial", 11, "bold"))
        lbl_info.pack(pady=(10, 5))

        frame_lang = tk.Frame(r)
        frame_lang.pack(pady=5)

        tk.Label(frame_lang, text="Z języka:").grid(row=0, column=0, padx=5)
        self.combo_src = ttk.Combobox(frame_lang, values=list(JEZYKI.keys()), state="readonly", width=12)
        self.combo_src.set("Polski")
        self.combo_src.grid(row=0, column=1, padx=5)

        tk.Label(frame_lang, text="Na język:").grid(row=0, column=2, padx=5)
        self.combo_target = ttk.Combobox(frame_lang, values=list(JEZYKI.keys()), state="readonly", width=12)
        self.combo_target.set("Kaszubski")
        self.combo_target.grid(row=0, column=3, padx=5)

        self.t = tk.Text(r, height=8, width=55)
        self.t.pack(pady=10, padx=10)
        
        self.btn = tk.Button(r, text="GENERUJ ETYKIETY", command=self.start_process, bg="green", fg="white", font=("Arial", 10, "bold"))
        self.btn.pack(pady=5)
        
        self.status_lbl = tk.Label(r, text="Gotowy do pracy", font=("Arial", 9))
        self.status_lbl.pack()

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

    def start_process(self):
        threading.Thread(target=self.go, daemon=True).start()

    def go(self):
        dane = [d.strip() for d in self.t.get("1.0", "end").split('\n') if d.strip()]
        if not dane: 
            messagebox.showwarning("Brak tekstu", "Wpisz co najmniej jedno słowo lub frazę!")
            return
            
        folder_sciezka = filedialog.askdirectory(title="Wybierz folder do zapisu etykiet")
        if not folder_sciezka: 
            return

        src_lang = JEZYKI[self.combo_src.get()]
        target_lang = JEZYKI[self.combo_target.get()]

        self.btn.config(state=tk.DISABLED)
        self.p["value"] = 0
        self.p["maximum"] = len(dane)
        
        sukcesy = 0
        bledy = []

        for i, org_text in enumerate(dane, 1):
            translated_text = org_text
            
            # Próba tłumaczenia z obsługą błędu braków w sieci
            try:
                self.status_lbl.config(text=f"Tłumaczenie ({i}/{len(dane)}): {org_text[:20]}...")
                if src_lang != target_lang:
                    translated_text = GoogleTranslator(source=src_lang, target=target_lang).translate(org_text)
            except Exception as err:
                bledy.append(f"{org_text}: Błąd tłumaczania ({err})")
                translated_text = org_text # używa oryginalnego tekstu w razie braku połączenia

            try:
                img = Image.new("RGB", (W, H), "white")
                draw = ImageDraw.Draw(img)
                h2 = H // 2
                
                self.rysuj_sekcje_auto(draw, translated_text, (0, h2))
                self.rysuj_sekcje_auto(draw, org_text, (h2, H))
                
                draw.line([(80, h2), (W - 80, h2)], fill="black", width=6)
                draw.rectangle([20, 20, W - 20, H - 20], outline="black", width=10)
                
                nazwa = f"{i:03d}_{nazwa_pliku(org_text)}.png"
                sciezka_pliku = os.path.join(folder_sciezka, nazwa)
                
                img.save(sciezka_pliku, "PNG", dpi=(300, 300))
                sukcesy += 1
            except Exception as err_save:
                bledy.append(f"{org_text}: Błąd zapisu pliku ({err_save})")
            
            self.p["value"] = i
            
        self.btn.config(state=tk.NORMAL)
        self.status_lbl.config(text="Zakończono!")
        
        if sukcesy > 0:
            messagebox.showinfo("Sukces!", f"Pomyślnie wygenerowano {sukcesy} etykiet w folderze:\n{folder_sciezka}")
        
        if bledy:
            messagebox.showwarning("Uwaga!", f"Wystąpiły problemy z poniższymi pozycjami:\n\n" + "\n".join(bledy[:5]))

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x450")
    TlumaczA6Auto(root)
    root.mainloop()
