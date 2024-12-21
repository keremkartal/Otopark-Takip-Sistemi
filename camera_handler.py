import cv2
import easyocr
from ultralytics import YOLO
from datetime import datetime
import sqlite3


# YOLO modelini yükle ve CUDA cihazını kullan
model = YOLO('yolov8m.pt')

# EasyOCR okuyucu başlat
reader = easyocr.Reader(['tr'], gpu=True)


class PlateDetection:
    def __init__(self, db_path="parking.db"):
        self.db_path = db_path
        self.create_database()

    def create_database(self):
        # SQLite veritabanını oluştur
        #belirtilen dosya yoluna göre veritabanı dosyasını açar ya da eğer dosya yoksa yeni bir veritabanı dosyası oluşturur.
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plate TEXT,
                entry_time TEXT,
                exit_time TEXT,
                fee REAL
            )
        ''')
        conn.commit()
        conn.close()
    
    def process_frame(self, frame):
        results = model(frame)
        detected_plates = []
        
        for result in results:
            boxes = result.boxes.xyxy
            scores = result.boxes.conf
            class_ids = result.boxes.cls

            for box, score, class_id in zip(boxes, scores, class_ids):
                if score >= 0.50:
                    x1, y1, x2, y2 = map(int, box)
                    label = model.names[int(class_id)]

                    # Nesne dikdörtgen çizin
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, f'{label} {score:.2f}', (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

        detected_text = self.detect_text(frame)
        detected_plates.extend(detected_text)  # Tespit edilen plakaları listeye ekle

        
        return detected_plates

    def detect_text(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray_frame, (3, 3), 1)  # Daha küçük kernel ve sigma

        # EasyOCR kullanarak metin tespiti yap
        results = reader.readtext(blurred)
        detected_text = []
        for (bbox, text, prob) in results:
            if prob > 0.5:  # Güvenilirlik %50 üzerinde olan metinleri kabul edin
                text = text.upper().replace(" ", "")  # Harfleri büyük yap ve boşlukları kaldır
                if self.is_valid_plate(text):  # Plaka formatına uygun mu kontrol et
                    detected_text.append(text)
                    (top_left, top_right, bottom_right, bottom_left) = bbox
                    top_left = tuple(map(int, top_left))
                    bottom_right = tuple(map(int, bottom_right))
                    cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
                    cv2.putText(frame, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Birden fazla plaka algılanırsa hepsini döndür
        return detected_text


    @staticmethod
    def is_valid_plate(plate):
        if len(plate) < 7 or len(plate) > 9:
            return False
        # Plaka formatını kontrol et: ilk 2 basamak sayı, ardından 2-3 harf, sonra tekrar sayı
        if plate[:2].isdigit() and plate[2:5].isalpha() and plate[5:].isdigit():
            return True
        elif plate[:2].isdigit() and plate[2:4].isalpha() and plate[4:].isdigit():
            return True
        return False

    def handle_plate(self, plate):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        current_time = datetime.now()

        # Çıkış kontrolü (açık kayıt var mı)
        cursor.execute("SELECT * FROM parking WHERE plate = ? AND exit_time IS NULL", (plate,))
        record = cursor.fetchone()

        if record:
            # Eğer açık bir kayıt varsa çıkışı kontrol et
            entry_time = datetime.strptime(record[2], '%Y-%m-%d %H:%M:%S')  # entry_time sütunu
            duration = (current_time - entry_time).total_seconds()

            # Girişten sonra 10 saniye içinde çıkış yapılamaz
            if duration < 10:
                print(f"Plate {plate}: Cannot exit within 10 seconds of entry.")
            else:
                exit_time = current_time
                fee = (duration / 60) * 10  # Dakika başına ücret hesaplama
                cursor.execute("UPDATE parking SET exit_time = ?, fee = ? WHERE id = ?",
                            (exit_time.strftime('%Y-%m-%d %H:%M:%S'), fee, record[0]))
                print(f"Exit recorded for plate {plate}. Fee: {fee:.2f} TL")
        else:
            # Giriş kontrolü (son çıkıştan sonra 10 saniye geçmesi gerekiyor)
            cursor.execute("SELECT * FROM parking WHERE plate = ? AND exit_time IS NOT NULL ORDER BY exit_time DESC LIMIT 1", (plate,))
            last_exit_record = cursor.fetchone()

            if last_exit_record:
                last_exit_time = datetime.strptime(last_exit_record[3], '%Y-%m-%d %H:%M:%S')  # exit_time sütunu
                time_since_exit = (current_time - last_exit_time).total_seconds()

                # Çıkıştan sonra 10 saniye içinde tekrar giriş yapılamaz
                if time_since_exit < 10:
                    print(f"Plate {plate}: Cannot enter within 10 seconds of last exit.")
                    conn.close()
                    return

            # Yeni bir giriş kaydı oluştur
            entry_time = current_time
            cursor.execute("INSERT INTO parking (plate, entry_time) VALUES (?, ?)",
                        (plate, entry_time.strftime('%Y-%m-%d %H:%M:%S')))
            print(f"Entry recorded for plate {plate}. Entry Time: {entry_time}")

        conn.commit()
        conn.close()

