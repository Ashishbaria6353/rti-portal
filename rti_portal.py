import streamlit as st
import pandas as pd
from datetime import date
import os
import base64
import gspread

# --- પેજ સેટઅપ ---
st.set_page_config(page_title="RTI Manage Portal", layout="wide")

# --- સ્માર્ટ અને પરફેક્ટ ગૂગલ શીટ કનેક્શન ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # ઓનલાઈન ક્લાઉડ માટે
    from google.oauth2.service_account import Credentials
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
except:
    # લોકલ કમ્પ્યુટર માટે
    from oauth2client.service_account import ServiceAccountCredentials
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

client = gspread.authorize(creds)
sheet = client.open("RTI_Database").sheet1

# --- શાનદાર કલર અને ડિઝાઇન માટેની CSS ---
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container { background-color: #f8f9fa; border: 2px solid #cfd8dc; border-radius: 12px; padding: 1.5rem 1rem !important; box-shadow: 0px 4px 12px rgba(0,0,0,0.1); margin-top: 1rem; }
button[kind="primary"] { background: linear-gradient(to right, #e53935, #ef5350) !important; color: white !important; font-weight: bold !important; border-radius: 6px !important; border: none !important; }
div[data-testid="stFormSubmitButton"] button { background: linear-gradient(to right, #1976d2, #42a5f5) !important; }

.box { padding: 14px 10px; border-radius: 10px; text-align: center; color: white; font-family: sans-serif; box-shadow: 0px 4px 8px rgba(0,0,0,0.15); margin-bottom: 12px; }
.b-blue { background: linear-gradient(to right, #1976d2, #42a5f5); }          
.b-orange { background: linear-gradient(to right, #f57c00, #ffa726); }       
.b-brown { background: linear-gradient(to right, #4e342e, #6d4c41); }        
.b-red { background: linear-gradient(to right, #d32f2f, #ef5350); }          
.b-purple { background: linear-gradient(to right, #7b1fa2, #ab47bc); }       
.b-deeppurple { background: linear-gradient(to right, #311b92, #5e35b1); }   
.b-green { background: linear-gradient(to right, #388e3c, #66bb6a); }         

.number-text { font-size: 26px; font-weight: bold; margin: 4px 0 0 0; }
.label-text { font-size: 14px; font-weight: 600; margin: 0; }

.table-header { background-color: #3b5998; color: white; padding: 8px; border-radius: 6px; font-weight: bold; text-align: center; margin-bottom: 6px; font-size: 13px; }
.table-row { background-color: white; padding: 8px; border-radius: 6px; border: 1px solid #cfd8dc; text-align: center; margin-bottom: 6px; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# --- પરમેનન્ટ લૉગિન સિસ્ટમ ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user_name' not in st.session_state: st.session_state['user_name'] = ""
if 'user_mobile' not in st.session_state: st.session_state['user_mobile'] = ""
if 'manage_action_id' not in st.session_state: st.session_state['manage_action_id'] = None

params = st.query_params
if "mobile" in params and not st.session_state['logged_in']:
    st.session_state['logged_in'] = True
    st.session_state['user_mobile'] = params["mobile"]
    if "name" in params: st.session_state['user_name'] = params["name"]

if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align: center; color: #1e3a8a; margin-top: 30px;'>RTI MANAGE PORTAL</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #2e7d32; margin-bottom: 5px;'>👋 આપનું સ્વાગત છે!</h4>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>કૃપા કરીને આગળ વધવા માટે નામ અને મોબાઈલ નંબર દાખલ કરો</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            u_name = st.text_input("તમારું પૂરું નામ")
            u_mob = st.text_input("તમારો મોબાઈલ નંબર")
            if st.form_submit_button("લૉગિન કરો (Login)", type="primary"):
                if u_name and u_mob:
                    st.session_state.update({'logged_in': True, 'user_name': u_name, 'user_mobile': str(u_mob)})
                    st.query_params.update({"mobile": str(u_mob), "name": u_name})
                    st.rerun()
                else:
                    st.error("નામ અને મોબાઈલ નંબર બંને દાખલ કરવા જરૂરી છે!")
    st.stop()

# --- સાઈડબાર ---
with st.sidebar:
    st.markdown("### 👤 તમારું પ્રોફાઈલ")
    st.info(f"**નામ:** {st.session_state['user_name']}\n\n**મોબાઈલ:** {st.session_state['user_mobile']}")
    st.markdown("---")
    if st.button("લૉગઆઉટ કરો (Logout)", type="primary", use_container_width=True):
        st.session_state.clear()
        st.query_params.clear()
        st.rerun()

EXTRA_DOCS_FILE = "rti_extra_docs_v6.csv"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return "ફાઈલ નથી"

ALL_COLS = ['ID', 'User_Mobile', 'સ્ટેટસ', 'RTI_તારીખ', 'PIO_કચેરી', 'PIO_સરનામું', 'PIO_પિનકોડ', 'PIO_મોબાઈલ', 'RTI_સ્પીડપોસ્ટ', 'RTI_ફાઈલ', 
            'FAA_તારીખ', 'FAA_સુનાવણી_તારીખ', 'FAA_અધિકારી', 'FAA_સરનામું', 'FAA_પિનકોડ', 'FAA_મોબાઈલ', 'FAA_સ્પીડપોસ્ટ', 'FAA_ફાઈલ', 
            'SA_તારીખ', 'SA_સુનાવણી_તારીખ', 'SA_સ્પીડપોસ્ટ', 'SA_ફાઈલ']

# --- ગૂગલ શીટમાંથી ડેટા લોડ કરવો (Crash Proof) ---
def load_data():
    try:
        data = sheet.get_all_records()
        if not data:
            return pd.DataFrame(columns=ALL_COLS)
        df = pd.DataFrame(data)
        for col in ALL_COLS:
            if col not in df.columns:
                df[col] = ""
        return df.astype(str)
    except:
        return pd.DataFrame(columns=ALL_COLS)

def save_data_to_sheet(df):
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

df = load_data()
user_df = df[df['User_Mobile'] == st.session_state['user_mobile']].copy() if not df.empty else pd.DataFrame(columns=ALL_COLS)

if not user_df.empty and 'સ્ટેટસ' in user_df.columns:
    user_df['સ્ટેટસ'] = user_df['સ્ટેટસ'].replace('', 'પેન્ડિંગ')

# --- ટોચ પર Home બટન, સેન્ટર હેડિંગ અને સર્ચ બોક્સ ---
col_home, col_title, col_search = st.columns([1, 2, 1.5])
with col_home:
    if st.button("🏠 Home", use_container_width=True):
        st.session_state['manage_action_id'] = None
        st.rerun()
with col_title:
    st.markdown("<h2 style='text-align: center; color: #1e3a8a; font-weight: bold; margin:0;'>RTI MANAGE PORTAL</h2>", unsafe_allow_html=True)
with col_search:
    search_term = st.text_input("🔍 સર્ચ કરો:", placeholder="ID, કચેરી કે મોબાઈલ...", label_visibility="collapsed")

st.markdown("<hr style='border: 1px solid #cfd8dc; margin: 10px 0;'>", unsafe_allow_html=True)

# --- કાઉન્ટર ડેટા મેળવો (Crash Proof) ---
total_rti = len(user_df) if not user_df.empty else 0
pending_rti = len(user_df[user_df["સ્ટેટસ"] != "નિકાલ"]) if not user_df.empty else 0
first_due = len(user_df[user_df["સ્ટેટસ"] == "પ્રથમ અપીલ બાકી"]) if not user_df.empty else 0
first_done = len(user_df[user_df["સ્ટેટસ"].isin(["પ્રથમ અપીલ પેન્ડિંગ", "બીજી અપીલ બાકી", "બીજી અપીલ પેન્ડિંગ"])]) if not user_df.empty else 0
second_due = len(user_df[user_df["સ્ટેટસ"] == "બીજી અપીલ બાકી"]) if not user_df.empty else 0
second_done = len(user_df[user_df["સ્ટેટસ"] == "બીજી અપીલ પેન્ડિંગ"]) if not user_df.empty else 0
nikal_rti = len(user_df[user_df["સ્ટેટસ"] == "નિકાલ"]) if not user_df.empty else 0

# --- કલરફુલ બોક્સ ---
r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
with r1_c1: st.markdown(f'<div class="box b-blue"><p class="label-text">કુલ RTI</p><p class="number-text">{total_rti}</p></div>', unsafe_allow_html=True)
with r1_c2: st.markdown(f'<div class="box b-orange"><p class="label-text">પેન્ડિંગ</p><p class="number-text">{pending_rti}</p></div>', unsafe_allow_html=True)
with r1_c3: st.markdown(f'<div class="box b-brown"><p class="label-text">પ્રથમ અપીલ બાકી</p><p class="number-text">{first_due}</p></div>', unsafe_allow_html=True)
with r1_c4: st.markdown(f'<div class="box b-red"><p class="label-text">પ્રથમ અપીલ</p><p class="number-text">{first_done}</p></div>', unsafe_allow_html=True)

r2_c1, r2_c2, r2_c3 = st.columns(3)
with r2_c1: st.markdown(f'<div class="box b-purple"><p class="label-text">બીજી અપીલ બાકી</p><p class="number-text">{second_due}</p></div>', unsafe_allow_html=True)
with r2_c2: st.markdown(f'<div class="box b-deeppurple"><p class="label-text">બીજી અપીલ</p><p class="number-text">{second_done}</p></div>', unsafe_allow_html=True)
with r2_c3: st.markdown(f'<div class="box b-green"><p class="label-text">નિકાલ</p><p class="number-text">{nikal_rti}</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- ટેબ્સ ---
tab1, tab2, tab3, tab4 = st.tabs(["🆕 નવી RTI", "⚖️ પ્રથમ અપીલ", "🏛️ બીજી અપીલ", "⚙️ મેનેજમેન્ટ & ડિલીટ"])

# નવી RTI
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
            new_id = "1" if df.empty else str(int(pd.to_numeric(df['ID'], errors='coerce').dropna().max() + 1))
            new_row = {col: "" for col in ALL_COLS}
            new_row.update({"ID": new_id, "User_Mobile": str(st.session_state['user_mobile']), "સ્ટેટસ": "પેન્ડિંગ", 
                            "RTI_તારીખ": str(rti_date), "PIO_કચેરી": pio_name, "PIO_સરનામું": pio_address, 
                            "PIO_પિનકોડ": pio_pin, "PIO_મોબાઈલ": pio_mob, "RTI_સ્પીડપોસ્ટ": rti_speed, 
                            "RTI_ફાઈલ": save_uploaded_file(rti_file)})
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data_to_sheet(df)
            st.success(f"નવી RTI સફળતાપૂર્વક ગૂગલ શીટમાં સેવ થઈ ગઈ છે! ID: {new_id}")
            st.rerun()

# પ્રથમ અપીલ
with tab2:
    st.subheader("⚖️ પ્રથમ અપીલની વિગતો")
    first_rtis = user_df[user_df['સ્ટેટસ'] != 'નિકાલ'] if not user_df.empty else pd.DataFrame()
    if not first_rtis.empty:
        selected_rti = st.selectbox("RTI પસંદ કરો", first_rtis.apply(lambda x: f"ID: {x['ID']} - {x['PIO_કચેરી']}", axis=1))
        rti_id = selected_rti.split(" - ")[0].replace("ID: ", "").strip()
        e_row = user_df[user_df['ID'] == rti_id].iloc[0]
        
        with st.form("first_appeal_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                faa_date = st.date_input("અપીલ કર્યાની તારીખ")
                faa_hearing = st.text_input("સુનાવણીની તારીખ", value=str(e_row.get('FAA_સુનાવણી_તારીખ', '')))
                faa_name = st.text_input("અધિકારી શ્રી નું નામ", value=str(e_row.get('FAA_અધિકારી', '')))
            with col_b:
                faa_address = st.text_area("સરનામું", value=str(e_row.get('FAA_સરનામું', '')))
                faa_speed = st.text_input("સ્પીડ પોસ્ટ ટ્રેકિંગ નંબર", value=str(e_row.get('FAA_સ્પીડપોસ્ટ', '')))
                faa_file = st.file_uploader("પ્રથમ અપીલની PDF", type=["pdf"])
            if st.form_submit_button("SAVE FIRST APPEAL"):
                r_idx = df[df['ID'] == rti_id].index[0]
                df.at[r_idx, 'FAA_તારીખ'] = str(faa_date)
                df.at[r_idx, 'FAA_સુનાવણી_તારીખ'] = str(faa_hearing)
                df.at[r_idx, 'FAA_અધિકારી'] = str(faa_name)
                df.at[r_idx, 'FAA_સરનામું'] = str(faa_address)
                df.at[r_idx, 'FAA_સ્પીડપોસ્ટ'] = str(faa_speed)
                if faa_file: df.at[r_idx, 'FAA_ફાઈલ'] = save_uploaded_file(faa_file)
                df.at[r_idx, 'સ્ટેટસ'] = 'પ્રથમ અપીલ પેન્ડિંગ'
                save_data_to_sheet(df)
                st.success("પ્રથમ અપીલ સેવ થઈ ગઈ છે!")
                st.rerun()
    else: st.info("કોઈ અરજી ઉપલબ્ધ નથી.")

# બીજી અપીલ
with tab3:
    st.subheader("🏛️ બીજી અપીલ (ગુજરાત માહિતી આયોગ)")
    if not first_rtis.empty:
        selected_sa = st.selectbox("અરજી પસંદ કરો (બીજી અપીલ)", first_rtis.apply(lambda x: f"ID: {x['ID']} - {x['PIO_કચેરી']}", axis=1))
        sa_id = selected_sa.split(" - ")[0].replace("ID: ", "").strip()
        e_row_sa = user_df[user_df['ID'] == sa_id].iloc[0]
        
        with st.form("second_appeal_form"):
            sa_date = st.date_input("બીજી અપીલની તારીખ")
            sa_hearing = st.text_input("સુનાવણીની તારીખ", value=str(e_row_sa.get('SA_સુનાવણી_તારીખ', '')))
            sa_speed = st.text_input("સ્પીડ પોસ્ટ નંબર", value=str(e_row_sa.get('SA_સ્પીડપોસ્ટ', '')))
            sa_file = st.file_uploader("બીજી અપીલની PDF", type=["pdf"])
            if st.form_submit_button("SAVE SECOND APPEAL"):
                r_idx = df[df['ID'] == sa_id].index[0]
                df.at[r_idx, 'SA_તારીખ'] = str(sa_date)
                df.at[r_idx, 'SA_સુનાવણી_તારીખ'] = str(sa_hearing)
                df.at[r_idx, 'SA_સ્પીડપોસ્ટ'] = str(sa_speed)
                if sa_file: df.at[r_idx, 'SA_ફાઈલ'] = save_uploaded_file(sa_file)
                df.at[r_idx, 'સ્ટેટસ'] = 'બીજી અપીલ પેન્ડિંગ'
                save_data_to_sheet(df)
                st.success("બીજી અપીલ સેવ થઈ ગઈ છે!")
                st.rerun()
    else: st.info("કોઈ અરજી ઉપલબ્ધ નથી.")

# મેનેજમેન્ટ
with tab4:
    st.subheader("✏️ અરજી ડિલીટ કરો અથવા નિકાલ કરો")
    if not user_df.empty:
        edit_choice = st.selectbox("અરજી પસંદ કરો:", user_df.apply(lambda x: f"ID: {x['ID']} - {x['PIO_કચેરી']}", axis=1))
        edit_id = edit_choice.split(" - ")[0].replace("ID: ", "").strip()
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✅ આ અરજીનો નિકાલ કરો (Dispose)", type="primary", use_container_width=True):
                r_idx = df[df['ID'] == edit_id].index[0]
                df.at[r_idx, 'સ્ટેટસ'] = 'નિકાલ'
                save_data_to_sheet(df)
                st.success("અરજીનો નિકાલ થઈ ગયો છે!")
                st.rerun()
        with col_btn2:
            if st.button("❌ આ અરજી ડિલીટ કરો", use_container_width=True):
                df = df[df['ID'] != edit_id]
                save_data_to_sheet(df)
                st.success("અરજી ડિલીટ થઈ ગઈ છે!")
                st.rerun()

# --- પ્રોફેશનલ ટેબલ અને વ્યુ (View) ફીચર ---
if st.session_state['manage_action_id']:
    real_m_id = st.session_state['manage_action_id']
    m_row_data = user_df[user_df['ID'] == real_m_id]
    if not m_row_data.empty:
        st.markdown("<div style='background-color: #f1f8ff; padding: 15px; border: 2px solid #7ab8eb; border-radius: 10px; margin: 15px 0;'>", unsafe_allow_html=True)
        col_t, col_btn = st.columns([3, 1])
        with col_t: st.markdown(f"<h4 style='color: #1e3a8a; margin:0;'>📂 દસ્તાવેજો: ID - {real_m_id}</h4>", unsafe_allow_html=True)
        with col_btn:
            if st.button("❌ બંધ કરો", use_container_width=True):
                st.session_state['manage_action_id'] = None
                st.rerun()
        
        m_row = m_row_data.iloc[0]
        def show_pdf(file_path, label):
            if file_path and str(file_path) != "ફાઈલ નથી" and os.path.exists(str(file_path)):
                st.write(f"**{label}**")
                with open(file_path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400px"></iframe>', unsafe_allow_html=True)
        
        show_pdf(m_row.get('RTI_ફાઈલ'), "RTI ફાઈલ")
        show_pdf(m_row.get('FAA_ફાઈલ'), "પ્રથમ અપીલ ફાઈલ")
        show_pdf(m_row.get('SA_ફાઈલ'), "બીજી અપીલ ફાઈલ")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.subheader("તમારી અરજીઓનું લિસ્ટ")

if not user_df.empty:
    filtered_df = user_df[user_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)] if search_term else user_df
    
    h1, h2, h3, h4, h5, h6 = st.columns([0.6, 1.2, 1.8, 2.2, 1.4, 1.4])
    with h1: st.markdown('<div class="table-header">Sr.</div>', unsafe_allow_html=True)
    with h2: st.markdown('<div class="table-header">ID</div>', unsafe_allow_html=True)
    with h3: st.markdown('<div class="table-header">Applicant</div>', unsafe_allow_html=True)
    with h4: st.markdown('<div class="table-header">PIO Office</div>', unsafe_allow_html=True)
    with h5: st.markdown('<div class="table-header">Status</div>', unsafe_allow_html=True)
    with h6: st.markdown('<div class="table-header">Action</div>', unsafe_allow_html=True)
    
    for i, (index, row) in enumerate(filtered_df.iterrows()):
        r1, r2, r3, r4, r5, r6 = st.columns([0.6, 1.2, 1.8, 2.2, 1.4, 1.4])
        with r1: st.markdown(f'<div class="table-row"><b>{i+1}</b></div>', unsafe_allow_html=True)
        with r2: st.markdown(f'<div class="table-row"><b>{row["ID"]}</b></div>', unsafe_allow_html=True)
        with r3: st.markdown(f'<div class="table-row">{st.session_state["user_name"]}</div>', unsafe_allow_html=True)
        with r4: st.markdown(f'<div class="table-row">{row.get("PIO_કચેરી", "-")}</div>', unsafe_allow_html=True)
        with r5: st.markdown(f'<div class="table-row">{row.get("સ્ટેટસ", "-")}</div>', unsafe_allow_html=True)
        with r6:
            if st.button("👁️ જુઓ", key=f"btn_{row['ID']}", use_container_width=True):
                st.session_state['manage_action_id'] = row['ID']
                st.rerun()
else:
    st.info("કોઈ અરજી ઉપલબ્ધ નથી.")