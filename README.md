# Chatbot Server

Dự án này là máy chủ chatbot được xây dựng bằng Node.js và tích hợp với Ollama để cung cấp khả năng trò chuyện thông minh. Nó được thiết kế để hoạt động cùng với ứng dụng chatbot client.

## Tính năng

* Cung cấp API cho ứng dụng chatbot client để tương tác với chatbot.
* Tích hợp với Ollama để xử lý các yêu cầu trò chuyện.
* Giao diện web trực quan được xây dựng bằng Streamlit.

## Cài đặt

1.  **Yêu cầu**:
    * Python (phiên bản 3.10)
    * conda (Miniconda hoặc Anaconda)
    * pip (Python package installer)
    * Ollama (đã cài đặt và cấu hình)
2.  **Tạo môi trường conda**:

    ```bash
    conda create -n server-env python=3.10
    conda activate server-env
    ```
3.  **Cài đặt ffmpeg**:
    ```bash
    conda install conda-forge::ffmpeg
    ```
4.  **Cài đặt các gói Python**:

    ```bash
    pip install -r requirements.txt
    ```

5.  **Cài đặt Ollama**:
    * Đảm bảo rằng bạn đã cài đặt và cấu hình Ollama theo hướng dẫn của nhà phát triển Ollama.
6.  **Chạy server**:

    ```bash
    python server.py
    ```
7.  **Chạy giao diện web**:
    ```bash
    streamlit run app.py
    ```

## Lưu ý

* Đảm bảo rằng Ollama đang chạy trước khi khởi động máy chủ chatbot.
* Bạn có thể tùy chỉnh các cài đặt của máy chủ trong tệp `server.py`.
* Tệp `requirements.txt` chứa danh sách các gói Python cần thiết.
* Tệp `app.py` chứa mã nguồn giao diện web.
