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
                user_id = pending_orders[order_code]
                
                # GỬI TIN NHẮN TỨC THÌ KHÔNG CẦN CHỜ ĐỢI
                await bot.send_message(
                    chat_id=user_id,
                    text=f"🎉 **Ting ting!** Quán đã nhận được {amount:,} VNĐ.\nMã đơn `{order_code}` của bạn đang được pha chế nhé!",
                    parse_mode="Markdown"
                )
                del pending_orders[order_code] # Gạch tên khỏi sổ
                
        return {"success": True}
    except Exception as e:
        print(f"❌ Lỗi xử lý Webhook: {e}")
        return {"success": False}


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
