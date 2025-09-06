import streamlit as st
from pdf2image import convert_from_bytes
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from PIL import Image
from io import BytesIO

# --- Helper functions ---
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
        img.save(buf, format="JPEG")
        buf.seek(0)
        reader = ImageReader(buf)
        c.drawImage(reader, x, y, width=cell_width, height=cell_height)
        buf.close()

def generate_microxerox(pdf_bytes, pages_per_sheet, dpi=150):
    images = convert_from_bytes(pdf_bytes, dpi=dpi)
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
        cols, rows = 8, 4

    output = BytesIO()
    c = canvas.Canvas(output, pagesize=A4)
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
    output.seek(0)
    return output

# --- Streamlit UI ---
st.set_page_config(page_title="Micro Xerox PDF Generator", page_icon="📄", layout="centered")

st.markdown(
    """
    <h1 style="text-align:center;">📄 Micro Xerox PDF Generator</h1>
    <p style="text-align:center; font-size:18px;">
    Convert your PDFs into printable mini-booklets with multiple pages per sheet.<br>
    Perfect for saving paper and creating micro xerox copies.
    </p>
    """,
    unsafe_allow_html=True
)

# Sidebar controls
st.sidebar.header("⚙️ Settings")
uploaded_file = st.sidebar.file_uploader("Upload your PDF", type="pdf")
pages_per_sheet = st.sidebar.selectbox("Pages per sheet", [2, 4, 8, 16, 32, 64])

if uploaded_file:
    if st.sidebar.button("🚀 Generate PDF"):
        with st.spinner("Processing your PDF..."):
            result_pdf = generate_microxerox(uploaded_file.read(), pages_per_sheet)
        st.success("✅ Your Micro Xerox PDF is ready!")
        st.download_button(
            label="📥 Download Micro Xerox PDF",
            data=result_pdf,
            file_name="microxerox.pdf",
            mime="application/pdf",
        )

# Footer
st.markdown(
    """
    <hr>
    <p style="text-align:center;">
    ☕ Like this tool? <a href="https://www.buymeacoffee.com/yourname" target="_blank">Buy me a coffee</a><br>
    Made with ❤️ using <a href="https://streamlit.io/" target="_blank">Streamlit</a>
    </p>
    """,
    unsafe_allow_html=True
)
