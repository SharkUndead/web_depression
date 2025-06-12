import pandas as pd
import random

city_level_map = {
    # S - Siêu đô thị
    'Mumbai': 'S',
    'Delhi': 'S',

    # I - Đô thị trung tâm
    'Bangalore': 'I', 'Kolkata': 'I', 'Chennai': 'I', 'Hyderabad': 'I',

        # II - Công nghiệp / Kinh tế lớn
    'Pune': 'II', 'Ahmedabad': 'II', 'Surat': 'II', 'Kanpur': 'II',

        # III - Thủ phủ & Vùng
    'Lucknow': 'III', 'Jaipur': 'III', 'Nagpur': 'III', 'Indore': 'III',
    'Patna': 'III', 'Bhopal': 'III', 'Visakhapatnam': 'III',

        # IV - Vệ tinh & CN nhỏ
    'Thane': 'IV', 'Ghaziabad': 'IV', 'Faridabad': 'IV', 'Vadodara': 'IV',
    'Meerut': 'IV', 'Nashik': 'IV', 'Kalyan': 'IV', 'Vasai-Virar': 'IV',
    'Rajkot': 'IV', 'Ludhiana': 'IV',

        # V - Đặc thù
    'Srinagar': 'V', 'Varanasi': 'V', 'Agra': 'V'
    }
vn_city_groups = {
    'Đặc Biệt': ['Hà Nội', 'TP. Hồ Chí Minh'],
    'I': ['Hải Phòng', 'Đà Nẵng', 'Cần Thơ'],
    'II': ['Bình Dương', 'Đồng Nai', 'Bà Rịa - Vũng Tàu', 'Bắc Ninh', 'Quảng Ninh', 'Vĩnh Phúc', 'Thái Nguyên', 'Hải Dương'],
    'III': ['Thanh Hóa', 'Nghệ An', 'Khánh Hòa', 'Thừa Thiên Huế', 'Long An', 'Tiền Giang', 'Bắc Giang', 'Quảng Nam', 'Bình Định', 'Đắk Lắk'],
    'IV': ['Thái Bình', 'Hưng Yên', 'Nam Định', 'Hà Nam', 'Ninh Bình',
        'Bình Thuận', 'Phú Yên', 'Quảng Ngãi', 'Hà Tĩnh', 'Quảng Bình', 'Quảng Trị', 'Ninh Thuận',
        'An Giang', 'Kiên Giang', 'Bến Tre', 'Vĩnh Long', 'Trà Vinh', 'Sóc Trăng', 'Bạc Liêu', 'Cà Mau', 'Hậu Giang'],
    'V': ['Hà Giang', 'Cao Bằng', 'Bắc Kạn', 'Lạng Sơn', 'Tuyên Quang', 'Yên Bái', 'Lào Cai', 'Lai Châu',
        'Điện Biên', 'Sơn La', 'Hòa Bình', 'Kon Tum', 'Gia Lai', 'Đắk Nông', 'Lâm Đồng', 'Bình Phước', 'Tây Ninh'],
    'Di sản': ['Huế', 'Quảng Nam', 'Lâm Đồng', 'Ninh Bình']
    }

def map_indian_city_to_vietnamese(city):
        level = city_level_map.get(city)
        if not level:
            return "Khác"

        if level == 'S':
            choices = vn_city_groups['Đặc Biệt'] * 7 + vn_city_groups['I'] * 2 + vn_city_groups['II']
        elif level == 'I':
            choices = vn_city_groups['Đặc Biệt'] * 4 + (vn_city_groups['I'] + vn_city_groups['II']) * 4 + vn_city_groups['III'] * 2
        elif level == 'II':
            choices = vn_city_groups['II'] * 5 + (vn_city_groups['I'] + vn_city_groups['Đặc Biệt']) * 3 + vn_city_groups['III'] * 2
        elif level == 'III':
            choices = vn_city_groups['III'] * 4 + vn_city_groups['IV'] * 3 + vn_city_groups['II'] * 2 + (vn_city_groups['I'] + vn_city_groups['Đặc Biệt'])
        elif level == 'IV':
            choices = vn_city_groups['IV'] * 5 + vn_city_groups['III'] * 3 + vn_city_groups['V'] + vn_city_groups['II']
        elif level == 'V':
            choices = vn_city_groups['Di sản'] * 6 + (vn_city_groups['IV'] + vn_city_groups['III']) * 3 + ['Khác']
        else:
            return "Khác"

        return random.choice(choices)
