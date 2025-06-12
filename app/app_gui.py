import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import sys
import os
import traceback
import glob
import pandas as pd
import joblib
import threading

# Thêm đường dẫn gốc của dự án
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import các hàm xử lý và file dịch thuật mới
from utils.preprocessing import preprocess_user_data
from utils.advice_engine import generate_advice_from_features
from utils.file_predictor import predict_from_file as predict_file
from utils.localization import FIELD_LABELS, YES_NO_OPTIONS, GENDER_OPTIONS # << IMPORT MỚI

# (Các hàm và lớp còn lại giữ nguyên cấu trúc như trước)
# LỚP TẠO FRAME CÓ THANH CUỘN
class ScrollableFrame(ttk.Frame):
    # ... (Giữ nguyên toàn bộ nội dung lớp ScrollableFrame như phiên bản trước)
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.bind_mousewheel(canvas)
        self.bind_mousewheel(self.scrollable_frame)

    def bind_mousewheel(self, widget):
        widget.bind_all("<MouseWheel>", self._on_mousewheel, add="+")

    def _on_mousewheel(self, event):
        canvas = self.winfo_children()[0]
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# Tải tài nguyên
def load_resources():
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        resources = {
            "base_dir": base_dir,
            "model": joblib.load(os.path.join(base_dir, 'models', 'lgbm_model.pkl')),
            "label_encoders": joblib.load(os.path.join(base_dir, 'models', 'label_encoders.pkl')),
            "feature_order": joblib.load(os.path.join(base_dir, 'models', 'feature_order_lightgbm.pkl'))
        }
        return resources
    except FileNotFoundError as e:
        messagebox.showerror("Lỗi nghiêm trọng", f"Không tìm thấy file mô hình cần thiết: {e.filename}")
        return None

resources = load_resources()
if not resources:
    sys.exit("Không thể tải tài nguyên, ứng dụng đóng.")

# Danh sách các trường (key nội bộ)
input_fields = [
    'age', 'city', 'degree', 'sleep_duration', 'dietary_habits',
    'work/study_hours', 'academic_pressure', 'study_satisfaction',
    'financial_stress', 'cgpa'
]
binary_fields = [
    'gender', 'have_you_ever_had_suicidal_thoughts_?', 
    'family_history_of_mental_illness'
]

# --- Giao diện người dùng ---
root = tk.Tk()
root.title("Dự đoán Trầm cảm Sinh viên")
root.geometry("1024x768")
root.resizable(True, True)

# ... (Phần code ảnh nền không thay đổi)
ASSET_DIR = os.path.join(resources['base_dir'], 'app', 'assets', 'backgrounds')
bg_images = glob.glob(os.path.join(ASSET_DIR, '*.jpg')) + glob.glob(os.path.join(ASSET_DIR, '*.png'))
try:
    bg_photos = [ImageTk.PhotoImage(Image.open(p).resize((1920, 1080), Image.Resampling.LANCZOS)) for p in bg_images]
except Exception:
    bg_photos = []
bg_index = 0
bg_label = tk.Label(root)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

def change_background():
    global bg_index
    if bg_photos:
        bg_label.config(image=bg_photos[bg_index])
        bg_index = (bg_index + 1) % len(bg_photos)
        root.after(5000, change_background)
change_background()

# ... (Phần code layout chính không thay đổi)
main_frame = ttk.Frame(root, padding=20)
main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)
notebook = ttk.Notebook(main_frame)
notebook.pack(expand=True, fill="both", padx=10, pady=10)
frame_manual_scrollable = ScrollableFrame(notebook)
frame_manual = frame_manual_scrollable.scrollable_frame
frame_file = ttk.Frame(notebook, padding=10)
notebook.add(frame_manual_scrollable, text="Nhập tay")
notebook.add(frame_file, text="Dự đoán từ file")


# === Hàm dự đoán (không đổi) ===
def predict():
    # ... (Toàn bộ logic của hàm predict giữ nguyên như trước)
    try:
        user_input = {}
        for field in input_fields:
            value = entries[field].get().strip()
            if not value:
                messagebox.showwarning("Thiếu thông tin", f"Vui lòng nhập giá trị cho trường: {FIELD_LABELS.get(field, field)}")
                return
            user_input[field] = value
        for field in binary_fields:
            value = radio_vars[field].get()
            if not value:
                messagebox.showwarning("Thiếu thông tin", f"Vui lòng chọn giá trị cho trường: {FIELD_LABELS.get(field, field)}")
                return
            user_input[field] = value
        df_raw = pd.DataFrame([user_input])
        df_processed = preprocess_user_data(df_raw.copy(), resources["label_encoders"])
        if df_processed.empty:
             messagebox.showerror("Lỗi dữ liệu", "Dữ liệu nhập vào không hợp lệ sau khi xử lý.")
             return
        advice = generate_advice_from_features(df_processed.iloc[0])
        df_final = df_processed[resources["feature_order"]]
        prediction = resources["model"].predict(df_final)[0]
        msg = "✅ Không có dấu hiệu trầm cảm.\n" if prediction == 0 else "⚠️ Có dấu hiệu TRẦM CẢM!\n"
        if advice:
            msg += "\n🧾 Gợi ý cải thiện:\n- " + "\n- ".join(advice)
        result_text.config(state="normal")
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, msg)
        result_text.config(state="disabled")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã có lỗi không xác định xảy ra: {e}")
        traceback.print_exc()

# === Xây dựng Tab Nhập tay (ĐÃ CẬP NHẬT ĐỂ VIỆT HÓA) ===
ttk.Label(frame_manual, text="📋 Nhập thông tin sinh viên", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
entries = {}
radio_vars = {}
start_row_manual = 1
# THAY ĐỔI 1: Lấy nhãn Tiếng Việt từ FIELD_LABELS
for i, field in enumerate(input_fields):
    display_text = FIELD_LABELS.get(field, field.replace('_', ' ').capitalize())
    ttk.Label(frame_manual, text=display_text).grid(row=start_row_manual + i, column=0, sticky='w', padx=5, pady=5)
    if field in resources["label_encoders"]:
        values = resources["label_encoders"][field].classes_.tolist()
        cb = ttk.Combobox(frame_manual, values=values, width=30)
        cb.grid(row=start_row_manual + i, column=1, padx=5, pady=5)
        entries[field] = cb
    else:
        entry = ttk.Entry(frame_manual, width=33)
        entry.grid(row=start_row_manual + i, column=1, padx=5, pady=5)
        entries[field] = entry

start_row_binary = start_row_manual + len(input_fields)
# THAY ĐỔI 2: Lấy các lựa chọn Tiếng Việt từ GENDER_OPTIONS và YES_NO_OPTIONS
for i, field in enumerate(binary_fields):
    display_text = FIELD_LABELS.get(field, field.replace('_', ' ').capitalize())
    ttk.Label(frame_manual, text=display_text).grid(row=start_row_binary + i, column=0, sticky='w', padx=5, pady=5)
    var = tk.StringVar()
    radio_vars[field] = var
    
    # Quyết định dùng bộ lựa chọn nào
    options = GENDER_OPTIONS if field == 'gender' else YES_NO_OPTIONS
    
    radio_container = ttk.Frame(frame_manual)
    radio_container.grid(row=start_row_binary + i, column=1, sticky='w')
    # `text` là Tiếng Việt, `val` là Tiếng Anh
    for text, val in options:
        ttk.Radiobutton(radio_container, text=text, variable=var, value=val).pack(side=tk.LEFT)

predict_button_manual = ttk.Button(frame_manual, text="👉 DỰ ĐOÁN", command=predict)
predict_button_manual.grid(row=start_row_binary + len(binary_fields), column=0, columnspan=2, pady=10)

result_text = tk.Text(frame_manual, height=12, width=80, font=("Segoe UI", 12), fg="white", bg="#000000", wrap="word")
result_text.grid(row=start_row_binary + len(binary_fields) + 1, column=0, columnspan=2, pady=15)
result_text.config(state="disabled")


# === Tab Dự đoán từ file và các hàm liên quan (không đổi) ===
# ... (Toàn bộ phần code cho Tab 2 giữ nguyên)
def call_predict_from_file():
    path = selected_file_path.get()
    if not path:
        messagebox.showwarning("Chưa chọn file", "Vui lòng chọn một file CSV để dự đoán.")
        return
    threading.Thread(target=run_prediction_task, daemon=True).start()
def run_prediction_task():
    path = selected_file_path.get()
    output_name = output_filename.get() or "predicted_results.csv"
    predict_file_button.config(state="disabled")
    file_result_label.config(text="Đang xử lý, vui lòng chờ...", foreground="blue")
    try:
        result_msg = predict_file(
            path, output_name, os.path.join(resources["base_dir"], 'models', 'lgbm_model.pkl'), 
            os.path.join(resources["base_dir"], 'models', 'label_encoders.pkl'), 
            os.path.join(resources["base_dir"], 'models', 'feature_order_lightgbm.pkl'), 
            resources["base_dir"])
        color = "green" if "✅" in result_msg else "red"
        file_result_label.config(text=result_msg, foreground=color)
    except Exception as e:
        file_result_label.config(text=f"❌ Lỗi: {e}", foreground="red")
        traceback.print_exc()
    finally:
        predict_file_button.config(state="normal")
ttk.Label(frame_file, text="📂 Dự đoán từ file CSV", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=3, pady=10)
selected_file_path = tk.StringVar()
output_filename = tk.StringVar(value="predicted_results.csv")
file_entry = ttk.Entry(frame_file, textvariable=selected_file_path, width=60, state="readonly")
file_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
ttk.Button(frame_file, text="🔍 Chọn file", command=lambda: selected_file_path.set(filedialog.askopenfilename(filetypes=(("CSV Files", "*.csv"),)))).grid(row=1, column=2)
ttk.Label(frame_file, text="Tên file kết quả (.csv):").grid(row=2, column=0, sticky='w', padx=5)
ttk.Entry(frame_file, textvariable=output_filename, width=40).grid(row=2, column=1, pady=5)
predict_file_button = ttk.Button(frame_file, text="📤 DỰ ĐOÁN TỪ FILE", command=call_predict_from_file)
predict_file_button.grid(row=3, column=0, columnspan=3, pady=10)
file_result_label = ttk.Label(frame_file, text="", font=("Segoe UI", 12, "bold"))
file_result_label.grid(row=4, column=0, columnspan=3, pady=15)


root.mainloop()