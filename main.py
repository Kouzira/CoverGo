import os
import glob
import time

# Import các module đã tách
import config_manager as config
import report_generator
import data_processor
import gemini_client

def main():
    start_time = time.time()
    
    # --- BUOC 0: DOC CONFIG, KIEM TRA VA TAO THU MUC ---
    if not config.validate_config():
        return # Dừng nếu config lỗi
    config.create_directories() # Tạo folder 'charts/' và 'report/'
    
    # Cấu hình API Key cho module gemini_client
    if not gemini_client.configure_api(config.API_KEY):
        print("Dừng chương trình do lỗi cấu hình API.")
        return

    # --- BUOC 1: TICH XUAT TEXT TU PDF TEMPLATE ---
    report_template_text = report_generator.extract_text_from_pdf(config.TEMPLATE_PDF_FILE)
    if not report_template_text:
        print("Không thể đọc PDF template. Dừng chương trình.")
        return

    # --- BUOC 2: TIM VA XU LY TAT CA CAC FILE CSV ---
    all_charts_info = [] 
    csv_pattern = os.path.join(config.CSV_FOLDER, '*.csv')
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        print(f"Lỗi: Không tìm thấy file CSV nào trong thư mục '{config.CSV_FOLDER}'.")
        return
        
    print(f"Tìm thấy {len(csv_files)} file CSV để phân tích: {csv_files}")

    for csv_file in csv_files:
        # Hàm này sẽ tự gọi Gemini 1, chạy code, và trả về ds chart
        charts_from_file = data_processor.process_csv_file(
            csv_file, 
            config.CHART_FOLDER
        )
        all_charts_info.extend(charts_from_file)

    # --- BUOC 3: KIEM TRA KET QUA BIEU DO ---
    if not all_charts_info:
        print("Không có biểu đồ nào được tạo. Dừng chương trình.")
        return

    print(f"\n--- Tổng hợp: Đã tạo được {len(all_charts_info)} biểu đồ ---")
    for chart in all_charts_info:
        print(f"- {chart['filename']} (Tiêu đề: {chart['title']})")

    # --- BUOC 4: GOI GEMINI (LAN 2) DE VIET BAO CAO TONG HOP ---
    analysis_text = gemini_client.get_report_from_gemini(
        all_charts_info, 
        report_template_text
    )

    # --- BUOC 5: TAO FILE HTML ---
    if analysis_text:
        # Gửi đường dẫn output đầy đủ vào hàm
        report_generator.create_html_report(
            analysis_text, 
            all_charts_info, 
            config.OUTPUT_HTML_PATH 
        )
    else:
        print("Không nhận được phân tích từ Gemini (Lần 2). Dừng chương trình.")
        
    end_time = time.time()
    print(f"\nHoàn tất! Tổng thời gian chạy: {end_time - start_time:.2f} giây.")

# --- Chạy hàm main ---
if __name__ == "__main__":
    main()