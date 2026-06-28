# --- GIAO DIỆN CHÍNH & BỘ LỌC ĐA CẤP ---
st.subheader("🎯 TRỢ LÝ SỐ SĂN THƯỞNG LŨY TIẾN")
st.caption(f"👤 Tuyến: {st.session_state.user_name} | 📅 Kỳ báo cáo: Tháng {current_month}/{current_year}")

# Khởi tạo dữ liệu shop mặc định (chế độ nhập tay)
store_data = {"luy_ke": 0, "mocs": [0]*5, "tiens": [0]*5}

if not df_sheet.empty:
    st.markdown("<div class='section-title'>🏢 Bộ lọc phân cấp tuyến:</div>", unsafe_allow_html=True)
    
    # 1. Chọn Center
    center_list = sorted(df_sheet["Center"].dropna().unique())
    selected_center = st.selectbox("1. Chọn Center:", center_list)
    df_filtered = df_sheet[df_sheet["Center"] == selected_center]
    
    # 2. Chọn Office
    office_list = sorted(df_filtered["Office"].dropna().unique())
    selected_office = st.selectbox("2. Chọn Office:", office_list)
    df_filtered = df_filtered[df_filtered["Office"] == selected_office]
    
    # 3. Chọn Nhân viên (THAY ĐỔI: Hiển thị và lọc hoàn toàn dựa trên IDnhanvien)
    if "IDnhanvien" in df_filtered.columns:
        # Nếu muốn hiển thị kèm Tên bên cạnh ID cho Sales dễ nhìn (Ví dụ: "NV001 (Nguyễn Văn A)")
        if "Tên nhân viên" in df_filtered.columns:
            df_filtered["NV_Display"] = df_filtered["IDnhanvien"].astype(str) + " (" + df_filtered["Tên nhân viên"].astype(str) + ")"
            nv_list = sorted(df_filtered["NV_Display"].dropna().unique())
            selected_nv_display = st.selectbox("3. Chọn Nhân viên (Theo ID):", nv_list)
            # Lọc ngược lại bản gốc dựa trên bản hiển thị được chọn
            df_filtered = df_filtered[df_filtered["NV_Display"] == selected_nv_display]
        else:
            # Nếu file chỉ có cột IDnhanvien đơn thuần
            nv_list = sorted(df_filtered["IDnhanvien"].dropna().unique())
            selected_nv = st.selectbox("3. Chọn Nhân viên (Theo ID):", nv_list)
            df_filtered = df_filtered[df_filtered["IDnhanvien"] == selected_nv]
    else:
        st.error("⚠️ Không tìm thấy cột 'IDnhanvien' trong file dữ liệu của bạn!")
        st.stop()
    
    # 4. Chọn Tuyến thứ
    tuyen_thu_list = sorted(df_filtered["Tuyến thứ"].dropna().unique()) if "Tuyến thứ" in df_filtered.columns else []
    
    if tuyen_thu_list:
        selected_tuyen_thu = st.selectbox("4. Chọn Tuyến thứ:", tuyen_thu_list)
        df_filtered = df_filtered[df_filtered["Tuyến thứ"] == selected_tuyen_thu]
    else:
        st.warning("⚠️ Không tìm thấy danh sách Tuyến thứ phù hợp cho Mã nhân viên này!")
        selected_tuyen_thu = st.selectbox("4. Chọn Tuyến thứ:", ["Trống"])
    
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
else:
    selected_store = "[Tùy chỉnh nhập tay bên dưới]"
