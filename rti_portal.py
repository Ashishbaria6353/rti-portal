# --- tab1 ના અંતે SAVE RTI બટન પછી આ મુજબ ફેરફાર કરો ---

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

    # --- અહીં ડ્રોપડાઉન ફિલ્ટર મૂક્યું છે ---
    st.markdown("---")
    st.subheader("તમારી અરજીઓનું લિસ્ટ")
    filter_option = st.selectbox("📂 સ્ટેટસ મુજબ અરજીઓ ફિલ્ટર કરો:", ["બધી અરજીઓ (All)", "પેન્ડિંગ અરજીઓ", "પ્રથમ અપીલ બાકી", "પ્રથમ અપીલ પેન્ડિંગ", "બીજી અપીલ બાકી", "બીજી અપીલ પેન્ડિંગ", "નિકાલ થયેલ"], key="table_filter_box")

    if not user_df.empty:
        if search_term:
            filtered_df = user_df[user_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
        else:
            if filter_option == "પેન્ડિંગ અરજીઓ":
                filtered_df = user_df[user_df["સ્ટેટસ"] != "નિકાલ"]
            elif filter_option == "પ્રથમ અપીલ બાકી":
                filtered_df = user_df[user_df["સ્ટેટસ"] == "પ્રથમ અપીલ બાકી"]
            elif filter_option == "પ્રથમ અપીલ પેન્ડિંગ":
                filtered_df = user_df[user_df["સ્ટેટસ"] == "પ્રથમ અપીલ પેન્ડિંગ"]
            elif filter_option == "બીજી અપીલ બાકી":
                filtered_df = user_df[user_df["સ્ટેટસ"] == "બીજી અપીલ બાકી"]
            elif filter_option == "બીજી અપીલ પેન્ડિંગ":
                filtered_df = user_df[user_df["સ્ટેટસ"] == "બીજી અપીલ પેન્ડિંગ"]
            elif filter_option == "નિકાલ થયેલ":
                filtered_df = user_df[user_df["સ્ટેટસ"] == "નિકાલ"]
            else:
                filtered_df = user_df
    else:
        filtered_df = pd.DataFrame()

# --- બાકીનો કોડ નીચે મુજબ રહેશે ---