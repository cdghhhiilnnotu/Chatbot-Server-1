import streamlit as st
import json
from datetime import datetime
import os
from copy import deepcopy
import time

from modules.configs import FAISS_PATH
from modules.extractings import PDFExtractor, HTMLExtractor, DOCXExtractor, TXTExtractor
from modules.chunkings import SemanticChunk
from modules.embeddings import HFEmbedding
from modules.storings import FAISSDatabase

 # Initialize chunks list in session state
if "chunks" not in st.session_state:
    st.session_state.chunks = []

# Initialize delete state
if "delete_index" not in st.session_state:
    st.session_state.delete_index = None

if "updated_rag" not in st.session_state:
    st.session_state.updated_rag = False

def load_chat_history(folder_path="database/chats"):
    try:
        all_chats = {}
        for file in os.listdir(folder_path):
            if file.endswith('.json'):
                student_id = file.replace('.json', '')
                with open(os.path.join(folder_path, file), 'r', encoding='utf-8') as f:
                    all_chats[student_id] = json.load(f)
        return all_chats
    except FileNotFoundError:
        print("File not found!")
        return {}
    except Exception as e:
        print(e)
        return {}

def display_chat_messages(messages):
    # Create a container with scrollbar
    
    for msg in messages:
        if msg["type"].lower() == "user":
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                st.write("👤 User:", msg["text"])
            with col2:
                st.write(msg["chat_at"])
        else:
            col1, col2 = st.columns([0.7, 0.3])
            with col1:
                st.write("🤖 Server:", msg["text"])
            with col2:
                st.write(msg["chat_at"])
    

def filter_chats_by_date(chat_data, start_date, end_date):
    filtered_chats = {}
    for chat_id, chat_info in chat_data.items():
        chat_date = datetime.strptime(chat_info['createdAt'], "%Y-%m-%d %H:%M:%S")
        if start_date <= chat_date.date() <= end_date:
            filtered_chats[chat_id] = chat_info
    return filtered_chats

def reset_state():
    st.session_state.chunks = []
    st.session_state.delete_index = None
    st.session_state.updated_rag = True

def main():
    st.title("Hệ thống quản lý Chatbot")
    
    page = st.sidebar.selectbox("Chọn 1 cái", 
                               ["Lịch sử chat", "Cập nhật kiến thức"])
    
    if page == "Lịch sử chat":
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

    elif page == "Cập nhật kiến thức":
        st.header("Cập nhật kiến thức cho Chatbot")

        uploaded_file = st.file_uploader("Tải lên tệp", type=['txt', 'pdf', 'html', 'docx'])

        if uploaded_file:            
            try:
                # File handling logic
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

                # Display and manage chunks
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

                    # Handle deletion
                    if st.session_state.delete_index is not None:
                        st.session_state.chunks.pop(st.session_state.delete_index)
                        st.session_state.delete_index = None
                        st.rerun()

                    # Add new chunk
                    if st.button("Thêm"):
                        new_chunk = deepcopy(st.session_state.chunks[-1]) if st.session_state.chunks else SemanticChunk()
                        new_chunk.page_content = ""
                        st.session_state.chunks.append(new_chunk)
                        st.rerun()

                    # Save chunks
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

if __name__ == "__main__":
    main()
