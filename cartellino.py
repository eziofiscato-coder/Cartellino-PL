import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv, os

GIO_LIST = ["01 G","02 V","03 S","04 D","05 L","06 M","07 M","08 G","09 V","10 S",
            "11 D","12 L","13 M","14 M","15 G","16 V","17 S","18 D","19 L","20 M",
            "21 M","22 G","23 V","24 S","25 D","26 L","27 M","28 M","29 G","30 V","31 S"]
MOD_LIST = ["PM001","PM001","PM001","PMFSNL","PM001","PM001","PM001","PM001","PM001","PM001","PMFSNL","PM001","PM001","PM001","PM001","PM001","PM001","PMFSNL","PM001","PM001","PM001","PM001","PM001","PM001","PMFSNL","PM001","PM001","PM001","PM001","PM001","PM001"]
COLS = ["GIO.", "MOD.", "E", "U", "E", "U", "DOV", "EFF", "-/+", "STR", "TURNO", "B. P.", "GIUSTIFICATIVI"]

class CartellinoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Controllo Timbrature - Dati Giornalieri")
        self.root.geometry("1350x700")
        try:
            if os.path.exists("icona.ico"):
                self.root.iconbitmap("icona.ico")
        except:
            pass
        
        toolbar = tk.Frame(root, bg="#e5e5e5")
        toolbar.pack(fill="x")
        tk.Label(toolbar, text="Dati Giornalieri | Dati Periodo", bg="#e5e5e5", font=("Segoe UI", 10, "bold"), fg="#0078d7").pack(side="left", padx=10, pady=5)
        ttk.Button(toolbar, text="Controlla", command=self.controlla).pack(side="right", padx=5, pady=3)
        ttk.Button(toolbar, text="Salva CSV", command=self.salva_csv).pack(side="right", padx=5, pady=3)
        ttk.Button(toolbar, text="Salva Excel", command=self.salva_excel).pack(side="right", padx=5, pady=3)

        # tabella
        self.entries = []
        header_frame = tk.Frame(root)
        header_frame.pack()
        # headers
        for c,h in enumerate(COLS):
            tk.Label(header_frame, text=h, bg="#d9d9d9", font=("Segoe UI",8,"bold"), borderwidth=1, relief="solid", width=12 if c<12 else 28).grid(row=0,column=c, sticky="nsew", ipady=4)
        for r, gio in enumerate(GIO_LIST):
            row=[]
            for c, col in enumerate(COLS):
                if col=="GIO.":
                    fg="red" if " D" in gio else "black"
                    tk.Label(header_frame, text=gio, fg=fg, borderwidth=1, relief="solid").grid(row=r+1,column=c, sticky="nsew")
                    row.append(None)
                elif col=="MOD.":
                    tk.Label(header_frame, text=MOD_LIST[r], borderwidth=1, relief="solid").grid(row=r+1,column=c, sticky="nsew")
                    row.append(None)
                else:
                    e=tk.Entry(header_frame, justify="center")
                    if r==0 and c==2: e.insert(0,"06:52")
                    e.grid(row=r+1,column=c, sticky="nsew")
                    row.append(e)
            self.entries.append(row)

    def controlla(self):
        messagebox.showinfo("Controllo", "Controllo timbrature OK!")

    def salva_csv(self):
        path=filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not path: return
        with open(path,"w",newline="",encoding="utf-8") as f:
            import csv
            w=csv.writer(f, delimiter=";")
            w.writerow(COLS)
            for r, gio in enumerate(GIO_LIST):
                data=[gio, MOD_LIST[r]]+[ (self.entries[r][c].get() if self.entries[r][c] else "") for c in range(2,len(COLS))]
                w.writerow(data)
        messagebox.showinfo("Salvato", path)

    def salva_excel(self):
        try:
            import openpyxl
            path=filedialog.asksaveasfilename(defaultextension=".xlsx")
            if not path: return
            wb=openpyxl.Workbook()
            ws=wb.active
            ws.append(COLS)
            for r, gio in enumerate(GIO_LIST):
                ws.append([gio, MOD_LIST[r]]+[(self.entries[r][c].get() if self.entries[r][c] else "") for c in range(2,len(COLS))])
            wb.save(path)
            messagebox.showinfo("Salvato", path)
        except Exception as e:
            messagebox.showerror("Errore", str(e))

if __name__=="__main__":
    root=tk.Tk()
    CartellinoApp(root)
    root.mainloop()
