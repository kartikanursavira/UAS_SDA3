import pandas as pd
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt

# === BACA DAN PERSIAPAN DATA ===
data = pd.read_csv("penilaian_mahasiswa.csv")

# Konversi keaktifan ke nilai numerik
konversi_keaktifan = {
    "Tidak Aktif": 20,
    "Kurang Aktif": 40,
    "Cukup Aktif": 60,
    "Aktif": 80,
    "Sangat Aktif": 100
}
data["Keaktifan di kelas"] = data["Keaktifan di kelas"].map(konversi_keaktifan)

# Encode status kelulusan
label_lulus = LabelEncoder()
data["Status Kelulusan"] = label_lulus.fit_transform(data["Status Kelulusan"])

# Buat fitur rata-rata tugas
data['Avg_Tugas'] = data[['Tugas 1', 'Tugas 2', 'Tugas 3', 'Tugas 4']].mean(axis=1)

# Fitur dan target
fitur = ["Nilai UTS", "Nilai UAS", "Avg_Tugas", "Nilai Kuis", "Presensi (%)", "Keaktifan di kelas"]
X = data[fitur]
y = data["Status Kelulusan"]

# Split data menjadi training dan testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Inisialisasi dan latih model Decision Tree
model = DecisionTreeClassifier(min_samples_split=2, random_state=42)
model.fit(X_train, y_train)

# === STRUKTUR TREE MANUAL ===
class TreeNode:
    def __init__(self, data):
        self.data = data
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

    def print_tree(self, prefix="", is_last=True):
        connector = "└── " if is_last else "├── "
        print(prefix + connector + str(self.data))
        child_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(self.children):
            child.print_tree(child_prefix, i == len(self.children) - 1)

# Membuat struktur pohon keputusan manual
root = TreeNode("Presensi (%)")
root.add_child(TreeNode("≤ 74.5 → Tidak Lulus (Kehadiran)"))
right_node = TreeNode("> 74.5")
root.add_child(right_node)

uas_node = TreeNode("Nilai UAS")
right_node.add_child(uas_node)
uas_node.add_child(TreeNode("≤ 49.0 → Tidak Lulus (UAS)"))

uts_branch = TreeNode("> 49.0")
uas_node.add_child(uts_branch)

uts_node = TreeNode("Nilai UTS")
uts_branch.add_child(uts_node)
uts_node.add_child(TreeNode("≤ 49.5 → Tidak Lulus (UTS)"))

uts_right = TreeNode("> 49.5")
uts_node.add_child(uts_right)

keaktifan_node = TreeNode("Keaktifan di kelas")
uts_right.add_child(keaktifan_node)
keaktifan_node.add_child(TreeNode("≤ 35.0 → Tidak Lulus (Keaktifan)"))

keaktifan_right = TreeNode("> 35.0")
keaktifan_node.add_child(keaktifan_right)

kuis_node = TreeNode("Nilai Kuis")
keaktifan_right.add_child(kuis_node)
kuis_node.add_child(TreeNode("≤ 38.0 → Tidak Lulus (Kuis)"))

kuis_right = TreeNode("> 38.0")
kuis_node.add_child(kuis_right)

tugas_node = TreeNode("Rata-rata Tugas")
kuis_right.add_child(tugas_node)
tugas_node.add_child(TreeNode("≤ 73.8 → Tidak Lulus (Tugas)"))  # Sesuaikan ambang batas
tugas_node.add_child(TreeNode("> 73.8 → Lulus"))

# === FORM GUI BARU DENGAN BACKGROUND ===
def buka_form_prediksi():
    splash.destroy()

    form = tk.Tk()
    form.title("Form Prediksi Kelulusan")
    form.attributes("-fullscreen", True)

    screen_width = form.winfo_screenwidth()
    screen_height = form.winfo_screenheight()

    bg_img = Image.open("bg prediksi.png")
    bg_img = bg_img.resize((screen_width, screen_height), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_img)

    canvas = tk.Canvas(form, width=screen_width, height=screen_height)
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=bg_photo, anchor=tk.NW)

    frame_overlay = tk.Frame(form, bg="#ffffff", bd=0, highlightbackground="#ccc", highlightthickness=2)
    frame_window = canvas.create_window(screen_width//2, screen_height//2, window=frame_overlay, anchor="center")

    title = tk.Label(frame_overlay, text="📘 Form Input Nilai Mahasiswa", font=("Segoe UI", 22, "bold"),
                     bg="#ffffff", fg="#0d47a1", pady=10)
    title.pack()

    input_frame = tk.Frame(frame_overlay, bg="#ffffff")
    input_frame.pack(pady=10)

    labels = ["Nilai UTS", "Nilai UAS", "Tugas 1", "Tugas 2", "Tugas 3", "Tugas 4",
              "Nilai Kuis", "Presensi (%)", "Keaktifan di kelas"]

    entries = {}
    style_font = ("Segoe UI", 12)
    entry_width = 25

    for i, label in enumerate(labels):
        tk.Label(input_frame, text=label, font=style_font, bg="#ffffff", anchor="w").grid(row=i, column=0, sticky="w", pady=6, padx=10)
        
        if label == "Keaktifan di kelas":
            combo = ttk.Combobox(input_frame, values=list(konversi_keaktifan.keys()), state="readonly",
                                font=style_font, width=entry_width)
            combo.grid(row=i, column=1, pady=6, padx=10)
            combo.set("Cukup Aktif")
            entries[label] = combo
        else:
            ent = tk.Entry(input_frame, font=style_font, width=entry_width)
            ent.grid(row=i, column=1, pady=6, padx=10)
            entries[label] = ent

    def prediksi():
        try:
            uts = float(entries["Nilai UTS"].get())
            uas = float(entries["Nilai UAS"].get())
            t1 = float(entries["Tugas 1"].get())
            t2 = float(entries["Tugas 2"].get())
            t3 = float(entries["Tugas 3"].get())
            t4 = float(entries["Tugas 4"].get())
            kuis = float(entries["Nilai Kuis"].get())
            presensi = float(entries["Presensi (%)"].get())
            aktif_score = konversi_keaktifan[entries["Keaktifan di kelas"].get()]

            avg_tugas = (t1 + t2 + t3 + t4) / 4

            # Logika prediksi kelulusan
            if presensi < 75:
                hasil = "Tidak Lulus (Kehadiran)"
            elif uas < 50:
                hasil = "Tidak Lulus (UAS)"
            elif uts < 50:
                hasil = "Tidak Lulus (UTS)"
            elif aktif_score < 35:
                hasil = "Tidak Lulus (Keaktifan)"
            elif avg_tugas < 73.8:
                hasil = "Tidak Lulus (Tugas)"
            else:
                hasil = "Lulus"

            messagebox.showinfo("Hasil Prediksi", f"Mahasiswa dinyatakan: {hasil}")
        except ValueError:
            messagebox.showerror("Error", "Input tidak valid. Pastikan semua nilai diisi dengan benar.")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {e}")

    button_frame = tk.Frame(frame_overlay, bg="#ffffff")
    button_frame.pack(pady=20)

    tk.Button(button_frame, text="Prediksi", font=("Helvetica", 14, "bold"),
              bg="#0d47a1", fg="white", padx=10, pady=5, command=prediksi).grid(row=0, column=0, padx=10)

    tk.Button(button_frame, text="Keluar", font=("Helvetica", 12),
              command=form.destroy).grid(row=0, column=1, padx=10)

    form.mainloop()

# === TAMPILKAN STRUKTUR & VISUALISASI SEBELUM GUI ===
print("=== STRUKTUR DECISION TREE (Manual) ===")
root.print_tree()

print("\n=== VISUALISASI DECISION TREE ===")
plt.figure(figsize=(13, 4))
plot_tree(model, feature_names=fitur, class_names=label_lulus.classes_,
          filled=True, rounded=True)
plt.title("Visualisasi Decision Tree")
plt.show()

# === SPLASH SCREEN ===
splash = tk.Tk()
splash.title("Prediksi Kelulusan")
splash.attributes("-fullscreen", True)

screen_width = splash.winfo_screenwidth()
screen_height = splash.winfo_screenheight()

bg_image = Image.open("Prediksi Kelulusan Mahasiswa Sains Data 1.png")
bg_image = bg_image.resize((screen_width, screen_height), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

canvas = tk.Canvas(splash, width=screen_width, height=screen_height, highlightthickness=0)
canvas.pack()
canvas.create_image(0, 0, anchor=tk.NW, image=bg_photo)

start_btn = tk.Button(splash, text="START", font=("Helvetica", 16, "bold"),
                      bg="#e3f2fd", fg="#0d47a1", padx=20, pady=10,
                      relief="flat", cursor="hand2",
                      command=buka_form_prediksi)
canvas.create_window(screen_width//2, screen_height//2 + 50, window=start_btn)

splash.mainloop()