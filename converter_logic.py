from pdf2docx import Converter

def convert_now(pdf_path):
    try:
        # PDF ke naam ke peeche .docx laga kar naya path banana
        word_path = pdf_path.replace(".pdf", ".docx")
        
        # Actual conversion start
        cv = Converter(pdf_path)
        cv.convert(word_path, start=0, end=None)
        cv.close()
        
        return True, word_path
    except Exception as e:
        return False, str(e)