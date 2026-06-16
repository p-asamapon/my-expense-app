import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบบันทึกค่าใช้จ่ายรายวีคอัจฉริยะ V2", layout="wide")
st.title("💰 ระบบบันทึกและคำนวณค่าใช้จ่ายรายปักษ์ (แยกรายเดือนชัดเจน)")
st.write("บันทึกค่าใช้จ่ายตามวันจริง คำนวณแยกตามงวดรอบวันที่ 15 / 30 และแยกตามเดือน-ปี ไม่ปนกัน")

# ชื่อไฟล์ฐานข้อมูล CSV
CSV_FILE = "expense_database.csv"

# รายชื่อเดือนภาษาไทยสำหรับแสดงผล
MONTHS_TH = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

# ฟังก์ชันสำหรับดึงข้อมูลจากไฟล์ CSV
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=["User", "Date", "MonthYear", "Period", "Income", "Item", "Expense"])

# ฟังก์ชันสำหรับเซฟข้อมูลลงไฟล์ CSV
def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# โหลดข้อมูลเก่าขึ้นมาแสดงผล
df_all = load_data()

# ส่วนเลือกผู้ใช้งานด้านข้าง
st.sidebar.header("👤 บัญชีผู้ใช้งาน")
current_user = st.sidebar.radio("เลือกรายชื่อผู้ใช้งาน:", ["พลอย", "คิม"])
st.sidebar.markdown("---")
st.sidebar.info("💡 ข้อมูลจะถูกแยกตามชื่อผู้ใช้, งวดเงินออก และเดือน/ปี อย่างชัดเจน สามารถเก็บประวัติยาวๆ ได้เลยค่ะ")

# หน้าจอหลักแบ่งเป็น 2 ฝั่ง
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader(f"📝 บันทึกข้อมูลของ คุณ{current_user}")
    
    # 1. ส่วนเลือก เดือน และ ปี ที่เงินเดือนก้อนนี้ออก
    st.write("**📌 เลือกเดือน/ปี และงวดของเงินเดือน:**")
    c1, c2 = st.columns(2)
    with c1:
        current_month_idx = datetime.now().month - 1
        select_month = st.selectbox("เลือกเดือนที่เงินออก:", MONTHS_TH, index=current_month_idx)
    with c2:
        current_year = datetime.now().year
        select_year = st.selectbox("เลือกปี (ค.ศ.):", [current_year, current_year+1], index=0)
        
    # รวมร่างเป็นข้อความระบุเดือนปี เช่น "มิถุนายน-2026"
    month_year_str = f"{select_month}-{select_year}"
    
    # 2. เลือกงวดรอบวันที่ 15 หรือ 30
    selected_period = st.radio("เงินเดือนงวดรอบวันที่:", ["งวดวันที่ 15", "งวดวันที่ 30"], horizontal=True)
    
    # กรอกยอดเงินเดือนที่ได้รับในงวดนั้น
    income = st.number_input("จำนวนเงินเดือนที่ได้รับในงวดนี้ (บาท):", min_value=0.0, value=15000.0, step=500.0)
    
    st.markdown("---")
    st.write("**➕ เพิ่มรายการค่าใช้จ่ายของวันนี้**")
    
    # ล็อกวันที่ปัจจุบันอัตโนมัติ
    today_str = datetime.now().strftime("%Y-%m-%d")
    st.info(f"📅 วันที่บันทึกรายการ: {today_str} (บันทึกตามวันจริง)")
    
    item_name = st.text_input("ชื่อรายการค่าใช้จ่าย:", placeholder="เช่น ค่าอาหาร, ค่าน้ำมัน, ช้อปปิ้ง")
    item_amount = st.number_input("จำนวนเงิน (บาท):", min_value=0.0, value=0.0, step=50.0)
    
    if st.button("บันทึกรายการค่าใช้จ่าย"):
        if item_name != "" and item_amount > 0:
            # สร้างข้อมูลแถวใหม่ที่มี MonthYear เพิ่มเข้ามาด้วย
            new_row = pd.DataFrame([{
                "User": current_user,
                "Date": today_str,
                "MonthYear": month_year_str,
                "Period": selected_period,
                "Income": income,
                "Item": item_name,
                "Expense": item_amount
            }])
            
            # บันทึกลงไฟล์
            df_updated = pd.concat([df_all, new_row], ignore_index=True)
            save_data(df_updated)
            
            st.success(f"บันทึก '{item_name}' เข้างวด {selected_period} ของเดือน {select_month} เรียบร้อย!")
            st.rerun()
        else:
            st.error("กรุณากรอกชื่อรายการและจำนวนเงินให้ถูกต้อง")

with col2:
    st.subheader(f"📊 ตารางสรุปและคำนวณเงินคงเหลือของ คุณ{current_user}")
    
    # ส่วนตัวกรองข้อมูลฝั่งขวา เพื่อกดเลือกดูข้อมูลย้อนหลังตามเดือนและงวดที่ต้องการ
    st.write("**🔍 เลือกงวดและเดือนที่ต้องการเรียกดูรายงาน:**")
    v1, v2 = st.columns(2)
    with v1:
        view_month_year = st.selectbox("เลือกเดือน/ปี ที่จะดู:", MONTHS_TH, index=current_month_idx, key="view_month")
        view_month_year_str = f"{view_month_year}-{current_year}" # สามารถปรับโค้ดเพิ่มให้สลับดูปีอื่นได้ในอนาคต
    with v2:
        view_period = st.selectbox("เลือกงวดรอบวันที่ที่จะดู:", ["งวดวันที่ 15", "งวดวันที่ 30"], key="view_period")
    
    # กรองข้อมูลตาม เงื่อนไขทั้ง 4 (User + เดือนปี + งวด)
    if not df_all.empty:
        df_filtered = df_all[
            (df_all["User"] == current_user) & 
            (df_all["MonthYear"] == view_month_year_str) & 
            (df_all["Period"] == view_period)
        ]
    else:
        df_filtered = pd.DataFrame()
        
    if df_filtered is not None and not df_filtered.empty:
        # คำนวณยอดเงิน
        total_income = df_filtered["Income"].iloc[-1]
        total_expense = df_filtered["Expense"].sum()
        balance = total_income - total_expense
        
        # แสดงกล่องสรุปตัวเลข
        m1, m2, m3 = st.columns(3)
        m1.metric(label=f"เงินงวด {view_period} ({view_month_year})", value=f"{total_income:,.2f} บาท")
        m2.metric(label="รวมค่าใช้จ่ายที่ใช้ไป", value=f"{total_expense:,.2f} บาท", delta=f"-{total_expense:,.2f}", delta_color="inverse")
        
        if balance >= 0:
            m3.metric(label="คงเหลือเงินสุทธิ", value=f"{balance:,.2f} บาท")
        else:
            m3.metric(label="เงินคงเหลือ (เกินงบแล้ว!)", value=f"{balance:,.2f} บาท", delta=f"{balance:,.2f}", delta_color="normal")
            st.error("⚠️ คำเตือน: ยอดรวมค่าใช้จ่ายเกินวงเงินเดือนที่คุณตั้งไว้ในงวดนี้แล้ว!")
            
        st.markdown("---")
        st.write(f"**📋 รายละเอียดการจ่ายเงินย้อนหลังของ {view_period} เดือน {view_month_year}**")
        # แสดงตารางรายการ
        st.dataframe(df_filtered[["Date", "Item", "Expense"]].sort_values(by="Date", ascending=False), use_container_width=True)
        
        # ปุ่มลบข้อมูลเจาะจงเฉพาะงวดนั้นๆ ของเดือนนั้นๆ
        if st.button(f"❌ ล้างข้อมูลเฉพาะ {view_period} ของเดือน {view_month_year}"):
            df_remain = df_all[~(
                (df_all["User"] == current_user) & 
                (df_all["MonthYear"] == view_month_year_str) & 
                (df_all["Period"] == view_period)
            )]
            save_data(df_remain)
            st.warning("ลบข้อมูลของงวดดังกล่าวเรียบร้อยแล้ว")
            st.rerun()
    else:
        st.info(f"ยังไม่มีข้อมูลประวัติการบันทึกของ คุณ{current_user} ในงวด {view_period} ของเดือน {view_month_year}")