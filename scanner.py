import cv2
from urllib.parse import urlparse, parse_qs

qr_detector = cv2.QRCodeDetector()

def extract_mediscan_id(data):
    """Extract MediScan ID from QR data — handles both raw ID and full URL formats."""
    if not data:
        return None
    # Direct ID format
    if data.startswith("MC-"):
        return data
    # URL format: https://...?scan=MC-XXXXXXXX
    try:
        parsed = urlparse(data)
        scan_value = parse_qs(parsed.query).get("scan", [None])[0]
        if scan_value and scan_value.startswith("MC-"):
            return scan_value
    except Exception:
        pass
    return None

def decode_qr_from_frame(frame):
    try:
        data, points, _ = qr_detector.detectAndDecode(frame)
        return extract_mediscan_id(data)
    except Exception:
        pass
    return None

def draw_qr_box(frame):
    try:
        data, points, _ = qr_detector.detectAndDecode(frame)
        if points is not None and len(points) > 0:
            points = points[0].astype(int)
            for i in range(4):
                pt1 = tuple(points[i])
                pt2 = tuple(points[(i + 1) % 4])
                cv2.line(frame, pt1, pt2, (0, 255, 0), 3)
            if data:
                mediscan_id = extract_mediscan_id(data)
                label = mediscan_id if mediscan_id else data
                x, y = points[0]
                cv2.putText(frame, label, (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    except Exception:
        pass
    return frame