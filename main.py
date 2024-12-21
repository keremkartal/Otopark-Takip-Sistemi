import cv2
from camera_handler import PlateDetection





def main():
    plate_detection = PlateDetection()
    cap = cv2.VideoCapture(0)  # Kamerayı aç

    print("Press 'q' to exit...")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame. Exiting...")
            break

        # Kare üzerinde plaka tespiti yap
        plates = plate_detection.process_frame(frame)
        for plate in plates:
            plate_detection.handle_plate(plate)  # Her plakayı tek tek gönder

        # Annotated frame'i göster
        cv2.imshow("Plate Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
