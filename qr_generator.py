import qrcode
import io

def generate_qr(user_id: str, port: int = 8501) -> bytes:
    # Use the deployed Streamlit Cloud URL instead of local IP
    url = f"https://mediscan-emergency-qr-vswhbctby3xj78mcijchre.streamlit.app/?scan={user_id}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1a1a2e", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()