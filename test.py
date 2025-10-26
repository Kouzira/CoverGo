import pandas as pd
import matplotlib.pyplot as plt
import google.generativeai as genai
from PIL import Image
import os
import re
import json
import glob
import pdfplumber
import markdown
import time

# --- TOÀN BỘ PHẦN CÀI ĐẶT FONT PDF ĐÃ ĐƯỢC XÓA BỎ ---

# --- HÀM 1: ĐỌC PDF TEMPLATE (Giữ nguyên) ---
def extract_text_from_pdf(pdf_path):
    """
    Trích xuất toàn bộ văn bản từ file PDF.
    """
    print(f"Dang doc file template PDF: {pdf_path}...")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        
        if not full_text.strip():
            print("Canh bao: File PDF template khong co van ban hoac khong the doc.")
            return None
            
        print("Da trich xuat van ban tu PDF template thanh cong.")
        return full_text
    except Exception as e:
        print(f"Loi khi doc file PDF template: {e}")
        return None


# --- HÀM 2: GỌI GEMINI LẦN 1 (Giữ nguyên) ---
def get_charting_code_from_gemini(csv_file_path, api_key):
    """
    (LẦN GỌI 1) Yêu cầu Gemini trả về JSON chứa 'chart_title' và 'python_code'.
    """
    print(f"\n--- Dang phan tich file: {csv_file_path} ---")
    try:
        df = pd.read_csv(csv_file_path)
        csv_sample = df.head(10).to_string()
        csv_columns = df.columns.tolist()
        base_name = os.path.basename(csv_file_path).replace('.csv', '')
        safe_base_name = re.sub(r'[\\/*?:"<>|]', '_', base_name)
    except Exception as e:
        print(f"Loi khi doc CSV '{csv_file_path}': {e}")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-pro')
        print(f"Dang gui yeu cau phan tich CSV '{csv_file_path}' den Gemini...")
        
        prompt = f"""
        Ban la mot chuyen gia phan tich du lieu bang Python.
        Toi co mot file CSV ten la '{csv_file_path}' (cot: {csv_columns}).
        Day la du lieu mau:
        {csv_sample}

        Nhiem vu cua ban la:
        1. Phan tich du lieu va de xuat (toi da 2) bieu do huu ich nhat.
        2. Tra ve mot JSON ARRAY. Moi object trong array phai co 2 key:
           - "chart_title": Mot string Tieu de tieng Viet cho bieu do.
           - "python_code": Mot string chua code Python (dung matplotlib) de ve bieu do do.

        Yeu cau cho "python_code":
        - Code PHAI luu file vao thu muc 'charts/'.
        - Ten file PHAI bat dau bang '{safe_base_name}_'.
        - Code PHAI dung plt.close() sau khi luu.
        - Code gia dinh bien 'df' (pandas DataFrame) da ton tai.

        Hay tra loi chi voi noi dung JSON, khong co ```json ... ``` bao quanh.
        """
        
        response = model.generate_content(prompt)
        print(f"Da nhan phan hoi JSON cho file '{csv_file_path}'.")
        
        try:
            cleaned_text = response.text.strip().replace("```json", "").replace("```", "")
            chart_requests = json.loads(cleaned_text)
            return chart_requests
        except json.JSONDecodeError as json_err:
            print(f"Loi phan tich JSON tu Gemini: {json_err}")
            print(f"Noi dung loi: {response.text}")
            return None
    
    except Exception as e:
        print(f"Loi khi goi Gemini (Lan 1): {e}")
        return None


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
        print(f"Loi khi thuc thi code cua Gemini: {e}\n--- Code bi loi ---\n{code_block}\n--- Ket thuc code loi ---")
        return "error"


# --- HÀM 4: GỌI GEMINI LẦN 2 (Giữ nguyên) ---
def get_report_from_gemini(all_charts_info, template_text, api_key):
    """
    (LẦN GỌI 2) Gửi danh sách ảnh (và placeholder) để Gemini viết báo cáo.
    """
    print(f"\n--- Dang gui {len(all_charts_info)} bieu do tong hop len Gemini (Lan 2) ---")
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"Loi cau hinh API key: {e}")
        return None

    try:
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        charts_list_for_prompt = []
        for chart in all_charts_info:
            charts_list_for_prompt.append(
                f"- Tieu de: \"{chart['title']}\"\n  Tag de chen: [INSERT_CHART: {chart['filename']}]"
            )
        charts_list_string = "\n".join(charts_list_for_prompt)
        
        image_parts = [Image.open(chart['filename']) for chart in all_charts_info]

        # --- PROMPT ĐÃ ĐƯỢC CẬP NHẬT NGHIÊM NGẶT HƠN ---
        prompt_parts = [
            "Ban la mot nha phan tich du lieu cap cao, dang viet mot bao cao chuyen nghiep.",
            f"Hay phan tich tat ca {len(image_parts)} bieu do duoc cung cap.",
            "\nHay viet mot bao cao TONG HOP hoan chinh (viet bang kieu Markdown), su dung van phong, cau truc, va cac de muc tu van ban mau duoi day:",
            "--- VAN BAN MAU (TU PDF) ---",
            template_text,
            "--- KET THUC MAU ---",
            
            "\n--- QUY TAC BAT BUOC ---",
            "Day la danh sach cac bieu do ban co the su dung:",
            charts_list_string,
            "\nKhi ban phan tich mot bieu do va muon no hien thi ngay sau doan van ban do,",
            "hay CHEN NGUYEN VEN DONG 'Tag de chen' (vi du: [INSERT_CHART: charts/ten_file.png]) vao mot DONG RIENG.",
            "Hay su dung dung dinh dang Markdown (vi du: # Tieu de, ## Tieu de phu, * De muc, **in dam**).",
            "\nQUAN TRỌNG: Bắt đầu báo cáo NGAY LẬP TỨC.",
            "Phản hồi của bạn CHỈ được chứa nội dung báo cáo bằng Markdown.",
            "KHÔNG viết bất kỳ lời chào, lời giới thiệu hay câu xác nhận nào (như 'Chắc chắn rồi...', 'Dưới đây là...').",
            "Bắt đầu ngay với dòng tiêu đề (ví dụ: `# Báo cáo Phân tích`).",
            "\n Không được copy nội dung trong template vào bài report",
            "\n Có dự đoán cho thị trường trong 1 tháng tiếp theo",
            "\n Xác định chính xác ngày tháng trong file báo cáo dựa vào các thông tin dữ liệu",
            "\nDay la cac bieu do (dung de xem):",
        ]
        prompt_parts.extend(image_parts)

        response = model.generate_content(prompt_parts)
        print("Da nhan phan tich bao cao TONG HOP tu Gemini.")
        
        return response.text

    except Exception as e:
        print(f"Loi khi goi Gemini (Lan 2): {e}")
        return None


# --- HÀM 5: TẠO HTML (Giữ nguyên) ---
def create_html_report(analysis_text, all_charts_info, output_filename="BaoCaoTongHop.html"):
    """
    Tạo file HTML, chuyển đổi Markdown và chèn ảnh vào đúng vị trí.
    """
    print(f"\nBat dau tao file HTML: {output_filename}...")
    
    # Tạo một dictionary để tra cứu title từ filename
    title_lookup = {chart['filename']: chart['title'] for chart in all_charts_info}

    # Hàm nội bộ để thay thế tag [INSERT_CHART:...] bằng thẻ <img>
    def replace_chart_tag(match):
        img_path = match.group(1).strip()
        if os.path.exists(img_path):
            title = title_lookup.get(img_path, os.path.basename(img_path))
            # Trả về thẻ HTML hoàn chỉnh cho biểu đồ
            return f"""
<div class="chart-container">
    <img src="{img_path}" alt="{title}">
    <p class="caption">Hình: {title}</p>
</div>
"""
        else:
            return f"""<p style="color: red;">[Loi: Khong tim thay anh tai {img_path}]</p>"""

    # --- Bước 1: Tiền xử lý, thay thế các tag [INSERT_CHART:...] bằng HTML ---
    # re.IGNORECASE để phòng trường hợp Gemini viết sai (ví dụ: [insert_chart:...)
    processed_text = re.sub(
        r"\[INSERT_CHART:\s*(.*?)\s*\]", 
        replace_chart_tag, 
        analysis_text, 
        flags=re.IGNORECASE | re.DOTALL
    )

    # --- Bước 2: Chuyển đổi toàn bộ văn bản (đã chèn <img>) từ Markdown sang HTML ---
    # 'fenced_code' cho phép ```code```
    # 'tables' cho phép Markdown tạo bảng
    html_body = markdown.markdown(processed_text, extensions=['fenced_code', 'tables'])

    # --- Bước 3: Tạo một file HTML hoàn chỉnh với CSS cơ bản ---
    html_template = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo cáo Phân tích Tự động</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            background-color: #f9f9f9;
            color: #333;
            max-width: 900px;
            margin: 20px auto;
            padding: 25px;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        h1, h2, h3 {{
            border-bottom: 2px solid #eee;
            padding-bottom: 5px;
            color: #2c3e50;
        }}
        h1 {{ font-size: 2em; }}
        h2 {{ font-size: 1.5em; }}
        h3 {{ font-size: 1.2em; }}
        
        .chart-container {{
            margin: 30px 0;
            padding: 15px;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            background-color: #fff;
            text-align: center;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }}
        
        .caption {{
            font-size: 0.9em;
            font-style: italic;
            color: #777;
            margin-top: 10px;
        }}
        
        p {{
            margin-bottom: 15px;
        }}
        
        ul, ol {{
            padding-left: 30px;
        }}
        
        li {{
            margin-bottom: 5px;
        }}

        /* Style cho code (từ 'fenced_code') */
        pre {{
            background-color: #282c34;
            color: #abb2bf;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        code {{
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            font-size: 0.95em;
        }}
        
        /* Style cho bảng (từ 'tables') */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            border: 1px solid #ccc;
        }}
        th, td {{
            padding: 12px;
            border: 1px solid #ccc;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
    </style>
</head>
<body>
    {html_body}
</body>
</html>
    """

    # --- Bước 4: Lưu file ---
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(html_template)
        print(f"\n*** TAO BAO CAO HTML THANH CONG: {output_filename} ***")
    except Exception as e:
        print(f"Loi khi ghi file HTML: {e}")


# --- HÀM 6: HÀM CHAY CHINH (MAIN) - ĐÃ CẬP NHẬT ---
def main():
    # --- Cau hinh ---
    YOUR_API_KEY = "AIzaSyBfkA1ArqYivqu4MqHof_W874XZacCjsnY"

    TEMPLATE_PDF_FILE = 'bao-cao-chien-luoc-thi-truong-tuan-30-09-04-10-2024.pdf'
    
    CSV_FOLDER = 'csv/'
    CSV_PATTERN = os.path.join(CSV_FOLDER, '*.csv')
    CHART_FOLDER = 'charts'
    
    # --- THAY ĐỔI TÊN FILE OUTPUT ---
    OUTPUT_HTML = 'BaoCaoTongHop_Final.html'
    
    # --- BUOC 0: TAO THU MUC 'charts' ---
    if not os.path.exists(CHART_FOLDER):
        print(f"Dang tao thu muc... '{CHART_FOLDER}'")
        os.makedirs(CHART_FOLDER)

    # Kiem tra cac file can thiet
    if YOUR_API_KEY == "YOUR_API_KEY":
        print("Loi: Vui long thay 'YOUR_API_KEY' bang API Key that.")
        return
    if not os.path.exists(TEMPLATE_PDF_FILE):
        print(f"Loi: Khong tim thay file template '{TEMPLATE_PDF_FILE}'")
        return
    if not os.path.exists(CSV_FOLDER):
        print(f"Loi: Khong tim thay thu muc CSV '{CSV_FOLDER}'")
        return

    # --- BUOC 1: TICH XUAT TEXT TU PDF TEMPLATE ---
    report_template_text = extract_text_from_pdf(TEMPLATE_PDF_FILE)
    if not report_template_text:
        print("Khong the doc PDF template. Dung chuong trinh.")
        return

    # --- BUOC 2: TIM VA XU LY TAT CA CAC FILE CSV ---
    all_charts_info = [] 
    csv_files = glob.glob(CSV_PATTERN)
    
    if not csv_files:
        print(f"Loi: Khong tim thay file CSV nao trong thu muc '{CSV_FOLDER}'.")
        return
        
    print(f"Tim thay {len(csv_files)} file CSV de phan tich: {csv_files}")

    for csv_file in csv_files:
        
        # -----------------------------------------------------------------

        # 2a. Goi Gemini (Lan 1) de lay JSON
        chart_requests = get_charting_code_from_gemini(csv_file, YOUR_API_KEY)
        
        if chart_requests:
            try:
                df_current = pd.read_csv(csv_file)
            except Exception as e:
                print(f"Loi doc file {csv_file}, bo qua: {e}")
                continue
            
            # 2b. Lặp qua từng yêu cầu biểu đồ trong JSON
            for request in chart_requests:
                code_block = request.get('python_code')
                chart_title = request.get('chart_title', 'Bieu do khong co tieu de')
                
                if not code_block:
                    print(f"Canh bao: JSON request thieu 'python_code'.")
                    continue
                        
                # --- [SỬA LỖI 1] THAY THẾ REGEX TÌM KIẾM CHUNG CHUNG ---
                # 2c. Regex 1 bước (Đã sửa lỗi)
                filename = None
                
                # Tìm chính xác chuỗi văn bản bắt đầu bằng 'charts/' và kết thúc bằng '.png'
                # Regex này sẽ bỏ qua các chuỗi khác như 'Ngày'
                path_match = re.search(r"['\"](charts/[^'\"]+\.png)['\"]", code_block)
                
                if path_match:
                    filename = path_match.group(1)
                # --- KẾT THÚC SỬA LỖI 1 ---

                if not filename:
                    print(f"Canh bao: Code tu Gemini thieu 'savefig' hoac regex loi.")
                    print(f"--- Code da bo qua ---\n{code_block}\n--- Ket thuc code ---")
                    continue
                
                # 2d. Thuc thi code
                exec_status = execute_charting_code(code_block, df_current)
                time.sleep(5) # Giữ thời gian chờ I/O
                
                # 2e. Thu thap thong tin neu thanh cong
                if exec_status == "success" and os.path.exists(filename):
                    print(f"-> Da tao thanh cong: {filename} (Tieu de: {chart_title})")
                    all_charts_info.append({'filename': filename, 'title': chart_title})
                elif exec_status == "success":
                      print(f"Loi: Code da chay nhung khong tim thay file {filename}.")
    
    # --- BUOC 3: KIEM TRA KET QUA BIEU DO ---
    if not all_charts_info:
        print("Khong co bieu do nao duoc tao. Dung chuong trinh.")
        return

    print(f"\n--- Tong hop: Da tao duoc {len(all_charts_info)} bieu do ---")
    for chart in all_charts_info:
        print(f"- {chart['filename']} (Tieu de: {chart['title']})")

    # --- BUOC 4: GOI GEMINI (LAN 2) DE VIET BAO CAO TONG HOP ---
    analysis_text = get_report_from_gemini(all_charts_info, report_template_text, YOUR_API_KEY)

    # --- BUOC 5: TAO FILE HTML ---
    if analysis_text:
        create_html_report(analysis_text, all_charts_info, OUTPUT_HTML)
    else:
        print("Khong nhan duoc phan tich tu Gemini (Lan 2). Dung chuong trinh.")


# --- Chạy hàm main ---
if __name__ == "__main__":
    main()