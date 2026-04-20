import asyncio
import logging
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

# Tạm gọi các biến từ file bot.py của bạn
from src.bot import bot, dp, pending_orders 
from src.payment import payos_client

# 1. Khởi tạo FastAPI
app = FastAPI()

# 2. Đưa Endpoint Webhook trực tiếp vào đây
@app.post("/payos-webhook")
async def handle_payos_webhook(request: Request):
    body = await request.json()
    
    try:
        webhook_data = payos_client.verifyPaymentWebhookData(body)
        
        if webhook_data.code == "00":
            order_code = webhook_data.orderCode
            amount = webhook_data.amount
            
            print(f"💰 [WEBHOOK] Nhận được {amount} cho đơn {order_code}")
            
            # Vì lúc này Webhook và Bot chung 1 nhà, ta có thể gọi thẳng bot.send_message
            if order_code in pending_orders:
                order_info = pending_orders[order_code]
                user_id = order_info["user_id"]
                items = order_info["items"]
                total = order_info["total_amount"]
                
                await bot.send_message(
                    chat_id=user_id,
                    text=f"🎉 **Ting ting!** Quán đã nhận được {amount:,} VNĐ.\nMã đơn `{order_code}` của bạn đang được pha chế nhé!",
                    parse_mode="Markdown"
                )

                # --- 2. TỔNG HỢP THÔNG TIN LÀM MÓN VÀ GIAO HÀNG ---
                kitchen_ticket = f"🔔 **PHIẾU BẾP - ĐƠN {order_code}** 🔔\n"
                kitchen_ticket += "---------------------------\n"
                for idx, item in enumerate(items, 1):
                    item_id = item.get("item_id", "Unknown")
                    size = item.get("size", "M")
                    qty = item.get("quantity", 1)
                    note = item.get("note", "Không có")
                    
                    # In món chính
                    kitchen_ticket += f"{idx}. Mã: {item_id} | Size: {size} | SL: {qty}\n"
                    
                    # --- THÊM KHÚC NÀY ĐỂ IN TOPPING ---
                    toppings = item.get("toppings", [])
                    if toppings:
                        for t in toppings:
                            t_id = t.get("item_id")
                            t_qty = t.get("quantity", 1)
                            kitchen_ticket += f"   ➕ Topping: Mã {t_id} (SL: {t_qty})\n"
                    # -----------------------------------
                            
                    # In ghi chú
                    if note != "none" and note != "":
                        kitchen_ticket += f"   📝 Ghi chú: {note}\n"
                
                kitchen_ticket += "---------------------------\n"
                kitchen_ticket += f"Khách hàng (Telegram ID): `{user_id}`\n"
                kitchen_ticket += "Trạng thái: ĐÃ THANH TOÁN ✅\n\n"
                
                kitchen_ticket += "_(💡 Ghi chú của Dev: Trong thực tế, phiếu này sẽ được tự động gửi vào một Group Telegram riêng của nhân viên pha chế. Nhưng để test, hệ thống sẽ gửi thẳng phiếu này lại cho bạn để demo nhé!)_"
                
                # Gửi phiếu bếp này thẳng cho người order (user_id) để họ thấy được luồng dữ liệu
                await bot.send_message(
                    chat_id=user_id,
                    text=kitchen_ticket,
                    parse_mode="Markdown"
                )
                del pending_orders[order_code] # Gạch tên khỏi sổ
                
        return {"success": True}
    except Exception as e:
        print(f"❌ Lỗi xử lý Webhook: {e}")
        return {"success": False}

@app.get("/")
async def root():
    return {"message": "Bot is running mượt mà!", "status": "ok"}

@app.head("/")
async def root_head():
    return {"status": "ok"}

async def setup_bot_commands():
    commands = [
        BotCommand(command="start", description="Bắt đầu/Khởi động lại bot"),
        BotCommand(command="menu", description="Xem thực đơn quán"),
    ]
    await bot.set_my_commands(commands)

# 3. Kích hoạt Bot khi FastAPI khởi động
@app.on_event("startup")
async def on_startup():
    logging.basicConfig(level=logging.INFO)
    print("🚀 Khởi động Server tích hợp cả Webhook và Bot...")
    
    await setup_bot_commands()
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Tạo một task chạy ngầm cho bot Telegram
    asyncio.create_task(dp.start_polling(bot))
