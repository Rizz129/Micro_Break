import cv2
import time
import math
from collections import deque
from datetime import datetime
import sys
import argparse

# Resolusi
RESOLUSI = [
    ("120p", (160, 120)),
    ("240p", (320, 240)),
    ("360p", (480, 360)),
    ("480p", (640, 480)),
    ("720p", (1280, 720)),
    ("1080p", (1920, 1080))
]

class AngleStabilizer:
    """Kelas untuk menstabilkan pembacaan sudut dengan moving average"""
    def __init__(self, window_size=10):
        self.window_size = window_size
        self.angles = deque(maxlen=window_size)
    
    def add_angle(self, angle):
        self.angles.append(angle)
    
    def get_stable_angle(self):
        if len(self.angles) == 0:
            return None
        sorted_angles = sorted(self.angles)
        mid = len(sorted_angles) // 2
        if len(sorted_angles) % 2 == 0:
            return (sorted_angles[mid-1] + sorted_angles[mid]) / 2
        return sorted_angles[mid]
    
    def reset(self):
        self.angles.clear()

class FacePresenceMonitor:
    """
    Monitor kehadiran wajah dengan fitur:
    - Target waktu monitoring: 1 menit (configurable)
    - Timeout jika user keluar > 10 detik (configurable)
    - Auto-reset jika timeout tercapai
    - Auto-close aplikasi jika target tercapai dan user masih ada
    - Kontrol runtime: R=resolusi, ↑↓=scaleFactor, ←→=minNeighbors
    """
    def __init__(self, target_duration=60, timeout_duration=10, res_index=3, 
                 scaleFactor=1.2, minNeighbors=5):
        self.target_duration = target_duration
        self.timeout_duration = timeout_duration
        self.res_index = res_index
        
        # Variabel monitoring
        self.total_active_time = 0.0
        self.session_start_time = None
        self.last_seen_time = None
        self.prev_time = None
        
        # Variabel deteksi (configurable)
        self.scaleFactor = scaleFactor
        self.minNeighbors = minNeighbors
        self.frame_count = 0
        self.stabilizers = []
        
        # Load cascades
        self.load_cascades()
        
        # Init camera
        self.init_camera()
        
        # Session info
        self.session_number = 1
        
        # Flag untuk target tercapai
        self.target_reached = False
    
    def load_cascades(self):
        face_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        eye_path = cv2.data.haarcascades + "haarcascade_eye.xml"
        self.face_cascade = cv2.CascadeClassifier(face_path)
        self.eye_cascade = cv2.CascadeClassifier(eye_path)
        
        if self.face_cascade.empty() or self.eye_cascade.empty():
            raise RuntimeError("Gagal memuat Haar Cascade.")
        
        print("✓ Cascade classifiers loaded")
    
    def init_camera(self):
        name, (w, h) = RESOLUSI[self.res_index]
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        time.sleep(0.5)
        self.width, self.height = w, h
        self.res_name = name
        print(f"✓ Camera initialized at {name} ({w}x{h})")
    
    def change_resolution(self):
        """Ubah resolusi kamera"""
        self.cap.release()
        self.res_index = (self.res_index + 1) % len(RESOLUSI)
        name, (w, h) = RESOLUSI[self.res_index]
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        time.sleep(0.5)
        self.width, self.height = w, h
        self.res_name = name
        self.stabilizers.clear()
        self.frame_count = 0
        print(f"[INFO] Resolusi diubah ke: {name} ({w}x{h})")
    
    def calculate_angle(self, eye1, eye2):
        dx = eye2[0] - eye1[0]
        dy = eye2[1] - eye1[1]
        return math.degrees(math.atan2(dy, dx))
    
    def detect_faces(self, frame):
        """Deteksi wajah dan mata, return jumlah wajah terdeteksi"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=self.scaleFactor, 
            minNeighbors=self.minNeighbors, 
            minSize=(80, 80)
        )
        
        # Sync stabilizers
        while len(self.stabilizers) < len(faces):
            self.stabilizers.append(AngleStabilizer(8))
        
        for idx, (fx, fy, fw, fh) in enumerate(faces):
            # Draw face rectangle
            cv2.rectangle(frame, (fx, fy), (fx + fw, fy + fh), (0, 255, 0), 2)
            
            # ROI for eyes
            roi_y_start = fy
            roi_y_end = fy + int(fh * 0.6)
            roi_gray = gray[roi_y_start:roi_y_end, fx:fx+fw]
            roi_color = frame[roi_y_start:roi_y_end, fx:fx+fw]
            
            eyes = self.eye_cascade.detectMultiScale(
                roi_gray, 
                scaleFactor=1.05, 
                minNeighbors=7,
                minSize=(int(fw*0.15), int(fh*0.1)), 
                maxSize=(int(fw*0.4), int(fh*0.3))
            )
            
            stable_angle = None
            
            if len(eyes) >= 2:
                eyes = sorted(eyes, key=lambda x: x[0])
                
                valid_eyes = [eyes[0]]
                for eye in eyes[1:]:
                    if eye[0] - valid_eyes[-1][0] > fw * 0.2:
                        valid_eyes.append(eye)
                        if len(valid_eyes) >= 2: 
                            break
                
                if len(valid_eyes) >= 2:
                    eye1 = valid_eyes[0]
                    eye2 = valid_eyes[1]
                    
                    eye1_center = (fx + eye1[0] + eye1[2]//2, roi_y_start + eye1[1] + eye1[3]//2)
                    eye2_center = (fx + eye2[0] + eye2[2]//2, roi_y_start + eye2[1] + eye2[3]//2)
                    
                    cv2.circle(frame, eye1_center, 5, (255, 0, 0), -1)
                    cv2.circle(frame, eye2_center, 5, (255, 0, 0), -1)
                    cv2.line(frame, eye1_center, eye2_center, (255, 255, 0), 2)
                    
                    raw_angle = self.calculate_angle(eye1_center, eye2_center)
                    self.stabilizers[idx].add_angle(raw_angle)
                    stable_angle = self.stabilizers[idx].get_stable_angle()
                    
                    for eye in valid_eyes[:2]:
                        ex, ey, ew, eh = eye
                        cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (255, 0, 0), 2)
            
            # Display tilt info
            if stable_angle is not None:
                if abs(stable_angle) < 5:
                    tilt_status = "LURUS"
                    color = (0, 255, 0)
                elif stable_angle > 0:
                    tilt_status = f"KANAN {abs(stable_angle):.1f}°"
                    color = (0, 165, 255)
                else:
                    tilt_status = f"KIRI {abs(stable_angle):.1f}°"
                    color = (0, 165, 255)
                
                cv2.putText(frame, f"Tilt: {stable_angle:.1f}°", (fx, fy - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(frame, tilt_status, (fx, fy - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            else:
                cv2.putText(frame, "Detecting...", (fx, fy - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (128, 128, 128), 2)
        
        if len(faces) < len(self.stabilizers):
            self.stabilizers = self.stabilizers[:len(faces)]
        
        return len(faces), frame
    
    def reset_session(self):
        """Reset session untuk monitoring baru"""
        print(f"\n{'='*60}")
        print(f"SESSION #{self.session_number} - RESET")
        print(f"{'='*60}")
        print(f"Waktu aktif sebelumnya: {self.total_active_time:.1f} detik")
        print(f"Target tidak tercapai - User keluar lebih dari {self.timeout_duration} detik")
        print(f"Memulai session baru...\n")
        
        self.total_active_time = 0.0
        self.session_start_time = None
        self.last_seen_time = None
        self.prev_time = None
        self.stabilizers.clear()
        self.session_number += 1
        self.target_reached = False
    
    def close_application(self):
        """Menutup aplikasi secara keseluruhan"""
        print(f"\n{'='*60}")
        print(f"🎉 TARGET TERCAPAI - USER MASIH HADIR! 🎉")
        print(f"{'='*60}")
        print(f"Session #{self.session_number} selesai")
        print(f"Total waktu aktif: {self.format_time(self.total_active_time)}")
        print(f"User masih terdeteksi di depan layar")
        print(f"{'='*60}")
        print(f"\n⚠️  APLIKASI AKAN DITUTUP DALAM 3 DETIK... ⚠️\n")
        
        # Countdown
        for i in range(3, 0, -1):
            print(f"Menutup dalam {i}...")
            time.sleep(1)
        
        print("\n[INFO] Aplikasi ditutup - Target tercapai!")
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        
        # Exit program
        sys.exit(0)
    
    def format_time(self, seconds):
        """Format detik ke MM:SS"""
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m:02d}:{s:02d}"
    
    def run(self):
        """Main loop monitoring"""
        print(f"\n{'='*60}")
        print(f"FACE PRESENCE MONITOR - SESSION #{self.session_number}")
        print(f"{'='*60}")
        print(f"Target waktu: {self.target_duration} detik ({self.target_duration//60} menit)")
        print(f"Timeout: {self.timeout_duration} detik")
        print(f"Resolusi: {self.res_name}")
        print(f"ScaleFactor: {self.scaleFactor:.2f}")
        print(f"MinNeighbors: {self.minNeighbors}")
        print(f"{'='*60}")
        print(f"⚠️  PERHATIAN: Aplikasi akan MENUTUP otomatis jika target tercapai dan user masih hadir!")
        print(f"\nKontrol Runtime:")
        print(f"  Q/ESC    : Keluar")
        print(f"  R        : Ubah Resolusi")
        print(f"  W/S      : ScaleFactor +/- 0.05")
        print(f"  A/D      : MinNeighbors +/- 1")
        print(f"  +/-      : ScaleFactor +/- 0.05 (alternatif)")
        print(f"  [ / ]    : MinNeighbors +/- 1 (alternatif)")
        print(f"  SPACE    : Reset Manual")
        print(f"{'='*60}\n")
        
        fps_time = time.time()
        fps_count = 0
        fps = 0
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Tidak dapat membaca frame dari kamera")
                break
            
            frame = cv2.flip(frame, 1)
            current_time = time.time()
            
            # Deteksi wajah
            num_faces, frame = self.detect_faces(frame)
            
            # Hitung FPS
            fps_count += 1
            if current_time - fps_time >= 1.0:
                fps = fps_count
                fps_count = 0
                fps_time = current_time
            
            # Logic monitoring
            if num_faces > 0:
                # User hadir
                if self.session_start_time is None:
                    self.session_start_time = current_time
                    self.prev_time = current_time
                    self.last_seen_time = current_time
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ User terdeteksi - Mulai monitoring")
                else:
                    dt = current_time - self.prev_time
                    self.total_active_time += dt
                    self.prev_time = current_time
                    self.last_seen_time = current_time
                
                remaining = self.target_duration - self.total_active_time
                status = "✅ USER HADIR"
                status_color = (0, 255, 0)
                
                # Cek apakah target tercapai
                if self.total_active_time >= self.target_duration:
                    if not self.target_reached:
                        self.target_reached = True
                        self.close_application()
                
            else:
                # User tidak hadir
                if self.last_seen_time is not None:
                    elapsed = current_time - self.last_seen_time
                    
                    if elapsed < self.timeout_duration:
                        # Masih dalam grace period
                        status = f"⏳ MENUNGGU ({int(elapsed)}s/{self.timeout_duration}s)"
                        status_color = (0, 165, 255)
                        remaining = self.target_duration - self.total_active_time
                    else:
                        # Timeout - Reset session
                        status = "❌ TIMEOUT - RESET"
                        status_color = (0, 0, 255)
                        remaining = self.target_duration
                        
                        self.reset_session()
                        continue
                else:
                    status = "⏳ MENUNGGU USER"
                    status_color = (128, 128, 128)
                    remaining = self.target_duration
            
            # Display info pada frame
            # Status bar background
            cv2.rectangle(frame, (0, 0), (self.width, 180), (0, 0, 0), -1)
            
            # Status
            cv2.putText(frame, status, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
            
            # Time info
            if self.session_start_time:
                time_info = f"Aktif: {self.format_time(self.total_active_time)} / {self.format_time(self.target_duration)}"
                remain_info = f"Sisa: {self.format_time(max(0, remaining))}"
                
                # Warning jika mendekati target
                if remaining <= 10 and remaining > 0:
                    warning_text = f"⚠️ CLOSING IN {int(remaining)}s ⚠️"
                    cv2.putText(frame, warning_text, (self.width//2 - 150, self.height - 80), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            else:
                time_info = "Menunggu user..."
                remain_info = f"Target: {self.format_time(self.target_duration)}"
            
            cv2.putText(frame, time_info, (10, 65), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, remain_info, (10, 95), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            # Detection parameters
            cv2.putText(frame, f"Res: {self.res_name} | Scale: {self.scaleFactor:.2f} | Neigh: {self.minNeighbors}", 
                       (10, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 0), 2)
            
            # Session & FPS info
            cv2.putText(frame, f"Session #{self.session_number} | FPS: {fps} | Faces: {num_faces}", 
                       (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            
            # Controls hint
            cv2.putText(frame, "R:Res | W/S:Scale | A/D:Neigh | +/-:Scale | [/]:Neigh | SPACE:Reset | Q:Quit", 
                       (10, self.height - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)
            
            # Progress bar
            if self.session_start_time:
                progress = min(1.0, self.total_active_time / self.target_duration)
                bar_width = int(self.width * 0.8)
                bar_x = (self.width - bar_width) // 2
                bar_y = self.height - 40
                
                # Background bar
                cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + 20), 
                             (50, 50, 50), -1)
                
                # Progress bar - merah jika hampir selesai
                if progress > 0.9:
                    bar_color = (0, 0, 255)  # Merah
                elif progress > 0.7:
                    bar_color = (0, 165, 255)  # Orange
                else:
                    bar_color = (0, 255, 0)  # Hijau
                
                cv2.rectangle(frame, (bar_x, bar_y), 
                             (bar_x + int(bar_width * progress), bar_y + 20), 
                             bar_color, -1)
                # Border
                cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + 20), 
                             (255, 255, 255), 2)
                
                # Percentage
                percent_text = f"{int(progress * 100)}%"
                cv2.putText(frame, percent_text, 
                           (bar_x + bar_width + 10, bar_y + 15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow('Face Presence Monitor', frame)
            
            # Console output (setiap 5 detik)
            if self.session_start_time and int(self.total_active_time) % 5 == 0 and self.total_active_time > 0:
                if not hasattr(self, '_last_print') or int(self.total_active_time) != self._last_print:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Progress: {self.format_time(self.total_active_time)}/{self.format_time(self.target_duration)} "
                          f"({int(self.total_active_time/self.target_duration*100)}%)")
                    self._last_print = int(self.total_active_time)
            
            # Keyboard control
            key = cv2.waitKey(1) & 0xFF
            
            # Debug: print key code (uncomment untuk debugging)
            # if key != 255:
            #     print(f"Key pressed: {key}")
            
            if key == ord('q') or key == ord('Q') or key == 27:  # Q atau ESC
                print("\n[INFO] Program dihentikan oleh user")
                break
            
            elif key == ord('r') or key == ord('R'):  # R = Ubah Resolusi
                self.change_resolution()
            
            # Arrow keys - support multiple key codes
            elif key in [82, 0]:  # Arrow UP (82 di Windows, 0 di beberapa sistem)
                # Cek dengan waitKeyEx untuk special keys
                pass
            elif key == ord('w') or key == ord('W'):  # W = Increase scaleFactor
                old_scale = self.scaleFactor
                self.scaleFactor = round(min(self.scaleFactor + 0.05, 2.0), 2)
                print(f"[INFO] ScaleFactor: {old_scale:.2f} → {self.scaleFactor:.2f}")
            
            elif key == ord('s') or key == ord('S'):  # S = Decrease scaleFactor
                old_scale = self.scaleFactor
                self.scaleFactor = round(max(self.scaleFactor - 0.05, 1.01), 2)
                print(f"[INFO] ScaleFactor: {old_scale:.2f} → {self.scaleFactor:.2f}")
            
            elif key == ord('d') or key == ord('D'):  # D = Increase minNeighbors
                old_neigh = self.minNeighbors
                self.minNeighbors = min(self.minNeighbors + 1, 15)
                print(f"[INFO] MinNeighbors: {old_neigh} → {self.minNeighbors}")
            
            elif key == ord('a') or key == ord('A'):  # A = Decrease minNeighbors
                old_neigh = self.minNeighbors
                self.minNeighbors = max(self.minNeighbors - 1, 1)
                print(f"[INFO] MinNeighbors: {old_neigh} → {self.minNeighbors}")
            
            elif key == ord('+') or key == ord('='):  # + = Increase scaleFactor
                old_scale = self.scaleFactor
                self.scaleFactor = round(min(self.scaleFactor + 0.05, 2.0), 2)
                print(f"[INFO] ScaleFactor: {old_scale:.2f} → {self.scaleFactor:.2f}")
            
            elif key == ord('-') or key == ord('_'):  # - = Decrease scaleFactor
                old_scale = self.scaleFactor
                self.scaleFactor = round(max(self.scaleFactor - 0.05, 1.01), 2)
                print(f"[INFO] ScaleFactor: {old_scale:.2f} → {self.scaleFactor:.2f}")
            
            elif key == ord('[') or key == ord('{'):  # [ = Decrease minNeighbors
                old_neigh = self.minNeighbors
                self.minNeighbors = max(self.minNeighbors - 1, 1)
                print(f"[INFO] MinNeighbors: {old_neigh} → {self.minNeighbors}")
            
            elif key == ord(']') or key == ord('}'):  # ] = Increase minNeighbors
                old_neigh = self.minNeighbors
                self.minNeighbors = min(self.minNeighbors + 1, 15)
                print(f"[INFO] MinNeighbors: {old_neigh} → {self.minNeighbors}")
            
            elif key == 32:  # SPACE = Reset manual
                print(f"[INFO] Reset manual oleh user")
                self.reset_session()
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        
        print("\n[INFO] Program selesai")
        print(f"Total session: {self.session_number}")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Face Presence Monitor - Monitor kehadiran user dengan auto-close',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Contoh penggunaan:
  python script.py                                    # Default settings
  python script.py -t 120 -o 15                       # Target 2 menit, timeout 15 detik
  python script.py -r 720p -s 1.3 -n 7                # 720p, scale 1.3, neighbors 7
  python script.py -t 30 -o 5 -r 1080p -s 1.15 -n 6   # Full custom

Resolusi tersedia: 120p, 240p, 360p, 480p, 720p, 1080p
        '''
    )
    
    parser.add_argument('-t', '--target', type=int, default=60,
                        help='Target waktu monitoring dalam detik (default: 60)')
    parser.add_argument('-o', '--timeout', type=int, default=10,
                        help='Timeout keluar dalam detik (default: 10)')
    parser.add_argument('-r', '--resolution', type=str, default='480p',
                        choices=['120p', '240p', '360p', '480p', '720p', '1080p'],
                        help='Resolusi kamera (default: 480p)')
    parser.add_argument('-s', '--scale', type=float, default=1.2,
                        help='ScaleFactor untuk deteksi (1.01-2.0, default: 1.2)')
    parser.add_argument('-n', '--neighbors', type=int, default=5,
                        help='MinNeighbors untuk deteksi (1-15, default: 5)')
    
    args = parser.parse_args()
    
    # Validasi input
    if args.scale < 1.01 or args.scale > 2.0:
        print("Error: ScaleFactor harus antara 1.01 dan 2.0")
        sys.exit(1)
    
    if args.neighbors < 1 or args.neighbors > 15:
        print("Error: MinNeighbors harus antara 1 dan 15")
        sys.exit(1)
    
    # Cari index resolusi
    res_names = [r[0] for r in RESOLUSI]
    res_index = res_names.index(args.resolution)
    
    # Print konfigurasi
    print("\n" + "="*60)
    print("FACE PRESENCE MONITOR - Console Version with CLI")
    print("="*60)
    print(f"Konfigurasi:")
    print(f"  Target waktu    : {args.target} detik ({args.target//60} menit {args.target%60} detik)")
    print(f"  Timeout         : {args.timeout} detik")
    print(f"  Resolusi        : {args.resolution}")
    print(f"  ScaleFactor     : {args.scale:.2f}")
    print(f"  MinNeighbors    : {args.neighbors}")
    print("="*60)
    print("⚠️  APLIKASI AKAN MENUTUP jika target tercapai dan user masih hadir!")
    print("="*60 + "\n")
    
    try:
        monitor = FacePresenceMonitor(
            target_duration=args.target,
            timeout_duration=args.timeout,
            res_index=res_index,
            scaleFactor=args.scale,
            minNeighbors=args.neighbors
        )
        monitor.run()
    except KeyboardInterrupt:
        print("\n[INFO] Program dihentikan (Ctrl+C)")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()