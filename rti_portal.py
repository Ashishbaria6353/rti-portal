import streamlit as st
import pandas as pd
from datetime import date
import os
import base64
import gspread
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# --- પેજ સેટઅપ ---
st.set_page_config(page_title="RTI Manage Portal", initial_sidebar_state="expanded", layout="wide")

# --- ગૂગલ ડ્રાઇવ ફોલ્ડર ID ---
DRIVE_FOLDER_ID = "11tVZZ7RaaPspQB2CQa1exDJpfhnnn3jz"

# --- સ્માર્ટ ગૂગલ શીટ અને ડ્રાઇવ કનેક્શન ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
try:
    from google.oauth2.service_account import Credentials
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
except:
    from oauth2client.service_account import ServiceAccountCredentials
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

client = gspread.authorize(creds)
sheet = client.open("RTI_Database").sheet1

# --- શાનદાર CSS ડિઝાઇન ---
st.markdown("""
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
.block-container { background-color: #f4f7f6; padding-top: 3rem !important; padding-bottom: 1.5rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
.login-card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0px 8px 16px rgba(0,0,0,0.1); max-width: 450px; margin: auto; border-top: 4px solid #1e3a8a; }
.box { padding: 15px 10px; border-radius: 8px; text-align: center; color: white; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); margin-bottom: 12px; }
.b-blue { background: linear-gradient(135deg, #1e3a8a, #3b82f6); }          
.b-orange { background: linear-gradient(135deg, #ea580c, #f97316); }       
.b-brown { background: linear-gradient(135deg, #57534e, #78716c); }        
.b-red { background: linear-gradient(135deg, #b91c1c, #ef4444); }          
.b-purple { background: linear-gradient(135deg, #6d28d9, #8b5cf6); }       
.b-deeppurple { background: linear-gradient(135deg, #4338ca, #6366f1); }   
.b-green { background: linear-gradient(135deg, #15803d, #22c55e); }         
.number-text { font-size: 28px; font-weight: bold; margin: 5px 0 0 0; }
.label-text { font-size: 14px; font-weight: 600; margin: 0; }
.table-header { background-color: #1e3a8a; color: white; padding: 10px; border-radius: 6px; font-weight: bold; text-align: center; font-size: 14px; margin-bottom: 5px;}
.table-row { background-color: white; padding: 10px; border-radius: 6px; border: 1px solid #e5e7eb; text-align: center; font-size: 14px; box-shadow: 0px 2px 4px rgba(0,0,0,0.05); margin-bottom: 5px;}
.detail-card { background-color: white; padding: 15px; border-radius: 8px; border-left: 4px solid #1e3a8a; box-shadow: 0px 2px 4px rgba(0,0,0,0.05); margin-bottom: 10px; }
.detail-title { font-weight: bold; color: #1e3a8a; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px; margin-bottom: 10px; }
.detail-item { margin-bottom: 5px; font-size: 14px;}
.detail-label { font-weight: 600; color: #4b5563; }
</style>
""", unsafe_allow_html=True)

# --- પરમેનન્ટ લૉગિન સિસ્ટમ ---
if 'logged_in' not in st.session_state: 
    st.session_state['logged_in'] = False
    st.session_state['user_name'] = ""
    st.session_state['user_mobile'] = ""
if 'manage_action_id' not in st.session_state: 
    st.session_state['manage_action_id'] = None

params = st.query_params
if "mobile" in params and "name" in params and not st.session_state['logged_in']:
    st.session_state['logged_in'] = True
    st.session_state['user_mobile'] = params["mobile"]
    st.session_state['user_name'] = params["name"]

if not st.session_state['logged_in']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div class="login-card">
            <h2 style='text-align: center; color: #1e3a8a; margin-top: 0;'>RTI MANAGE PORTAL<br>માં આપનું સ્વાગત છે</h2>
            <p style='text-align: center; color: gray;'>કૃપા કરીને આગળ વધવા માટે નામ અને મોબાઈલ નંબર દાખલ કરો</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            u_name = st.text_input("તમારું પૂરું નામ")
            u_mob = st.text_input("તમારો મોબાઈલ નંબર")
            if st.form_submit_button("લૉગિન કરો (Login)", type="primary", use_container_width=True):
                if u_name and u_mob:
                    st.session_state['logged_in'] = True
                    st.session_state['user_name'] = u_name
                    st.session_state['user_mobile'] = str(u_mob)
                    st.query_params["mobile"] = str(u_mob)
                    st.query_params["name"] = u_name
                    st.rerun()
                else:
                    st.error("નામ અને મોબાઈલ નંબર બંને દાખલ કરવા જરૂરી છે!")
    st.stop()

# --- સાઈડબાર ---
with st.sidebar:
    st.markdown("### 👤 તમારું પ્રોફાઈલ")
    st.info(f"**નામ:**\n{st.session_state['user_name']}\n\n**મોબાઈલ:**\n{st.session_state['user_mobile']}")
    st.divider()
    if st.button("લૉગઆઉટ કરો (Logout)", type="primary", use_container_width=True):
        st.session_state.clear()
        st.query_params.clear() 
        st.rerun()

ALL_COLS = ['ID', 'User_Mobile', 'સ્ટેટસ', 'RTI_તારીખ', 'PIO_કચેરી', 'PIO_સરનામું', 'PIO_પિનકોડ', 'PIO_મોબાઈલ', 'RTI_સ્પીડપોસ્ટ', 'RTI_ફાઈલ', 
            'FAA_તારીખ', 'FAA_સુનાવણી_તારીખ', 'FAA_અધિકારી', 'FAA_સરનામું', 'FAA_પિનકોડ', 'FAA_મોબાઈલ', 'FAA_સ્પીડપોસ્ટ', 'FAA_ફાઈલ', 
            'SA_તારીખ', 'SA_સુનાવણી_તારીખ', 'SA_સ્પીડપોસ્ટ', 'SA_ફાઈલ']

# --- ગૂગલ ડ્રાઇવમાં ફાઈલ અપલોડ કરવાનું સ્માર્ટ ફંક્શન ---
def save_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        try:
            drive_service = build('drive', 'v3', credentials=creds)
            file_metadata = {'name': uploaded_file.name, 'parents': [DRIVE_FOLDER_ID]}
            media = MediaIoBaseUpload(io.BytesIO(uploaded_file.getvalue()), mimetype=uploaded_file.type, resumable=True)
            file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            file_id = file.get('id')
            
            # ફાઈલને પ્રિવ્યૂ માટે એક્સેસ આપવી
            drive_service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'reader'}).execute()
            return file_id # ડ્રાઇવનો ID રિટર્ન કરશે
        except Exception as e:
            st.error(f"ડ્રાઇવમાં ફાઈલ સેવ કરવામાં ભૂલ: {e}")
            return ""
    return ""

def load_data():
    try:
        data = sheet.get_all_records()
        if not data: return pd.DataFrame(columns=ALL_COLS)
        df = pd.DataFrame(data)
        for col in ALL_COLS:
            if col not in df.columns: df[col] = ""
        return df.astype(str)
    except:
        return pd.DataFrame(columns=ALL_COLS)

def save_data_to_sheet(df):
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

df = load_data()

# --- ઓટોમેટિક તારીખ લૉજિક ---
updated = False
today = date.today()
if not df.empty:
    for i, row in df.iterrows():
        status = row.get('સ્ટેટસ', 'પેન્ડિંગ')
        if status in ['નિકાલ', '']: continue
        
        rti_str = str(row.get('RTI_તારીખ', ''))
        faa_str = str(row.get('FAA_તારીખ', ''))
        
        rti_dt = pd.to_datetime(rti_str, errors='coerce').date() if rti_str and rti_str != "nan" else None
        faa_dt = pd.to_datetime(faa_str, errors='coerce').date() if faa_str and faa_str != "nan" else None
        
        if rti_dt and pd.notna(rti_dt) and not faa_dt:
            if (today - rti_dt).days > 30 and status == 'પેન્ડિંગ':
                df.at[i, 'સ્ટેટસ'] = 'પ્રથમ અપીલ બાકી'
                updated = True
                
        if faa_dt and pd.notna(faa_dt):
            if (today - faa_dt).days > 45 and status == 'પ્રથમ અપીલ પેન્ડિંગ':
                df.at[i, 'સ્ટેટસ'] = 'બીજી અપીલ બાકી'
                updated = True

    if updated: save_data_to_sheet(df)

user_df = df[df['User_Mobile'] == st.session_state['user_mobile']].copy() if not df.empty else pd.DataFrame(columns=ALL_COLS)

# --- ટોચનું હેડર ---
col_home, col_title, col_search = st.columns([1, 2, 1.5])
with col_home:
    if st.button("🏠 Home", use_container_width=True):
        st.session_state['manage_action_id'] = None
        st.rerun()
with col_title:
    st.markdown("<h2 style='text-align: center; color: #1e3a8a; font-weight: bold; margin:0;'>RTI MANAGE PORTAL</h2>", unsafe_allow_html=True)
with col_search:
    search_term = st.text_input("🔍 સર્ચ કરો:", placeholder="ID કે કચેરી શોધો...", label_visibility="collapsed")

st.markdown("<hr style='border: 1px solid #cfd8dc; margin: 10px 0;'>", unsafe_allow_html=True)

# --- કાઉન્ટર ડેટા ---
total_rti = len(user_df)
pending_rti = len(user_df[user_df["સ્ટેટસ"] != "નિકાલ"]) if not user_df.empty else 0
first_due = len(user_df[user_df["સ્ટેટસ"] == "પ્રથમ અપીલ બાકી"]) if not user_df.empty else 0
first_done = len(user_df[user_df["સ્ટેટસ"].isin(["પ્રથમ અપીલ પેન્ડિંગ", "બીજી અપીલ બાકી", "બીજી અપીલ પેન્ડિંગ"])]) if not user_df.empty else 0
second_due = len(user_df[user_df["સ્ટેટસ"] == "બીજી અપીલ બાકી"]) if not user_df.empty else 0
second_done = len(user_df[user_df["સ્ટેટસ"] == "બીજી અપીલ પેન્ડિંગ"]) if not user_df.empty else 0
nikal_rti = len(user_df[user_df["સ્ટેટસ"] == "નિકાલ"]) if not user_df.empty else 0

# --- કલરફુલ બોક્સ ---
r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
with r1_c1: st.markdown(f'<div class="box b-blue"><p class="label-text">કુલ RTI</p><p class="number-text">{total_rti}</p></div>', unsafe_allow_html=True)
with r1_c2: st.markdown(f'<div class="box b-orange"><p class="label-text">પેન્ડિંગ (કુલ બાકી)</p><p class="number-text">{pending_rti}</p></div>', unsafe_allow_html=True)
with r1_c3: st.markdown(f'<div class="box b-brown"><p class="label-text">પ્રથમ અપીલ બાકી</p><p class="number-text">{first_due}</p></div>', unsafe_allow_html=True)
with r1_c4: st.markdown(f'<div class="box b-red"><p class="label-text">પ્રથમ અપીલ કરેલ</p><p class="number-text">{first_done}</p></div>', unsafe_allow_html=True)

r2_c1, r2_c2, r2_c3 = st.columns(3)
with r2_c1: st.markdown(f'<div class="box b-purple"><p class="label-text">બીજી અપીલ બાકી</p><p class="number-text">{second_due}</p></div>', unsafe_allow_html=True)
with r2_c2: st.markdown(f'<div class="box b-deeppurple"><p class="label-text">બીજી અપીલ કરેલ</p><p class="number-text">{second_done}</p></div>', unsafe_allow_html=True)
with r2_c3: st.markdown(f'<div class="box b-green"><p class="label-text">અરજીનો નિકાલ</p><p class="number-text">{nikal_rti}</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- ટેબ્સ ---
tab1, tab2, tab3, tab4 = st.tabs(["🆕 નવી RTI", "⚖️ પ્રથમ અપીલ", "🏛️ બીજી અપીલ", "⚙️ મેનેજમેન્ટ, એડિટ & નિકાલ"])

with tab1:
    with st.form("new_rti_form", clear_on_submit=True):
        st.subheader("જાહેર માહિતી અધિકારીશ્રીની વિગતો")
        col_a, col_b = st.columns(2)
        with col_a:
            rti_date = st.date_input("RTI કર્યાની તારીખ")
            pio_name = st.text_input("કચેરીનું નામ")
            pio_address = st.text_area("સરનામું")
        with col_b:
            pio_pin = st.text_input("પિન કોડ")
            pio_mob = st.text_input("મોબાઈલ નંબર")
            rti_speed = st.text_input("સ્પીડ પોસ્ટ નંબર")
            rti_file = st.file_uploader("PDF ફાઈલ અપલોડ કરો", type=["pdf", "png", "jpg"])
        
        if st.form_submit_button("SAVE RTI"):
            with st.spinner('ગૂગલ ડ્રાઇવમાં સેવ થઈ રહ્યું છે...'):
                new_id = "1" if df.empty else str(int(pd.to_numeric(df['ID'], errors='coerce').dropna().max() + 1))
                new_row = {col: "" for col in ALL_COLS}
                new_row.update({"ID": new_id, "User_Mobile": str(st.session_state['user_mobile']), "સ્ટેટસ": "પેન્ડિંગ", 
                                "RTI_તારીખ": str(rti_date), "PIO_કચેરી": pio_name, "PIO_સરનામું": pio_address, 
                                "PIO_પિનકોડ": pio_pin, "PIO_મોબાઈલ": pio_mob, "RTI_સ્પીડપોસ્ટ": rti_speed, 
                                "RTI_ફાઈલ": save_uploaded_file(rti_file)})
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data_to_sheet(df)
            st.success(f"નવી RTI સફળતાપૂર્વક ડ્રાઇવમાં સેવ થઈ ગઈ છે! ID: {new_id}")
            st.rerun()

with tab2:
    first_rtis = user_df[user_df['સ્ટેટસ'].isin(['પ્રથમ અપીલ બાકી', 'પેન્ડિંગ'])] if not user_df.empty else pd.DataFrame()
    if not first_rtis.empty:
        selected_rti = st.selectbox("RTI પસંદ કરો", first_rtis.apply(lambda x: f"ID: {x['ID']} - {x['PIO_કચેરી']} ({x['સ્ટેટસ']})", axis=1))
        rti_id = selected_rti.split(" - ")[0].replace("ID: ", "").strip()
        e_row = user_df[user_df['ID'] == rti_id].iloc[0]
        
        with st.form("first_appeal_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                faa_date = st.date_input("અપીલ કર્યાની તારીખ")
                faa_hearing = st.text_input("સુનાવણીની તારીખ", value=str(e_row.get('FAA_સુનાવણી_તારીખ', '')))
                faa_name = st.text_input("અધિકારી શ્રી નું નામ/હોદ્દો", value=str(e_row.get('FAA_અધિકારી', '')))
            with col_b:
                faa_address = st.text_area("સરનામું", value=str(e_row.get('FAA_સરનામું', '')))
                faa_speed = st.text_input("સ્પીડ પોસ્ટ નંબર", value=str(e_row.get('FAA_સ્પીડપોસ્ટ', '')))
                faa_file = st.file_uploader("પ્રથમ અપીલની PDF", type=["pdf"])
            if st.form_submit_button("SAVE FIRST APPEAL"):
                with st.spinner('ગૂગલ ડ્રાઇવમાં સેવ થઈ રહ્યું છે...'):
                    r_idx = df[df['ID'] == rti_id].index[0]
                    df.at[r_idx, 'FAA_તારીખ'] = str(faa_date)
                    df.at[r_idx, 'FAA_સુનાવણી_તારીખ'] = str(faa_hearing)
                    df.at[r_idx, 'FAA_અધિકારી'] = str(faa_name)
                    df.at[r_idx, 'FAA_સરનામું'] = str(faa_address)
                    df.at[r_idx, 'FAA_સ્પીડપોસ્ટ'] = str(faa_speed)
                    if faa_file: df.at[r_idx, 'FAA_ફાઈલ'] = save_uploaded_file(faa_file)
                    df.at[r_idx, 'સ્ટેટસ'] = 'પ્રથમ અપીલ પેન્ડિંગ'
                    save_data_to_sheet(df)
                st.success("પ્રથમ અપીલ ડ્રાઇવમાં સેવ થઈ ગઈ છે!")
                st.rerun()
    else: st.warning("પ્રથમ અપીલ માટે કોઈ અરજી બાકી નથી.")

with tab3:
    second_rtis = user_df[user_df['સ્ટેટસ'].isin(['બીજી અપીલ બાકી', 'પ્રથમ અપીલ પેન્ડિંગ'])] if not user_df.empty else pd.DataFrame()
    if not second_rtis.empty:
        selected_sa = st.selectbox("અરજી પસંદ કરો (બીજી અપીલ)", second_rtis.apply(lambda x: f"ID: {x['ID']} - {x['PIO_કચેરી']} ({x['સ્ટેટસ']})", axis=1))
        sa_id = selected_sa.split(" - ")[0].replace("ID: ", "").strip()
        e_row_sa = user_df[user_df['ID'] == sa_id].iloc[0]
        
        with st.form("second_appeal_form"):
            sa_date = st.date_input("બીજી અપીલની તારીખ")
            sa_hearing = st.text_input("સુનાવણીની તારીખ", value=str(e_row_sa.get('SA_સુનાવણી_તારીખ', '')))
            sa_speed = st.text_input("સ્પીડ પોસ્ટ નંબર", value=str(e_row_sa.get('SA_સ્પીડપોસ્ટ', '')))
            sa_file = st.file_uploader("બીજી અપીલની PDF", type=["pdf"])
            if st.form_submit_button("SAVE SECOND APPEAL"):
                with st.spinner('ગૂગલ ડ્રાઇવમાં સેવ થઈ રહ્યું છે...'):
                    r_idx = df[df['ID'] == sa_id].index[0]
                    df.at[r_idx, 'SA_તારીખ'] = str(sa_date)
                    df.at[r_idx, 'SA_સુનાવણી_તારીખ'] = str(sa_hearing)
                    df.at[r_idx, 'SA_સ્પીડપોસ્ટ'] = str(sa_speed)
                    if sa_file: df.at[r_idx, 'SA_ફાઈલ'] = save_uploaded_file(sa_file)
                    df.at[r_idx, 'સ્ટેટસ'] = 'બીજી અપીલ પેન્ડિંગ'
                    save_data_to_sheet(df)
                st.success("બીજી અપીલ ડ્રાઇવમાં સેવ થઈ ગઈ છે!")
                st.rerun()
    else: st.warning("બીજી અપીલ માટે કોઈ અરજી બાકી નથી.")

with tab4:
    if not user_df.empty:
        edit_choice = st.selectbox("એડિટ, નિકાલ કે ડિલીટ કરવા અરજી પસંદ કરો:", user_df.apply(lambda x: f"ID: {x['ID']} - {x['PIO_કચેરી']}", axis=1))
        edit_id = edit_choice.split(" - ")[0].replace("ID: ", "").strip()
        e_row = user_df[user_df['ID'] == edit_id].iloc[0]
        
        with st.form("edit_rti_form"):
            st.markdown("##### ✏️ અરજીની વિગતો સુધારો (Edit)")
            c1, c2 = st.columns(2)
            with c1:
                ed_pio = st.text_input("કચેરીનું નામ", value=str(e_row.get('PIO_કચેરી', '')))
                ed_addr = st.text_area("સરનામું", value=str(e_row.get('PIO_સરનામું', '')))
            with c2:
                ed_speed = st.text_input("સ્પીડ પોસ્ટ નંબર", value=str(e_row.get('RTI_સ્પીડપોસ્ટ', '')))
                ed_mob = st.text_input("મોબાઈલ નંબર", value=str(e_row.get('PIO_મોબાઈલ', '')))
            
            if st.form_submit_button("✅ વિગતો અપડેટ કરો"):
                r_idx = df[df['ID'] == edit_id].index[0]
                df.at[r_idx, 'PIO_કચેરી'] = str(ed_pio)
                df.at[r_idx, 'PIO_સરનામું'] = str(ed_addr)
                df.at[r_idx, 'RTI_સ્પીડપોસ્ટ'] = str(ed_speed)
                df.at[r_idx, 'PIO_મોબાઈલ'] = str(ed_mob)
                save_data_to_sheet(df)
                st.success("અરજીની વિગતો સફળતાપૂર્વક અપડેટ થઈ ગઈ છે!")
                st.rerun()
        
        st.markdown("<hr>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✅ જવાબ આવી ગયો (નિકાલ કરો)", type="primary", use_container_width=True):
                r_idx = df[df['ID'] == edit_id].index[0]
                df.at[r_idx, 'સ્ટેટસ'] = 'નિકાલ'
                save_data_to_sheet(df)
                st.success("અરજીનો નિકાલ થઈ ગયો છે!")
                st.rerun()
        with col_btn2:
            if st.button("❌ આ અરજી કાયમ માટે ડિલીટ કરો", use_container_width=True):
                df = df[df['ID'] != edit_id]
                save_data_to_sheet(df)
                st.success("અરજી ડિલીટ થઈ ગઈ છે!")
                st.rerun()
    else:
        st.info("કોઈ અરજી ઉપલબ્ધ નથી.")

# --- વ્યુ (View) ફીચર (ગૂગલ ડ્રાઇવ પ્રિવ્યૂ સાથે) ---
if st.session_state['manage_action_id']:
    real_m_id = st.session_state['manage_action_id']
    m_row_data = user_df[user_df['ID'] == real_m_id]
    if not m_row_data.empty:
        st.markdown(f"<div style='background-color: #e0f2fe; padding: 15px; border-radius: 10px; margin: 15px 0;'><h4>📂 અરજીની સંપૂર્ણ વિગતો: ID - {real_m_id}</h4></div>", unsafe_allow_html=True)
        if st.button("❌ બંધ કરો", use_container_width=True):
            st.session_state['manage_action_id'] = None
            st.rerun()
        
        m_row = m_row_data.iloc[0]
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="detail-card"><div class="detail-title">📝 મૂળ RTI ની વિગતો</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="detail-item"><span class="detail-label">RTI તારીખ:</span> {m_row.get("RTI_તારીખ", "-")}</div><div class="detail-item"><span class="detail-label">PIO કચેરી:</span> {m_row.get("PIO_કચેરી", "-")}</div><div class="detail-item"><span class="detail-label">સરનામું:</span> {m_row.get("PIO_સરનામું", "-")}</div><div class="detail-item"><span class="detail-label">સ્પીડ પોસ્ટ:</span> {m_row.get("RTI_સ્પીડપોસ્ટ", "-")}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="detail-card"><div class="detail-title">⚖️ પ્રથમ અપીલની વિગતો</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="detail-item"><span class="detail-label">અપીલ તારીખ:</span> {m_row.get("FAA_તારીખ", "-")}</div><div class="detail-item"><span class="detail-label">અધિકારી:</span> {m_row.get("FAA_અધિકારી", "-")}</div><div class="detail-item"><span class="detail-label">સુનાવણી તારીખ:</span> {m_row.get("FAA_સુનાવણી_તારીખ", "-")}</div><div class="detail-item"><span class="detail-label">સ્પીડ પોસ્ટ:</span> {m_row.get("FAA_સ્પીડપોસ્ટ", "-")}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="detail-card"><div class="detail-title">🏛️ બીજી અપીલની વિગતો</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="detail-item"><span class="detail-label">અપીલ તારીખ:</span> {m_row.get("SA_તારીખ", "-")}</div><div class="detail-item"><span class="detail-label">સુનાવણી તારીખ:</span> {m_row.get("SA_સુનાવણી_તારીખ", "-")}</div><div class="detail-item"><span class="detail-label">સ્પીડ પોસ્ટ:</span> {m_row.get("SA_સ્પીડપોસ્ટ", "-")}</div></div>', unsafe_allow_html=True)

        st.markdown("#### 📄 અપલોડ કરેલા દસ્તાવેજો (ગૂગલ ડ્રાઇવ)")
        def show_pdf(file_id, label):
            if file_id and str(file_id) != "nan" and str(file_id).strip() != "":
                st.write(f"**{label}**")
                # જો તે ડ્રાઇવનો ID હોય (જેમાં સ્લેશ / ના હોય અને લંબાઈ 15 થી વધુ હોય)
                if "/" not in str(file_id) and "\\" not in str(file_id) and len(str(file_id)) > 15:
                    iframe_url = f"https://drive.google.com/file/d/{file_id}/preview"
                    st.markdown(f'<iframe src="{iframe_url}" width="100%" height="450px" style="border: none; border-radius: 8px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);"></iframe>', unsafe_allow_html=True)
                else:
                    # જૂની લોકલ ફાઈલોનો બેકઅપ (જો કોઈ હોય તો)
                    if os.path.exists(str(file_id)):
                        with open(file_id, "rb") as f:
                            b64 = base64.b64encode(f.read()).decode('utf-8')
                        st.markdown(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="450px"></iframe>', unsafe_allow_html=True)

        show_pdf(m_row.get('RTI_ફાઈલ'), "RTI ફાઈલ")
        show_pdf(m_row.get('FAA_ફાઈલ'), "પ્રથમ અપીલ ફાઈલ")
        show_pdf(m_row.get('SA_ફાઈલ'), "બીજી અપીલ ફાઈલ")

st.markdown("---")

# --- લિસ્ટ અને ડ્રોપડાઉન ફિલ્ટર ---
st.subheader("તમારી અરજીઓનું લિસ્ટ")
filter_option = st.selectbox("📂 સ્ટેટસ મુજબ અરજીઓ ફિલ્ટર કરો:", ["બધી અરજીઓ", "પેન્ડિંગ અરજીઓ", "પ્રથમ અપીલ બાકી", "પ્રથમ અપીલ પેન્ડિંગ", "બીજી અપીલ બાકી", "બીજી અપીલ પેન્ડિંગ", "નિકાલ થયેલ"])

if not user_df.empty:
    if search_term:
        filtered_df = user_df[user_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
    else:
        if filter_option == "પેન્ડિંગ અરજીઓ": filtered_df = user_df[user_df["સ્ટેટસ"] != "નિકાલ"]
        elif filter_option == "બધી અરજીઓ": filtered_df = user_df
        else: filtered_df = user_df[user_df["સ્ટેટસ"] == filter_option]
    
    h1, h2, h3, h4, h5, h6, h7 = st.columns([0.6, 1.2, 1.8, 2.2, 1.5, 1.5, 1.2])
    with h1: st.markdown('<div class="table-header">Sr.</div>', unsafe_allow_html=True)
    with h2: st.markdown('<div class="table-header">ID</div>', unsafe_allow_html=True)
    with h3: st.markdown('<div class="table-header">Applicant</div>', unsafe_allow_html=True)
    with h4: st.markdown('<div class="table-header">PIO Office</div>', unsafe_allow_html=True)
    with h5: st.markdown('<div class="table-header">RTI Date</div>', unsafe_allow_html=True)
    with h6: st.markdown('<div class="table-header">Status</div>', unsafe_allow_html=True)
    with h7: st.markdown('<div class="table-header">Action</div>', unsafe_allow_html=True)
    
    for i, (index, row) in enumerate(filtered_df.iterrows()):
        r1, r2, r3, r4, r5, r6, r7 = st.columns([0.6, 1.2, 1.8, 2.2, 1.5, 1.5, 1.2])
        with r1: st.markdown(f'<div class="table-row"><b>{i+1}</b></div>', unsafe_allow_html=True)
        with r2: st.markdown(f'<div class="table-row"><b>{row["ID"]}</b></div>', unsafe_allow_html=True)
        with r3: st.markdown(f'<div class="table-row">{st.session_state["user_name"]}</div>', unsafe_allow_html=True)
        with r4: st.markdown(f'<div class="table-row">{row.get("PIO_કચેરી", "-")}</div>', unsafe_allow_html=True)
        with r5: st.markdown(f'<div class="table-row">{row.get("RTI_તારીખ", "-")}</div>', unsafe_allow_html=True) 
        with r6: st.markdown(f'<div class="table-row"><b>{row.get("સ્ટેટસ", "-")}</b></div>', unsafe_allow_html=True)
        with r7:
            if st.button("👁️ જુઓ", key=f"btn_{row['ID']}", use_container_width=True):
                st.session_state['manage_action_id'] = row['ID']
                st.rerun()
else:
    st.info("કોઈ અરજી ઉપલબ્ધ નથી.")