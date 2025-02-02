import os
import time
import streamlit as st
from copy import deepcopy
from datetime import datetime
from PIL import Image
from streamlit_option_menu import option_menu

from modules.configs import FAISS_PATH
from modules.embeddings import HFEmbedding
from modules.storings import FAISSDatabase
from modules.chunkings import SemanticChunk
from modules.configs import SIDEBAR_IMG_PATH
from modules.extractings import PDFExtractor, HTMLExtractor, DOCXExtractor, TXTExtractor
from modules.admins import load_chat_history, filter_chats_by_date, reset_state, \
                        display_chat_messages, setup_state, add_account, \
                        load_accounts, update_account, load_account

def page_chats():
    st.header("Tìm kiếm cuộc trò chuyện")
    
    chat_history = load_chat_history()
    
    if chat_history:
        reset_state()
        student_list = ["Lựa chon mã sinh viên"] + sorted(list(chat_history.keys()))
        selected_student = st.selectbox("Mã sinh viên", options=student_list)
        
        if selected_student != "Lựa chon mã sinh viên":
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Từ ngày", format="DD/MM/YYYY")
            with col2:
                end_date = st.date_input("Đến ngày", format="DD/MM/YYYY")
            
            st.subheader(f"Lịch sử trò chuyện: {selected_student}")
            filtered_chats = filter_chats_by_date(chat_history[selected_student], start_date, end_date)
            
            if filtered_chats:
                sorted_chats = sorted(filtered_chats.items(), 
                                    key=lambda x: datetime.strptime(x[1]['createdAt'], "%Y-%m-%d %H:%M:%S"),
                                    reverse=True)
                
                for chat_id, chat_data in sorted_chats:
                    create_date = chat_data['createdAt'].split(" ")[0]
                    with st.expander(f"ID: {chat_id} - Ngày tạo: {create_date}"):
                        if chat_data['messages']:
                            display_chat_messages(chat_data['messages'])
                        else:
                            st.info("Không có cuộc trò chuyện nào.")
            else:
                st.info("Không tìm thấy cuộc trò chuyện trong khoảng thời gian này.")
        else:
            st.info("Chọn mã sinh để tìm kiếm cuộc trò chuyện.")
    else:
        st.warning("Không có lịch sử trò chuyện.")

def page_knowledge():
    st.header("Cập nhật kiến thức cho Chatbot")

    uploaded_file = st.file_uploader("Tải lên tệp", type=['txt', 'pdf', 'html', 'docx'])

    if uploaded_file:            
        try:
            if uploaded_file.name.endswith('.docx'):
                with open("temp.docx", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                docx_extractor = DOCXExtractor()
                doc = docx_extractor.load("temp.docx")
                os.remove("temp.docx")
            elif uploaded_file.name.endswith('.pdf'):
                with open("temp.pdf", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                pdf_extractor = PDFExtractor()
                doc = pdf_extractor.load("temp.pdf")
                os.remove("temp.pdf")
            elif uploaded_file.name.endswith('.html'):
                with open("temp.html", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                html_extractor = HTMLExtractor()
                doc = html_extractor.load("temp.html")
                os.remove("temp.html")
            elif uploaded_file.name.endswith('.txt'):
                with open("temp.txt", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                txt_extractor = TXTExtractor()
                doc = txt_extractor.load("temp.txt")
                os.remove("temp.txt")

            preview_text = st.text_area(label="Xem trước nội dung", value=doc.page_content, height=200)

            if st.button("Chia nhỏ dữ liệu"):
                doc.page_content = preview_text
                embedding = HFEmbedding()
                chunker = SemanticChunk(embedding_model=embedding)
                chunks = chunker.chunking([doc])
                st.session_state.chunks = deepcopy(chunks)

            if st.session_state.chunks:
                for i in range(len(st.session_state.chunks)):
                    col1, col2 = st.columns([9, 1])
                    with col1:
                        st.session_state.chunks[i].page_content = st.text_area(
                            label=f"Mẩu {i}",
                            value=st.session_state.chunks[i].page_content,
                            height=200,
                            key=f"chunk_{i}"
                        )
                    with col2:
                        if st.button("Xóa", key=f"delete_{i}"):
                            st.session_state.delete_index = i
                            break

                if st.session_state.delete_index is not None:
                    st.session_state.chunks.pop(st.session_state.delete_index)
                    st.session_state.delete_index = None
                    st.rerun()

                if st.button("Thêm"):
                    new_chunk = deepcopy(st.session_state.chunks[-1]) if st.session_state.chunks else SemanticChunk()
                    new_chunk.page_content = ""
                    st.session_state.chunks.append(new_chunk)
                    st.rerun()

                if st.button("Lưu"):
                    try:
                        vector_store = FAISSDatabase(HFEmbedding(), FAISS_PATH)
                        db = vector_store.db_get()
                        vector_store.db_add(st.session_state.chunks)
                        reset_state()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi khi lưu tệp JSON: {str(e)}")
            
            if st.session_state.updated_rag:
                st.success("Cập nhật kiến thức thành công!")
                time.sleep(3)
                st.session_state.updated_rag = False

        except Exception as e:
            st.error(f"Gặp lỗi khi xử lý file: {str(e)}")

def page_account(username):
    st.markdown('<p style="font-size:30px; font-weight:bold;">Thông tin tài khoản</p>', unsafe_allow_html=True)
    username, name, role, _, password = load_account(username)
    roles = ["Viewer"]
    role_index = roles.index(role)
    
    with st.form("infor",clear_on_submit=True):
        st.markdown(f'<p style="font-size:20px; font-weight:bold;">{username}</p>', unsafe_allow_html=True)
        name = st.text_input("Họ và tên", placeholder=f"{name}")
        password = st.text_input("Mật khẩu", type="password", placeholder=f"{password}")
        role = st.selectbox("Quyền truy cập",roles, index=role_index)
        modify_clicked = st.form_submit_button("Lưu")
    
        if modify_clicked:
            if update_account(username, name, role, password):
                st.success("Thay đổi thành công")
            else:
                st.error("Đã xảy ra lỗi")

def page_access():
    st.markdown('<p style="font-size:30px; font-weight:bold;">Quyền truy cập</p>', unsafe_allow_html=True)
    selected = option_menu(
        menu_title=None,
        options=['Thêm tài khoản', 'Chỉnh sửa'],
        icons=['patch-plus-fill', 'diagram-2-fill'],
        styles={
            "nav-link": {"font-size": "18px", "font-family": "'Source Sans Pro', sans-serif", "font-weight": "400", "font-style": "normal"},
            "nav-link-selected": {"font-size": "18px", "font-family": "'Source Sans Pro', sans-serif", "font-weight": "700", "font-style": "bold"}
        },
        orientation='horizontal'
    )
    if selected == "Thêm tài khoản":
        with st.form("signup_form",clear_on_submit=True):
            name = st.text_input("Họ và tên")
            username = st.text_input("Tên đăng nhập")
            password = st.text_input("Mật khẩu", type="password")
            role = st.selectbox("Quyền truy cập",("Admin", "Viewer"))
            signup_clicked = st.form_submit_button("Thêm")
        
            if signup_clicked:
                if add_account(username, name, role, password):
                    st.success("Thêm thành công")
                else:
                    st.error("Đã xảy ra lỗi")
    if selected == "Chỉnh sửa":
        list_username, list_names, list_roles, _, list_password, _, _, _, _ = load_accounts()
        list_username.append("none")
        selected_username = st.selectbox("Quyền truy cập", list_username, index=len(list_username)-1)
        if selected_username.lower() != "none":
            index = list_username.index(selected_username)
            roles = ["Admin", "Viewer"]
            role_index = roles.index(list_roles[index])
            with st.form("modify_form",clear_on_submit=True):
                st.markdown(f'<p style="font-size:20px; font-weight:bold;">{selected_username}</p>', unsafe_allow_html=True)
                name = st.text_input("Họ và tên", placeholder=f"{list_names[index]}")
                password = st.text_input("Mật khẩu", type="password", placeholder=f"{list_password[index]}")
                role = st.selectbox("Quyền truy cập",roles, index=role_index)
                modify_clicked = st.form_submit_button("Hoàn tất")
            
                if modify_clicked:
                    if update_account(selected_username, name, role, password):
                        st.success("Thay đổi thành công")
                    else:
                        st.error("Đã xảy ra lỗi")

def page_admin():
    with st.sidebar:
        image = Image.open(os.path.join(SIDEBAR_IMG_PATH))
        st.image(image, use_container_width=True)
        page = option_menu(
            menu_title=None,
            options=["Lịch sử chat", "Cập nhật kiến thức", "Quyền truy cập"],
            icons=['clock-history', 'journal-plus', 'patch-check-fill'],
            styles={
                "nav-link": {"font-size": "18px", "font-family": "'Source Sans Pro', sans-serif", "font-weight": "400", "font-style": "normal"},
                "nav-link-selected": {"font-size": "18px", "font-family": "'Source Sans Pro', sans-serif", "font-weight": "700", "font-style": "bold"}
            },
            )
    
    if page == "Lịch sử chat":
        page_chats()
    elif page == "Cập nhật kiến thức":
        page_knowledge()
    elif page == "Quyền truy cập":
        page_access()

def page_viewer(username):
    with st.sidebar:
        image = Image.open(os.path.join(SIDEBAR_IMG_PATH))
        st.image(image, use_container_width=True)
        page = option_menu(
            menu_title=None,
            options=["Lịch sử chat", "Tài khoản"],
            icons=['clock-history', 'person-fill-gear'],
            styles={
                "nav-link": {"font-size": "18px", "font-family": "'Source Sans Pro', sans-serif", "font-weight": "400", "font-style": "normal"},
                "nav-link-selected": {"font-size": "18px", "font-family": "'Source Sans Pro', sans-serif", "font-weight": "700", "font-style": "bold"}
            },
            )
    
    if page == "Lịch sử chat":
        page_chats()
    elif page == "Tài khoản":
        page_account(username)

def run_page(username, role):
    if role.lower() == "admin":
        setup_state()
        st.title("Hệ thống quản lý Chatbot")
        page_admin()
    elif role.lower() == "viewer": 
        setup_state()
        st.title("Hệ thống quản lý Chatbot")
        page_viewer(username)