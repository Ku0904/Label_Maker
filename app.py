import streamlit as st
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
from collections import defaultdict
import pytz

# Define the size in pixels for 100mm x 50mm image (assuming 300 DPI)
dpi = 300
width_mm, height_mm = 100, 50
width_px, height_px = int(width_mm / 25.4 * dpi), int(height_mm / 25.4 * dpi)

# Directory to save QR code images
save_dir = "qr_code_images"
os.makedirs(save_dir, exist_ok=True)

# Initialize Streamlit session state
if "page" not in st.session_state:
    st.session_state.page = "main"

def load_font(size):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except IOError:
        return ImageFont.load_default()

def generate_qr_code():
    st.title("QR Code Generator")

    # Input fields for manual data entry
    part_name = st.text_input("PART NAME", value="03-003-YSD-001-B:MAIN HOUSING")
    part_no = st.text_input("PART NO", value="BOC000012090")
    total_quantity = st.text_input("TOTAL QUANTITY", value="600.00")
    qty_per_pkt = st.text_input("QTY. PER PKT", value="25")
    invoice_no = st.text_input("INVOICE NO", value="26.08.24/4761")
    batch_no = st.text_input("BATCH NO", value="250824B17SRV-01")

    # Data for QR code
    qr_data = (
        f"KAPILA INDUSTRIES, FBD\n"
        f"PART NAME: {part_name}\n"
        f"PART NO: {part_no}\n"
        f"TOTAL QUANTITY: {total_quantity}\n"
        f"QTY. PER PKT: {qty_per_pkt}\n"
        f"INVOICE NO: {invoice_no}\n"
        f"BATCH NO: {batch_no}"
    )

    if st.button("Generate QR Code"):
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill="black", back_color="white")

        img = Image.new("RGB", (width_px, height_px), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        font = load_font(30)
        bold_font = load_font(40)

        kapila_text = "KAPILA INDUSTRIES, FBD"
        kapila_text_bbox = draw.textbbox((0, 0), kapila_text, font=bold_font)
        text_width = kapila_text_bbox[2] - kapila_text_bbox[0]
        draw.text(((width_px - text_width) / 2, 10), kapila_text, font=bold_font, fill=(0, 0, 0))

        text_x = 10
        y_positions = [70, 120, 170, 220, 270, 320]
        details = [
            f"PART NAME: {part_name}",
            f"PART NO: {part_no}",
            f"TOTAL QUANTITY: {total_quantity}",
            f"QTY. PER PKT: {qty_per_pkt}",
            f"INVOICE NO: {invoice_no}",
            f"BATCH NO: {batch_no}",
        ]
        for y, detail in zip(y_positions, details):
            draw.text((text_x, y), detail, font=font, fill=(0, 0, 0))

        qr_size = int(height_px * 0.5)
        qr_img = qr_img.resize((qr_size, qr_size))
        img.paste(qr_img, (width_px - qr_size - 20, 70))

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        img_path = os.path.join(save_dir, f"qr_{timestamp}.jpg")
        img.save(img_path, "JPEG")

        st.image(img_path)

        with open(img_path, "rb") as file:
            st.download_button(
                label="Download Image",
                data=file,
                file_name=os.path.basename(img_path),
                mime="image/jpeg",
            )

def show_qr_code_history():
    st.title("QR Code History")

    # Define the local timezone (e.g., Asia/Kolkata for India)
    local_tz = pytz.timezone("Asia/Kolkata")

    image_files = [f for f in os.listdir(save_dir) if f.endswith(".jpg")]

    if image_files:
        images_by_date = defaultdict(list)
        for image_file in image_files:
            # Extract timestamp from filename
            timestamp_str = image_file.split("qr_")[1].split(".jpg")[0]
            
            try:
                # Try parsing with full timestamp format
                date_obj = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            except ValueError:
                try:
                    # If full format fails, try parsing just the date
                    date_obj = datetime.strptime(timestamp_str[:8], "%Y%m%d")
                except ValueError:
                    # If both parsing attempts fail, use file modification time
                    file_path = os.path.join(save_dir, image_file)
                    date_obj = datetime.fromtimestamp(os.path.getmtime(file_path))

            # Convert the date object to the local timezone
            date_obj = date_obj.replace(tzinfo=pytz.utc).astimezone(local_tz)

            formatted_date = date_obj.strftime("%B %d, %Y")
            formatted_time = date_obj.strftime("%I:%M:%S %p")
            images_by_date[formatted_date].append((image_file, formatted_time))

        for date, files_and_times in sorted(images_by_date.items(), reverse=True):
            st.header(date)
            for image_file, formatted_time in sorted(files_and_times, key=lambda x: x[0], reverse=True):
                image_path = os.path.join(save_dir, image_file)

                st.subheader(f"Generated at {formatted_time}")
                st.image(image_path, use_column_width=True)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"View {image_file}", key=f"view_{image_file}"):
                        st.image(image_path, caption=f"Viewing: {image_file}")
                with col2:
                    if st.button(f"Delete {image_file}", key=f"delete_{image_file}"):
                        try:
                            os.remove(image_path)
                            st.success(f"Deleted {image_file}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error deleting {image_file}: {str(e)}")
    else:
        st.write("No QR codes generated yet.")

# Navigation
if st.session_state.page == "main":
    generate_qr_code()
    if st.sidebar.button("View QR Code History"):
        st.session_state.page = "history"
        st.rerun()
elif st.session_state.page == "history":
    show_qr_code_history()
    if st.sidebar.button("Back to Generator"):
        st.session_state.page = "main"
        st.rerun()