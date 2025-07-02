import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import os
import traceback
import glob
import pandas as pd
import joblib
import threading

# Cố gắng import thư viện xử lý ảnh
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    messagebox.showwarning("Thiếu thư viện", "Thư viện 'Pillow' không được tìm thấy.\nChức năng ảnh nền sẽ bị vô hiệu hóa.\nĐể cài đặt, chạy: pip install Pillow")

# ================== ĐƯỜNG DẪN VÀ IMPORT ==================
try:
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, PROJECT_ROOT)

    from utils.preprocessing import preprocess_user_data
    from utils.advice_gui import generate_support_gui
    from utils.file_predictor import predict_from_file as predict_file
    from utils.localization import FIELD_LABELS, YES_NO_OPTIONS, GENDER_OPTIONS
except ImportError as e:
    messagebox.showerror("Lỗi Import", f"Không thể tìm thấy các module cần thiết: {e}\nVui lòng đảm bảo cấu trúc thư mục của bạn đúng.")
    sys.exit()

# LỚP TẠO FRAME CÓ THANH CUỘN
class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, borderwidth=0, background="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas, style="White.TFrame")
        self.frame_window_id = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        def on_canvas_configure(event):
            canvas.itemconfig(self.frame_window_id, width=event.width)
        
        self.scrollable_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        canvas.bind('<Enter>', self._bind_mousewheel)
        canvas.bind('<Leave>', self._unbind_mousewheel)

    def _bind_mousewheel(self, event):
        self.bind_all("<MouseWheel>", self._on_mousewheel)
    def _unbind_mousewheel(self, event):
        self.unbind_all("<MouseWheel>")
    def _on_mousewheel(self, event):
        canvas = self.winfo_children()[0]
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# LỚP ỨNG DỤNG CHÍNH
class DepressionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hệ thống Hỗ trợ Sức khỏe Tinh thần")
        self.geometry("850x700")
        self.minsize(700, 500)

        self.resources = self._load_resources()
        if not self.resources:
            self.destroy()
            return

        # Danh sách các trường (key nội bộ)
        self.input_fields = ['age', 'city', 'degree', 'sleep_duration', 'dietary_habits', 'work/study_hours', 'academic_pressure', 'study_satisfaction', 'financial_stress', 'cgpa']
        self.binary_fields = ['gender', 'have_you_ever_had_suicidal_thoughts_?', 'family_history_of_mental_illness']

        self.bg_photos = [] 
        self.bg_index = 0
        
        self._setup_styles()
        self.create_widgets()
        self.change_background()

    def _load_resources(self):
        try:
            base_dir = getattr(sys, '_MEIPASS', PROJECT_ROOT)
            return {
                "base_dir": base_dir,
                "model": joblib.load(os.path.join(base_dir, 'models', 'stacking_model.pkl')),
                "label_encoders": joblib.load(os.path.join(base_dir, 'models', 'label_encoders.pkl')),
                "feature_order": joblib.load(os.path.join(base_dir, 'models', 'feature_stacking.pkl'))
            }
        except FileNotFoundError as e:
            messagebox.showerror("Lỗi nghiêm trọng", f"Không tìm thấy file mô hình cần thiết: {e.filename}")
            return None
            
    def _setup_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use('vista') 
        except tk.TclError:
            style.theme_use('clam')
        style.configure("White.TFrame", background="white")
        style.configure("White.TRadiobutton", background="white")
        
    def create_widgets(self):
        self.bg_label = tk.Label(self)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        if PIL_AVAILABLE:
            ASSET_DIR = os.path.join(self.resources['base_dir'], 'app', 'assets', 'backgrounds')
            bg_images_paths = glob.glob(os.path.join(ASSET_DIR, '*.jpg')) + glob.glob(os.path.join(ASSET_DIR, '*.png'))
            if bg_images_paths:
                try:
                    for p in bg_images_paths:
                        img = Image.open(p).resize((self.winfo_screenwidth(), self.winfo_screenheight()), Image.Resampling.LANCZOS)
                        self.bg_photos.append(ImageTk.PhotoImage(img))
                except Exception as e:
                    print(f"Lỗi tải ảnh nền: {e}")
        
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(expand=True, fill="both")
        
        frame_manual_scrollable = ScrollableFrame(notebook)
        self.frame_manual = frame_manual_scrollable.scrollable_frame
        frame_file = ttk.Frame(notebook, padding=10, style="White.TFrame")
        
        notebook.add(frame_manual_scrollable, text="Đánh giá Cá nhân")
        notebook.add(frame_file, text="Đánh giá từ File")
        
        notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self._create_manual_tab()
        self._create_file_tab(frame_file)

    def change_background(self):
        if self.bg_photos:
            current_image = self.bg_photos[self.bg_index]
            self.bg_label.config(image=current_image)
            self.bg_index = (self.bg_index + 1) % len(self.bg_photos)
            self.after(5000, self.change_background)

    def _on_tab_changed(self, event):
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.config(state="disabled")
        if hasattr(self, 'file_result_label'):
            self.file_result_label.config(text="")

    def _create_manual_tab(self):
        self.frame_manual.grid_columnconfigure(0, weight=1) 
        self.frame_manual.grid_columnconfigure(2, weight=1) 
        content_form_frame = ttk.Frame(self.frame_manual, style="White.TFrame")
        content_form_frame.grid(row=0, column=1, pady=20, padx=20) 

        ttk.Label(content_form_frame, text="📋 Nhập thông tin Sinh viên", font=("Segoe UI", 14, "bold"), background='white').grid(row=0, column=0, columnspan=2, pady=10)
        
        self.entries = {}
        self.radio_vars = {}
        current_row = 1
        for field in self.input_fields:
            ttk.Label(content_form_frame, text=FIELD_LABELS.get(field, field), background='white').grid(row=current_row, column=0, sticky='w', padx=5, pady=5)
            if field in self.resources["label_encoders"]:
                cb = ttk.Combobox(content_form_frame, values=list(self.resources["label_encoders"][field].classes_), width=30, state="readonly")
                cb.grid(row=current_row, column=1, padx=5, pady=5)
                self.entries[field] = cb
            else:
                entry = ttk.Entry(content_form_frame, width=33)
                entry.grid(row=current_row, column=1, padx=5, pady=5)
                self.entries[field] = entry
            current_row += 1

        for field in self.binary_fields:
            ttk.Label(content_form_frame, text=FIELD_LABELS.get(field, field), background='white').grid(row=current_row, column=0, sticky='w', padx=5, pady=5)
            var = tk.StringVar()
            self.radio_vars[field] = var
            options = GENDER_OPTIONS if field == 'gender' else YES_NO_OPTIONS
            radio_container = ttk.Frame(content_form_frame, style="White.TFrame")
            radio_container.grid(row=current_row, column=1, sticky='w')
            for text, val in options:
                ttk.Radiobutton(radio_container, text=text, variable=var, value=val, style="White.TRadiobutton").pack(side=tk.LEFT)
            current_row += 1
        
        predict_button_manual = ttk.Button(content_form_frame, text="👉 Phân tích", command=self._predict)
        predict_button_manual.grid(row=current_row, column=0, columnspan=2, pady=20)
        current_row += 1

        result_frame_container = ttk.Frame(content_form_frame, height=250)
        result_frame_container.grid(row=current_row, column=0, columnspan=2, pady=15, sticky="nsew")
        result_frame_container.grid_propagate(False)
        result_frame_container.grid_rowconfigure(0, weight=1)
        result_frame_container.grid_columnconfigure(0, weight=1)

        result_text_scrollable = ScrollableFrame(result_frame_container)
        result_text_scrollable.grid(row=0, column=0, sticky="nsew")
        self.result_text = tk.Text(result_text_scrollable.scrollable_frame, font=("Segoe UI", 10), wrap="word", relief="flat", borderwidth=0)
        self.result_text.pack(expand=True, fill="both")
        
        self.result_text.tag_configure("title_red", font=("Segoe UI", 13, "bold"), foreground="#d32f2f")
        self.result_text.tag_configure("title_green", font=("Segoe UI", 13, "bold"), foreground="#2e7d32")
        self.result_text.tag_configure("subtitle", font=("Segoe UI", 11, "bold", "underline"))
        self.result_text.tag_configure("bold_text", font=("Segoe UI", 10, "bold"))
        self.result_text.tag_configure("disclaimer", font=("Segoe UI", 9, "italic"), foreground="gray")
        self.result_text.config(state="disabled")

    def _create_file_tab(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(2, weight=1)
        content_file_frame = ttk.Frame(parent_frame, style="White.TFrame")
        content_file_frame.grid(row=0, column=1, pady=20)

        ttk.Label(content_file_frame, text="📂 Đánh giá hàng loạt từ file CSV", font=("Segoe UI", 14, "bold"), background='white').grid(row=0, column=0, columnspan=3, pady=10)
        
        self.selected_file_path = tk.StringVar()
        self.output_filename = tk.StringVar(value="ket_qua_danh_gia.csv")
        
        file_entry_frame = ttk.Frame(content_file_frame, style="White.TFrame")
        file_entry_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky='ew')
        
        file_entry = ttk.Entry(file_entry_frame, textvariable=self.selected_file_path, width=60, state="readonly")
        file_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(file_entry_frame, text="🔍 Chọn file", command=lambda: self.selected_file_path.set(filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")]))).pack(side="left", padx=(5,0))

        ttk.Label(content_file_frame, text="Tên file kết quả:", background='white').grid(row=2, column=0, sticky='w', padx=5, pady=(10,5))
        ttk.Entry(content_file_frame, textvariable=self.output_filename, width=40).grid(row=2, column=1, pady=(10,5), columnspan=2, sticky='w')

        self.predict_file_button = ttk.Button(content_file_frame, text="📤 Bắt đầu Đánh giá", command=self._call_predict_from_file)
        self.predict_file_button.grid(row=3, column=0, columnspan=3, pady=20)

        self.file_result_label = ttk.Label(content_file_frame, text="", font=("Segoe UI", 12, "bold"), background='white', wraplength=500, justify='center')
        self.file_result_label.grid(row=4, column=0, columnspan=3, pady=15)

    def _call_predict_from_file(self):
        path = self.selected_file_path.get()
        if not path:
            messagebox.showwarning("Chưa chọn file", "Vui lòng chọn một file CSV để dự đoán.")
            return
        threading.Thread(target=self._run_prediction_task, daemon=True).start()

    def _run_prediction_task(self):
        path = self.selected_file_path.get()
        output_name = self.output_filename.get().strip() or "ket_qua_danh_gia.csv"
        if not output_name.lower().endswith('.csv'):
            output_name += '.csv'

        self.predict_file_button.config(state="disabled")
        self.file_result_label.config(text="Đang xử lý, vui lòng chờ...", foreground="blue")
        
        try:
            output_dir = os.path.join(self.resources["base_dir"], "data", "predict")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            result_msg = predict_file(path, output_name,
                os.path.join(self.resources["base_dir"], 'models', 'stacking_model.pkl'), 
                os.path.join(self.resources["base_dir"], 'models', 'label_encoders.pkl'), 
                os.path.join(self.resources["base_dir"], 'models', 'feature_stacking.pkl'), 
                output_dir)
            color = "green" if "✅" in result_msg else "red"
            self.file_result_label.config(text=result_msg, foreground=color)
        except Exception as e:
            self.file_result_label.config(text=f"❌ Lỗi: {e}", foreground="red")
            traceback.print_exc()
        finally:
            self.predict_file_button.config(state="normal")

    def _predict(self):
        try:
            user_input = {}
            for field in self.input_fields:
                value = self.entries[field].get().strip()
                if not value:
                    messagebox.showwarning("Thiếu thông tin", f"Vui lòng nhập giá trị cho trường: {FIELD_LABELS.get(field, field)}")
                    return
                user_input[field] = value
            for field in self.binary_fields:
                value = self.radio_vars[field].get()
                if not value:
                    messagebox.showwarning("Thiếu thông tin", f"Vui lòng chọn giá trị cho trường: {FIELD_LABELS.get(field, field)}")
                    return
                user_input[field] = value
            
            df_raw = pd.DataFrame([user_input])
            
            support_results = generate_support_gui(user_input)
            
            df_processed = preprocess_user_data(df_raw.copy(), self.resources["label_encoders"])
            if df_processed.empty:
                messagebox.showerror("Lỗi dữ liệu", "Dữ liệu nhập vào không hợp lệ.")
                return
                
            df_final = df_processed[self.resources["feature_order"]]
            prediction = self.resources["model"].predict(df_final)[0]
            
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", tk.END)
            
            self.result_text.insert(tk.END, support_results.get("disclaimer", "") + "\n", "disclaimer")

            if prediction == 1:
                title = '⚠️ Mức độ Lo âu / Căng thẳng: CAO'
            else:
                title = '✅ Mức độ Lo âu / Căng thẳng: THẤP - TRUNG BÌNH'
            
            self.result_text.insert(tk.END, title + "\n", "title_red" if prediction == 1 else "title_green")

            if support_results.get("critical_alerts"):
                self.result_text.insert(tk.END, "❗ Cảnh báo Quan trọng:\n", "subtitle")
                self.result_text.insert(tk.END, "\n".join(support_results.get("critical_alerts", [])) + "\n\n")

            if support_results.get("observations"):
                self.result_text.insert(tk.END, "💡 Nhận định từ hệ thống:\n", "subtitle")
                for obs in support_results.get("observations", []):
                    self.result_text.insert(tk.END, f"  • {obs}\n")

            if support_results.get("resource_categories"):
                self.result_text.insert(tk.END, "🧾 Gợi ý và Nguồn lực:\n", "subtitle")
                for category in support_results.get("resource_categories", []):
                    self.result_text.insert(tk.END, f"  - {category.get('title', '')}:\n", "bold_text")
                    self.result_text.insert(tk.END, f"    {category.get('content', '')}\n")
            
            self.result_text.config(state="disabled")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã có lỗi không xác định xảy ra: {e}")
            traceback.print_exc()

if __name__ == '__main__':
    app = DepressionApp()
    app.mainloop()