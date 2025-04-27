import fitz
import os

def load_pdf(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist")

    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
        text += "\n"
    doc.close()

    cleaned_text = text.replace('\n\n', '\n').strip()
    return cleaned_text

if __name__ == "__main__":
    path = "backend/documents/onboarding.pdf"
    document_text = load_pdf(path)
    #print(document_text[:1000])