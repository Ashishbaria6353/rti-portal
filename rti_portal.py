import streamlit as st
import pandas as pd
from datetime import date
import os
import base64

st.set_page_config(page_title="RTI Manage Portal", layout="wide")

# --- CSS Design ---
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

# --- Logic setup ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user_name' not in st.session_state: st.session_state['user_name'] = ""
if 'user_mobile' not in st.session_state: st.session_state['user_mobile'] = ""
if 'manage_action_id' not in st.session_state: st.session_state['manage_action_id'] = None
if 'selected_filter' not in st.session_state: st.session_state['selected_filter'] = "All"

params = st.query_params
if "mobile" in params and not st.session_state['logged_in']:
    st.session_state['logged_in'] = True
    st.session_state['user_mobile'] = params["mobile"]
    st.session_state['user_name'] = params.get("name", "")

if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>RTI MANAGE PORTAL</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        u_name = st.text_input("તમારું પૂરું નામ")
        u_mob = st.text_input("તમારો મોબાઈલ નંબર")
        if st.form_submit_button("લૉગિન કરો"):
            if u_name and u_mob:
                st.session_state.update({'logged_in': True, 'user_name': u_name, 'user_mobile': u_mob})
                st.query_params.update({"mobile": u_mob, "name": u_name})
                st.rerun()
    st.stop()

with st.sidebar:
    st.markdown("### 👤 તમારું પ્રોફાઈલ")
    st.info(f"**નામ:** {st.session_state['user_name']}\n\n**મોબાઈલ:** {st.session_state['user_mobile']}")
    if st.button("લૉગઆઉટ કરો (Logout)", type="primary"):
        st.session_state.clear()
        st.query_params.clear()
        st.rerun()

DATA_FILE = "rti_data_v6.csv"
EXTRA_DOCS_FILE = "rti_extra_docs_v6.csv"
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER): os.makedirs(UPLOAD_FOLDER)

def load_data():
    cols = ['ID', 'User_Mobile', 'સ્ટેટસ', 'RTI_તારીખ', 'PIO_કચેરી', 'PIO_સરનામું', 'PIO_પિનકોડ', 'PIO_મોબાઈલ', 'RTI_સ્પીડપોસ્ટ', 'RTI_ફાઈલ', 'FAA_તારીખ', 'FAA_સુનાવણી_તારીખ', 'FAA_અધિકારી', 'FAA_સરનામું', 'FAA_પિનકોડ', 'FAA_મોબાઈલ', 'FAA_સ્પીડપોસ્ટ', 'FAA_ફાઈલ', 'SA_તારીખ', 'SA_સુનાવણી_તારીખ', 'SA_સ્પીડપોસ્ટ', 'SA_ફાઈલ']
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, dtype=str)
        for col in cols: 
            if col not in df.columns: df[col] = ""
        return df
    return pd.DataFrame(columns=cols)

df = load_data()
user_df = df[df['User_Mobile'] == st.session_state['user_mobile']].copy() if not df.empty else pd.DataFrame()
if not user_df.empty and 'સ્ટેટસ' not in user_df.columns: user_df['સ્ટેટસ'] = 'પેન્ડિંગ'

# --- Header & Counters ---
col_home, col_title, col_search = st.columns([1, 2, 1.5])
with col_home:
    if st.button("🏠 Home"): st.session_state['manage_action_id'] = None; st.rerun()
with col_title: st.markdown("<h2 style='text-align: center; color: #1e3a8a;'>RTI MANAGE PORTAL</h2>", unsafe_allow_html=True)
with col_search: search_term = st.text_input("🔍 સર્ચ કરો:", placeholder="ID કે કચેરી...")

st.markdown("<hr>", unsafe_allow_html=True)

# Stats Calculation
total_rti = len(user_df)
pending_rti = len(user_df[user_df["સ્ટેટસ"] != "નિકાલ"])
first_due = len(user_df[user_df["સ્ટેટસ"] == "પ્રથમ અપીલ બાકી"])
first_done = len(user_df[user_df["સ્ટેટસ"].isin(["પ્રથમ અપીલ પેન્ડિંગ", "બીજી અપીલ બાકી", "બીજી અપીલ પેન્ડિંગ"])])
second_due = len(user_df[user_df["સ્ટેટસ"] == "બીજી અપીલ બાકી"])
second_done = len(user_df[user_df["સ્ટેટસ"] == "બીજી અપીલ પેન્ડિંગ"])
nikal_rti = len(user_df[user_df["સ્ટેટસ"] == "નિકાલ"])

r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
with r1_c1: st.markdown(f'<div class="box b-blue">કુલ RTI<p class="number-text">{total_rti}</p></div>', unsafe_allow_html=True)
with r1_c2: st.markdown(f'<div class="box b-orange">પેન્ડિંગ<p class="number-text">{pending_rti}</p></div>', unsafe_allow_html=True)
with r1_c3: st.markdown(f'<div class="box b-brown">પ્રથમ અપીલ બાકી<p class="number-text">{first_due}</p></div>', unsafe_allow_html=True)
with r1_c4: st.markdown(f'<div class="box b-red">પ્રથમ અપીલ<p class="number-text">{first_done}</p></div>', unsafe_allow_html=True)
r2_c1, r2_c2, r2_c3 = st.columns(3)
with r2_c1: st.markdown(f'<div class="box b-purple">બીજી અપીલ બાકી<p class="number-text">{second_due}</p></div>', unsafe_allow_html=True)
with r2_c2: st.markdown(f'<div class="box b-deeppurple">બીજી અપીલ<p class="number-text">{second_done}</p></div>', unsafe_allow_html=True)
with r2_c3: st.markdown(f'<div class="box b-green">નિકાલ<p class="number-text">{nikal_rti}</p></div>', unsafe_allow_html=True)

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["🆕 નવી RTI", "⚖️ પ્રથમ અપીલ", "🏛️ બીજી અપીલ", "⚙️ મેનેજમેન્ટ & ડિલીટ"])

with tab1:
    with st.form("new_rti_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            rti_date = st.date_input("RTI તારીખ")
            pio_name = st.text_input("કચેરી")
        with col_b:
            pio_mob = st.text_input("મોબાઈલ")
            rti_file = st.file_uploader("PDF ફાઈલ", type=["pdf"])
        if st.form_submit_button("SAVE RTI"):
            # (Save logic same as before)
            st.success("સેવ થઈ ગયું!")

    # --- ફિલ્ટર ડ્રોપડાઉન અહીં મૂક્યું છે ---
    st.markdown("---")
    st.subheader("તમારી અરજીઓનું લિસ્ટ")
    filter_option = st.selectbox("📂 સ્ટેટસ ફિલ્ટર કરો:", ["બધી અરજીઓ (All)", "પેન્ડિંગ અરજીઓ", "પ્રથમ અપીલ બાકી", "પ્રથમ અપીલ પેન્ડિંગ", "બીજી અપીલ બાકી", "બીજી અપીલ પેન્ડિંગ", "નિકાલ થયેલ"])
    
    # Render table logic (using filtered_df)
    # ... (Rest of table logic)