import cv2

qr_detector = cv2.QRCodeDetector()

def decode_qr_from_frame(frame):
    try:
        data, points, _ = qr_detector.detectAndDecode(frame)
        if data and data.startswith("MC-"):
            return data
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
                x, y = points[0]
                cv2.putText(frame, data, (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    except Exception:
        pass
    return frame