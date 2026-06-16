import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ระบบบันทึกค่าใช้จ่ายรายวีค ถาวรสูงสุด", layout="wide")
st.title("💰 ระบบบันทึกและคำนวณค่าใช้จ่ายรายปักษ์ (พร้อมระบบสำรองข้อมูล)")
st.write("บันทึกค่าใช้จ่ายรายวัน และจัดหมวดหมู่งวดเงินเดือนไม่ให้หายด้วยระบบ Backup")

# ชื่อไฟล์ฐานข้อมูล CSV
CSV_FILE = "expense_database.csv"

# รายชื่อเดือนภาษาไทย
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

# ==================== 🛠️ เพิ่มระบบดึงข้อมูลสำรอง (Restore Data) ด้านข้าง ====================
st.sidebar.header("💾 ระบบสำรองข้อมูล")

# ช่องให้อัปโหลดไฟล์เก่าคืนกรณีคลาวด์หลับลืมข้อมูล
uploaded_backup = st.sidebar.file_saver = st.sidebar.file_uploader("กู้คืนข้อมูล (อัปโหลดไฟล์ CSV ที่เคยเซฟไว้):", type=["csv"])
if uploaded_backup is not None:
    try:
        df_backup = pd.read_csv(uploaded_backup)
        # ตรวจสอบคอลัมน์ว่าถูกต้องไหมก่อนเซฟทับ
        if "MonthYear" in df_backup.columns and "Expense" in df_backup.columns:
            save_data(df_backup)
            st.sidebar.success("🔄 กู้คืนประวัติข้อมูลสำเร็จแล้ว!")
            # โหลดข้อมูลใหม่หลังจากกู้คืน
            df_all = load_data()
        else:
            st.sidebar.error("ไฟล์ไม่ถูกต้อง กรุณาใช้ไฟล์ที่ดาวน์โหลดจากระบบนี้เท่านั้นค่ะ")
    except Exception as e:
        st.sidebar.error("เกิดข้อผิดพลาดในการอ่านไฟล์")

st.sidebar.markdown("---")

# ส่วนเลือกผู้ใช้งานด้านข้าง
st.sidebar.header("👤 บัญชีผู้ใช้งาน")
current_user = st.sidebar.radio("เลือกรายชื่อผู้ใช้งาน:", ["พลอย", "คิม"])

# หน้าจอหลักแบ่งเป็น 2 ฝั่ง
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader(f"📝 บันทึกข้อมูลของ คุณ{current_user}")
    
    st.write("**📌 เลือกเดือน/ปี และงวดของเงินเดือน:**")
    c1, c2 = st.columns(2)
    with c1:
        current_month_idx = datetime.now().month - 1
        select_month = st.selectbox("เลือกเดือนที่เงินออก:", MONTHS_TH, index=current_month_idx)
    with c2:
        current_year = datetime.now().year
        select_year = st.selectbox("เลือกปี (ค.ศ.):", [current_year, current_year+1], index=0)
        
    month_year_str = f"{select_month}-{select_year}"
    selected_period = st.radio("เงินเดือนงวดรอบวันที่:", ["งวดวันที่ 15", "งวดวันที่ 30"], horizontal=True)
    income = st.number_input("จำนวนเงินเดือนที่ได้รับในงวดนี้ (บาท):", min_value=0.0, value=15000.0, step=500.0)
    
    st.markdown("---")
    st.write("**➕ เพิ่มรายการค่าใช้จ่ายของวันนี้**")
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    st.info(f"📅 วันที่บันทึกรายการ: {today_str} (บันทึกตามวันจริง)")
    
    item_name = st.text_input("ชื่อรายการค่าใช้จ่าย:", placeholder="เช่น ค่าอาหาร, ค่าน้ำมัน, ช้อปปิ้ง")
    item_amount = st.number_input("จำนวนเงิน (บาท):", min_value=0.0, value=0.0, step=50.0)
    
    if st.button("บันทึกรายการค่าใช้จ่าย"):
        if item_name != "" and item_amount > 0:
            new_row = pd.DataFrame([{
                "User": current_user,
                "Date": today_str,
                "MonthYear": month_year_str,
                "Period": selected_period,
                "Income": income,
                "Item": item_name,
                "Expense": item_amount
            }])
            
            df_updated = pd.concat([df_all, new_row], ignore_index=True)
            save_data(df_updated)
            
            st.success(f"บันทึก '{item_name}' เรียบร้อย!")
            st.rerun()
        else:
            st.error("กรุณากรอกชื่อรายการและจำนวนเงินให้ถูกต้อง")

with col2:
    st.subheader(f"📊 ตารางสรุปและคำนวณเงินคงเหลือของ คุณ{current_user}")
    
    st.write("**🔍 เลือกงวดและเดือนที่ต้องการเรียกดูรายงาน:**")
    v1, v2 = st.columns(2)
    with v1:
        view_month_year = st.selectbox("เลือกเดือน/ปี ที่จะดู:", MONTHS_TH, index=current_month_idx, key="view_month")
        view_month_year_str = f"{view_month_year}-{current_year}"
    with v2:
        view_period = st.selectbox("เลือกงวดรอบวันที่ที่จะดู:", ["งวดวันที่ 15", "งวดวันที่ 30"], key="view_period")
    
    # กรองข้อมูลตาม เงื่อนไข
    if not df_all.empty:
        df_filtered = df_all[
            (df_all["User"] == current_user) & 
            (df_all["MonthYear"] == view_month_year_str) & 
            (df_all["Period"] == view_period)
        ]
    else:
        df_filtered = pd.DataFrame()
        
    if df_filtered is not None and not df_filtered.empty:
        total_income = df_filtered["Income"].iloc[-1]
        total_expense = df_filtered["Expense"].sum()
        balance = total_income - total_expense
        
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
        st.dataframe(df_filtered[["Date", "Item", "Expense"]].sort_values(by="Date", ascending=False), use_container_width=True)
        
        # ==================== 📥 เพิ่มปุ่มดาวน์โหลดข้อมูลทั้งหมดแปลงเป็น Excel/CSV ====================
        st.markdown("---")
        st.write("**📥 ดาวน์โหลดสำรองข้อมูลทั้งหมดในระบบ**")
        
        # แปลงข้อมูลทั้งหมดเป็น CSV รูปแบบ UTF-8 สำหรับเปิดใน Excel ภาษาไทยไม่เพี้ยน
        csv_data = df_all.to_csv(index=False).encode('utf-8-sig')
        
        st.download_button(
            label="📥 ดาวน์โหลดไฟล์ประวัติค่าใช้จ่ายทั้งหมด (.csv)",
            data=csv_data,
            file_name=f"expense_backup_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
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