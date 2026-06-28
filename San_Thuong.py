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
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1jDeehUfAtHBitdM4BpqKV-5VSzdJdsDYoWPZvG-1Gb4/edit?usp=sharing"

df_sheet = pd.DataFrame()

try:
    csv_url = GOOGLE_SHEET_URL.replace("/edit?usp=sharing", "/export?format=csv")
    df_sheet = pd.read_csv(csv_url)
    df_sheet.columns = df_sheet.columns.str.strip()
    
    # Chuẩn hóa cột ID nhân viên thành dạng chuỗi text thuần túy
    if "IDnhanvien" in df_sheet.columns:
        df_sheet["IDnhanvien"] = df_sheet["IDnhanvien"].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        
    # Ép kiểu dữ liệu số cho các cột tính toán thưởng lũy tiến
    mocs_cols = [f"Moc_thuong {i}" for i in range(1, 6)]
    tiens_cols = [f"Tiền Thưởng mốc {i}" for i in range(1, 6)]
    
    for col in ["Luy_ke", "Tien_thuong"] + mocs_cols + tiens_cols:
        if col in df_sheet.columns:
            df_sheet[col] = df_sheet[col].astype(str).str.replace(r'[^\d]', '', regex=True)
            df_sheet[col] = pd.to_numeric(df_sheet[col]).fillna(0).astype(int)
            
except Exception as e:
    st.error(f"⚠️ Lỗi cấu trúc hoặc kết nối Google Sheet: {e}")

# --- GIAO DIỆN CHÍNH & BỘ LỌC ĐA CẤP ---
st.subheader("🎯 TRỢ LÝ SỐ SĂN THƯỞNG LŨY TIẾN")
st.caption(f"👤 Tuyến: {st.session_state.user_name} | 📅 Kỳ báo cáo: Tháng {current_month}/{current_year}")

# Khởi tạo dữ liệu shop mặc định (chế độ nhập tay)
store_data = {"luy_ke": 0, "mocs": [0]*5, "tiens": [0]*5}
selected_store = "[Tùy chỉnh nhập tay bên dưới]"

if not df_sheet.empty:
    st.markdown("<div class='section-title'>🏢 Bộ lọc phân cấp tuyến:</div>", unsafe_allow_html=True)
    
    # 1. Chọn Center
    center_list = sorted(df_sheet["Center"].dropna().unique()) if "Center" in df_sheet.columns else []
    if center_list:
        selected_center = st.selectbox("1. Chọn Center:", center_list)
        df_filtered = df_sheet[df_sheet["Center"] == selected_center]
    else:
        df_filtered = df_sheet.copy()
    
    # 2. Chọn Office
    office_list = sorted(df_filtered["Office"].dropna().unique()) if "Office" in df_filtered.columns else []
    if office_list:
        selected_office = st.selectbox("2. Chọn Office:", office_list)
        df_filtered = df_filtered[df_filtered["Office"] == selected_office]
        
    # 3. Chọn Nhân viên (LỌC HOÀN TOÀN THEO IDnhanvien)
    if "IDnhanvien" in df_filtered.columns:
        nv_id_list = sorted(df_filtered["IDnhanvien"].dropna().unique())
        selected_nv_id = st.selectbox("3. Chọn Mã nhân viên (ID):", nv_id_list)
        df_filtered = df_filtered[df_filtered["IDnhanvien"] == selected_nv_id]
        
        if "Tên nhân viên" in df_filtered.columns and not df_filtered.empty:
            ten_nv_hien_tai = df_filtered["Tên nhân viên"].iloc[0]
            st.info(f"👨‍💼 Nhân viên: **{ten_nv_hien_tai}**")
    else:
        st.error("⚠️ Không tìm thấy cột 'IDnhanvien' trong dữ liệu!")
    
    # 4. Chọn Tuyến thứ
    tuyen_thu_list = sorted(df_filtered["Tuyến thứ"].dropna().unique()) if "Tuyến thứ" in df_filtered.columns else []
    if tuyen_thu_list:
        selected_tuyen_thu = st.selectbox("4. Chọn Tuyến thứ:", tuyen_thu_list)
        df_filtered = df_filtered[df_filtered["Tuyến thứ"] == selected_tuyen_thu]
    else:
        st.warning("⚠️ Không tìm thấy danh sách Tuyến thứ phù hợp!")
    
    # 5. Chọn Shop
    shop_list = sorted(df_filtered["Shop"].dropna().unique()) if "Shop" in df_filtered.columns else []
    shop_options = shop_list + ["[Tùy chỉnh nhập tay bên dưới]"]
    
    st.markdown("<div class='section-title'>🏪 Chọn khách hàng ghé thăm:</div>", unsafe_allow_html=True)
    selected_store = st.selectbox("Danh sách shop đã lọc theo tuyến:", shop_options)
    
    if selected_store != "[Tùy chỉnh nhập tay bên dưới]" and not df_filtered.empty:
        df_shop = df_filtered[df_filtered["Shop"] == selected_store]
        if not df_shop.empty:
            row = df_shop.iloc[0]
            store_data = {
                "luy_ke": int(row.get("Luy_ke", 0)),
                "mocs": [int(row.get(f"Moc_thuong {i}", 0)) for i in range(1, 6)],
                "tiens": [int(row.get(f"Tiền Thưởng mốc {i}", 0)) for i in range(1, 6)]
            }

# --- GIAO DIỆN NHẬP ĐƠN HÀNG ---
col_s1, col_s2 = st.columns(2)
with col_s1:
    current_accumulated = st.number_input("Doanh số đã mua lũy kế (Đ):", min_value=0, value=store_data["luy_ke"], step=100000)
with col_s2:
    today_order_value = st.number_input("Đơn hàng định chốt hôm nay (Đ):", min_value=0, value=500000, step=50000)

mocs = store_data["mocs"]
tiens = store_data["tiens"]

if selected_store == "[Tùy chỉnh nhập tay bên dưới]":
    st.markdown("<details><summary>🛠️ Cấu hình nhanh 5 mức thưởng (Nhấp để mở)</summary>", unsafe_allow_html=True)
    for i in range(1, 6):
        col1, col2 = st.columns(2)
        with col1: mocs[i-1] = st.number_input(f"Mốc {i} (Đ):", min_value=0, value=i*5000000, step=500000)
        with col2: tiens[i-1] = st.number_input(f"Tiền thưởng {i} (Đ):", min_value=0, value=i*100000, step=50000)
    st.markdown("</details>", unsafe_allow_html=True)

# --- 🧠 LOGIC XỬ LÝ LŨY TIẾN ---
total_revenue = current_accumulated + today_order_value

def evaluate_reward(revenue, mocs, tiens):
    current_idx = -1
    for i in range(len(mocs)):
        if revenue >= mocs[i] and mocs[i] > 0:
            current_idx = i
    next_idx = current_idx + 1 if current_idx < len(mocs) - 1 else None
    cur_moc_val = mocs[current_idx] if current_idx >= 0 else 0
    cur_reward = tiens[current_idx] if current_idx >= 0 else 0
    next_moc_val = mocs[next_idx] if next_idx is not None else None
    next_reward = tiens[next_idx] if next_idx is not None else None
    return current_idx + 1, cur_moc_val, cur_reward, next_idx + 1 if next_idx else None, next_moc_val, next_reward

curr_level, _, curr_reward, _, _, _ = evaluate_reward(current_accumulated, mocs, tiens)
after_level, after_moc, after_reward, next_level, next_moc, next_reward = evaluate_reward(total_revenue, mocs, tiens)

gap_to_next = (next_moc - total_revenue) if next_moc else 0
reward_diff = (next_reward - after_reward) if next_reward else 0
effective_discount = (after_reward / today_order_value * 100) if (today_order_value > 0 and after_reward > 0) else 0.0

# --- 📋 MỚI BỔ SUNG: BẢNG CƠ CẤU MỐC THƯỞNG CỦA SHOP ---
st.markdown("<div class='section-title'>📋 Bảng cơ cấu mốc thưởng áp dụng cho Shop:</div>", unsafe_allow_html=True)

table_rows = ""
for i in range(5):
    # Đánh dấu highlight dòng mốc thưởng tiếp theo mà nhân viên cần đạt tới
    is_next_target = (next_level == (i + 1))
    row_bg = "#fffde7" if is_next_target else ("#f9f9f9" if i % 2 == 0 else "#ffffff")
    row_weight = "bold" if is_next_target else "normal"
    target_star = "🎯 " if is_next_target else ""
    
    table_rows += f"""
    <tr style="background-color: {row_bg}; font-weight: {row_weight}; border-bottom: 1px solid #e0e0e0;">
        <td style="padding: 6px; font-size: 0.8rem; color: #333;">{target_star}Mốc {i+1}</td>
        <td style="padding: 6px; text-align: right; font-size: 0.8rem; color: #1565c0;">{mocs[i]:,.0f} Đ</td>
        <td style="padding: 6px; text-align: right; font-size: 0.8rem; color: #2e7d32;">+{tiens[i]:,.0f} Đ</td>
    </tr>
    """

mocs_table_html = f"""
<table style="width:100%; border-collapse: collapse; border: 1px solid #e0e0e0; font-family: sans-serif; margin-bottom: 10px;">
    <tr style="background-color: #f5f5f5; border-bottom: 2px solid #e0e0e0; font-weight: bold;">
        <td style="padding: 6px; font-size: 0.8rem; color: #555;">Bậc thưởng</td>
        <td style="padding: 6px; text-align: right; font-size: 0.8rem; color: #555;">Doanh số yêu cầu</td>
        <td style="padding: 6px; text-align: right; font-size: 0.8rem; color: #555;">Tiền thưởng nhận</td>
    </tr>
    {table_rows}
</table>
"""
st.markdown(mocs_table_html, unsafe_allow_html=True)


# --- 📊 HIỂN THỊ KẾT QUẢ ĐÒN BẨY & THÔNG BÁO ---
st.markdown("<div class='section-title'>📊 Kế hoạch đòn bẩy & Nhắc mốc săn thưởng:</div>", unsafe_allow_html=True)

max_target_moc = next_moc if next_moc else mocs[-1]
pct_progress = min(1.0, total_revenue / max_target_moc) if max_target_moc > 0 else 0.0
st.caption(f"Tiến độ tổng tích lũy tháng: {total_revenue:,.0f} Đ / {max_target_moc:,.0f} Đ")
st.progress(pct_progress)

if after_reward == 0:
    status_html = f"""
    <div style="background-color: #fff3e0; border: 1px solid #ffe0b2; border-radius: 8px; padding: 10px; font-family: sans-serif; font-size: 0.82rem; line-height: 1.5;">
        <div style="text-align: center; font-weight: bold; color: {time_color}; font-size: 0.95rem; margin-bottom: 6px; background-color: #ffeb3b; padding: 4px; border-radius: 4px;">{time_warning_text}</div>
        <div style="text-align: center; font-weight: bold; color: #d32f2f; font-size: 0.85rem; margin-bottom: 6px;">⚠️ ĐƠN HÀNG CHƯA ĐỦ ĐỂ ĐẠT MỐC THƯỞNG NÀO</div>
        <table style="width:100%; border-collapse: collapse;">
            <tr style="border-bottom: 1px solid #ffe0b2;"><td style="padding: 4px 0;">🎯 <b>Mốc thưởng 1 cần đạt:</b></td><td style="text-align: right; font-weight: bold; color: #1565c0;">{mocs[0]:,.0f} Đ</td></tr>
            <tr style="border-bottom: 1px solid #ffe0b2;"><td style="padding: 4px 0;">📉 <b>Còn thiếu để lấy tiền:</b></td><td style="text-align: right; font-weight: bold; color: #d32f2f;">Thiếu {mocs[0] - total_revenue:,.0f} Đ</td></tr>
            <tr><td style="padding: 4px 0; color: #666;">🎁 Tiền thưởng mốc 1:</td><td style="text-align: right; color: #2e7d32; font-weight: bold;">+{tiens[0]:,.0f} Đ</td></tr>
        </table>
    </div>
    """
else:
    status_html = f"""
    <div style="background-color: #e8f5e9; border: 1px solid #c8e6c9; border-radius: 8px; padding: 10px; font-family: sans-serif; font-size: 0.82rem; line-height: 1.5;">
        <div style="text-align: center; font-weight: bold; color: #1b5e20; font-size: 0.95rem; margin-bottom: 6px; background-color: #c8e6c9; padding: 4px; border-radius: 4px;">🎉 ĐÃ KHÓA THÀNH CÔNG MỐC THƯỞNG {after_level}</div>
        <table style="width:100%; border-collapse: collapse; margin-bottom: 6px;">
            <tr style="border-bottom: 1px solid #c8e6c9;"><td style="padding: 3px 0;">💰 <b>Tiền thưởng đút túi:</b></td><td style="text-align: right; font-weight: bold; color: #2e7d32; font-size: 0.95rem;">+{after_reward:,.0f} VNĐ</td></tr>
            <tr style="border-bottom: 1px solid #c8e6c9;"><td style="padding: 3px 0;">🛒 Tổng tích lũy sau đơn:</td><td style="text-align: right; font-weight: bold; color: #333;">{total_revenue:,.0f} Đ</td></tr>
            <tr style="border-bottom: 1px solid #c8e6c9;"><td style="padding: 3px 0;">📉 Vốn thực tế của đơn hôm nay:</td><td style="text-align: right; font-weight: bold; color: #1565c0;">{max(0, today_order_value - (after_reward - curr_reward)):,.0f} Đ</td></tr>
        </table>
        <div style="background-color: #1b5e20; color: white; border-radius: 5px; padding: 4px; text-align: center; font-weight: bold; font-size: 0.8rem; margin-bottom: 8px;">
            🔥 ĐỒN BẨY GIẢM GIÁ NGẦM ĐƠN HÔM NAY: {effective_discount:.1f}%
        </div>
    """
    if next_level:
        status_html += f"""
        <div style="background-color: #fffde7; border: 1px solid #fff59d; border-radius: 6px; padding: 8px; margin-top: 5px;">
            <div style="color: #f57f17; font-weight: bold; text-align: center; margin-bottom: 4px; font-size: 0.85rem;">🚀 CHIÊU KÍCH ĐƠN: LÊN MỐC {next_level}</div>
            <table style="width:100%; font-size: 0.78rem;">
                <tr><td style="color:#555;">➕ Chỉ cần cố thêm:</td><td style="text-align: right; font-weight: bold; color: #d32f2f;">{gap_to_next:,.0f} Đ nữa</td></tr>
                <tr><td style="color:#555;">🎁 Tiền thưởng tăng thêm:</td><td style="text-align: right; font-weight: bold; color: #2e7d32;">+{reward_diff:,.0f} Đ (Tổng nhận: {next_reward:,.0f} Đ)</td></tr>
            </table>
        </div>
        """
    else:
        status_html += """
        <div style="background-color: #e3f2fd; color: #0d47a1; border: 1px solid #90caf9; border-radius: 6px; padding: 6px; text-align: center; font-weight: bold; font-size: 0.8rem; margin-top: 5px;">
            🏆 ĐÃ ĐẠT CẤP ĐỘ THƯỞNG CAO NHẤT (MỐC KỊCH TRẦN)!
        </div>
        """
    status_html += "</div>"

st.markdown(status_html, unsafe_allow_html=True)

st.write("")
if st.button("Đăng xuất ✖️", use_container_width=True):
    st.session_state.logged_in = False
    st.rerun()
