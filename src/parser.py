from ast import Try
import pandas as pd
import json

def load_menu(file_path: str = 'menu.csv') -> str:
    """
    Đọc file CSV, xử lý lỗi font, lọc món đang bán và trả về chuỗi JSON 
    để nhúng vào System Prompt của OpenAI.
    """
    df = pd.read_csv(file_path)
    
    df = df[df['available'].astype(str).str.upper() == 'TRUE']
    
    df = df.drop(columns=['available'])
    
    df = df.fillna(0)

    menu_records = df.to_dict(orient='records')
    
    return json.dumps(menu_records, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    try:
        menu_json = load_menu('../Menu.csv')
        print("✅ Đọc menu thành công! Dưới đây là dữ liệu sẽ nhồi cho AI:\n")
        print(menu_json[:600] + "\n\n... [Đã cắt bớt phần dưới để dễ nhìn] ...")
    except FileNotFoundError:
        print("❌ Lỗi: Không tìm thấy file menu.csv. Hãy kiểm tra lại đường dẫn!")