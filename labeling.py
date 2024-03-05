import streamlit as st
import pandas as pd
import time
import os
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import gspread

conn = st.connection("gsheets", type=GSheetsConnection)

st.set_page_config(
    page_title="Labeling Tool by Rey",
    page_icon="🥵",
    menu_items={
        'Get Help': 'https://api.whatsapp.com/send/?phone=6282114931994&text&type=phone_number&app_absent=0',
        'Report a bug': "https://api.whatsapp.com/send/?phone=6282114931994&text&type=phone_number&app_absent=0",
        'About': "# This is a labeling tool for skripsi"
    }
)

@st.cache_data
def load_data():
    data = pd.read_csv('dataset/df_all_keywords_no_duplicates.csv')
    data['label'] = None
    return data


def save_labeled_data(labeled_data, conn):  
    labeled_data.to_csv('dataset/labeled_dataset.csv', mode='a', header=not st.session_state.saved, index=False)
    st.session_state.saved = True

    gc = gspread.models.Spreadsheet()
    gc.client.open_by_key('18ZpFBkmaIFgEnbTJNlK61VetBETX1VcUN92Wn58VX_0')  

    worksheet = gc.Sheet1

    cell_range = f'A1:B{len(labeled_data) + 1}'  
    cell_list = worksheet.range(cell_range)

    # Flatten the labeled_data DataFrame into a list
    labeled_data_values = labeled_data.values.flatten()

    for cell, value in zip(cell_list, labeled_data_values):
        cell.value = value

    # Update the worksheet with the new values
    worksheet.update_cells(cell_list)

def titles():
    st.title('Pangan Olahan Ilegal Labeling Tool')
    st.caption('Dibuat untuk penelitian **PENERAPAN TEXT MINING PADA E-COMMERCE ANALYTICS TOOL UNTUK DETEKSI PENJUALAN PANGAN OLAHAN ILEGAL** oleh **Muhamad Luthfi Reynaldi**. Data yang digunakan berasal dari situs **shopee.co.id** [Diakses pada **9 Februari 2024**].')

    st.caption("📄 **Petunjuk penggunaaan:**")
    st.caption("\
    1. Lakukan pelabelan **per halaman**. Satu halaman terdiri dari **20 produk** (total: 3425 produk).\n \
    2. Pada setiap halaman ditampilkan judul, harga, lokasi, dan banyak produk terjual.\n \
    3. Untuk melihat lebih detail pada sumber situs, Anda dapat **menekan tautan** pada setiap produk.\n \
    4. Silakan simpan data yang sudah terlabeli (20 produk) dengan menekan tombol **Simpan data terlabeli** pada bagian bawah halaman.\n \
    5. Jika sudah tersimpan, silakan **berpindah ke halaman selanjutnya** menggunakan tombol (+) atau (-) di bagian atas halaman.\n\
    6. Jika ingin memperbarui label produk yang sudah dilabeli sebelumnya, pindah ke halaman produk tersebut dan simpan kembali label terbaru dengan menekan tombol **Simpan data terlabeli**.")

def labeling_tool():
    if 'data' not in st.session_state:
        st.session_state.data = load_data()
        st.session_state.saved = False
    
    titles()
    page_number = st.number_input('Halaman', min_value=1, max_value=(len(st.session_state.data) - 1) // 20 + 1, value=1)
    st.caption("Ketik atau gunakan (+) dan (-) untuk berpindah halaman.")

    start_index = (page_number - 1) * 20
    end_index = min(len(st.session_state.data), page_number * 20)

    labeled_data = pd.read_csv('dataset/labeled_dataset.csv') if 'labeled_dataset.csv' in os.listdir('dataset') else pd.DataFrame(columns=["title", "price", "sold", "location", "link", "label", "timestamp"])
    
    st.caption(f":blue[{labeled_data.drop_duplicates(subset=['link']).shape[0]} data] telah dilabeli")

    labeled_rows = []

    with st.form(key="submit-20-data"):
        for index, row in st.session_state.data.iloc[start_index:end_index].iterrows():
            st.write(f"<h1 style='font-size: 24px;'>{index + 1}. {row['title']}</h1>", unsafe_allow_html=True)
            st.caption(f"Rp{row['price']} - " f"{row['location']} - " f"{row['sold']}")
            st.markdown(f"👁 Lihat lebih detail pada situs [Shopee]({row['link']}).")
            label = st.radio("Pilih label yang sesuai:", options=["Legal", "Ilegal"], key=index)
            
            if label == "Legal":
                row['label'] = 0
            elif label == "Ilegal":
                row['label'] = 1
            
            if row['link'] in labeled_data['link'].values:
                filled_label = labeled_data.loc[labeled_data['link'] == row['link'], ['label', 'timestamp']].sort_values(by='timestamp', ascending=False).values[0]
                st.caption(f"Anda sebelumnya melabeli {filled_label[0]} pada produk ini. Simpan kembali untuk memperbarui label.")
            
            labeled_rows.append(row)

        # Save labeled data
        st.caption("Silakan simpan data yang sudah dilabeli dengan menekan tombol berikut.")
        submit = st.form_submit_button(label="💾 Simpan data terlabeli", type="primary")
        if submit:
            label_df = pd.DataFrame(labeled_rows)
            label_df['timestamp'] = datetime.now()
            save_labeled_data(label_df, conn)
            st.caption(f":blue[{labeled_data.drop_duplicates(subset=['link']).shape[0] + len(label_df)} data] telah dilabeli")
            st.write("🥳 Data berhasil disimpan... Silakan ke halaman selanjutnya!")
            st.balloons()

def main():
    labeling_tool()

if __name__ == "__main__":
    main()
