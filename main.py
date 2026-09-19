import tkinter as tk
from tkinter import ttk, messagebox
from deep_translator import GoogleTranslator

class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tłumacz PL <-> EN")
        self.root.geometry("600x450")
        self.root.resizable(False, False)

        # Kierunek tłumaczenia
        self.source_lang = "pl"
        self.target_lang = "en"

        # Interfejs użytkownika
        main_frame = ttk.Frame(root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        direction_frame = ttk.Frame(main_frame)
        direction_frame.pack(fill=tk.X, pady=(0, 10))

        self.lang_label = ttk.Label(
            direction_frame, 
            text="Kierunek: Polski -> Angielski", 
            font=("Arial", 11, "bold")
        )
        self.lang_label.pack(side=tk.LEFT)

        swap_btn = ttk.Button(
            direction_frame, 
            text="Zamień języki ⇄", 
            command=self.swap_languages
        )
        swap_btn.pack(side=tk.RIGHT)

        ttk.Label(main_frame, text="Tekst wejściowy:").pack(anchor=tk.W)
        self.input_text = tk.Text(main_frame, height=6, font=("Arial", 10))
        self.input_text.pack(fill=tk.X, pady=(2, 10))

        translate_btn = ttk.Button(
            main_frame, 
            text="Tłumacz", 
            command=self.translate_text
        )
        translate_btn.pack(pady=5)

        ttk.Label(main_frame, text="Wynik tłumaczenia:").pack(anchor=tk.W)
        self.output_text = tk.Text(main_frame, height=6, font=("Arial", 10), state=tk.DISABLED)
        self.output_text.pack(fill=tk.X, pady=(2, 0))

    def swap_languages(self):
        if self.source_lang == "pl":
            self.source_lang = "en"
            self.target_lang = "pl"
            self.lang_label.config(text="Kierunek: Angielski -> Polski")
        else:
            self.source_lang = "pl"
            self.target_lang = "en"
            self.lang_label.config(text="Kierunek: Polski -> Angielski")

    def translate_text(self):
        text = self.input_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Brak tekstu", "Wprowadź tekst do przetłumaczenia.")
            return

        try:
            translated = GoogleTranslator(
                source=self.source_lang, 
                target=self.target_lang
            ).translate(text)

            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, translated)
            self.output_text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Błąd", f"Wystąpił błąd:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()
