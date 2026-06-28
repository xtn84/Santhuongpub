import datetime
import calendar
import pandas as pd
import streamlit as st

# 1. CẤU HÌNH MOBILE FIRST & NÉN KHÔNG GIAN
st.set_page_config(page_title="Trợ Lý Săn Thưởng Lũy Tiến", layout="centered")

st.markdown(
    """
    <style>
    .block-container { padding-top: 2.2rem !important; padding-bottom: 0.4rem !important; }
    div[data-testid="stVerticalBlock"] > div { padding-top: 0.1rem !important; padding-bottom: 0.1rem !important; }
    .section-title { font-size: 0.9rem !important; font-weight: bold; margin-top: 10px !important; margin-bottom: 4px !important; color: #555; }
    </style>
""",
    unsafe_allow_html=True,
)

# 2. HỆ THỐNG BẢO MẬT: MẬT KHẨU TRUY CẬP (Theo phân cấp Văn phòng/Khu vực)
ALLOWED_PASSWORDS = {
    "orion@hn1": "Sales Hà Nội 1",
    "orion@hn2": "Sales Hà Nội 2",
    "orion@ht1": "Sales Hà Tây 1",
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
time_warning_text = (
    "🚨 HÔM NAY LÀ NGÀY CUỐI CÙNG CHỐT SỐ THÁNG!"
    if remaining_days == 0
    else f"⏳ CHỈ CÒN ĐÚNG {remaining_days} NGÀY ĐỂ GIẬT THƯỞNG!"
)
time_color = "#d32f2f" if remaining_days == 0 else "#e65100"

# --- 📊 ĐỌC DATA TỰ ĐỘNG TỪ GOOGLE SHEETS ---
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1jDeehUfAtHBitdM4BpqKV-5VSzdJdsDYoWPZvG-1Gb4/edit?usp=sharing"

# Chuẩn bị DataFrame trống để tránh lỗi biến chưa định nghĩa
df_sheet = pd.DataFrame()

try:
    csv_url = GOOGLE_SHEET_URL.replace("/edit?usp=sharing", "/export?format=csv")
    df_sheet = pd.read_csv(csv_url)

    # Đảm bảo các cột phân cấp chuẩn hóa thành chuỗi text để tránh lỗi drop-down
    required_cols = [
        "Center",
        "Office",
        "IDnhanvien",
        "Tên nhân viên",
        "Tuyến thứ",
        "Shop",
        "Luy_ke",
        "Moc_thuong",
        "Tien_thuong",
    ]
    for col in required_cols:
        if col in df_sheet.columns:
            if col in ["Luy_ke", "Moc_thuong", "Tien_thuong"]:
                df_sheet[col] = pd.to_numeric(df_sheet[col]).fillna(0).astype(int)
            else:
                df_sheet[col] = df_sheet[col].astype(str).str.strip()
except Exception as e:
    st.error(f"⚠️ Không thể đồng bộ dữ liệu từ Google Sheet. Vui lòng kiểm tra lại cấu trúc cột!")

# --- GIAO DIỆN CHÍNH ---
st.subheader("🎯 TRỢ LÝ SỐ SĂN THƯỞNG")
st.caption(
    f"👤 Tài khoản: {st.session_state.user_name} | 📅 Kỳ báo cáo: Tháng {current_month}/{current_year}"
)

# Khởi tạo giá trị mặc định cho dữ liệu shop
store_data = {"luy_ke": 0, "moc_thuong": 0, "tien_thuong": 0}
selected_store = "[Tùy chỉnh nhập tay bên dưới]"

st.markdown(
    "<div class='section-title'>🏢 Phân cấp tuyến bán hàng:</div>",
    unsafe_allow_html=True,
)

if not df_sheet.empty:
    # 1. Chọn Center
    center_list = sorted(df_sheet["Center"].unique())
    selected_center = st.selectbox("Chọn Center:", center_list)

    # 2. Chọn Office thuộc Center đã chọn
    df_filtered = df_sheet[df_sheet["Center"] == selected_center]
    office_list = sorted(df_filtered["Office"].unique())
    selected_office = st.selectbox("Chọn Office:", office_list)

    # 3. Chọn Nhân viên thuộc Office đã chọn
    df_filtered = df_filtered[df_filtered["Office"] == selected_office]
    nv_list = sorted(df_filtered["Nhan_vien"].unique())
    selected_nv = st.selectbox("Chọn Nhân viên:", nv_list)

    # 4. Chọn Tuyến thứ
    df_filtered = df_filtered[df_filtered["Nhan_vien"] == selected_nv]
    # Gộp Tuyến và Thứ lại hoặc hiển thị theo thiết kế file của bạn (ở đây hiển thị riêng biệt tùy chọn ghép chuỗi)
    df_filtered["Tuyen_Thu"] = (
        df_filtered["Tuyen"] + " - " + df_filtered["Thu"]
    )
    tuyen_thu_list = sorted(df_filtered["Tuyen_Thu"].unique())
    selected_tuyen_thu = st.selectbox("Chọn Tuyến - Thứ:", tuyen_thu_list)

    # 5. Chọn Khách hàng (Shop) thuộc tuyến đã lọc
    df_filtered = df_filtered[df_filtered["Tuyen_Thu"] == selected_tuyen_thu]
    shop_list = sorted(df_filtered["Shop"].unique())
    shop_options = shop_list + ["[Tùy chỉnh nhập tay bên dưới]"]

    st.markdown(
        "<div class='section-title'>🏪 1. Chọn khách hàng ghé thăm:</div>",
        unsafe_allow_html=True,
    )
    selected_store = st.selectbox("Danh sách shop đã lọc:", shop_options)

    if selected_store != "[Tùy chỉnh nhập tay bên dưới]":
        row_data = df_filtered[df_filtered["Shop"] == selected_store].iloc[0]
        store_data = {
            "luy_ke": int(row_data["Luy_ke"]),
            "moc_thuong": int(row_data["Moc_thuong"]),
            "tien_thuong": int(row_data["Tien_thuong"]),
        }
else:
    # Dự phòng hoàn toàn nếu lỗi Sheet
    st.warning("⚠️ Đang sử dụng chế độ Nhập tay do lỗi kết nối dữ liệu.")
    selected_store = st.selectbox(
        "Danh sách shop:", ["[Tùy chỉnh nhập tay bên dưới]"]
    )

# Giao diện hiển thị/nhập số liệu doanh số
col_s1, col_s2 = st.columns(2)
with col_s1:
    current_accumulated = st.number_input(
        "Doanh số đã mua lũy kế (Đ):",
        min_value=0,
        value=store_data["luy_ke"],
        step=100000,
    )
with col_s2:
    target_threshold = st.number_input(
        "Mốc doanh số ăn thưởng (Đ):",
        min_value=0,
        value=store_data["moc_thuong"],
        step=100000,
    )

reward_money = st.number_input(
    "Tiền thưởng công ty trả khi đạt mốc (Đ):",
    min_value=0,
    value=store_data["tien_thuong"],
    step=50000,
)

st.markdown(
    "<div class='section-title'>🛒 2. Đơn hàng thương lượng hôm nay:</div>",
    unsafe_allow_html=True,
)
today_order_value = st.number_input(
    "Giá trị đơn hàng định chốt (Đ):", min_value=0, value=500000, step=50000
)

# XỬ LÝ LOGIC SỐ LIỆU
gap_before = max(0, target_threshold - current_accumulated)
total_after_order = current_accumulated + today_order_value
gap_after = max(0, target_threshold - total_after_order)
pct_before = (
    min(1.0, current_accumulated / target_threshold)
    if target_threshold > 0
    else 0.0
)
pct_after = (
    min(1.0, total_after_order / target_threshold) if target_threshold > 0 else 0.0
)
is_unlocked = total_after_order >= target_threshold
effective_discount_pct = (
    (reward_money / today_order_value) * 100
    if (is_unlocked and today_order_value > 0)
    else 0.0
)

st.markdown(
    "<div class='section-title'>📊 3. Biểu đồ tiến độ & Đòn bẩy chốt đơn:</div>",
    unsafe_allow_html=True,
)
st.caption(
    f"Tiến độ hiện tại: {pct_before*100:.1f}% ➡️ Sau đơn hôm nay: {pct_after*100:.1f}%"
)
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
