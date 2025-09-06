import streamlit as st
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from PIL import Image
from io import BytesIO
import os

# --- Utility functions ---
def create_blank_page(size):
    return Image.new("RGB", size, "white")

def draw_grid(c, images, cols, rows, page_width, page_height):
    cell_width = page_width / cols
    cell_height = page_height / rows

    for idx, img in enumerate(images):
        col = idx % cols
        row = idx // cols

        x = col * cell_width
        y = page_height - (row + 1) * cell_height

        buf = BytesIO()
        img.save(buf, format='JPEG')
        buf.seek(0)
        reader = ImageReader(buf)
        c.drawImage(reader, x, y, width=cell_width, height=cell_height)
        buf.close()

def generate_microxerox(input_pdf, output_pdf, pages_per_sheet, dpi=150):
    images = convert_from_path(input_pdf, dpi=dpi)
    total_pages = len(images)

    pad = (pages_per_sheet - total_pages % pages_per_sheet) % pages_per_sheet
    if pad:
        blank = create_blank_page(images[0].size)
        images.extend([blank] * pad)
        total_pages += pad

    sheet_count = total_pages // pages_per_sheet
    pages_per_side = pages_per_sheet // 2

    if pages_per_side == 1:
        cols, rows = 1, 1
    elif pages_per_side == 2:
        cols, rows = 2, 1
    elif pages_per_side == 4:
        cols, rows = 2, 2
    elif pages_per_side == 8:
        cols, rows = 4, 2
    elif pages_per_side == 16:
        cols, rows = 4, 4
    else:
        cols, rows = 8, 4  # For 32 pages per sheet (16 per side)

    c = canvas.Canvas(output_pdf, pagesize=A4)
    page_width, page_height = A4

    for i in range(sheet_count):
        start = i * pages_per_sheet
        sheet_pages = images[start:start+pages_per_sheet]

        front = sheet_pages[:pages_per_side]
        back = sheet_pages[pages_per_side:]

        draw_grid(c, front, cols, rows, page_width, page_height)
        c.showPage()

        draw_grid(c, back, cols, rows, page_width, page_height)
        c.showPage()

    c.save()

# --- Streamlit UI ---
st.title("📄 Micro Xerox PDF Generator")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
pages_per_sheet = st.selectbox("Pages per sheet", [2, 4, 8, 16, 32, 64])

if uploaded_file and st.button("Generate Micro Xerox PDF"):
    input_path = "input.pdf"
    with open(input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    output_path = "output_microxerox.pdf"
    generate_microxerox(input_path, output_path, pages_per_sheet)

    st.success("✅ PDF generated successfully!")
    with open(output_path, "rb") as f:
        st.download_button("📥 Download File", f, file_name="microxerox.pdf")
