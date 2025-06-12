# 🎓 Student Depression Prediction

Ứng dụng Machine Learning giúp dự đoán mức độ trầm cảm ở sinh viên dựa trên thông tin học tập, sức khỏe và thói quen sinh hoạt.

## 📌 Mục tiêu
- Phát hiện sớm nguy cơ trầm cảm trong sinh viên
- Hỗ trợ ban tư vấn tâm lý trong nhà trường
- Giao diện dễ sử dụng (Tkinter GUI)

## 🧠 Mô hình sử dụng
- ✅ Random Forest (hiệu quả nhất)
- ✅ LightGBM
- ✅ Neural Network (Keras MLP)

## 🛠 Pipeline gồm các bước:
1. Làm sạch dữ liệu
2. Tạo đặc trưng tổng hợp (Stress, Resilience, Risk...)
3. Chia tập train/test
4. Huấn luyện và đánh giá mô hình
5. Giao diện dự đoán bằng tay (GUI)
6. Dự đoán hàng loạt từ file CSV

## 🖥 Giao diện người dùng (Tkinter)

- Dropdown menu: `gender`, `degree`, `city`
- Button chọn Yes/No cho các trường nhị phân
- Giao diện theo chủ đề tối
- Slideshow ảnh nền động

## 📂 Cấu trúc thư mục
## 📈 Một số đặc trưng tổng hợp
- `balanced_life_score`  
- `total_stress`, `sleep_stress_ratio`  
- `resilience_index`, `suicidal_risk_index`

## ▶️ Hướng dẫn chạy nhanh

**1. Cài thư viện**
```bash
pip install -r requirements.txt
python app/app_gui.py
python scripts/predict_csv.py
data/predict/predicted_results.csv