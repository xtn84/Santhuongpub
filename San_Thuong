import streamlit as st
import pandas as pd
import datetime
import calendar

# 1. CẤU HÌNH MOBILE FIRST & NÉN KHÔNG GIAN
st.set_page_config(page_title="Trợ Lý Săn Thưởng Lũy Tiến", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 2.2rem !important; padding-bottom: 0.4rem !important; }
    div[data-testid="stVerticalBlock"] > div { padding-top: 0.1rem !important; padding-bottom: 0.1rem !important; }
    .section-title { font-size: 0.9rem !important; font-weight: bold; margin-top: 10px !important; margin-bottom: 4px !important; color: #555; }
    </style>
""", unsafe_allow_html=True)

# 2. HỆ THỐNG BẢO MẬT: MẬT KHẨU TRUY CẬP
ALLOWED_PASSWORDS = {
    "orion@hn1": "Sales Hà Nội 1",
    "orion@hn2": "Sales Hà Nội 2",
    "orion@ht1": "Sales Hà Tây 1"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 ĐĂNG NHẬP HỆ THỐNG")
    user_pass = st.text_input("Nhập mật khẩu được cấp:", type="password")
    if st.button("Kích Hoạt 🔓", use_container_width=True):
        if user_pass in ALLOWED_PASSWORDS:
            st.session_state.logged_in = True
            st.session_state.user_name = ALLOWED_PASSWORDS[user_pass]
            st.rerun()
        else:
            st.error("❌ Mật khẩu sai hoặc đã bị thu hồi!")
    st.stop()

# --- ⏰ TỰ ĐỘNG TÍNH TOÁN THỜI GIAN ĐẾM NGƯỢC ---
now = datetime.datetime.now()
current_day, current_month, current_year = now.day, now.month, now.year
_, last_day = calendar.monthrange(current_year, current_month)
remaining_days = last_day - current_day
time_warning_text = "🚨 HÔM NAY LÀ NGÀY CUỐI CÙNG CHỐT SỐ THÁNG!" if remaining_days == 0 else f"⏳ CHỈ CÒN ĐÚNG {remaining_days} NGÀY ĐỂ GIẬT THƯỞNG!"
time_color = "#d32f2f" if remaining_days == 0 else "#e65100"

# --- 📊 ĐỌC DATA TỰ ĐỘNG TỪ GOOGLE SHEETS ---
# DÁN ĐƯỜNG LINK FILE GOOGLE SHEETS CỦA BẠN VÀO ĐÂY ĐỂ THAY THẾ LINK MẪU NÀY
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1jDeehUfAtHBitdM4BpqKV-5VSzdJdsDYoWPZvG-1Gb4/edit?usp=sharing"

try:
    # Biến đổi link edit thành link xuất bản dữ liệu dạng CSV để pandas đọc trực tiếp cực nhanh
    csv_url = GOOGLE_SHEET_URL.replace("/edit?usp=sharing", "/export?format=csv")
    df_sheet = pd.read_csv(csv_url)
    
    # Chuyển đổi dữ liệu bảng tính thành dạng cấu trúc dữ liệu cho app chạy
    MOCK_STORES = {}
    for _, row in df_sheet.iterrows():
        MOCK_STORES[str(row["Shop"])] = {
            "luy_ke": int(row["Luy_ke"]),
            "moc_thuong": int(row["Moc_thuong"]),
            "tien_thuong": int(row["Tien_thuong"])
        }
except Exception as e:
    # Nếu file lỗi hoặc mất mạng, tự động dùng data dự phòng để Sales không bị sập app giữa tuyến
    MOCK_STORES = {"[Lỗi kết nối Sheet] Vui lòng nhập tay bên dưới": {"luy_ke": 0, "moc_thuong": 0, "tien_thuong": 0}}

# Thêm lựa chọn nhập tay linh hoạt cuối danh sách
MOCK_STORES["[Tùy chỉnh nhập tay bên dưới]"] = {"luy_ke": 0, "moc_thuong": 0, "tien_thuong": 0}

# --- GIAO DIỆN CHÍNH ---
st.subheader("🎯 TRỢ LÝ SỐ SĂN THƯỞNG")
st.caption(f"👤 Tuyến: {st.session_state.user_name} | 📅 Kỳ báo cáo: Tháng {current_month}/{current_year}")

st.markdown("<div class='section-title'>🏪 1. Chọn khách hàng ghé thăm:</div>", unsafe_allow_html=True)
selected_store = st.selectbox("Danh sách shop tự động đồng bộ từ Google Sheets:", list(MOCK_STORES.keys()))
store_data = MOCK_STORES[selected_store]

col_s1, col_s2 = st.columns(2)
with col_s1:
    current_accumulated = st.number_input("Doanh số đã mua lũy kế (Đ):", min_value=0, value=store_data["luy_ke"], step=100000)
with col_s2:
    target_threshold = st.number_input("Mốc doanh số ăn thưởng (Đ):", min_value=0, value=store_data["moc_thuong"], step=100000)

reward_money = st.number_input("Tiền thưởng công ty trả khi đạt mốc (Đ):", min_value=0, value=store_data["tien_thuong"], step=50000)

st.markdown("<div class='section-title'>🛒 2. Đơn hàng thương lượng hôm nay:</div>", unsafe_allow_html=True)
today_order_value = st.number_input("Giá trị đơn hàng định chốt (Đ):", min_value=0, value=500000, step=50000)

# XỬ LÝ LOGIC SỐ LIỆU
gap_before = max(0, target_threshold - current_accumulated)
total_after_order = current_accumulated + today_order_value
gap_after = max(0, target_threshold - total_after_order)
pct_before = min(1.0, current_accumulated / target_threshold) if target_threshold > 0 else 0.0
pct_after = min(1.0, total_after_order / target_threshold) if target_threshold > 0 else 0.0
is_unlocked = total_after_order >= target_threshold
effective_discount_pct = (reward_money / today_order_value) * 100 if (is_unlocked and today_order_value > 0) else 0.0

st.markdown("<div class='section-title'>📊 3. Biểu đồ tiến độ & Đòn bẩy chốt đơn:</div>", unsafe_allow_html=True)
st.caption(f"Tiến độ hiện tại: {pct_before*100:.1f}% ➡️ Sau đơn hôm nay: {pct_after*100:.1f}%")
st.progress(pct_after)

if not is_unlocked:
    status_html = f"""
    <div style="background-color: #fff3e0; border: 1px solid #ffe0b2; border-radius: 8px; padding: 10px; font-family: sans-serif; font-size: 0.8rem; line-height: 1.4;">
        <div style="text-align: center; font-weight: bold; color: {time_color}; font-size: 0.95rem; margin-bottom: 8px; background-color: #ffeb3b; padding: 4px; border-radius: 4px;">{time_warning_text}</div>
        <div style="text-align: center; font-weight: bold; color: #e65100; font-size: 0.85rem; margin-bottom: 6px; border-top: 1px dashed #ffd180; padding-top: 6px;">⚠️ CỬA HÀNG CHƯA ĐỦ ĐỂ ĂN THƯỞNG</div>
        <table style="width:100%; border-collapse: collapse; font-size: 0.8rem;">
            <tr style="border-bottom: 1px solid #ffd180;"><td style="padding: 4px 0;">📉 <strong>Khoảng cách mốc thưởng:</strong></td><td style="text-align: right; font-weight: bold; color: #d32f2f;">Còn thiếu {gap_before:,.0f} Đ</td></tr>
            <tr style="border-bottom: 1px solid #ffd180;"><td style="padding: 4px 0;">📦 <strong>Nhiệm vụ đơn hôm nay:</strong></td><td style="text-align: right; font-weight: bold; color: #1565c0;">Nâng đơn lên {gap_before:,.0f} Đ để chốt</td></tr>
            <tr><td style="padding: 4px 0; color: #666;">🎁 Tiền thưởng của shop đang treo:</td><td style="text-align: right; color: #666; font-weight: bold;">{reward_money:,.0f} Đ</td></tr>
        </table>
    </div>
    """
else:
    status_html = f"""
    <div style="background-color: #e8f5e9; border: 1px solid #c8e6c9; border-radius: 8px; padding: 10px; font-family: sans-serif; font-size: 0.8rem; line-height: 1.4;">
        <div style="text-align: center; font-weight: bold; color: #2e7d32; font-size: 0.8rem; margin-bottom: 6px; background-color: #c8e6c9; border-radius: 4px; padding: 2px;">{time_warning_text}</div>
        <div style="text-align: center; font-weight: bold; color: #1b5e20; font-size: 1rem; margin-bottom: 4px;">🎉 CHÚC MỪNG CHỊ! ĐÃ CÁN MỐC ĂN THƯỞNG</div>
        <table style="width:100%; border-collapse: collapse; font-size: 0.78rem; margin-bottom: 6px;">
            <tr style="border-bottom: 1px solid #c8e6c9;"><td style="padding: 3px 0;">💰 <strong>Tiền thưởng đút túi:</strong></td><td style="text-align: right; font-weight: bold; color: #2e7d32; font-size: 0.9rem;">+{reward_money:,.0f} VNĐ</td></tr>
            <tr style="border-bottom: 1px solid #c8e6c9;"><td style="padding: 3px 0;">🛒 Giá trị đơn lấy hôm nay:</td><td style="text-align: right; font-weight: bold; color: #333;">{today_order_value:,.0f} Đ</td></tr>
            <tr><td style="padding: 3px 0; color: #1565c0;">📉 <strong>Vốn thực tế sau trừ thưởng:</strong></td><td style="text-align: right; font-weight: bold; color: #1565c0; font-size: 0.9rem;">{(today_order_value - reward_money):,.0f} Đ</td></tr>
        </table>
        <div style="background-color: #1b5e20; color: white; border-radius: 6px; padding: 6px; text-align: center; font-weight: bold; font-size: 0.85rem; margin-top: 4px;">
            🔥 ĐƠN HÔM NAY GIẢM GIÁ NGẦM: {effective_discount_pct:.1f}%
        </div>
    </div>
    """

st.markdown(status_html, unsafe_allow_html=True)

st.write("")
if st.button("Đăng xuất ✖️", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()
