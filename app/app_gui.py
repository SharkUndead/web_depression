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

# Thêm đường dẫn gốc của dự án để import các module tiện ích
try:
    # Lấy đường dẫn thư mục gốc của dự án (giả sử file này nằm trong thư mục con 'app')
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(project_root)
    from utils.preprocessing import preprocess_user_data
    from utils.advice_engine import generate_advice_from_features
    from utils.file_predictor import predict_from_file as predict_file
    from utils.localization import FIELD_LABELS, YES_NO_OPTIONS, GENDER_OPTIONS
except ImportError:
    messagebox.showerror("Lỗi Import", "Không thể tìm thấy các module trong thư mục 'utils'.\nVui lòng đảm bảo cấu trúc thư mục của bạn là:\n\nproject_root/\n|-- app/ (chứa file này)\n|-- utils/\n|-- models/\n|-- ...")
    sys.exit()

# LỚP TẠO FRAME CÓ THANH CUỘN (PHIÊN BẢN HOÀN CHỈNH)
class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        # 1. TẠO CANVAS VÀ THANH CUỘN
        canvas = tk.Canvas(self, borderwidth=0, background="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        
        # 2. TẠO FRAME CON BÊN TRONG CANVAS ĐỂ CHỨA NỘI DUNG
        s = ttk.Style()
        s.configure("Scroll.TFrame", background="white")
        self.scrollable_frame = ttk.Frame(canvas, style="Scroll.TFrame")
        
        # 3. ĐẶT FRAME CON VÀO CANVAS
        self.frame_window_id = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # 4. HÀM VÀ EVENT BINDING ĐỂ XỬ LÝ CO GIÃN VÀ CUỘN
        def on_frame_configure(event):
            # Khi frame nội dung thay đổi (thêm widget...), cập nhật lại vùng cuộn
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            # Khi canvas thay đổi kích thước (phóng to cửa sổ...),
            # buộc frame nội dung phải có chiều rộng bằng canvas.
            canvas.itemconfig(self.frame_window_id, width=event.width)
        
        self.scrollable_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Đóng gói
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Kích hoạt cuộn chuột
        self.bind_mousewheel(canvas)
        self.bind_mousewheel(self.scrollable_frame)
        self.scrollable_frame.bind("<Enter>", lambda _: self.bind_all_children(self.scrollable_frame))

    def bind_all_children(self, parent_widget):
         canvas = self.winfo_children()[0]
         for child in parent_widget.winfo_children():
            # Gán sự kiện cuộn chuột cho từng widget con
            child.bind("<MouseWheel>", lambda e, c=canvas: self._on_mousewheel(e, c), add="+")
            if child.winfo_children():
                self.bind_all_children(child)

    def bind_mousewheel(self, widget):
        canvas = self.winfo_children()[0]
        widget.bind("<MouseWheel>", lambda e, c=canvas: self._on_mousewheel(e, c), add="+")

    def _on_mousewheel(self, event, canvas):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# Tải tài nguyên
def load_resources():
    try:
        # Đường dẫn an toàn, hoạt động kể cả khi đóng gói bằng PyInstaller
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
root.minsize(800, 600)

style = ttk.Style()
try:
    style.theme_use('vista') 
except tk.TclError:
    style.theme_use('clam') 

# --- SỬA ĐỔI: Thêm style cho Frame viền ---
# 1. Định nghĩa một style mới cho Frame để làm viền
style.configure('Border.TFrame', background='white', relief='solid', borderwidth=1)

# 2. Cố gắng loại bỏ viền gốc của Entry và Combobox để tránh xung đột
style.configure('TEntry', relief='flat')
# Cấu hình cho Combobox phức tạp hơn
style.layout('Custom.TCombobox', style.layout('TCombobox'))
style.configure('Custom.TCombobox', relief='flat')
style.map('Custom.TCombobox', fieldbackground=[('readonly', 'white')])

# --- Phần ảnh nền ---
ASSET_DIR = os.path.join(resources['base_dir'], 'app', 'assets', 'backgrounds')
bg_images = glob.glob(os.path.join(ASSET_DIR, '*.jpg')) + glob.glob(os.path.join(ASSET_DIR, '*.png'))
bg_photos = []
if bg_images:
    try:
        bg_photos = [ImageTk.PhotoImage(Image.open(p).resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.Resampling.LANCZOS)) for p in bg_images]
    except Exception as e:
        print(f"Lỗi tải ảnh nền: {e}")

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

# --- Layout chính ---
main_frame = ttk.Frame(root, padding=20)
main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)
notebook = ttk.Notebook(main_frame)
notebook.pack(expand=True, fill="both", padx=10, pady=10)

# Khởi tạo các tab
frame_manual_scrollable = ScrollableFrame(notebook)
frame_manual = frame_manual_scrollable.scrollable_frame
style.configure("TFrame", background="white")
frame_file = ttk.Frame(notebook, padding=10, style="TFrame")
notebook.add(frame_manual_scrollable, text="Nhập tay")
notebook.add(frame_file, text="Dự đoán từ file")

# === Hàm dự đoán ===
def predict():
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

# === Xây dựng Tab Nhập tay ===
# 1. Cấu hình grid của frame_manual để có các cột đệm co giãn
frame_manual.grid_columnconfigure(0, weight=1) 
frame_manual.grid_columnconfigure(2, weight=1) 

# 2. Tạo một frame con để chứa toàn bộ nội dung, frame này sẽ không co giãn
content_form_frame = ttk.Frame(frame_manual, style="Scroll.TFrame")
content_form_frame.grid(row=0, column=1, pady=20) 

# 3. Đặt tất cả các widget vào `content_form_frame`
entries = {}
radio_vars = {}
style.configure("TRadiobutton", background='white') # Đảm bảo radio button có nền trắng
ttk.Label(content_form_frame, text="📋 Nhập thông tin sinh viên", font=("Segoe UI", 14, "bold"), background='white').grid(row=0, column=0, columnspan=2, pady=10)
start_row_manual = 1


# --- SỬA ĐỔI: Vòng lặp tạo widget được thay đổi để sử dụng kỹ thuật "bọc Frame" ---
for i, field in enumerate(input_fields):
    display_text = FIELD_LABELS.get(field, field.replace('_', ' ').capitalize())
    ttk.Label(content_form_frame, text=display_text, background='white').grid(row=start_row_manual + i, column=0, sticky='w', padx=5, pady=5)
    
    # Tạo một Frame để làm viền bọc ngoài
    border_frame = ttk.Frame(content_form_frame, style='Border.TFrame')
    border_frame.grid(row=start_row_manual + i, column=1, padx=5, pady=5)
    
    if field in resources["label_encoders"]:
        values = list(resources["label_encoders"][field].classes_)
        # Tạo Combobox bên trong Frame viền
        cb = ttk.Combobox(border_frame, values=values, width=30, state="readonly", style='Custom.TCombobox')
        cb.pack(fill="both", expand=True)
        entries[field] = cb
    else:
        # Tạo Entry bên trong Frame viền
        entry = ttk.Entry(border_frame, width=33)
        entry.pack()
        entries[field] = entry


start_row_binary = start_row_manual + len(input_fields)
for i, field in enumerate(binary_fields):
    display_text = FIELD_LABELS.get(field, field.replace('_', ' ').capitalize())
    ttk.Label(content_form_frame, text=display_text, background='white').grid(row=start_row_binary + i, column=0, sticky='w', padx=5, pady=5)
    var = tk.StringVar()
    radio_vars[field] = var
    
    options = GENDER_OPTIONS if field == 'gender' else YES_NO_OPTIONS
    
    radio_container = ttk.Frame(content_form_frame, style="Scroll.TFrame")
    radio_container.grid(row=start_row_binary + i, column=1, sticky='w')

    for text, val in options:
        ttk.Radiobutton(radio_container, text=text, variable=var, value=val).pack(side=tk.LEFT)

predict_button_manual = ttk.Button(content_form_frame, text="👉 DỰ ĐOÁN", command=predict)
predict_button_manual.grid(row=start_row_binary + len(binary_fields), column=0, columnspan=2, pady=20)

result_text = tk.Text(content_form_frame, height=10, width=80, font=("Segoe UI", 12), fg="white", bg="#2c2c2c", wrap="word", relief="solid", borderwidth=1)
result_text.grid(row=start_row_binary + len(binary_fields) + 1, column=0, columnspan=2, pady=15)
result_text.config(state="disabled")

# === Xây dựng Tab Dự đoán từ file ===
frame_file.grid_columnconfigure(0, weight=1)
frame_file.grid_columnconfigure(2, weight=1)

content_file_frame = ttk.Frame(frame_file, style="TFrame")
content_file_frame.grid(row=0, column=1, pady=20)

def call_predict_from_file():
    path = selected_file_path.get()
    if not path:
        messagebox.showwarning("Chưa chọn file", "Vui lòng chọn một file CSV để dự đoán.")
        return
    threading.Thread(target=run_prediction_task, daemon=True).start()

def run_prediction_task():
    path = selected_file_path.get()
    output_name = output_filename.get().strip() or "predicted_results.csv"
    if not output_name.lower().endswith('.csv'):
        output_name += '.csv'

    predict_file_button.config(state="disabled")
    file_result_label.config(text="Đang xử lý, vui lòng chờ...", foreground="blue")
    
    try:
        output_dir = os.path.join(resources["base_dir"], "data", "processed")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        result_msg = predict_file(path, output_name, os.path.join(resources["base_dir"], 'models', 'lgbm_model.pkl'), 
            os.path.join(resources["base_dir"], 'models', 'label_encoders.pkl'), os.path.join(resources["base_dir"], 'models', 'feature_order_lightgbm.pkl'), 
            output_dir)
        color = "green" if "✅" in result_msg else "red"
        file_result_label.config(text=result_msg, foreground=color)
    except Exception as e:
        file_result_label.config(text=f"❌ Lỗi: {e}", foreground="red")
        traceback.print_exc()
    finally:
        predict_file_button.config(state="normal")

ttk.Label(content_file_frame, text="📂 Dự đoán từ file CSV", font=("Segoe UI", 14, "bold"), background='white').grid(row=0, column=0, columnspan=3, pady=10)

selected_file_path = tk.StringVar()
output_filename = tk.StringVar(value="predicted_results.csv")

file_entry = ttk.Entry(content_file_frame, textvariable=selected_file_path, width=60, state="readonly")
file_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
ttk.Button(content_file_frame, text="🔍 Chọn file", command=lambda: selected_file_path.set(filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")]))).grid(row=1, column=2, padx=(5, 0))

ttk.Label(content_file_frame, text="Tên file kết quả:", background='white').grid(row=2, column=0, sticky='w', padx=5, pady=(10,5))
ttk.Entry(content_file_frame, textvariable=output_filename, width=40).grid(row=2, column=1, pady=(10,5), sticky='w')

predict_file_button = ttk.Button(content_file_frame, text="📤 DỰ ĐOÁN TỪ FILE", command=call_predict_from_file)
predict_file_button.grid(row=3, column=0, columnspan=3, pady=20)

file_result_label = ttk.Label(content_file_frame, text="", font=("Segoe UI", 12, "bold"), background='white', wraplength=500, justify='center')
file_result_label.grid(row=4, column=0, columnspan=3, pady=15)

# Chạy vòng lặp chính của ứng dụng
root.mainloop()