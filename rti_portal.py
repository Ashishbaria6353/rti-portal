import streamlit as st
import pandas as pd
from datetime import date
import os
import base64
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="RTI Manage Portal", layout="wide")

# --- ગૂગલ શીટ કનેક્શન સેટઅપ (Streamlit Secrets દ્વારા) ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
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
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            u_name = st.text_input("તમારું પૂરું નામ")
            u_mob = st.text_input("તમારો મોબાઈલ નંબર")
            if st.form_submit_button("લૉગિન કરો", type="primary"):
                if u_name and u_mob:
                    st.session_state.update({'logged_in': True, 'user_name': u_name, 'user_mobile': str(u_mob)})
                    st.query_params.update({"mobile": str(u_mob), "name": u_name})
                    st.rerun()
    st.stop()

# --- ગૂગલ શીટ ફંક્શન્સ ---
def load_data():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    if df.empty:
        return pd.DataFrame(columns=['ID', 'User_Mobile', 'સ્ટેટસ', 'RTI_તારીખ', 'PIO_કચેરી', 'PIO_સરનામું', 'PIO_પિનકોડ', 'PIO_મોબાઈલ', 'RTI_સ્પીડપોસ્ટ', 'RTI_ફાઈલ', 'FAA_તારીખ', 'FAA_સુનાવણી_તારીખ', 'FAA_અધિકારી', 'FAA_સરનામું', 'FAA_પિનકોડ', 'FAA_મોબાઈલ', 'FAA_સ્પીડપોસ્ટ', 'FAA_ફાઈલ', 'SA_તારીખ', 'SA_સુનાવણી_તારીખ', 'SA_સ્પીડપોસ્ટ', 'SA_ફાઈલ'])
    return df.astype(str)

def save_data_to_sheet(df):
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

# --- બાકીનો લોજિક (તમારો અગાઉનો કોડ અહીંથી ચાલુ રાખો) ---
df = load_data()
user_df = df[df['User_Mobile'] == st.session_state['user_mobile']].copy() if not df.empty else pd.DataFrame()