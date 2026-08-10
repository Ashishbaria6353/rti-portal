import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="RTI Manage Portal", layout="wide")

# --- Streamlit ના ડિફોલ્ટ વોટરમાર્ક/મેનૂ છુપાવવા માટેની CSS ---
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container { background-color: #f8f9fa; border: 2px solid #cfd8dc; border-radius: 12px; padding: 1.5rem 1rem !important; box-shadow: 0px 4px 12px rgba(0,0,0,0.1); margin-top: 1rem; }
button[kind="primary"] { background: linear-gradient(to right, #e53935, #ef5350) !important; color: white !important; font-weight: bold !important; border-radius: 6px !important; border: none !important; }
div[data-testid="stFormSubmitButton"] button { background: linear-gradient(to right, #1976d2, #42a5f5) !important; }
.box { padding: 12px; border-radius: 8px; text-align: center; color: white; font-family: sans-serif; box-shadow: 2px 2px 5px rgba(0,0,0,0.2); margin-bottom: 8px; }
.blue-box { background: linear-gradient(to right, #3b5998, #4c70ba); }
.green-box { background: linear-gradient(to right, #4CAF50, #66bb6a); }
.red-box { background: linear-gradient(to right, #f44336, #ef5350); }
.orange-box { background: linear-gradient(to right, #ff9800, #ffb74d); }
.purple-box { background: linear-gradient(to right, #9c27b0, #ba68c8); }
.number-text { font-size: 28px; font-weight: bold; margin: 0; }
.mobile-card { background: white; padding: 15px; border-radius: 8px; border: 1px solid #b0bec5; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# --- પરમેનન્ટ લૉગિન સિસ્ટમ (રિફ્રેશ કરવાથી લૉગિન જતું ન રહે તે માટે) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""
if 'user_mobile' not in st.session_state:
    st.session_state['user_mobile'] = ""
if 'manage_action_id' not in st.session_state:
    st.session_state['manage_action_id'] = None

# કુકી દ્વારા લૉગિન સેવ રાખવા માટે query params નો ઉપયોગ
params = st.query_params
if "mobile" in params and not st.session_state['logged_in']:
    st.session_state['logged_in'] = True
    st.session_state['user_mobile'] = params["mobile"]
    if "name" in params:
        st.session_state['user_name'] = params["name"]

if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align: center; color: #1e3a8a; margin-top: 50px;'>RTI MANAGE PORTAL</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>કૃપા કરીને આગળ વધવા માટે લૉગિન કરો</p>", unsafe_allow_html=True)
    
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

# --- સાઈડબાર (Profile & Logout) ---
with st.sidebar:
    st.markdown("### 👤 તમારું પ્રોફાઈલ")
    st.info(f"**નામ:** {st.session_state['user_name']}\n\n**મોબાઈલ:** {st.session_state['user_mobile']}")
    st.markdown("---")
    if st.button("લૉગઆઉટ કરો (Logout)", type="primary", use_container_width=True):
        st.session_state.clear()
        st.query_params.clear()
        st.rerun()

DATA_FILE = "rti_data_v5.csv"
EXTRA_DOCS_FILE = "rti_extra_docs_v5.csv"
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
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, dtype=str)
        for col in df.columns:
            if 'સ્ટેટ' in col or 'status' in col.lower():
                df.rename(columns={col: 'સ્ટેટસ'}, inplace=True)
        if 'સ્ટેટસ' not in df.columns:
            df['સ્ટેટસ'] = 'પેન્ડિંગ'
        df['RTI_તારીખ'] = pd.to_datetime(df['RTI_તારીખ'], errors='coerce').dt.date
        df['FAA_તારીખ'] = pd.to_datetime(df['FAA_તારીખ'], errors='coerce').dt.date
        return df
    else:
        cols = ['ID', 'User_Mobile', 'સ્ટેટસ', 'RTI_તારીખ', 'PIO_કચેરી', 'PIO_સરનામું', 'PIO_પિનકોડ', 'PIO_મોબાઈલ', 'RTI_સ્પીડપોસ્ટ', 'RTI_ફાઈલ', 
                'FAA_અધિકારી', 'FAA_સરનામું', 'FAA_પિનકોડ', 'FAA_મોબાઈલ', 'FAA_તારીખ', 'FAA_સ્પીડપોસ્ટ', 'FAA_ફાઈલ', 
                'SA_તારીખ', 'SA_સ્પીડપોસ્ટ', 'SA_ફાઈલ']
        return pd.DataFrame(columns=cols)

def load_extra_docs():
    if os.path.exists(EXTRA_DOCS_FILE):
        return pd.read_csv(EXTRA_DOCS_FILE, dtype=str)
    return pd.DataFrame(columns=['ID', 'Doc_Name', 'File_Path'])

df = load_data()
user_df = df[df['User_Mobile'] == st.session_state['user_mobile']].copy()
extra_docs_df = load_extra_docs()

if 'સ્ટેટસ' not in user_df.columns:
    user_df['સ્ટેટસ'] = 'પેન્ડિંગ'

# --- ઓટોમેટિક લોજિક ---
if not user_df.empty:
    today = date.today()
    changed = False
    for index, row in user_df.iterrows():
        real_index = df[df['ID'] == row['ID']].index[0]
        status_val = str(row.get('સ્ટેટસ', 'પેન્ડિંગ'))
        if status_val == 'પેન્ડિંગ' and pd.notna(row.get('RTI_તારીખ')):
            if (today - row['RTI_તારીખ']).days > 30:
                df.at[real_index, 'સ્ટેટસ'] = 'પ્રથમ અપીલ બાકી'
                changed = True
        elif status_val == 'પ્રથમ અપીલ પેન્ડિંગ' and pd.notna(row.get('FAA_તારીખ')):
            if (today - row['FAA_તારીખ']).days > 45:
                df.at[real_index, 'સ્ટેટસ'] = 'બીજી અપીલ બાકી'
                changed = True
    if changed:
        df.to_csv(DATA_FILE, index=False)
        user_df = df[df['User_Mobile'] == st.session_state['user_mobile']].copy()

# --- ટોચ પર Home બટન, ટાઇટલ અને સર્ચ ઓપ્શન ---
col_home, col_title, col_search = st.columns([0.8, 1.7, 1.5])
with col_home:
    if st.button("Home", use_container_width=True):
        st.session_state['manage_action_id'] = None
        st.rerun()
with col_title:
    st.markdown("<h3 style='color: #1e3a8a; font-weight: bold; margin:0;'>RTI PORTAL</h3>", unsafe_allow_html=True)
with col_search:
    search_term = st.text_input("🔍 શોધો:", placeholder="ID કે કચેરી...", label_visibility="collapsed")

st.markdown("<hr style='border: 1px solid #cfd8dc; margin: 10px 0;'>", unsafe_allow_html=True)

if search_term:
    filtered_df = user_df[user_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
else:
    filtered_df = user_df

c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.markdown(f'<div class="box blue-box"><small>કુલ RTI</small><p class="number-text">{len(user_df)}</p></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="box orange-box"><small>પેન્ડિંગ</small><p class="number-text">{len(user_df[user_df["સ્ટેટસ"] == "પેન્ડિંગ"])}</p></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="box red-box"><small>પ્રથમ અપીલ</small><p class="number-text">{len(user_df[user_df["સ્ટેટસ"].isin(["પ્રથમ અપીલ બાકી", "પ્રથમ અપીલ પેન્ડિંગ"])])}</p></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="box purple-box"><small>બીજી અપીલ</small><p class="number-text">{len(user_df[user_df["સ્ટેટસ"].isin(["બીજી અપીલ બાકી", "બીજી અપીલ પેન્ડિંગ"])])}</p></div>', unsafe_allow_html=True)
with c5: st.markdown(f'<div class="box green-box"><small>નિકાલ</small><p class="number-text">{len(user_df[user_df["સ્ટેટસ"] == "નિકાલ"])}</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

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
            
            new_row = {"ID": new_id, "User_Mobile": st.session_state['user_mobile'], "સ્ટેટસ": "પેન્ડિંગ", "RTI_તારીખ": rti_date, "PIO_કચેરી": pio_name, "PIO_સરનામું": pio_address, 
                       "PIO_પિનકોડ": pio_pin, "PIO_મોબાઈલ": pio_mob, "RTI_સ્પીડપોસ્ટ": rti_speed, "RTI_ફાઈલ": save_uploaded_file(rti_file)}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success(f"નવી RTI સફળતાપૂર્વક દાખલ થઈ ગઈ છે! (ID: {new_id})")
            st.rerun()

with tab2:
    pending_rtis = user_df[user_df['સ્ટેટસ'].isin(['પેન્ડિંગ', 'પ્રથમ અપીલ બાકી'])]
    if not pending_rtis.empty:
        selected_rti = st.selectbox("RTI પસંદ કરો", pending_rtis.apply(lambda x: f"ID: {x['ID']} - {x['PIO_કચેરી']}", axis=1))
        rti_id = selected_rti.split(" - ")[0].replace("ID: ", "").strip()
        with st.form("first_appeal_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                faa_date = st.date_input("અપીલ કર્યાની તારીખ")
                faa_name = st.text_input("પ્રથમ અપીલ અધિકારી શ્રી નું નામ/હોદ્દો")
                faa_address = st.text_area("સરનામું (પ્રથમ અપીલ)")
            with col_b:
                faa_pin = st.text_input("પિન કોડ")
                faa_mob = st.text_input("મોબાઈલ નંબર")
                faa_speed = st.text_input("સ્પીડ પોસ્ટ ટ્રેકિંગ નંબર")
                faa_file = st.file_uploader("પ્રથમ અપીલની PDF", type=["pdf", "png", "jpg"])
            if st.form_submit_button("SAVE RTI"):
                r_idx = df[df['ID'] == rti_id].index[0]
                df.at[r_idx, 'FAA_અધિકારી'], df.at[r_idx, 'FAA_સરનામું'], df.at[r_idx, 'FAA_પિનકોડ'], df.at[r_idx, 'FAA_મોબાઈલ'], df.at[r_idx, 'FAA_તારીખ'], df.at[r_idx, 'FAA_સ્પીડપોસ્ટ'], df.at[r_idx, 'FAA_ફાઈલ'], df.at[r_idx, 'સ્ટેટસ'] = faa_name, faa_address, faa_pin, faa_mob, faa_date, faa_speed, save_uploaded_file(faa_file), 'પ્રથમ અપીલ પેન્ડિંગ'
                df.to_csv(DATA_FILE, index=False)
                st.success("પ્રથમ અપીલ દાખલ થઈ ગઈ છે!")
                st.rerun()
    else: st.info("કોઈ અરજી પ્રથમ અપીલ માટે બાકી નથી.")

with tab3:
    appeal_rtis = user_df[user_df['સ્ટેટસ'].isin(['પ્રથમ અપીલ પેન્ડિંગ', 'બીજી અપીલ બાકી'])]
    if not appeal_rtis.empty:
        selected_sa = st.selectbox("અરજી પસંદ કરો", appeal_rtis.apply(lambda x: f"ID: {x['ID']} - {x['PIO_કચેરી']}", axis=1))
        sa_id = selected_sa.split(" - ")[0].replace("ID: ", "").strip()
        st.info("**🏛️ ગુજરાત માહિતી આયોગ** | **સરનામું:** કર્મયોગી ભવન, ગાંધીનગર - 382010")
        with st.form("second_appeal_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                sa_date = st.date_input("બીજી અપીલની તારીખ")
                sa_speed = st.text_input("સ્પીડ પોસ્ટ નંબર")
            with col_b:
                sa_file = st.file_uploader("બીજી અપીલની PDF", type=["pdf", "png", "jpg"])
            if st.form_submit_button("SAVE RTI"):
                r_idx = df[df['ID'] == sa_id].index[0]
                df.at[r_idx, 'SA_તારીખ'], df.at[r_idx, 'SA_સ્પીડપોસ્ટ'], df.at[r_idx, 'SA_ફાઈલ'], df.at[r_idx, 'સ્ટેટસ'] = sa_date, sa_speed, save_uploaded_file(sa_file), 'બીજી અપીલ પેન્ડિંગ'
                df.to_csv(DATA_FILE, index=False)
                st.success("બીજી અપીલ નોંધાઈ ગઈ છે!")
                st.rerun()
    else: st.info("કોઈ અરજી બીજી અપીલ માટે બાકી નથી.")

# TAB 4: મેનેજમેન્ટ, એડિટ અને ડિલીટ ઓપ્શન
with tab4:
    st.subheader("📊 એક્સેલ રિપોર્ટ ડાઉનલોડ કરો")
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
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
                    df.at[r_idx, 'PIO_કચેરી'], df.at[r_idx, 'PIO_સરનામું'], df.at[r_idx, 'RTI_સ્પીડપોસ્ટ'], df.at[r_idx, 'PIO_મોબાઈલ'] = ed_pio, ed_addr, ed_speed, ed_mob
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
    m_row_data = user_df[user_df['ID'] == real_m_id]
    
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
        st.write("**મૂળ અરજીઓ:**")
        c1, c2, c3 = st.columns(3)
        with c1:
            if pd.notna(m_row.get('RTI_ફાઈલ')) and str(m_row['RTI_ફાઈલ']) != "ફાઈલ નથી" and os.path.exists(str(m_row['RTI_ફાઈલ'])):
                with open(str(m_row['RTI_ફાઈલ']), "rb") as f: st.download_button("⬇️ RTI ફાઈલ", f, file_name=f"RTI_{real_m_id}.pdf")
        with c2:
            if pd.notna(m_row.get('FAA_ફાઈલ')) and str(m_row['FAA_ફાઈલ']) != "ફાઈલ નથી" and os.path.exists(str(m_row['FAA_ફાઈલ'])):
                with open(str(m_row['FAA_ફાઈલ']), "rb") as f: st.download_button("⬇️ પ્રથમ અપીલ ફાઈલ", f, file_name=f"FAA_{real_m_id}.pdf")
        with c3:
            if pd.notna(m_row.get('SA_ફાઈલ')) and str(m_row['SA_ફાઈલ']) != "ફાઈલ નથી" and os.path.exists(str(m_row['SA_ફાઈલ'])):
                with open(str(m_row['SA_ફાઈલ']), "rb") as f: st.download_button("⬇️ બીજી અપીલ ફાઈલ", f, file_name=f"SA_{real_m_id}.pdf")
        
        st.markdown("---")
        st.write("**આ કેસના અન્ય પત્રો/દસ્તાવેજો:**")
        case_docs = extra_docs_df[extra_docs_df['ID'] == real_m_id]
        if not case_docs.empty:
            for i, doc_row in case_docs.iterrows():
                if os.path.exists(str(doc_row['File_Path'])):
                    with open(str(doc_row['File_Path']), "rb") as f: st.download_button(f"⬇️ {doc_row['Doc_Name']}", f, file_name=f"Doc_{real_m_id}_{i}.pdf", key=f"btn_{i}")
        else: st.info("કોઈ વધારાનો પત્ર અપલોડ કરેલ નથી.")
        
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
# મોબાઈલ અને ડેસ્કટોપ ફ્રેંડલી રિસ્પોન્સિવ લિસ્ટ
# ==========================================
def render_responsive_table(df_subset, tab_key):
    if df_subset.empty:
        st.info("કોઈ અરજી ઉપલબ્ધ નથી.")
        return
    
    for i, (index, row) in enumerate(df_subset.iterrows()):
        dt = row.get('RTI_તારીખ', '-')
        status = row.get('સ્ટેટસ', '-')
        color = "#d32f2f" if "પેન્ડિંગ" in str(status) or "બાકી" in str(status) else "#2e7d32"
        
        # મોબાઈલ માટે કાર્ડ ડિઝાઈન અને ડેસ્કટોપ માટે પ્રોપર લિસ્ટ
        st.markdown(f"""
        <div class="mobile-card">
            <b>ક્રમ:</b> {i+1} | <b>ID:</b> {row['ID']}<br>
            <b>કચેરી:</b> {row.get('PIO_કચેરી', '-')}<br>
            <b>તારીખ:</b> {dt}<br>
            <b>સ્ટેટસ:</b> <span style="color: {color}; font-weight: bold;">{status}</span>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("👁️ જુઓ / 📤 અપલોડ", key=f"btn_{row['ID']}_{tab_key}", use_container_width=True):
            st.session_state['manage_action_id'] = row['ID']
            st.rerun()
        st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

st.markdown("---")
st.subheader("તમારી અરજીઓનું લિસ્ટ અને નિકાલ")
list_tab1, list_tab2, list_tab3 = st.tabs(["આખી યાદી (All)", "પ્રથમ અપીલમાં ગયેલી", "બીજી અપીલમાં (આયોગમાં) ગયેલી"])

with list_tab1: render_responsive_table(filtered_df, "all")
with list_tab2: render_responsive_table(filtered_df[filtered_df['સ્ટેટસ'].isin(['પ્રથમ અપીલ બાકી', 'પ્રથમ અપીલ પેન્ડિંગ'])], "first")
with list_tab3: render_responsive_table(filtered_df[filtered_df['સ્ટેટસ'].isin(['બીજી અપીલ બાકી', 'બીજી અપીલ પેન્ડિંગ'])], "second")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### ✅ અરજીનો નિકાલ (જવાબ આવી ગયો હોય તો)")
dispose_rtis = user_df[user_df['સ્ટેટસ'] != 'નિકાલ']
if not dispose_rtis.empty:
    dispose_id_str = st.selectbox("નિકાલ કરવા માટે અરજી પસંદ કરો:", dispose_rtis.apply(lambda x: f"ID: {x['ID']} - {x['PIO_કચેરી']}", axis=1))
    if st.button("આ અરજીનો નિકાલ કરો (Dispose)", type="primary"):
        r_idx = df[df['ID'] == dispose_id_str.split(" - ")[0].replace("ID: ", "").strip()].index[0]
        df.at[r_idx, 'સ્ટેટસ'] = 'નિકાલ'
        df.to_csv(DATA_FILE, index=False)
        st.success("અરજીનો સફળતાપૂર્વક નિકાલ થઈ ગઈ છે!")
        st.rerun()