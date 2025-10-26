import configparser
import os

# Đọc file config
config = configparser.ConfigParser()
config.read('config.ini')

# --- Đọc các giá trị ---
# [API]
API_KEY = config['API'].get('GEMINI_API_KEY', 'YOUR_API_KEY')

# [PATHS]
TEMPLATE_PDF_FILE = config['PATHS'].get('TEMPLATE_PDF')
CSV_FOLDER = config['PATHS'].get('CSV_FOLDER')
CHART_FOLDER = config['PATHS'].get('CHART_FOLDER')
REPORT_FOLDER = config['PATHS'].get('REPORT_FOLDER')
OUTPUT_FILENAME = config['PATHS'].get('OUTPUT_FILENAME')

# --- Tạo đường dẫn đầy đủ cho file output ---
# Path này sẽ là 'report/BaoCaoTongHop_Final.html'
OUTPUT_HTML_PATH = os.path.join(REPORT_FOLDER, OUTPUT_FILENAME)

def validate_config():
    """Kiểm tra các giá trị config quan trọng."""
    if API_KEY == 'YOUR_API_KEY' or not API_KEY:
        print("Lỗi: Vui lòng đặt GEMINI_API_KEY trong file config.ini.")
        return False
    
    paths_to_check = {
        "TEMPLATE_PDF_FILE": TEMPLATE_PDF_FILE,
        "CSV_FOLDER": CSV_FOLDER
    }
    
    for name, path in paths_to_check.items():
        if not path:
            print(f"Lỗi: Thiếu giá trị cho {name} trong config.ini")
            return False
        if name != "CSV_FOLDER" and not os.path.exists(path):
            print(f"Lỗi: Không tìm thấy đường dẫn cho {name}: {path}")
            return False
        if name == "CSV_FOLDER" and not os.path.isdir(path):
            print(f"Lỗi: Đường dẫn cho {name} ({path}) không phải là thư mục.")
            return False
            
    print("Cấu hình hợp lệ.")
    return True

def create_directories():
    """Tạo các thư mục output nếu chúng chưa tồn tại."""
    for folder in [CHART_FOLDER, REPORT_FOLDER]:
        if not os.path.exists(folder):
            print(f"Đang tạo thư mục... '{folder}'")
            os.makedirs(folder)