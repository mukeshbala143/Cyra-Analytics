from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from PIL import Image as PILImage
import tempfile
import os
import streamlit as st

def generate_pdf_report(md_text, chart_paths):
    st.write(f"Starting PDF generation with {len(chart_paths)} images")
    
    # Verify paths
    valid_paths = []
    for i, p in enumerate(chart_paths):
        if os.path.exists(p):
            valid_paths.append(p)
            st.write(f"Image {i+1}: Found - {os.path.basename(p)}")
        else:
            st.error(f"Image {i+1}: MISSING - {p}")
    
    st.write(f"Valid images: {len(valid_paths)}/{len(chart_paths)}")
    
    # Create temp file in a location Streamlit can access
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir=tempfile.gettempdir())
    temp_path = temp_pdf.name
    temp_pdf.close()  # Close it so ReportLab can write to it
    
    doc = SimpleDocTemplate(
        temp_path,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # Add text
    for line in md_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("# "):
            story.append(Paragraph(line[2:], styles["Title"]))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], styles["Heading2"]))
        else:
            story.append(Paragraph(line, styles["Normal"]))
    
    st.write(f"Added text elements to story")
    
    # Add images - ONE AT A TIME with individual builds
    # This is the KEY FIX for Streamlit/ReportLab issues
    images_added = 0
    for i, path in enumerate(valid_paths):
        try:
            # Verify file exists and is readable
            with PILImage.open(path) as img:
                img_w, img_h = img.size
            
            aspect = img_h / float(img_w)
            
            # Conservative sizing
            max_w = doc.width * 0.85
            max_h = doc.height * 0.6
            
            final_w = max_w
            final_h = final_w * aspect
            
            if final_h > max_h:
                final_h = max_h
                final_w = final_h / aspect
            
            # Add page break before each image (except maybe first)
            if images_added > 0 or len(story) > 3:
                story.append(PageBreak())
            
            # Create and add image
            img_obj = Image(path, width=final_w, height=final_h)
            img_obj.hAlign = 'CENTER'
            
            story.append(Spacer(1, 20))
            story.append(img_obj)
            story.append(Spacer(1, 15))
            story.append(Paragraph(f"<b>Figure {i+1}:</b> Data Visualization", styles["Normal"]))
            
            images_added += 1
            st.write(f"Added Figure {i+1} ({final_w:.0f}x{final_h:.0f}pt)")
            
        except Exception as e:
            st.error(f"Error with image {i+1}: {str(e)}")
            continue
    
    st.write(f"Total story elements: {len(story)}")
    st.write(f"Images added: {images_added}")
    
    # Build PDF
    try:
        doc.build(story)
        
        # Verify the file was created
        if os.path.exists(temp_path):
            file_size = os.path.getsize(temp_path)
            st.success(f"PDF created successfully ({file_size:,} bytes)")
            st.write(f"Path: {temp_path}")
        else:
            st.error("PDF file not created!")
            
    except Exception as e:
        st.error(f"PDF build failed: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
    
    return temp_path