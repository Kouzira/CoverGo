import pandas as pd
import google.generativeai as genai
from PIL import Image
import os
import re
import json

def configure_api(api_key):
    """Cấu hình API key cho Gemini."""
    try:
        genai.configure(api_key=api_key)
        print("Đã cấu hình Gemini API thành công.")
        return True
    except Exception as e:
        print(f"Lỗi cấu hình API key: {e}")
        return False

# --- HÀM 2: GỌI GEMINI LẦN 1 (Cập nhật để nhận chart_folder) ---
def get_charting_code_from_gemini(csv_file_path, chart_folder_path):
    """
    (LẦN GỌI 1) Yêu cầu Gemini trả về JSON chứa 'chart_title' và 'python_code'.
    """
    print(f"\n--- Đang phân tích file: {csv_file_path} ---")
    try:
        df = pd.read_csv(csv_file_path)
        csv_sample = df.head(10).to_string()
        csv_columns = df.columns.tolist()
        base_name = os.path.basename(csv_file_path).replace('.csv', '')
        safe_base_name = re.sub(r'[\\/*?:"<>|]', '_', base_name)
    except Exception as e:
        print(f"Lỗi khi đọc CSV '{csv_file_path}': {e}")
        return None

    try:
        # --- SỬA TÊN MODEL (1.5 Pro ổn định hơn 2.5 Pro cho tác vụ này) ---
        model = genai.GenerativeModel('gemini-2.5-pro') 
        print(f"Đang gửi yêu cầu phân tích CSV '{csv_file_path}' đến Gemini...")
        
        prompt = f"""
        Bạn là một chuyên gia phân tích dữ liệu bằng Python.
        Tôi có một file CSV tên là '{csv_file_path}' (cột: {csv_columns}).
        Đây là 10 dòng dữ liệu mẫu:
        {csv_sample}

        Nhiệm vụ của bạn là:
        1. Phân tích dữ liệu và đề xuất (tối đa 2) biểu đồ hữu ích nhất.
        2. Trả về một JSON ARRAY. Mỗi object trong array phải có 2 key:
           - "chart_title": Một string Tiêu đề tiếng Việt cho biểu đồ.
           - "python_code": Một string chứa code Python (dùng matplotlib) để vẽ biểu đồ đó.

        Yêu cầu cho "python_code":
        - Code PHẢI lưu file vào thư mục '{chart_folder_path}'.
        - Tên file PHẢI bắt đầu bằng '{safe_base_name}_'.
        - Code PHẢI dùng plt.close() sau khi lưu.
        - Code giả định biến 'df' (pandas DataFrame) đã tồn tại.

        Hãy trả lời CHỈ với nội dung JSON, không có ```json ... ``` bao quanh.
        """
        
        response = model.generate_content(prompt)
        print(f"Đã nhận phản hồi JSON cho file '{csv_file_path}'.")
        
        try:
            cleaned_text = response.text.strip().replace("```json", "").replace("```", "")
            chart_requests = json.loads(cleaned_text)
            return chart_requests
        except json.JSONDecodeError as json_err:
            print(f"Lỗi phân tích JSON từ Gemini: {json_err}")
            print(f"Nội dung lỗi: {response.text}")
            return None
    
    except Exception as e:
        print(f"Lỗi khi gọi Gemini (Lần 1): {e}")
        return None

# --- HÀM 4: GỌI GEMINI LẦN 2 (Giữ nguyên logic) ---
def get_report_from_gemini(all_charts_info, template_text):
    """
    (LẦN GỌI 2) Gửi danh sách ảnh (và placeholder) để Gemini viết báo cáo.
    """
    print(f"\n--- Đang gửi {len(all_charts_info)} biểu đồ tổng hợp lên Gemini (Lần 2) ---")
    
    try:
        # --- SỬA TÊN MODEL ---
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        charts_list_for_prompt = []
        for chart in all_charts_info:
            charts_list_for_prompt.append(
                f"- Tiêu đề: \"{chart['title']}\"\n  Tag để chèn: [INSERT_CHART: {chart['filename']}]"
            )
        charts_list_string = "\n".join(charts_list_for_prompt)
        
        image_parts = []
        for chart in all_charts_info:
            try:
                # Đảm bảo đường dẫn dùng / (hoặc os.path.normpath)
                img_path = chart['filename'].replace('\\', '/')
                image_parts.append(Image.open(img_path))
            except Exception as img_e:
                print(f"Cảnh báo: Không thể mở ảnh {chart['filename']}. Bỏ qua. Lỗi: {img_e}")
                
        if not image_parts:
             print("Lỗi nghiêm trọng: Không có ảnh nào để gửi cho Gemini.")
             return None

        # --- PROMPT (Giữ nguyên) ---
        prompt_parts = [
            "Bạn là một nhà phân tích dữ liệu cấp cao, đang viết một báo cáo chuyên nghiệp.",
            f"Hãy phân tích tất cả {len(image_parts)} biểu đồ được cung cấp.",
            "\nHãy viết một báo cáo TỔNG HỢP hoàn chỉnh (viết bằng kiểu Markdown), sử dụng văn phong, cấu trúc, và các đề mục từ văn bản mẫu dưới đây:",
            "--- VĂN BẢN MẪU (TỪ PDF) ---",
            template_text,
            "--- KẾT THÚC MẪU ---",
            
            "\n--- QUY TẮC BẮT BUỘC ---",
            "Đây là danh sách các biểu đồ bạn có thể sử dụng:",
            charts_list_string,
            "\nKhi bạn phân tích một biểu đồ và muốn nó hiển thị ngay sau đoạn văn bản đó,",
            "hãy CHÈN NGUYÊN VẸN DÒNG 'Tag để chèn' (ví dụ: [INSERT_CHART: charts/ten_file.png]) vào một DÒNG RIÊNG.",
            "Hãy sử dụng đúng định dạng Markdown (ví dụ: # Tiêu đề, ## Tiêu đề phụ, * Đề mục, **in đậm**).",
            "\nQUAN TRỌNG: Bắt đầu báo cáo NGAY LẬP TỨC.",
            "Phản hồi của bạn CHỈ được chứa nội dung báo cáo bằng Markdown.",
            "KHÔNG viết bất kỳ lời chào, lời giới thiệu hay câu xác nhận nào (như 'Chắc chắn rồi...', 'Dưới đây là...').",
            "Bắt đầu ngay với dòng tiêu đề (ví dụ: `# Báo cáo Phân tích`).",
            "\nKhông được sao chép nội dung trong template vào bài report",
            "\nCó dự đoán cho thị trường trong 1 tháng tiếp theo",
            "\nXác định chính xác ngày tháng trong file báo cáo dựa vào các thông tin dữ liệu",
            "\nĐây là các biểu đồ (dùng để xem):",
        ]
        prompt_parts.extend(image_parts)

        response = model.generate_content(prompt_parts)
        print("Đã nhận phân tích báo cáo TỔNG HỢP từ Gemini.")
        
        return response.text

    except Exception as e:
        print(f"Lỗi khi gọi Gemini (Lần 2): {e}")
        return None