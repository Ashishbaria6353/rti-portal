import streamlit as st
import pandas as pd
import gspread

# --- સ્માર્ટ ગૂગલ શીટ કનેક્શન ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    from google.oauth2.service_account import Credentials
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
except:
    from oauth2client.service_account import ServiceAccountCredentials
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

client = gspread.authorize(creds)
sheet = client.open("RTI_Database").sheet1

# --- પેજ સેટઅપ અને CSS ---
st.set_page_config(page_title="RTI Manage Portal", layout="wide")
st.markdown("""
<style>
.box { padding: 15px; border-radius: 10px; color: white; text-align: center; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom:10px; }
.b-blue { background: #1976d2; }
.b-orange { background: #f57c00; }
.b-brown { background: #4e342e; }
.b-red { background: #d32f2f; }
.table-header { background: #3b5998; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- લોગિન સિસ્ટમ ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if not st.session_state['logged_in']:
    st.title("RTI MANAGE PORTAL - લોગિન")
    u_name = st.text_input("તમારું નામ")
    u_mob = st.text_input("મોબાઈલ નંબર")
    if st.button("લૉગિન કરો"):
        if u_name and u_mob:
            st.session_state.update({'logged_in': True, 'user_name': u_name, 'user_mobile': u_mob})
            st.rerun()
    st.stop()

# --- ડેટા ફંક્શન્સ (CRASH PROOF) ---
def load_data():
    data = sheet.get_all_records()
    if not data: # જો ગૂગલ શીટ ખાલી હશે તો એરર નહિ આપે, જાતે કોલમ બનાવશે
        return pd.DataFrame(columns=['ID', 'User_Mobile', 'સ્ટેટસ', 'PIO_કચેરી', 'PIO_મોબાઈલ'])
    return pd.DataFrame(data).astype(str)

def save_data_to_sheet(df):
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

df = load_data()

# ખાતરી કરીએ કે જરૂરી કોલમ શીટમાં છે જ
for col in ['ID', 'User_Mobile', 'સ્ટેટસ', 'PIO_કચેરી', 'PIO_મોબાઈલ']:
    if col not in df.columns:
        df[col] = ""

user_df = df[df['User_Mobile'] == st.session_state['user_mobile']] if not df.empty else pd.DataFrame()

# --- ડેશબોર્ડ ---
st.title(f"સ્વાગત છે, {st.session_state['user_name']}")
col1, col2, col3 = st.columns(3)

# ગણતરી વખતે એરર ન આવે તે માટે સેફ લૉજિક
total_rti = len(user_df)
pending_rti = len(user_df[user_df["સ્ટેટસ"]!="નિકાલ"]) if "સ્ટેટસ" in user_df.columns else 0
resolved_rti = len(user_df[user_df["સ્ટેટસ"]=="નિકાલ"]) if "સ્ટેટસ" in user_df.columns else 0

col1.markdown(f'<div class="box b-blue">કુલ RTI<br><b>{total_rti}</b></div>', unsafe_allow_html=True)
col2.markdown(f'<div class="box b-orange">પેન્ડિંગ<br><b>{pending_rti}</b></div>', unsafe_allow_html=True)
col3.markdown(f'<div class="box b-brown">નિકાલ<br><b>{resolved_rti}</b></div>', unsafe_allow_html=True)

# --- ટેબ્સ ---
tab1, tab2, tab3 = st.tabs(["🆕 નવી RTI", "📂 બધી અરજીઓ", "⚙️ મેનેજમેન્ટ"])

with tab1:
    with st.form("new_rti"):
        pio_name = st.text_input("PIO કચેરી")
        pio_mob = st.text_input("મોબાઈલ નંબર")
        if st.form_submit_button("સેવ કરો"):
            # નવો ID જાતે જનરેટ કરવા માટે
            if df.empty or 'ID' not in df.columns:
                new_id = "1"
            else:
                valid_ids = pd.to_numeric(df['ID'], errors='coerce').dropna()
                new_id = str(int(valid_ids.max()) + 1) if not valid_ids.empty else "1"
                
            new_row = {"ID": new_id, "User_Mobile": st.session_state['user_mobile'], "સ્ટેટસ": "પેન્ડિંગ", "PIO_કચેરી": pio_name, "PIO_મોબાઈલ": pio_mob}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data_to_sheet(df)
            st.success("સેવ થઈ ગયું!")
            st.rerun()

with tab2:
    if not user_df.empty:
        st.table(user_df[['ID', 'PIO_કચેરી', 'સ્ટેટસ']])
    else:
        st.info("અત્યારે તમારી કોઈ અરજી નથી. નવી અરજી ઉમેરો.")

with tab3:
    del_id = st.text_input("ડિલીટ કરવા માટે ID નાખો")
    if st.button("ડિલીટ કરો"):
        df = df[df['ID'] != del_id]
        save_data_to_sheet(df)
        st.success("ડિલીટ થઈ ગયું!")
        st.rerun()