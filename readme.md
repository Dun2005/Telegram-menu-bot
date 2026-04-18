# 🤖 Telegram AI Menu Bot

Dự án này là một hệ thống đặt món tự động qua Telegram cho quán **Trà Sữa Casso**, tích hợp trí tuệ nhân tạo (AI) để xử lý ngôn ngữ tự nhiên và hệ thống thanh toán thời gian thực qua **PayOS**.

---

## 🌟 Điểm nổi bật kỹ thuật

- **Kiến trúc Single-Process:** Dự án sử dụng **FastAPI** làm máy chủ trung tâm để chạy song song cả Telegram Bot (aiogram) và Webhook endpoint. Kiến trúc này giúp tối ưu tài nguyên, chia sẻ bộ nhớ (RAM) tức thì và đạt độ trễ gần như bằng 0 (Zero-delay) trong việc xử lý xác nhận thanh toán.
- **AI Function Calling:** Sử dụng OpenAI API với kỹ thuật **Function Calling** để bóc tách dữ liệu từ câu chat tự nhiên (món ăn, size, số lượng, ghi chú) thành cấu trúc JSON chuẩn, giúp hệ thống xử lý đơn hàng linh hoạt và chính xác.
- **Thanh toán Real-time:** Tích hợp PayOS Webhook để xác nhận trạng thái thanh toán ngay lập tức (Real-time) và tự động phản hồi khách hàng ngay khi tiền vào tài khoản.
- **Nghiệp vụ vận hành (Kitchen Ticket):** Sau khi xác nhận thanh toán thành công, hệ thống tự động tổng hợp "Phiếu Bếp" đầy đủ thông tin để sẵn sàng cho khâu pha chế và giao hàng.

## 🛠 Tech Stack

- **Ngôn ngữ:** Python 3.12+
- **Framework:** FastAPI (Backend & Webhook)
- **Library:** `aiogram` (Telegram Bot v3), `payos` (Payment Gateway), `openai` (LLM Engine), `pandas` (Data processing).
- **Deployment:** Render (Cloud Hosting) & UptimeRobot (Keep-alive).

## 📂 Cấu trúc dự án

```text
Telegram-menu-bot/
├── src/
│   ├── bot.py          # Logic xử lý tin nhắn và lệnh bot
│   ├── llm.py          # Tương tác với OpenAI (Function Calling)
│   ├── payment.py      # Tích hợp cổng thanh toán PayOS
│   ├── order.py        # Logic xử lý đơn hàng và tính toán
│   └── parser.py       # Xử lý dữ liệu thực đơn (CSV)
├── main.py             # File khởi chạy chính (FastAPI + Bot)
├── menu.csv            # Dữ liệu thực đơn quán
├── menu_image.png      # Ảnh thực đơn gửi cho khách
├── .env.example        # File mẫu cấu hình biến môi trường
└── requirements.txt    # Danh sách thư viện cần thiết
```

# 🚀 Hướng dẫn cài đặt & Chạy thử

## 1. Cài đặt môi trường Local

### 1. Clone dự án

```
git clone https://github.com/Dun2005/Telegram-menu-bot.git
cd Telegram-menu-bot
```

### 2. Tạo môi trường ảo

```
python -m venv .venv
```

#### Kích hoạt (Windows):

```
.venv\Scripts\activate
```

#### Kích hoạt (Mac/Linux):

```
source .venv/bin/activate
```

### 3. Cài đặt thư viện

```
pip install -r requirements.txt
```

## 2. Cấu hình biến môi trường

Tạo file `.env` tại thư mục gốc và điền các thông tin (Tham khảo `.env.example`):

- `TELEGRAM_TOKEN`: Token lấy từ BotFather.
- `OPENAI_API_KEY`: API Key từ OpenAI.
- `PAYOS_CLIENT_ID`: Client ID từ PayOS.
- `PAYOS_API_KEY`: API Key từ PayOS.
- `PAYOS_CHECKSUM_KEY`: Checksum Key từ PayOS.

## 3. Khởi chạy Local

```
uvicorn main:app --port 8000 --reload
```

## 🌐 Triển khai (Deployment)

Hệ thống đã được triển khai thực tế trên nền tảng **Render**.

- **URL Webhook:** `https://telegram-menu-bot-j324.onrender.com/payos-webhook`
- **Bot Telegram:** [@MenuCassoBot](https://t.me/MenuCassoBot)

> **Lưu ý về trải nghiệm:** Vì Render sử dụng gói Free Tier nên server sẽ "đi ngủ" sau 15 phút không có hoạt động. Tôi đã tích hợp **UptimeRobot** để "đánh thức" server mỗi 5 phút, đảm bảo hệ thống luôn sẵn sàng phản hồi ngay khi Ban Giám Khảo bắt đầu bài test.
