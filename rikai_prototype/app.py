import os
import sys

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

from ui.audit_app import main


if __name__ == "__main__":
    main()
else:
    main()


# & "C:\Program Files\Python311\python.exe" -m pip install -r requirements.txt

# & "C:\Program Files\Python311\python.exe" -m streamlit run app.py


# hãy đọc và phân tích các tệp đó và gửi các hearing sheet đến các partner @VendorB và nuoc_ngot.pdf là file mô tả nội dung còn hearing_sheet_question là nơi chứa các vấn đề càn partner trả lời  