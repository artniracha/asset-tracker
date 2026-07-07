import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# 1. ตั้งค่าการแสดงผลหน้าเว็บ
st.set_page_config(page_title="Long Do Asset Tracker", page_icon="💻", layout="wide")

st.title("💻 Long Do: ระบบตรวจสอบคอมพิวเตอร์เช่า")
st.markdown("ระบบสืบค้นข้อมูลตัวเครื่อง ยี่ห้อ/รุ่น สถานที่จัดวาง และหน่วยงานผู้รับผิดชอบ")
st.markdown("---")

# 2. ฟังก์ชันดึงข้อมูลแบบปลอดภัยและป้องกัน Error
@st.cache_data(ttl=300) # ปรับกลับเป็นแคชข้อมูล 5 นาที
def load_data():
    credentials_dict = dict(st.secrets["gcp_service_account"])
    
    # บรรทัดนี้สำคัญมาก! เป็นการแก้บั๊ก \n ใน Private Key โดยอัตโนมัติ
    credentials_dict["private_key"] = credentials_dict["private_key"].replace('\\n', '\n')
    
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
    client = gspread.authorize(creds)
    
    sheet = client.open("Computer_Asset_DB").sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

try:
    df = load_data()
    
    st.markdown("### 🔍 ค้นหาข้อมูลเครื่องคอมพิวเตอร์")
    search_option = st.radio("เลือกรูปแบบการค้นหา:", ["ชื่อผู้ครอบครอง", "Serial Number"], horizontal=True)
    
    if search_option == "ชื่อผู้ครอบครอง":
        search_query = st.text_input("กรอกชื่อ หรือ บางส่วนของชื่อ:")
        filtered_df = df[df['ชื่อผู้ครอบครอง'].astype(str).str.contains(search_query, case=False, na=False)] if search_query else pd.DataFrame()
    else:
        search_query = st.text_input("กรอก Serial Number:")
        filtered_df = df[df['Serial Number'].astype(str).str.contains(search_query, case=False, na=False)] if search_query else pd.DataFrame()

    if search_query:
        if not filtered_df.empty:
            st.success(f"พบข้อมูลคอมพิวเตอร์เช่าทั้งหมด {len(filtered_df)} รายการ")
            for _, row in filtered_df.iterrows():
                with st.container():
                    st.markdown(f"### 🖥️ Serial Number: {row['Serial Number']}")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric(label="⚙️ ยี่ห้อ/รุ่น", value=row['ยี่ห้อ/รุ่น'])
                    c2.metric(label="👤 ผู้ครอบครอง", value=row['ชื่อผู้ครอบครอง'])
                    c3.metric(label="🏢 หน่วยงาน", value=row['หน่วยงาน'])
                    c4.metric(label="📍 สถานที่ตั้ง", value=row['สถานที่ตั้ง'])
                    st.markdown("---")
        else:
            st.warning("❌ ไม่พบข้อมูลคอมพิวเตอร์เช่าที่ตรงกับเงื่อนไข")
            
except Exception as e:
    st.error("❌ ระบบไม่สามารถเชื่อมต่อฐานข้อมูลได้")
    st.markdown("### 📋 ข้อความข้อผิดพลาด:")
    st.code(str(e), language="text")
