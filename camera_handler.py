import cv2
import easyocr

# EasyOCR başlat
reader = easyocr.Reader(['en'], gpu=True)

class PlateDetection:
    def detect_text(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        results = reader.readtext(gray_frame)
        detected_text = [text for (_, text, prob) in results if prob > 0.5]
        return detected_text

if __name__ == "__main__":
    detector = PlateDetection()
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        plates = detector.detect_text(frame)
        for plate in plates:
            print(f"Detected Plate: {plate}")

        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
