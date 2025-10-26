import pdfplumber
import markdown
import os
import re

# --- HÀM 1: ĐỌC PDF TEMPLATE (Giữ nguyên) ---
def extract_text_from_pdf(pdf_path):
    """
    Trích xuất toàn bộ văn bản từ file PDF.
    """
    print(f"Đang đọc file template PDF: {pdf_path}...")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        
        if not full_text.strip():
            print("Cảnh báo: File PDF template không có văn bản hoặc không thể đọc.")
            return None
            
        print("Đã trích xuất văn bản từ PDF template thành công.")
        return full_text
    except Exception as e:
        print(f"Lỗi khi đọc file PDF template: {e}")
        return None

# --- HÀM 5: TẠO HTML (Cập nhật để nhận đường dẫn đầy đủ) ---
def create_html_report(analysis_text, all_charts_info, output_full_path):
    """
    Tạo file HTML, chuyển đổi Markdown và chèn ảnh vào đúng vị trí.
    """
    print(f"\nBắt đầu tạo file HTML: {output_full_path}...")
    
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
            return f"""<p style="color: red;">[Lỗi: Không tìm thấy ảnh tại {img_path}]</p>"""

    # --- Bước 1: Tiền xử lý, thay thế các tag [INSERT_CHART:...] bằng HTML ---
    processed_text = re.sub(
        r"\[INSERT_CHART:\s*(.*?)\s*\]", 
        replace_chart_tag, 
        analysis_text, 
        flags=re.IGNORECASE | re.DOTALL
    )

    # --- Bước 2: Chuyển đổi toàn bộ văn bản (đã chèn <img>) từ Markdown sang HTML ---
    html_body = markdown.markdown(processed_text, extensions=['fenced_code', 'tables'])

    # --- Bước 3: Tạo một file HTML hoàn chỉnh với CSS cơ bản (Giữ nguyên CSS) ---
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
        
        p {{ margin-bottom: 15px; }}
        ul, ol {{ padding-left: 30px; }}
        li {{ margin-bottom: 5px; }}

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

    # --- Bước 4: Lưu file (Sử dụng đường dẫn đầy đủ) ---
    try:
        with open(output_full_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        print(f"\n*** TẠO BÁO CÁO HTML THÀNH CÔNG: {output_full_path} ***")
    except Exception as e:
        print(f"Lỗi khi ghi file HTML: {e}")