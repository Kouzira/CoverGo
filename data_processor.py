import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import time

# Import các module khác
import gemini_client

# --- HÀM 3: THỰC THI CODE (Giữ nguyên) ---
def execute_charting_code(code_block, df):
    """
    Thực thi MỘT khối code Python.
    """
    try:
        exec_scope = {'df': df, 'plt': plt, 'pd': pd, 'os': os} 
        exec(code_block, exec_scope)
        return "success"
    except Exception as e:
        print(f"Lỗi khi thực thi code của Gemini: {e}\n--- Code bị lỗi ---\n{code_block}\n--- Kết thúc code lỗi ---")
        return "error"

def process_csv_file(csv_file, chart_folder_path):
    """
    Xử lý một file CSV:
    1. Gọi Gemini (Lần 1) để lấy code.
    2. Thực thi code để tạo biểu đồ.
    3. Trả về danh sách thông tin các biểu đồ đã tạo thành công.
    """
    charts_info = []
    
    # 2a. Goi Gemini (Lan 1) de lay JSON
    # Chuyển chart_folder_path vào hàm gọi gemini
    chart_requests = gemini_client.get_charting_code_from_gemini(csv_file, chart_folder_path)
    
    if not chart_requests:
        return charts_info # Trả về danh sách rỗng

    try:
        df_current = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Lỗi đọc file {csv_file}, bỏ qua: {e}")
        return charts_info # Trả về danh sách rỗng
    
    # 2b. Lặp qua từng yêu cầu biểu đồ trong JSON
    for request in chart_requests:
        code_block = request.get('python_code')
        chart_title = request.get('chart_title', 'Biểu đồ không có tiêu đề')
        
        if not code_block:
            print(f"Cảnh báo: JSON request thiếu 'python_code'.")
            continue
            
        # 2c. Regex 2 bước để tìm tên file
        filename = None
        savefig_match = re.search(r"savefig\((.*?)\)", code_block, re.DOTALL) 
        
        if savefig_match:
            params_string = savefig_match.group(1)
            # Tìm chuỗi trong dấu nháy đơn hoặc nháy kép
            filename_match = re.search(r"['\"]([^'\"]*)['\"]", params_string)
            if filename_match:
                filename = filename_match.group(1)

        if not filename:
            print(f"Cảnh báo: Code từ Gemini thiếu 'savefig' hoặc regex lỗi.")
            print(f"--- Code đã bỏ qua ---\n{code_block}\n--- Kết thúc code ---")
            continue
        
        # 2d. Thuc thi code
        exec_status = execute_charting_code(code_block, df_current)
        time.sleep(5)
        
        # 2e. Thu thap thong tin neu thanh cong
        if exec_status == "success" and os.path.exists(filename):
            print(f"-> Đã tạo thành công: {filename} (Tiêu đề: {chart_title})")
            charts_info.append({'filename': filename, 'title': chart_title})
        elif exec_status == "success":
            print(f"Lỗi: Code đã chạy nhưng không tìm thấy file {filename}.")
            
    return charts_info