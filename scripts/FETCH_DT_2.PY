import os
import json
import PyPDF2

directory_path = "D:/FU/1950-1955/1950-1955.json"
directory_path2 = "D:/FU/1950-1955/1950-1955fixed.json"
with open(directory_path, "r") as f:
    json_data = json.load(f)
f.close()

def judgement_extract(p):
    """Extracts the judgement from a PDF file.

    Args:
        p: The path to the PDF file.

    Returns:
        The judgement as a string.
    """
    print(p)
    pdffile = open(p, "rb")
    reader = PyPDF2.PdfReader(pdffile)
    total_pages = len(reader.pages)
    text = ""
    for i in range(total_pages):
        page = reader.pages[i]
        text += page.extract_text()

    return text

for files in os.listdir("D:/FU/1950-1955"):
    (name, extension) = os.path.splitext(files)
    for dictionary in json_data:
        if dictionary["id"] == name:
            dictionary["judgment"] = judgement_extract(f"D:/FU/1950-1955/{name}.pdf")

with open(directory_path2, "w") as f:
    json.dump(json_data, f, indent=4)
f.close()
