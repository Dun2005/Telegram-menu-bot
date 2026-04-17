import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from config import TELEGRAM_TOKEN
from llm import chat_with_ai
from payment import create_payment_link
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from order import calculate_total_amount

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Bộ nhớ tạm (In-memory) để lưu ngữ cảnh chat của từng khách hàng
user_sessions = {}

pending_orders = {}
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_sessions[user_id] = []
    
    # 1. Tạo các nút bấm
    kb = [
        [KeyboardButton(text="📜 Xem Menu")]
        
    ]
    
    # 2. Đóng gói thành bàn phím (resize_keyboard=True để nút không bị quá to)
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb, 
        resize_keyboard=True, 
        input_field_placeholder="Chọn thao tác hoặc gõ yêu cầu..."
    )
    
    welcome_text = "Chào bạn! Mình là AI Assistant của quán. Mình có thể giúp gì cho bạn hôm nay?"
    
    # 3. Gửi tin nhắn kèm bàn phím
    await message.answer(welcome_text, reply_markup=keyboard)

@dp.message(F.text)
async def handle_chat(message: types.Message):
    """Xử lý mọi tin nhắn text của khách hàng"""
    user_id = message.from_user.id
    user_text = message.text

    # Lấy lịch sử chat (nếu bot vừa khởi động lại mà khách chat tiếp)
    if user_id not in user_sessions:
        user_sessions[user_id] = []
    
    chat_history = user_sessions[user_id]

    # Hiển thị hành động "đang gõ..." cho có cảm giác giống người thật
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # Gọi OpenAI xử lý
    response = await chat_with_ai(str(user_id), user_text, chat_history)

    # Cập nhật lịch sử chat
    user_sessions[user_id].append({"role": "user", "content": user_text})
    
    if response["status"] == "chatting":
        # Bot chỉ chat bình thường
        ai_reply = response["reply"]
        user_sessions[user_id].append({"role": "assistant", "content": ai_reply})
        await message.answer(ai_reply)

    elif response["status"] == "checkout":
        ai_reply = response["reply"]
        order_data = response["order_data"] # Cục JSON do OpenAI nhả ra
        user_sessions[user_id].append({"role": "assistant", "content": ai_reply})
        await message.answer(ai_reply)

        # --- GỌI THANH TOÁN (ĐÃ XÓA HARDCODE) ---
        # 1. Lấy danh sách các món khách gọi
        items_list = order_data.get("items", []) 
        
        # 2. Truyền vào hàm để tra giá trong file CSV
        total_amount = calculate_total_amount(items_list, menu_file='../menu.csv')
        
        # 3. Bắt lỗi nếu tính tiền thất bại (tổng = 0)
        if total_amount == 0:
            await message.answer("Xin lỗi bạn, mình gặp chút sự cố khi tính tiền. Bạn có thể đặt lại giúp mình không?")
            user_sessions[user_id] = [] # Xóa giỏ hàng để đặt lại
            return 
        
        # 4. Tạo link payOS với số tiền thực tế
        payment_info = create_payment_link(amount=total_amount, order_description=f"Thanh toan bill {user_id}", timeout_minutes=15)
        
        if payment_info["success"]:
            order_code = payment_info["order_code"]
            
            # GHI VÀO SỔ TAY: Mã đơn này là của người khách này
            pending_orders[order_code] = user_id

            bill_text = f"💰 **Tổng bill của bạn là: {total_amount:,} VNĐ**\n\n"
            bill_text += "Bạn click vào link dưới đây để lấy mã QR thanh toán nhé (Link có hạn trong 15 phút):\n"
            bill_text += f"🔗 {payment_info['checkout_url']}"
            
            await message.answer(bill_text, parse_mode="Markdown")
        else:
            await message.answer("Xin lỗi bạn, hệ thống thanh toán đang gặp chút sự cố. Bạn chờ xíu nhé!")

        # Reset giỏ hàng sau khi ra link QR
        user_sessions[user_id] = []
    elif response["status"] == "show_menu":
        ai_reply = response["reply"]
        user_sessions[user_id].append({"role": "assistant", "content": ai_reply})
        
        # Gửi ảnh menu
        photo = FSInputFile("../menu_image.png")
        await message.answer_photo(photo=photo, caption=ai_reply)
    elif response["status"] == "cancel":
        user_sessions[user_id] = [] # Reset giỏ hàng
        await message.answer("Dạ vâng, mình đã hủy yêu cầu vừa rồi. Bạn muốn dùng món khác thì cứ nhắn mình nha!")