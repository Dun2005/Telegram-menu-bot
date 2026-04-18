import pandas as pd
import os # Import thêm thư viện os để xài đường dẫn tuyệt đối

def calculate_total_amount(order_items: list, menu_file: str = 'menu.csv') -> int:
    """Tính tổng tiền dựa trên danh sách món AI bóc ra và bảng giá trong CSV"""
    
    # Dùng đường dẫn tuyệt đối để tránh lỗi "Không tìm thấy file" trên Render
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(CURRENT_DIR)
    MENU_FILE_PATH = os.path.join(ROOT_DIR, menu_file)
    
    try:
        df = pd.read_csv(MENU_FILE_PATH) 
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file {MENU_FILE_PATH}")
        return 0
        
    total = 0
    for item in order_items:
        item_id = item.get("item_id")
        size = item.get("size", "M") # Mặc định size M
        quantity = item.get("quantity", 1)
        
        # 1. Tính tiền món chính
        matched_item = df[df['item_id'] == item_id]
        if not matched_item.empty:
            if size == "L":
                price = matched_item['price_l'].values[0]
            else:
                price = matched_item['price_m'].values[0]
            
            total += int(price) * int(quantity)
            
        # 2. Tính tiền topping (NẾU CÓ)
        toppings = item.get("toppings", []) # Lấy danh sách topping, nếu không có thì trả về mảng rỗng []
        for topping in toppings:
            topping_id = topping.get("item_id")
            topping_size = topping.get("size", "M")
            topping_quantity = topping.get("quantity", 1)
            
            matched_topping = df[df['item_id'] == topping_id]
            if not matched_topping.empty:
                if topping_size == "L":
                    topping_price = matched_topping['price_l'].values[0]
                else:
                    topping_price = matched_topping['price_m'].values[0]
                
                # Chú ý: Số lượng topping thường nhân với số lượng ly (item quantity)
                # Ví dụ: 2 ly trà sữa trân châu = 2 phần trà sữa + 2 phần trân châu
                total += int(topping_price) * int(topping_quantity) * int(quantity) 
            
    return total