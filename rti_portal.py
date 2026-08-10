import streamlit as st
import pandas as pd
from datetime import date
import os
import base64

st.set_page_config(page_title="RTI Manage Portal", layout="wide")

# --- શાનદાર કલર અને ડિઝાઇન માટેની CSS ---
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container { background-color: #f8f9fa; border: 2px solid #cfd8dc; border-radius: 12px; padding: 1.5rem 1rem !important; box-shadow: 0px 4px 12px rgba(0,0,0,0.1); margin-top: 1rem; }
button[kind="primary"] { background: linear-gradient(to right, #e53935, #ef5350) !important; color: white !important; font-weight: bold !important; border-radius: 6px !important; border: none !important; }
div[data-testid="stFormSubmitButton"] button { background: linear-gradient(to right, #1976d2, #42a5f5) !important; }

/* ૭ બોક્સ માટેના આકર્ષક અને યુનિક કલર્સ */
.box { padding: 14px 10px; border-radius: 10px; text-align: center; color: white; font-family: sans-serif; box-shadow: 0px 4px 8px rgba(0,0,0,0.15); margin-bottom: 8px; }
.b-blue { background: linear-gradient(to right, #1976d2, #42a5f5); }          /* કુલ RTI */
.b-orange { background: linear-gradient(to right, #f57c00, #ffa726); }       /* પેન્ડિંગ */
.b-brown { background: linear-gradient(to right, #4e342e, #6d4c41); }        /* પ્રથમ અપીલ બાકી */
.b-red { background: linear-gradient(to right, #d32f2f, #ef5350); }          /* પ્રથમ અપીલ */
.b-purple { background: linear-gradient(to right, #7b1fa2, #ab47bc); }       /* બીજી અપીલ બાકી */
.b-deeppurple { background: linear-gradient(to right, #311b92, #5e35b1); }   /* બીજી અપીલ */
.b-green { background: linear-gradient(to right, #388e3c, #66bb6a); }         /* નિકાલ */

.number-text { font-size: 28px; font-weight: bold; margin: 4px 0 0 0; }
.label-text { font-size: 14px; font-weight: 600; margin: 0; }

.table-header { background-color: #3b5998; color: white; padding: 8px; border-radius: 6px; font-weight: bold; text-align: center; margin-bottom: 6px; font-size: 13px; }
.table-row { background-color: white; padding: 8px; border-radius: 6px; border: 1px solid #cfd8dc; text-align: center; margin-bottom: 6px; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# --- પરમેનન્ટ લૉગિન સિસ્ટમ ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""
if 'user_mobile' not in st.session_state:
    st.session_state['user_mobile'] = ""
if 'manage_action_id' not in st.session_state:
    st.session_state['manage_action_id'] = None
if 'selected_filter' not in st.session_state:
    st.session_state['selected_filter'] = "All"

params = st.query_params
if "mobile" in params and not st.session_state['logged_in']:
    st.session_state['logged_in'] = True
    st.session_state['user_mobile'] = params["mobile"]
    if "name" in params:
        st.session_state['user_name'] = params["name"]

if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align: center; color: #1e3a8a; margin-top: 30px;'>RTI MANAGE PORTAL</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #2e7d32; margin-bottom: 5px;'>👋 આપનું સ્વાગત છે!</h4>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>કૃપા કરીને આગળ વધવા માટે નામ અને મોબાઈલ નંબર દાખલ કરો</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            u_name = st.text_input("તમારું પૂરું નામ")
            u_mob = st.text_input("તમારો મોબાઈલ નંબર")
            submitted = st.form_submit_button("લૉગિન કરો (Login)", type="primary")
            if submitted:
                if u_name != "" and u_mob != "":
                    st.session_state['logged_in'] = True
                    st.session_state['user_name'] = u_name
                    st.session_state['user_mobile'] = str(u_mob)
                    st.query_params["mobile"] = str(u_mob)
                    st.query_params["name"] = u_name
                    st.rerun()
                else:
                    st.error("નામ અને મોબાઈલ નંબર બંને દાખલ કરવા જરૂરી છે!")
    st.stop()

# --- સાઈડબાર (Sidebar / Slider સાથે પ્રોફાઈલ અને લૉગઆઉટ બટન) ---
with st.sidebar:
    st.markdown("### 👤 તમારું પ્રોફાઈલ")
    st.info(f"**નામ:** {st.session_state['user_name']}\n\n**મોબાઈલ:** {st.session_state['user_mobile']}")
    st.markdown("---")
    if st.button("લૉગઆઉટ કરો (Logout)", type="primary", use_container_width=True):
        st.session_state.clear()
        st.query_params.clear()
        st.rerun()

DATA_FILE = "rti_data_v6.csv"
EXTRA_DOCS_FILE = "rti_extra_docs_v6.csv"
UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def save_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return "ફાઈલ નથી"

def load_data():
    cols = ['ID', 'User_Mobile', 'સ્ટેટસ', 'RTI_તારીખ', 'PIO_કચેરી', 'PIO_સરનામું', 'PIO_પિનકોડ', 'PIO_મોબાઈલ', 'RTI_સ્પીડપોસ્ટ', 'RTI_ફાઈલ', 
            'FAA_તારીખ', 'FAA_સુનાવણી_તારીખ', 'FAA_અધિકારી', 'FAA_સરનામું', 'FAA_પિનકોડ', 'FAA_મોબાઈલ', 'FAA_સ્પીડપોસ્ટ', 'FAA_ફાઈલ', 
            'SA_તારીખ', 'SA_સુનાવણી_તારીખ', 'SA_સ્પીડપોસ્ટ', 'SA_ફાઈલ']
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE, dtype=str)
            if df.empty or 'RTI_તારીખ' not in df.columns:
                return pd.DataFrame(columns=cols)
            for col in cols:
                if col not in df.columns:
                    df[col] = ""
            return df
        except Exception:
            return pd.DataFrame(columns=cols)
    else:
        return pd.DataFrame(columns=cols)

def load_extra_docs():
    if os.path.exists(EXTRA_DOCS_FILE):
        return pd.read_csv(EXTRA_DOCS_FILE, dtype=str)
    return pd.DataFrame(columns=['ID', 'Doc_Name', 'File_Path'])

df = load_data()
user_df = df[df['User_Mobile'] == st.session_state['user_mobile']].copy() if not df.empty and 'User_Mobile' in df.columns else pd.DataFrame()
extra_docs_df = load_extra_docs()

if not user_df.empty and 'સ્ટેટસ' not in user_df.columns:
    user_df['સ્ટેટસ'] = 'પેન્ડિંગ'

# --- ઓટોમેટિક ટાઈમ લૉજિક ---
if not user_df.empty:
    today = date.today()
    changed = False
    for index, row in user_df.iterrows():
        real_index = df[df['ID'] == row['ID']].index[0]
        status_val = str(row.get('સ્ટેટસ', 'પેન્ડિંગ'))
        
        rti_str = str(row.get('RTI_તારીખ', ''))
        faa_str = str(row.get('FAA_તારીખ', ''))
        sa_str = str(row.get('SA_તારીખ', ''))
        
        rti_dt = pd.to_datetime(rti_str, errors='coerce').date() if rti_str and rti_str != "nan" else None
        faa_dt = pd.to_datetime(faa_str, errors='coerce').date() if faa_str and faa_str != "nan" else None
        sa_dt = pd.to_datetime(sa_str, errors='coerce').date() if sa_str and sa_str != "nan" else None
        
        if status_val != 'નિકાલ':
            if faa_dt is not None:
                if (today - faa_dt).days > 45 and (sa_dt is None):
                    if status_val != 'બીજી અપીલ બાકી':
                        df.at[real_index, 'સ્ટેટસ'] = 'બીજી અપીલ બાકી'
                        changed = True
                else:
                    if sa_dt is not None:
                        if status_val != 'બીજી અપીલ પેન્ડિંગ':
                            df.at[real_index, 'સ્ટેટસ'] = 'બીજી અપીલ પેન્ડિંગ'
                            changed = True
                    else:
                        if status_val != 'પ્રથમ અપીલ પેન્ડિંગ':
                            df.at[real_index, 'સ્ટેટસ'] = 'પ્રથમ અપીલ પેન્ડિંગ'
                            changed = True
            elif rti_dt is not None:
                if (today - rti_dt).days > 30:
                    if status_val != 'પ્રથમ અપીલ બાકી':
                        df.at[real_index, 'સ્ટેટસ'] = 'પ્રથમ અપીલ બાકી'
                        changed = True
                else:
                    if status_val != 'પેન્ડિંગ':
                        df.at[real_index, 'સ્ટેટસ'] = 'પેન્ડિંગ'
                        changed = True
                        
    if changed:
        df.to_csv(DATA_FILE, index=False)
        user_df = df[df['User_Mobile'] == st.session_state['user_mobile']].copy()

# --- ટોચ પર Home બટન, સેન્ટર હેડિંગ અને સર્ચ બોક્સ ---
col_home, col_title, col_search = st.columns([1, 2, 1.5])
with col_home:
    if st.button("🏠 Home", use_container_width=True):
        st.session_state['manage_action_id'] = None
        st.session_state['selected_filter'] = "All"
        st.rerun()
with col_title:
    st.markdown("<h2 style='text-align: center; color: #1e3a8a; font-weight: bold; margin:0;'>RTI MANAGE PORTAL</h2>", unsafe_allow_html=True)
with col_search:
    search_term = st.text_input("🔍 સર્ચ કરો:", placeholder="ID, કચેરી કે મોબાઈલ...", label_visibility="collapsed")

st.markdown("<hr style='border: 1px solid #cfd8dc; margin: 10px 0;'>", unsafe_allow_html=True)

# --- ફિલ્ટરિંગ લૉજિક ---
if not user_df.empty:
    if search_term:
        filtered_df = user_df[user_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
    else:
        f_val = st.session_state['selected_filter']
        if f_val == "All":
            filtered_df = user_df
        elif f_val == "Pending":
            filtered_df = user_df[user_df["સ્ટેટસ"] != "નિકાલ"]
        elif f_val == "FirstDue":
            filtered_df = user_df[user_df["સ્ટેટસ"] == "પ્રથમ અપીલ બાકી"]
        elif f_val == "FirstDone":
            filtered_df = user_df[user_df["સ્ટેટસ"].isin(["પ્રથમ અપીલ પેન્ડિંગ", "બીજી અપીલ બાકી", "બીજી અપીલ પેન્ડિંગ"])]
        elif f_val == "SecondDue":
            filtered_df = user_df[user_df["સ્ટેટસ"] == "બીજી અપીલ બાકી"]
        elif f_val == "SecondDone":
            filtered_df = user_df[user_df["સ્ટેટસ"] == "બીજી અપીલ પેન્ડિંગ"]
        elif f_val == "Nikal":
            filtered_df = user_df[user_df["સ્ટેટસ"] == "નિકાલ"]
        else:
            filtered_df = user_df
else:
    filtered_df = pd.DataFrame()

# --- કાઉન્ટર ડેટા મેળવો ---
total_rti = len(user_df) if not user_df.empty else 0
pending_rti = len(user_df[user_df["સ્ટેટસ"] != "નિકાલ"]) if not user_df.empty and "સ્ટેટસ" in user_df.columns else 0
first_due = len(user_df[user_df["સ્ટેટસ"] == "પ્રથમ અપીલ બાકી"]) if not user_df.empty and "સ્ટેટસ" in user_df.columns else 0
first_done = len(user_df[user_df["સ્ટેટસ"].isin(["પ્રથમ અપીલ પેન્ડિંગ", "બીજી અપીલ બાકી", "બીજી અપીલ પેન્ડિંગ"])]) if not user_df.empty and "સ્ટેટસ" in user_df.columns else 0
second_due = len(user_df[user_df["સ્ટેટસ"] == "બીજી અપીલ બાકી"]) if not user_df.empty and "સ્ટેટસ" in user_df.columns else 0
second_done = len(user_df[user_df["સ્ટેટસ"] == "બીજી અપીલ પેન્ડિંગ"]) if not user_df.empty and "સ્ટેટસ" in user_df.columns else 0
nikal_rti = len(user_df[user_df["સ્ટેટસ"] == "નિકાલ"]) if not user_df.empty and "સ્ટેટસ" in user_df.columns else 0

# --- ઉપર 4 કલરફુલ બોક્સ (જેના આંકડા પર ક્લિક કરવાથી નીચે ટેબમાં ફિલ્ટર થઈ જશે) ---
r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
with r1_c1:
    st.markdown(f'''
        <div class="box b-blue">
            <p class="label-text">કુલ RTI</p>
            <p class="number-text">{total_rti}</p>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("🔍 જુઓ", key="clk_all", use_container_width=True):
        st.session_state['selected_filter'] = "All"
        st.rerun()

with r1_c2:
    st.markdown(f'''
        <div class="box b-orange">
            <p class="label-text">પેન્ડિંગ</p>
            <p class="number-text">{pending_rti}</p>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("🔍 જુઓ", key="clk_pen", use_container_width=True):
        st.session_state['selected_filter'] = "Pending"
        st.rerun()

with r1_c3:
    st.markdown(f'''
        <div class="box b-brown">
            <p class="label-text">પ્રથમ અપીલ બાકી</p>
            <p class="number-text">{first_due}</p>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("🔍 જુઓ", key="clk_fdue", use_container_width=True):
        st.session_state['selected_filter'] = "FirstDue"
        st.rerun()

with r1_c4:
    st.markdown(f'''
        <div class="box b-red">
            <p class="label-text">પ્રથમ અપીલ</p>
            <p class="number-text">{first_done}</p>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("🔍 જુઓ", key="clk_fdone", use_container_width=True):
        st.session_state['selected_filter'] = "FirstDone"
        st.rerun()

# --- નીચે 3 કલરફુલ બોક્સ ---
r2_c1, r2_c2, r2_c3 = st.columns(3)
with r2_c1:
    st.markdown(f'''
        <div class="box b-purple">
            <p class="label-text">બીજી અપીલ બાકી</p>
            <p class="number-text">{second_due}</p>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("🔍 જુઓ", key="clk_sdue", use_container_width=True):
        st.session_state['selected_filter'] = "SecondDue"
        st.rerun()

with r2_c2:
    st.markdown(f'''
        <div class="box b-deeppurple">
            <p class="label-text">બીજી અપીલ</p>
            <p class="number-text">{second_done}</p>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("🔍 જુઓ", key="clk_sdone", use_container_width=True):
        st.session_state['selected_filter'] = "SecondDone"
        st.rerun()

with r2_c3:
    st.markdown(f'''
        <div class="box b-green">
            <p class="label-text">નિકાલ</p>
            <p class="number-text">{nikal_rti}</p>
        </div>
    ''', unsafe_allow_html=True)
    if st.button("🔍 જુઓ", key="clk_nikal", use_container_width=True):
        st.session_state['selected_filter'] = "Nikal"
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# --- ટેબ્સ ---
tab1, tab2, tab3, tab4 = st.tabs(["🆕 નવી RTI", "⚖️ પ્રથમ અપીલ", "🏛️ બીજી અપીલ", "⚙️ મેનેજમેન્ટ & ડિલીટ"])

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
            if df.empty:
                new_id = "1"
            else:
                existing_ids = pd.to_numeric(df['ID'], errors='coerce').dropna()
                if not existing_ids.empty:
                    new_id = str(int(existing_ids.max()) + 1)
                else:
                    new_id = "1"
            
            new_row = {"ID": new_id, "User_Mobile": st.session_state['user_mobile'], "સ્ટેટસ": "પેન્ડિંગ", "RTI_તારીખ": str(rti_date), "PIO_કચેરી": pio_name, "PIO_સરનામું": pio_address, 
                       "PIO_પિનકોડ": pio_pin, "PIO_મોબાઈલ": pio_mob, "RTI_સ્પીડપોસ્ટ": rti_speed, "RTI_ફાઈલ": save_uploaded_file(rti_file)}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success(f"નવી RTI સફળતાપૂર્વક દાખલ થઈ ગઈ છે! ID: {new_id}")
            st.rerun()

with tab2:
    st.subheader("⚖️ પ્રથમ અપીલની વિગતો અને સુનાવણી તારીખ")
    first_rtis = user_df[user_df['સ્ટેટસ'] != 'નિકાલ'] if not user_df.empty and 'સ્ટેટસ' in user_df.columns else pd.DataFrame()
    if not first_rtis.empty:
        selected_rti = st.selectbox("RTI પસંદ કરો", first_rtis.apply(lambda x: f"ID: {x['ID']} - {x['PIO_કચેરી']} (સ્ટેટસ: {x['સ્ટેટસ']})", axis=1), key="fa_select")
        rti_id = selected_rti.split(" - ")[0].replace("ID: ", "").strip()
        e_row = user_df[user_df['ID'] == rti_id].iloc[0]
        
        with st.form("first_appeal_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                fa_date_val = pd.to_datetime(e_row.get('FAA_તારીખ')).date() if pd.notna(e_row.get('FAA_તારીખ')) and str(e_row.get('FAA_તારીખ')) != "" and str(e_row.get('FAA_તારીખ')) != "NaT" else date.today()
                faa_date = st.date_input("અપીલ કર્યાની તારીખ", value=fa_date_val)
                
                hearing_val = str(e_row.get('FAA_સુનાવણી_તારીખ', ''))
                faa_hearing = st.text_input("સુનાવણીની તારીખ (જો પત્ર આવ્યો હોય તો)", value=hearing_val, placeholder="તારીખ અથવા વિગત લખો...")
                
                faa_name = st.text_input("પ્રથમ અપીલ અધિકારી શ્રી નું નામ/હોદ્દો", value=str(e_row.get('FAA_અધિકારી', '')))
                faa_address = st.text_area("સરનામું (પ્રથમ અપીલ)", value=str(e_row.get('FAA_સરનામું', '')))
            with col_b:
                faa_pin = st.text_input("પિન કોડ", value=str(e_row.get('FAA_પિનકોડ', '')))
                faa_mob = st.text_input("મોબાઈલ નંબર", value=str(e_row.get('FAA_મોબાઈલ', '')))
                faa_speed = st.text_input("સ્પીડ પોસ્ટ ટ્રેકિંગ નંબર", value=str(e_row.get('FAA_સ્પીડપોસ્ટ', '')))
                faa_file = st.file_uploader("પ્રથમ અપીલની PDF", type=["pdf", "png", "jpg"])
            
            if st.form_submit_button("SAVE FIRST APPEAL"):
                r_idx = df[df['ID'] == rti_id].index[0]
                df.at[r_idx, 'FAA_તારીખ'] = str(faa_date)
                df.at[r_idx, 'FAA_સુનાવણી_તારીખ'] = str(faa_hearing)
                df.at[r_idx, 'FAA_અધિકારી'] = str(faa_name)
                df.at[r_idx, 'FAA_સરનામું'] = str(faa_address)
                df.at[r_idx, 'FAA_પિનકોડ'] = str(faa_pin)
                df.at[r_idx, 'FAA_મોબાઈલ'] = str(faa_mob)
                df.at[r_idx, 'FAA_સ્પીડપોસ્ટ'] = str(faa_speed)
                if faa_file is not None:
                    df.at[r_idx, 'FAA_ફાઈલ'] = save_uploaded_file(faa_file)
                df.at[r_idx, 'સ્ટેટસ'] = 'પ્રથમ અપીલ પેન્ડિંગ'
                df.to_csv(DATA_FILE, index=False)
                st.success("પ્રથમ અપીલ સફળતાપૂર્વક સેવ થઈ ગઈ છે!")
                st.rerun()
    else: 
        st.info("કોઈ અરજી ઉપલબ્ધ નથી.")

with tab3:
    st.subheader("🏛️ બીજી અપીલ (ગુજરાત માહિતી આયોગ) વિગતો")
    second_rtis = user_df[user_df['સ્ટેટસ'] != 'નિકાલ'] if not user_df.empty and 'સ્ટેટસ' in user_df.columns else pd.DataFrame()
    if not second_rtis.empty:
        selected_sa = st.selectbox("અરજી પસંદ કરો", second_rtis.apply(lambda x: f"ID: {x['ID']} - {x['PIO_કચેરી']} (સ્ટેટસ: {x['સ્ટેટસ']})", axis=1), key="sa_select")
        sa_id = selected_sa.split(" - ")[0].replace("ID: ", "").strip()
        e_row_sa = user_df[user_df['ID'] == sa_id].iloc[0]
        
        st.info("**🏛️ ગુજરાત માહિતી આયોગ** | **સરનામું:** કર્મયોગી ભવન, ગાંધીનગર - 382010")
        with st.form("second_appeal_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                sa_date_val = pd.to_datetime(e_row_sa.get('SA_તારીખ')).date() if pd.notna(e_row_sa.get('SA_તારીખ')) and str(e_row_sa.get('SA_તારીખ')) != "" and str(e_row_sa.get('SA_તારીખ')) != "NaT" else date.today()
                sa_date = st.date_input("બીજી અપીલની તારીખ", value=sa_date_val)
                
                sa_hearing_val = str(e_row_sa.get('SA_સુનાવણી_તારીખ', ''))
                sa_hearing = st.text_input("બીજી અપીલ સુનાવણીની તારીખ", value=sa_hearing_val, placeholder="તારીખ અથવા વિગત લખો...")
                
                sa_speed = st.text_input("સ્પીડ પોસ્ટ નંબર", value=str(e_row_sa.get('SA_સ્પીડપોસ્ટ', '')))
            with col_b:
                sa_file = st.file_uploader("બીજી અપીલની PDF", type=["pdf", "png", "jpg"])
            
            if st.form_submit_button("SAVE SECOND APPEAL"):
                r_idx = df[df['ID'] == sa_id].index[0]
                df.at[r_idx, 'SA_તારીખ'] = str(sa_date)
                df.at[r_idx, 'SA_સુનાવણી_તારીખ'] = str(sa_hearing)
                df.at[r_idx, 'SA_સ્પીડપોસ્ટ'] = str(sa_speed)
                if sa_file is not None:
                    df.at[r_idx, 'SA_ફાઈલ'] = save_uploaded_file(sa_file)
                df.at[r_idx, 'સ્ટેટસ'] = 'બીજી અપીલ પેન્ડિંગ'
                df.to_csv(DATA_FILE, index=False)
                st.success("બીજી અપીલ સફળતાપૂર્વક સેવ થઈ ગઈ છે!")
                st.rerun()
    else: 
        st.info("કોઈ અરજી ઉપલબ્ધ નથી.")

# TAB 4: મેનેજમેન્ટ, એડિટ અને ડિલીટ
with tab4:
    st.subheader("📊 એક્સેલ રિપોર્ટ ડાઉનલોડ કરો")
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig') if not filtered_df.empty else ""
    st.download_button(label="📥 તમારો ડેટા એક્સેલમાં ડાઉનલોડ કરો", data=csv, file_name="RTI_Report.csv", mime="text/csv")
    
    st.markdown("---")
    st.subheader("✏️ અરજીની વિગતો સુધારો અથવા ડિલીટ કરો")
    if not user_df.empty:
        edit_choice = st.selectbox("અરજી પસંદ કરો:", user_df.apply(lambda x: f"ID: {x['ID']} - {x['PIO_કચેરી']}", axis=1), key="edit_select")
        if edit_choice:
            edit_id = edit_choice.split(" - ")[0].replace("ID: ", "").strip()
            e_row = user_df[user_df['ID'] == edit_id].iloc[0]
            with st.form("full_edit_form"):
                c1, c2 = st.columns(2)
                with c1:
                    ed_pio = st.text_input("કચેરીનું નામ", value=str(e_row.get('PIO_કચેરી', '')))
                    ed_addr = st.text_area("સરનામું", value=str(e_row.get('PIO_સરનામું', '')))
                with c2:
                    ed_speed = st.text_input("સ્પીડ પોસ્ટ નંબર", value=str(e_row.get('RTI_સ્પીડપોસ્ટ', '')))
                    ed_mob = st.text_input("મોબાઈલ નંબર", value=str(e_row.get('PIO_મોબાઈલ', '')))
                
                col_sub1, col_sub2 = st.columns(2)
                with col_sub1:
                    update_btn = st.form_submit_button("✅ વિગતો અપડેટ કરો")
                with col_sub2:
                    delete_btn = st.form_submit_button("❌ આ અરજી ડિલીટ કરો", type="primary")
                
                if update_btn:
                    r_idx = df[df['ID'] == edit_id].index[0]
                    df.at[r_idx, 'PIO_કચેરી'] = str(ed_pio)
                    df.at[r_idx, 'PIO_સરનામું'] = str(ed_addr)
                    df.at[r_idx, 'RTI_સ્પીડપોસ્ટ'] = str(ed_speed)
                    df.at[r_idx, 'PIO_મોબાઈલ'] = str(ed_mob)
                    df.to_csv(DATA_FILE, index=False)
                    st.success("માહિતી સફળતાપૂર્વક અપડેટ થઈ ગઈ છે!")
                    st.rerun()
                
                if delete_btn:
                    df = df[df['ID'] != edit_id]
                    df.to_csv(DATA_FILE, index=False)
                    st.success("અરજી સફળતાપૂર્વક ડિલીટ થઈ ગઈ છે!")
                    st.rerun()

# ==========================================
# 📂 વ્યુઝ અને અપલોડ પેનલ
# ==========================================
if st.session_state['manage_action_id']:
    real_m_id = st.session_state['manage_action_id']
    m_row_data = user_df[user_df['ID'] == real_m_id] if not user_df.empty and 'ID' in user_df.columns else pd.DataFrame()
    
    if not m_row_data.empty:
        m_row = m_row_data.iloc[0]
        st.markdown("<div style='background-color: #f1f8ff; padding: 15px; border: 2px solid #7ab8eb; border-radius: 10px; margin: 15px 0;'>", unsafe_allow_html=True)
        col_t, col_btn = st.columns([3, 1])
        with col_t: st.markdown(f"<h4 style='color: #1e3a8a; margin:0;'>📂 દસ્તાવેજો: ID - {real_m_id}</h4>", unsafe_allow_html=True)
        with col_btn:
            if st.button("❌ બંધ કરો", use_container_width=True):
                st.session_state['manage_action_id'] = None
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.write("**મૂળ અરજીઓ (બ્રાઉઝરમાં જુઓ અથવા ડાઉનલોડ કરો):**")
        
        def display_file_options(file_path, label_name):
            if pd.notna(file_path) and str(file_path) != "ફાઈલ નથી" and str(file_path) != "" and os.path.exists(str(file_path)):
                st.markdown(f"**{label_name}**")
                col_v, col_d = st.columns(2)
                with col_v:
                    if st.button(f"👁️ વ્યુ (View) {label_name}", key=f"view_{file_path}_{label_name}"):
                        with open(file_path, "rb") as f:
                            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500px" type="application/pdf"></iframe>'
                        st.markdown(pdf_display, unsafe_allow_html=True)
                with col_d:
                    with open(file_path, "rb") as f:
                        st.download_button(f"⬇️ ડાઉનલોડ {label_name}", f, file_name=os.path.basename(file_path), key=f"dl_{file_path}_{label_name}")
                st.markdown("---")

        display_file_options(m_row.get('RTI_ફાઈલ'), "RTI ફાઈલ")
        display_file_options(m_row.get('FAA_ફાઈલ'), "પ્રથમ અપીલ ફાઈલ")
        display_file_options(m_row.get('SA_ફાઈલ'), "બીજી અપીલ ફાઈલ")
        
        st.write("**આ કેસના અન્ય પત્રો/દસ્તાવેજો:**")
        case_docs = extra_docs_df[extra_docs_df['ID'] == real_m_id] if not extra_docs_df.empty and 'ID' in extra_docs_df.columns else pd.DataFrame()
        if not case_docs.empty:
            for i, doc_row in case_docs.iterrows():
                if os.path.exists(str(doc_row['File_Path'])):
                    display_file_options(doc_row['File_Path'], doc_row['Doc_Name'])
        else: 
            st.info("કોઈ વધારાનો પત્ર અપલોડ કરેલ નથી.")
        
        with st.form(f"upload_extra_{real_m_id}", clear_on_submit=True):
            st.write("**નવો પત્ર/દસ્તાવેજ અપલોડ કરો:**")
            doc_name = st.text_input("પત્રનું નામ/વિગત")
            new_doc_file = st.file_uploader("ફાઈલ અપલોડ કરો", type=["pdf", "jpg", "png"])
            if st.form_submit_button("ફાઈલ સેવ કરો"):
                if doc_name and new_doc_file:
                    saved_path = save_uploaded_file(new_doc_file)
                    new_doc_entry = {"ID": real_m_id, "Doc_Name": doc_name, "File_Path": saved_path}
                    extra_docs_df = pd.concat([extra_docs_df, pd.DataFrame([new_doc_entry])], ignore_index=True)
                    extra_docs_df.to_csv(EXTRA_DOCS_FILE, index=False)
                    st.success("પત્ર સફળતાપૂર્વક અપલોડ થઈ ગયો છે!")
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# પ્રોફેશનલ ટેબલ ફોર્મેટ (મુખ્ય યાદી)
# ==========================================
def render_professional_table(df_subset, tab_key):
    if df_subset.empty:
        st.info("કોઈ અરજી ઉપલબ્ધ નથી.")
        return
    
    h1, h2, h3, h4, h5, h6 = st.columns([0.6, 1.2, 1.8, 2.2, 1.4, 1.4])
    with h1: st.markdown('<div class="table-header">Sr.</div>', unsafe_allow_html=True)
    with h2: st.markdown('<div class="table-header">ID</div>', unsafe_allow_html=True)
    with h3: st.markdown('<div class="table-header">Applicant</div>', unsafe_allow_html=True)
    with h4: st.markdown('<div class="table-header">PIO Office</div>', unsafe_allow_html=True)
    with h5: st.markdown('<div class="table-header">Date</div>', unsafe_allow_html=True)
    with h6: st.markdown('<div class="table-header">Action</div>', unsafe_allow_html=True)
    
    for i, (index, row) in enumerate(df_subset.iterrows()):
        dt = row.get('RTI_તારીખ', '-')
        
        r1, r2, r3, r4, r5, r6 = st.columns([0.6, 1.2, 1.8, 2.2, 1.4, 1.4])
        with r1: st.markdown(f'<div class="table-row"><b>{i+1}</b></div>', unsafe_allow_html=True)
        with r2: st.markdown(f'<div class="table-row"><b>{row["ID"]}</b></div>', unsafe_allow_html=True)
        with r3: st.markdown(f'<div class="table-row">{st.session_state["user_name"]}</div>', unsafe_allow_html=True)
        with r4: st.markdown(f'<div class="table-row">{row.get("PIO_કચેરી", "-")}</div>', unsafe_allow_html=True)
        with r5: st.markdown(f'<div class="table-row">{dt}</div>', unsafe_allow_html=True)
        with r6:
            if st.button("👁️ જુઓ", key=f"btn_{row['ID']}_{tab_key}", use_container_width=True):
                st.session_state['manage_action_id'] = row['ID']
                st.rerun()

st.markdown("---")
st.subheader(f"તમારી અરજીઓનું લિસ્ટ (વ્યુ: {st.session_state['selected_filter']})")
render_professional_table(filtered_df, "main_list")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### ✅ અરજીનો નિકાલ (જવાબ આવી ગયો હોય તો)")
dispose_rtis = user_df[user_df['સ્ટેટસ'] != 'નિકાલ'] if not user_df.empty and 'સ્ટેટસ' in user_df.columns else pd.DataFrame()
if not dispose_rtis.empty:
    dispose_id_str = st.selectbox("નિકાલ કરવા માટે અરજી પસંદ કરો:", dispose_rtis.apply(lambda x: f"ID: {x['ID']} - {x['PIO_કચેરી']}", axis=1))
    if st.button("આ અરજીનો નિકાલ કરો (Dispose)", type="primary"):
        r_idx = df[df['ID'] == dispose_id_str.split(" - ")[0].replace("ID: ", "").strip()].index[0]
        df.at[r_idx, 'સ્ટેટસ'] = 'નિકાલ'
        df.to_csv(DATA_FILE, index=False)
        st.success("અરજીનો સફળતાપૂર્વક નિકાલ થઈ ગઈ છે!")
        st.rerun()