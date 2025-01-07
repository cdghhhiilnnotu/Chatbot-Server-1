import sys
sys.path.append('../../../demo-5')

from typing import List
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from modules.chunkings import BaseChunk


class RecursiveChunk(BaseChunk):
    name: str

    def __init__(self):
        super().__init__('RecursiveChunker')
        self.core = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)

    def chunking(self, documents: List[Document]):
        return self.core.split_documents(documents)


if __name__ == '__main__':
    doc = Document(page_content='''
        Học phần là khối lượng kiến thức tương đối trọn vẹn, thuận tiện cho sinh viên 
        tích lũy trong quá trình học tập. Mỗi học phần thực hành có khối lượng từ 1 đến 
        4 tín chỉ, mỗi học phần lý thuyết hoặc học phần có cả lý thuyết và bài tập, thực 
        hành có khối lượng từ 1 đến 5 tín chỉ. Nội dung mỗi học phần được bố trí giảng 
        dạy trọn vẹn và phân bố đều trong một học kỳ hoặc một phần (hay một nhịp) 
        của học kỳ. Đồ án tốt nghiệp là học phần đặc biệt, có khối lượng tương đương 
        10 đến 12 tín chỉ. Kiến thức trong mỗi học phần được thiết kế kiểu mô-đun theo
        từng môn học hoặc được kết cấu dưới dạng tổ hợp từ nhiều môn học. Từng học
        phần được ký hiệu bằng một mã riêng do Nhà trường qui định.
        Các loại học phần: học phần bắt buộc và học phần tự chọn

        a)Học phần bắt buộc là học phần chứa đựng những nội dung kiến thức
        chính yếu của mỗi chương trình và bắt buộc sinh viên phải tích lũy.

        b) Học phần tự chọn là học phần chứa đựng những nội dung kiến thức cần
        thiết, nhưng sinh viên được tự chọn theo hướng dẫn của Nhà trường nhằm đa
        dạng hoá hướng chuyên môn hoặc được tự chọn tuỳ ý để tích luỹ đủ số học phần
        quy định cho mỗi chương trình.
        Tín chỉ được sử dụng để tính khối lượng học tập (KLHT) của sinh viên. Một tín
        chỉ được quy định bằng 15 tiết học lý thuyết; 30 tiết thực hành, thí nghiệm, thảo
        luận, bài tập lớn, đồ án môn học và đồ án tốt nghiệp; 45 giờ thực tập tại cơ sở,
        làm tiểu luận.
        Đối với những học phần lý thuyết hoặc thực hành, thí nghiệm, để tiếp thu được
        một tín chỉ sinh viên phải dành ít nhất 30 giờ chuẩn bị cá nhân.
        Thời gian một tiết học được tính quy đổi bằng 45 phút.
    ''', metadata={'source': 'sources/working/quyche.pdf'})
      
    chunker = RecursiveChunk()
    chunks = chunker.chunking([doc])
    print(chunks)