# utils/advice_engine.py

def generate_support_resources(user_input):
    """
    Phân tích dữ liệu người dùng để cung cấp thông tin, giáo dục tâm lý và các
    nguồn lực tham khảo nhằm trao quyền cho người dùng tự chăm sóc sức khỏe tinh thần.
    Hàm này TUYỆT ĐỐI KHÔNG đưa ra lời khuyên chẩn đoán hay mệnh lệnh.
    """
    # THAY ĐỔI 1: Tăng cường mức độ chi tiết và trách nhiệm của các kết quả
    results = {
        "disclaimer": "QUAN TRỌNG: Công cụ này không phải là một công cụ chẩn đoán y khoa và không thể thay thế cho sự tư vấn từ các chuyên gia. Mục đích của nó là cung cấp thông tin để bạn tự phản ánh và tham khảo các nguồn lực phù hợp.",
        "critical_alerts": [],
        "resource_categories": [] # Thay 'observations' và 'suggestions' bằng một cấu trúc mới
    }
    
    try:
        academic_pressure = float(user_input.get('academic_pressure', 0))
        financial_stress = float(user_input.get('financial_stress', 0))
        work_study_hours = float(user_input.get('work/study_hours', 0))
        sleep_hours_map = {'Less than 5 hours': 4.5, '5-6 hours': 5.5, '7-8 hours': 7.5, 'More than 8 hours': 9.0}
        sleep_hours = sleep_hours_map.get(user_input.get('sleep_duration'), 7.5)
        had_suicidal_thoughts = 1 if user_input.get('have_you_ever_had_suicidal_thoughts_?') == 'Yes' else 0
    except (ValueError, TypeError):
        results["critical_alerts"].append("Dữ liệu đầu vào không hợp lệ, không thể xử lý.")
        return results

    # THAY ĐỔI 2: Xử lý cảnh báo khẩn cấp một cách cẩn trọng và có trách nhiệm
    if had_suicidal_thoughts == 1:
        results["critical_alerts"].append(
            "Hệ thống ghi nhận bạn đã chia sẻ về những suy nghĩ liên quan đến việc tự tử. "
            "Việc chia sẻ điều này đòi hỏi rất nhiều can đảm. Điều quan trọng nhất lúc này là bạn biết rằng bạn không đơn độc và sự giúp đỡ luôn sẵn có."
        )
        results["resource_categories"].append({
            "title": "❗ KẾT NỐI HỖ TRỢ KHẨN CẤP",
            "content": (
                "Sự an toàn của bạn là ưu tiên tuyệt đối. Nếu bạn đang ở trong một cuộc khủng hoảng, vui lòng liên hệ ngay với một trong các nguồn lực chuyên nghiệp và bảo mật dưới đây. Họ được đào tạo để lắng nghe và hỗ trợ bạn.<br>"
                "• <b>Đường dây nóng Ngày Mai:</b> 1900 6233<br>"
                "• <b>Đường dây nóng Sức khỏe Tâm thần (Bệnh viện Bạch Mai):</b> 1900 545484<br>"
                "<i>(Lưu ý: Vui lòng kiểm tra lại số điện thoại và giờ hoạt động trước khi gọi.)</i>"
            )
        })
    
    # THAY ĐỔI 3: Chuyển từ "lời khuyên" sang "thông tin & hướng tiếp cận"
    if academic_pressure >= 4:
        results["resource_categories"].append({
            "title": "💡 Về Áp lực Học tập",
            "content": (
                "Hệ thống ghi nhận áp lực học tập của bạn đang ở mức cao. Đây là một trải nghiệm rất phổ biến trong môi trường giáo dục, nhưng nó có thể ảnh hưởng đến động lực và sức khỏe tổng thể. "
                "Áp lực kéo dài có thể làm giảm khả năng tập trung và ghi nhớ.<br><br>"
                "<b>Một số hướng tiếp cận bạn có thể tham khảo:</b><br>"
                "• <b>Phân chia nhiệm vụ:</b> Kỹ thuật 'chia để trị' (chia công việc lớn thành các bước nhỏ) có thể giúp giảm cảm giác quá tải.<br>"
                "• <b>Đối thoại cởi mở:</b> Trao đổi với giảng viên hoặc cố vấn học tập về những khó khăn có thể mở ra các hướng hỗ trợ mà bạn chưa biết."
            )
        })

    if financial_stress >= 4:
        results["resource_categories"].append({
            "title": "💡 Về Căng thẳng Tài chính",
            "content": (
                "Việc lo lắng về tài chính là một nguồn gây căng thẳng đáng kể và có thể ảnh hưởng đến mọi khía cạnh của cuộc sống. Bạn không hề đơn độc khi đối mặt với điều này.<br><br>"
                "<b>Một số nguồn lực có thể hữu ích:</b><br>"
                "• <b>Hỗ trợ từ nhà trường:</b> Phòng công tác sinh viên thường có thông tin về các chương trình học bổng, miễn giảm hoặc hỗ trợ tài chính.<br>"
                "• <b>Kiến thức tài chính cá nhân:</b> Tìm hiểu về cách lập ngân sách đơn giản có thể giúp bạn cảm thấy kiểm soát tốt hơn tình hình của mình."
            )
        })

    if sleep_hours < 6:
        results["resource_categories"].append({
            "title": "💡 Về Giấc ngủ và Sức khỏe Tinh thần",
            "content": (
                f"Giấc ngủ ({sleep_hours} giờ/đêm) và cảm xúc có một mối liên kết hai chiều. Thiếu ngủ làm giảm khả năng điều tiết cảm xúc, và ngược lại, căng thẳng gây khó ngủ. "
                "Cải thiện giấc ngủ là một trong những nền tảng quan trọng nhất để xây dựng sức chịu đựng (resilience) trước stress.<br><br>"
                "<b>Khám phá về 'Vệ sinh giấc ngủ':</b><br>"
                "• Đây là một tập hợp các thói quen tốt cho giấc ngủ, ví dụ như: duy trì giờ ngủ/thức nhất quán, tạo không gian ngủ tối và yên tĩnh, hạn chế caffeine vào buổi chiều."
            )
        })

    # Thông điệp mặc định nếu không có cảnh báo hay gợi ý nào
    if not results["resource_categories"] and not results["critical_alerts"]:
        results["resource_categories"].append({
            "title": "🎉 Ghi nhận những điểm tích cực",
            "content": "Các thông tin bạn cung cấp cho thấy bạn đang có những chiến lược tự chăm sóc và đối mặt hiệu quả với các thách thức trong cuộc sống. Điều này thể hiện một sức mạnh nội tại đáng quý. Hãy tiếp tục lắng nghe và trân trọng những nhu cầu của bản thân mình nhé."
        })

    return results