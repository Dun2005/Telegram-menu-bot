import pandas as pd

def calculate_total_amount(order_items: list, menu_file: str = 'menu.csv') -> int:
    """Tính tổng tiền dựa trên danh sách món AI bóc ra và bảng giá trong CSV"""
    try:
        df = pd.read_csv(menu_file) 
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file {menu_file}")
        return 0
        
    total = 0
    for item in order_items:
        item_id = item.get("item_id")
        size = item.get("size", "M") # Nếu không nói size thì mặc định là M
        quantity = item.get("quantity", 1)
        
        matched_item = df[df['item_id'] == item_id]
        if not matched_item.empty:
            # Lấy giá tương ứng với size
            if size == "L":
                price = matched_item['price_l'].values[0]
            else:
                price = matched_item['price_m'].values[0]
            
            total += int(price) * int(quantity)
            
    return total