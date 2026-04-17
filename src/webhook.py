from fastapi import FastAPI, Request
from payment import payos_client
from bot import bot, pending_orders

app = FastAPI()

@app.post("/payos-webhook")
async def handle_payos_webhook(request: Request):
    """Điểm nối (Endpoint) để payOS gọi vào khi có người chuyển khoản"""
    
    # 1. Lấy dữ liệu payOS gửi về
    body = await request.json()
    
    try:
        # 2. Xác thực chữ ký để chống hack (Đảm bảo đúng là payOS gửi)
        webhook_data = payos_client.verifyPaymentWebhookData(body)
        
        # 3. Kiểm tra nếu giao dịch thành công (mã "00")
        if webhook_data.code == "00":
            order_code = webhook_data.orderCode
            amount = webhook_data.amount
            
            print(f"💰 Nhận được {amount} cho đơn {order_code}")
            
            # 4. Tìm xem ai là chủ nhân của đơn hàng này
            if order_code in pending_orders:
                user_id = pending_orders[order_code]
                
                # 5. Ra lệnh cho bot Telegram báo tin mừng
                await bot.send_message(
                    chat_id=user_id,
                    text=f"🎉 **Ting ting!** Quán đã nhận được {amount:,} VNĐ.\nMã đơn `{order_code}` của bạn đang được pha chế nhé!",
                    parse_mode="Markdown"
                )
                
                # Xóa khỏi sổ tay cho nhẹ bộ nhớ
                del pending_orders[order_code]
            else:
                print("not found")
                
        return {"success": True}
        
    except Exception as e:
        print(f"❌ Lỗi xử lý Webhook: {e}")
        return {"success": False}