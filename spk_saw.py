import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np

class SAW_HP_Selection:
    def __init__(self):
        self.hp_data = pd.DataFrame()
        self.weights = {
            'RAM (GB)': 0.25,
            'Storage (GB)': 0.20,
            'Harga (juta)': 0.25,
            'Kamera (MP)': 0.15,
            'Baterai (mAh)': 0.15
        }
        self.criteria_types = {
            'RAM (GB)': 'benefit',
            'Storage (GB)': 'benefit',
            'Harga (juta)': 'cost',
            'Kamera (MP)': 'benefit',
            'Baterai (mAh)': 'benefit'
        }
        self.normalized_data = None
        self.scores = None
    
    def load_data(self, data):
        # Konversi ke numeric
        for crit in self.weights.keys():
            # Pastikan kolom ada sebelum mencoba mengkonversi
            if crit in data.columns:
                data[crit] = pd.to_numeric(data[crit], errors='coerce')
                if data[crit].isnull().any():
                    raise ValueError(f"Data {crit} tidak valid")
            else:
                raise ValueError(f"Kolom '{crit}' tidak ditemukan dalam data.")
        self0.hp_data = data
    
    def normalize_data(self):
        if self.hp_data.empty:
            raise ValueError("Tidak ada data HP untuk dinormalisasi.")
        
        normalized_df = self.hp_data[['Nama HP']].copy() # Salin kolom Nama HP
        
        for criterion, crit_type in self.criteria_types.items():
            if criterion not in self.hp_data.columns:
                raise ValueError(f"Kriteria '{criterion}' tidak ditemukan dalam data HP.")

            values = self.hp_data[criterion]
            
            if crit_type == 'benefit':
                max_val = values.max()
                if max_val == 0: # Hindari pembagian dengan nol jika semua nilai 0
                    normalized_df[criterion] = 0
                else:
                    normalized_df[criterion] = values / max_val
            elif crit_type == 'cost':
                min_val = values.min()
                if min_val == 0: 
                    normalized_df[criterion] = values.apply(lambda x: min_val / x if x != 0 else 1)
                else:
                    normalized_df[criterion] = min_val / values
            else:
                raise ValueError(f"Tipe kriteria tidak valid: {crit_type}")
        
        self.normalized_data = normalized_df
        return normalized_df

    def calculate_scores(self):
        if self.normalized_data is None or self.normalized_data.empty:
            raise ValueError("Data belum dinormalisasi. Silakan normalisasi data terlebih dahulu.")
        
        scores = {}
        for index, row in self.normalized_data.iterrows():
            hp_name = row['Nama HP']
            score = 0
            for criterion, weight in self.weights.items():
                if criterion in row: # Pastikan kriteria ada di baris
                    score += row[criterion] * weight
                else:
                    print(f"Peringatan: Kriteria '{criterion}' tidak ditemukan di baris untuk '{hp_name}'.")
            scores[hp_name] = score
            
        self.scores = pd.DataFrame(list(scores.items()), columns=['Nama HP', 'Skor SAW'])
        self.scores = self.scores.sort_values(by='Skor SAW', ascending=False).reset_index(drop=True)
        return self.scores

class SAW_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SPK Pemilihan HP Terbaik (Metode SAW)")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        self.saw = SAW_HP_Selection()
        self.criteria = list(self.saw.weights.keys())
        
        self.setup_ui()
        self.update_treeview() # Panggil ini untuk mengisi tabel jika ada data awal

    def setup_ui(self):
        # Notebook dengan 2 tab
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)
        
        # Tab Input Data
        self.tab_input = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_input, text='Input Data HP')
        self.setup_input_tab()
        
        # Tab Hasil
        self.tab_result = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_result, text='Hasil Rekomendasi')
        self.setup_result_tab()
    
    def setup_input_tab(self):
        # Frame utama
        main_frame = ttk.Frame(self.tab_input)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Frame input data
        input_frame = ttk.LabelFrame(main_frame, text="Input Spesifikasi HP", padding=10)
        input_frame.pack(fill='x', pady=5)
        
        # Input fields
        ttk.Label(input_frame, text="Nama HP:").grid(row=0, column=0, sticky='w', pady=5)
        self.entry_nama = ttk.Entry(input_frame)
        self.entry_nama.grid(row=0, column=1, pady=5, padx=5, sticky='ew')
        
        self.entry_criteria = {}
        for i, crit in enumerate(self.criteria, 1):
            ttk.Label(input_frame, text=f"{crit}:").grid(row=i, column=0, sticky='w', pady=5)
            self.entry_criteria[crit] = ttk.Entry(input_frame)
            self.entry_criteria[crit].grid(row=i, column=1, pady=5, padx=5, sticky='ew')
        
        # Konfigurasi kolom 1 untuk melebar
        input_frame.grid_columnconfigure(1, weight=1)

        # Frame tombol
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=len(self.criteria)+1, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, 
                   text="Tambah HP", 
                   command=self.add_hp_data).pack(side='left', padx=5)
        
        ttk.Button(button_frame,
                   text="Hapus Terpilih",
                   command=self.delete_selected_hp).pack(side='left', padx=5)
        
        # Tabel data HP
        tree_frame = ttk.LabelFrame(main_frame, text="Daftar HP", padding=10)
        tree_frame.pack(fill='both', expand=True, pady=5)
        
        self.tree_hp = ttk.Treeview(tree_frame, columns=['Nama HP']+self.criteria, show='headings')
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_hp.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree_hp.xview)
        self.tree_hp.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree_hp.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Set heading
        for col in ['Nama HP'] + self.criteria:
            self.tree_hp.heading(col, text=col)
            self.tree_hp.column(col, width=100)
        
        # Tombol Hitung di bagian bawah
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill='x', pady=10)
        
        ttk.Button(bottom_frame,
                   text="HITUNG REKOMENDASI HP TERBAIK",
                   command=self.calculate_recommendation,
                   style='Accent.TButton').pack(pady=10, ipadx=20, ipady=10)

    def setup_result_tab(self):
        # Frame utama untuk tab hasil
        main_frame = ttk.Frame(self.tab_result)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Tabel hasil rekomendasi
        result_tree_frame = ttk.LabelFrame(main_frame, text="Peringkat HP Berdasarkan Metode SAW", padding=10)
        result_tree_frame.pack(fill='both', expand=True, pady=5)

        self.tree_result = ttk.Treeview(result_tree_frame, columns=['Peringkat', 'Nama HP', 'Skor SAW'], show='headings')
        vsb_result = ttk.Scrollbar(result_tree_frame, orient="vertical", command=self.tree_result.yview)
        hsb_result = ttk.Scrollbar(result_tree_frame, orient="horizontal", command=self.tree_result.xview)
        self.tree_result.configure(yscrollcommand=vsb_result.set, xscrollcommand=hsb_result.set)

        self.tree_result.grid(row=0, column=0, sticky='nsew')
        vsb_result.grid(row=0, column=1, sticky='ns')
        hsb_result.grid(row=1, column=0, sticky='ew')

        result_tree_frame.grid_columnconfigure(0, weight=1)
        result_tree_frame.grid_rowconfigure(0, weight=1)

        self.tree_result.heading('Peringkat', text='Peringkat')
        self.tree_result.heading('Nama HP', text='Nama HP')
        self.tree_result.heading('Skor SAW', text='Skor SAW')

        self.tree_result.column('Peringkat', width=70, anchor='center')
        self.tree_result.column('Nama HP', width=150)
        self.tree_result.column('Skor SAW', width=100, anchor='center')
    
    def add_hp_data(self):
        nama_hp = self.entry_nama.get().strip()
        if not nama_hp:
            messagebox.showerror("Error", "Nama HP tidak boleh kosong!")
            return

        # Cek apakah nama HP sudah ada
        if not self.saw.hp_data.empty and nama_hp in self.saw.hp_data['Nama HP'].values:
            messagebox.showerror("Error", f"HP dengan nama '{nama_hp}' sudah ada dalam daftar.")
            return

        new_data = {'Nama HP': nama_hp}
        
        try:
            for crit in self.criteria:
                value_str = self.entry_criteria[crit].get().strip()
                if not value_str:
                    messagebox.showerror("Error", f"Nilai untuk '{crit}' tidak boleh kosong!")
                    return
                # Handle 'Harga (juta)' yang mungkin mengandung koma sebagai desimal
                if crit == 'Harga (juta)':
                    value = float(value_str.replace(',', '.'))
                else:
                    value = float(value_str)
                new_data[crit] = value
        except ValueError:
            messagebox.showerror("Error", "Input kriteria harus berupa angka!")
            return
        
        # Tambahkan data baru ke DataFrame hp_data
        # Menggunakan pd.concat karena hp_data bisa kosong di awal
        new_hp_df = pd.DataFrame([new_data])
        self.saw.hp_data = pd.concat([self.saw.hp_data, new_hp_df], ignore_index=True)
        
        messagebox.showinfo("Sukses", f"Data HP '{nama_hp}' berhasil ditambahkan.")
        self.clear_input_fields()
        self.update_treeview()

    def delete_selected_hp(self):
        selected_items = self.tree_hp.selection()
        if not selected_items:
            messagebox.showwarning("Peringatan", "Pilih HP yang ingin dihapus terlebih dahulu.")
            return

        confirm = messagebox.askyesno("Konfirmasi Hapus", "Anda yakin ingin menghapus HP yang dipilih?")
        if confirm:
            names_to_delete = []
            for item in selected_items:
                hp_name = self.tree_hp.item(item, 'values')[0] # Ambil nama HP dari kolom pertama
                names_to_delete.append(hp_name)
            
            # Hapus dari DataFrame hp_data
            self.saw.hp_data = self.saw.hp_data[~self.saw.hp_data['Nama HP'].isin(names_to_delete)].reset_index(drop=True)
            
            messagebox.showinfo("Sukses", f"{len(names_to_delete)} HP berhasil dihapus.")
            self.update_treeview()
            self.update_result_treeview() # Perbarui juga tabel hasil jika data berubah

    def update_treeview(self):
        # Hapus semua item yang ada di treeview
        for item in self.tree_hp.get_children():
            self.tree_hp.delete(item)
        
        # Masukkan data dari self.saw.hp_data ke treeview
        if not self.saw.hp_data.empty:
            for index, row in self.saw.hp_data.iterrows():
                values = [row['Nama HP']] + [row[crit] for crit in self.criteria]
                self.tree_hp.insert('', 'end', values=values)
    
    def clear_input_fields(self):
        self.entry_nama.delete(0, tk.END)
        for crit in self.criteria:
            self.entry_criteria[crit].delete(0, tk.END)

    def calculate_recommendation(self):
        if self.saw.hp_data.empty:
            messagebox.showwarning("Peringatan", "Tidak ada data HP. Silakan masukkan data HP terlebih dahulu.")
            return

        try:
            # Load data ke SAW_HP_Selection (sudah dilakukan saat add_hp_data, tapi pastikan terbaru)
            # Karena self.saw.hp_data langsung diubah, ini tidak perlu lagi:
            # self.saw.load_data(self.saw.hp_data.copy()) # Gunakan copy agar tidak mengubah hp_data asli saat normalisasi

            # Normalisasi data
            self.saw.normalize_data()
            
            # Hitung skor
            self.saw.calculate_scores()
            
            self.update_result_treeview()
            self.notebook.select(self.tab_result) # Pindah ke tab hasil

        except ValueError as e:
            messagebox.showerror("Error Perhitungan", str(e))
        except Exception as e:
            messagebox.showerror("Error Umum", f"Terjadi kesalahan: {e}")

    def update_result_treeview(self):
        # Hapus semua item yang ada di tree_result
        for item in self.tree_result.get_children():
            self.tree_result.delete(item)
        
        if self.saw.scores is not None and not self.saw.scores.empty:
            for i, (index, row) in enumerate(self.saw.scores.iterrows()):
                self.tree_result.insert('', 'end', values=[i + 1, row['Nama HP'], f"{row['Skor SAW']:.4f}"])
        else:
            messagebox.showinfo("Info", "Belum ada hasil rekomendasi untuk ditampilkan.")


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    # Pastikan tema 'clam' atau tema lain yang mendukung Accent.TButton digunakan
    style.theme_use('clam') # 'default', 'alt', 'clam', 'vista', 'xpnative'

    # Gaya untuk tombol aksen
    style.configure('Accent.TButton', 
                    font=('Helvetica', 10, 'bold'), 
                    foreground='white', 
                    background='#007bff', # Warna biru bootstrap
                    relief='flat')
    style.map('Accent.TButton', 
              background=[('active', '#0056b3')], # Warna biru lebih gelap saat aktif
              foreground=[('pressed', 'white'), ('active', 'white')])

    app = SAW_GUI(root)
    root.mainloop()
