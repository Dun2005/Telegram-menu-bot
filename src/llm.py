import json
from openai import AsyncOpenAI
from config import OPENAI_API_KEY
from src.parser import load_menu
import openai

# Khởi tạo client OpenAI (Dùng Async vì bot Telegram chạy bất đồng bộ)
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Load menu 1 lần khi khởi động để nhét vào prompt
MENU_JSON = load_menu('menu.csv')

SYSTEM_PROMPT = f"""
Bạn là AI Assistant hỗ trợ đặt món của một quán trà sữa. 
Bạn giao tiếp lịch sự, chuyên nghiệp, xưng là "mình" hoặc "shop" và gọi khách là "bạn" (hoặc "anh/chị" nếu ngữ cảnh phù hợp). Luôn giữ thái độ thân thiện và dạ thưa lễ phép.

Nhiệm vụ của bạn:
1. Tư vấn món cho khách một cách ngắn gọn, súc tích dựa trên MENU dưới đây. Tuyệt đối không tự bịa ra món không có trong menu.
2. Với các món có nhiều size, bắt buộc phải hỏi khách chọn size M hay L.
3. Chủ động gợi ý khách có muốn thêm Topping không.
4. Xác nhận lại toàn bộ danh sách món và tổng tiền trước khi chốt đơn.
5. Khi khách đã đồng ý chốt đơn, BẮT BUỘC HÃY GỌI HÀM `checkout_order` để hệ thống xử lý thanh toán.

*** QUY TẮC QUAN TRỌNG VỀ TOPPING VÀ MÓN CHÍNH ***
Trong thực đơn, có sự trùng lặp từ khóa giữa món chính (Ví dụ: "Trà Sữa Trân Châu Đen" - Mã TS02) và topping (Ví dụ: "Trân Châu Đen" - Mã TP01). Hãy phân tích kỹ ngữ cảnh câu nói của khách:

1. NẾU khách gọi trực tiếp tên món: "Cho 1 trà sữa trân châu đen" -> Đây là MÓN CHÍNH (TS02). Tuyệt đối không tách thành Trà sữa + Topping trân châu.
2. NẾU khách dùng các từ "thêm", "cùng với", "bỏ thêm" vào một món nước khác: "Cho 1 Trà Olong thêm trân châu đen" -> Lúc này Trân Châu Đen đóng vai trò là TOPPING (TP01), phải được đặt vào mảng `toppings` bên trong món Trà Olong.
3. KHÔNG BAO GIỜ để một mã Topping (TP...) đứng đơn độc như một món chính. Topping luôn phải nằm bên trong một món nước.

Bạn không được tính tổng tiền cũng như trả lời tổng tiền
--- MENU QUÁN ---
{MENU_JSON}
--- KẾT THÚC MENU ---
"""

TOOLS = [
    {
    "type": "function",
    "function": {
        "name": "checkout_order",
        "description": "Gọi hàm này khi khách hàng xác nhận chốt đơn để tính tiền.",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "description": "Danh sách các món chính khách đặt",
                    "items": {
                        "type": "object",
                        "properties": {
                            "item_id": {
                                "type": "string", 
                                "description": "Mã món (VD: TS01)"
                            },
                            "quantity": {
                                "type": "integer"
                            },
                            "size": {
                                "type": "string", 
                                "enum": ["M", "L", "none"], 
                                "description": "Size M hoặc L."
                            },
                            "note": {
                                "type": "string", 
                                "description": "Ghi chú (ít đá, ít đường...)"
                            },
                            "toppings": {
                                "type": "array",
                                "description": "Danh sách các topping đi kèm kẹp bên trong món nước này (nếu khách có gọi)",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "item_id": {
                                            "type": "string", 
                                            "description": "Mã topping (VD: TP01)"
                                        },
                                        "quantity": {
                                            "type": "integer",
                                            "description": "Số lượng phần topping"
                                        },
                                        "size": {
                                            "type": "string", 
                                            "enum": ["M", "L", "none"],
                                            "description": "Size của topping, thường để none"
                                        }
                                    },
                                    "required": ["item_id", "quantity"]
                                }
                            }
                        },
                        "required": ["item_id", "quantity", "size"]
                    }
                }
            },
            "required": ["items"]
        }
    }
},
    {
        "type": "function",
        "function": {
            "name": "show_menu_image",
            "description": "Chỉ gọi hàm này khi khách hàng CÓ Ý ĐỊNH yêu cầu xem thực đơn/menu. KHÔNG gọi nếu khách chỉ nhắc đến từ 'menu' trong câu chuyện bình thường.",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_order",
            "description": "Gọi hàm này khi người dùng CÓ Ý ĐỊNH RÕ RÀNG muốn từ chối, hủy bỏ đơn hàng, không muốn tiếp tục mua hoặc muốn đặt lại từ đầu.",
        }
    }
]

async def chat_with_ai(user_id: str, user_message: str, chat_history: list) -> dict:
    """
    Gửi tin nhắn của khách lên OpenAI và nhận phản hồi.
    chat_history: Danh sách các tin nhắn cũ để AI nhớ ngữ cảnh.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + chat_history
    messages.append({"role": "user", "content": user_message})

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo", 
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message

        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                if tool_call.function.name == "checkout_order":
                    order_data = json.loads(tool_call.function.arguments)
                    return {
                        "status": "checkout",
                        "order_data": order_data, 
                        "reply": "Dạ, để mình tổng hợp đơn và lên mã QR thanh toán cho bạn nhé!" 
                    }
                elif tool_call.function.name == "show_menu_image":
                    return {
                        "status": "show_menu",
                        "reply": "Dạ đây là menu của quán, bạn xem muốn uống gì cứ nhắn mình nhé!"
                    }
                elif tool_call.function.name == "cancel_order":
                    return {
                        "status": "cancel",
                        "reply": ""
                    }   
        return {
            "status": "chatting",
            "reply": response_message.content
        }
        
    except openai.RateLimitError:
        # Bắt riêng lỗi hết tiền/quá tải của OpenAI
        return {
            "status": "chatting",
            "reply": "Xin lỗi bạn, hệ thống AI của quán đang tạm bảo trì do hết dung lượng. Bạn vui lòng quay lại sau nhé!"
        }
    except Exception as e:
        # Bắt các lỗi mạng, lỗi server khác
        print(f"Lỗi LLM: {e}")
        return {
            "status": "chatting",
            "reply": "Hệ thống đang gặp sự cố kết nối, bạn chờ mình một chút nha."
        }