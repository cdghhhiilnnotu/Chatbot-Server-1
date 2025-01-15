import streamlit as st
import json
import pandas as pd
from datetime import datetime
import faiss
import numpy as np
import os
import PyPDF2
from copy import deepcopy
from bs4 import BeautifulSoup
import docx
from modules.extractings import PDFExtractor, HTMLExtractor, DOCXExtractor, TXTExtractor
from modules.chunkings import SemanticChunk
from modules.embeddings import HFEmbedding
from modules.storings import FAISSDatabase

docs_dir = "sources/working"
faiss_dir = "./sources/database/faiss/v0"
VECTOR_DIMENSION = 768  # Standard dimension for many embedding models

def load_chat_history(file_path="chats.json"):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def display_chat_messages(messages):
    for msg in messages:
        if msg["type"] == "user":
            st.write("👤 User:", msg["text"])
        else:
            st.write("🤖 Server:", msg["text"])

def filter_chats_by_date(chat_data, start_date, end_date):
    filtered_chats = {}
    for chat_id, chat_info in chat_data.items():
        chat_date = datetime.strptime(chat_info['createdAt'], "%Y-%m-%d %H:%M:%S")
        if start_date <= chat_date.date() <= end_date:
            filtered_chats[chat_id] = chat_info
    return filtered_chats

def get_index_dimension(index_path):
    """Get the dimension of an existing FAISS index"""
    try:
        index = faiss.read_index(index_path)
        return index.d
    except:
        return VECTOR_DIMENSION

def load_faiss_index():
    faiss_files = [f for f in os.listdir(faiss_dir) if f.endswith('.faiss')]
    if not faiss_files:
        index = faiss.IndexFlatL2(VECTOR_DIMENSION)
        faiss.write_index(index, os.path.join(faiss_dir, "v_1.faiss"))
        return index
    
    latest_file = sorted(faiss_files)[-1]
    latest_path = os.path.join(faiss_dir, latest_file)
    
    try:
        return faiss.read_index(latest_path)
    except Exception as e:
        st.error(f"Error loading FAISS index: {e}")
        return faiss.IndexFlatL2(VECTOR_DIMENSION)

def create_dummy_vector(dimension):
    """Create a dummy vector with the correct dimension"""
    return np.random.rand(1, dimension).astype('float32')

def get_docx_content(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def get_file_content(file_path, file_type):
    content = ""
    if file_type == "pdf":
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                content += page.extract_text()
    elif file_type == "html":
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            content = soup.get_text()
    elif file_type == "docx":
        content = get_docx_content(file_path)
    return content

def save_faiss_index(index):
    faiss_files = [f for f in os.listdir(faiss_dir) if f.endswith('.faiss')]
    if faiss_files:
        latest_version = max([int(f.split('_')[1].split('.')[0]) for f in faiss_files])
        new_version = latest_version + 1
    else:
        new_version = 1
    
    new_filename = f"v_{new_version}.faiss"
    new_path = os.path.join(faiss_dir, new_filename)
    faiss.write_index(index, new_path)
    return new_filename

def main():
    st.title("Hệ thống quản lý Chatbot")
    
    page = st.sidebar.selectbox("Chọn 1 cái", 
                               ["Lịch sử chat", "Cập nhật kiến thức"])
    
    if page == "Lịch sử chat":
        st.header("Tìm kiếm cuộc trò chuyện")
        
        chat_history = load_chat_history()
        
        if chat_history:
            student_list = ["Lựa chon mã sinh viên"] + sorted(list(chat_history.keys()))
            selected_student = st.selectbox("Mã sinh viên", options=student_list)
            
            if selected_student != "Lựa chon mã sinh viên":
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Từ ngày")
                with col2:
                    end_date = st.date_input("Đến ngày")
                
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

        # Initialize chunks list in session state
        if "chunks" not in st.session_state:
            st.session_state.chunks = []

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
                        for i, chunk in enumerate(st.session_state.chunks):
                            col1, col2 = st.columns([9, 1])
                            with col1:
                                st.session_state.chunks[i].page_content = st.text_area(
                                    label=f"Mẩu {i}",
                                    value=chunk.page_content,
                                    height=200,
                                    key=f"chunk_{i}"
                                )
                            with col2:
                                if st.button("Xóa", key=f"delete_{i}"):
                                    st.session_state.chunks.pop(i)
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
                                vector_store = FAISSDatabase(HFEmbedding(), './sources/database/faiss/v_1')
                                db = vector_store.db_get()
                                vector_store.db_add(st.session_state.chunks)
                                st.success("Cập nhật kiến thức cho Chatbot thành công!")
                            except Exception as e:
                                st.error(f"Lỗi khi lưu tệp JSON: {str(e)}")

            except Exception as e:
                st.error(f"Gặp lỗi khi xử lý file: {str(e)}")

if __name__ == "__main__":
    main()
