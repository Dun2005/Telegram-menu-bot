import time
from payos import PayOS, PaymentData
from config import PAYOS_CLIENT_ID, PAYOS_API_KEY, PAYOS_CHECKSUM_KEY

# Khởi tạo PayOS client với các Key lấy từ file .env
payos_client = PayOS(
    client_id=PAYOS_CLIENT_ID,
    api_key=PAYOS_API_KEY,
    checksum_key=PAYOS_CHECKSUM_KEY
)

def generate_order_code() -> int:
    """
    Tạo mã đơn hàng ngẫu nhiên.
    """
    return int(time.time() * 1000) % 1000000000

def create_payment_link(amount: int, order_description: str, timeout_minutes: int) -> dict:
    """
    Gọi API của payOS để tạo link/QR thanh toán.
    """
    order_code = generate_order_code()
    
    # Rút gọn description vì payOS giới hạn tối đa 25 ký tự
    safe_description = order_description[:25]
    expired_at = int(time.time()) + (timeout_minutes * 60)

    # Cấu hình dữ liệu thanh toán
    payment_data = PaymentData(
        orderCode=order_code,
        amount=amount,
        description=safe_description,
        cancelUrl="https://t.me/MenuCassoBot",
        returnUrl="https://t.me/MenuCassoBot",
        expiredAt=expired_at 
    )

    try:
        # Gọi API tạo thanh toán
        payment_link_data = payos_client.createPaymentLink(payment_data)
        
        # Hàm này sẽ trả về một Dictionary chứa các link quan trọng
        return {
            "success": True,
            "order_code": order_code,
            "checkout_url": payment_link_data.checkoutUrl, # Link mở ra trang thanh toán của payOS
            "qr_code_url": payment_link_data.qrCode        # Link ảnh mã QR tĩnh (VietQR)
        }
    except Exception as e:
        print(f"❌ Lỗi tạo thanh toán payOS: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# --- TEST NHANH ---
if __name__ == "__main__":
    print("Đang tạo link thanh toán test...")
    # Thử tạo một hóa đơn 50k
    result = create_payment_link(50000, "Thanh toan TS01", 10)
    if result["success"]:
        print(f"✅ Tạo thành công! Mã đơn: {result['order_code']}")
        print(f"🔗 Link thanh toán: {result['checkout_url']}")
    else:
        print("Cần kiểm tra lại API Key trong file .env")