<div align="center">
  <img src="https://github.com/Rizz129/Micro_Break/blob/196e920b89b6dcdb3f51601d20d4008d0a8a5138/image.png" width="700">
</div>

# Micro_Break
Micro Break adalah proyek yang kami buat untuk membantu pengguna menjaga produktivitas dan kesehatan selama bekerja di depan komputer. Sistem ini dirancang untuk memberikan pengingat istirahat singkat (micro break) secara berkala, agar pengguna dapat meregangkan tubuh, mengistirahatkan mata, dan mengurangi kelelahan.

## Team Pengembang
| No. | Nama | NRP |
|-----|------|-----|
| 1 | Farrel Juan Manalif   | 2122600015|
| 2 | Muhammad Rizqi Atmajaya | 2122600025 |
| 3 | Ahmad Miftahur Rif'at  | 2122600046 |
| 4 | Dera Berlian      | 2122600057 |

# Fitur
## 🧩 Fitur Implementasi Real-Time Detection

| No. | Fitur | Deskripsi Singkat |
|:--:|:--|:--|
| 1 | **Face Detection** | Mendeteksi wajah manusia secara real-time menggunakan model `haarcascade_frontalface_default.xml`. Frame dikonversi ke grayscale dan dilakukan histogram equalization untuk stabilitas deteksi. |
| 2 | **Real-Time Parameter Control** | Pengguna dapat menyesuaikan parameter `scaleFactor` dan `minNeighbors` secara langsung (tombol W/S dan A/D) untuk menyeimbangkan akurasi dan kecepatan. |
| 3 | **Eye Detection (ROI-Based)** | Deteksi mata hanya dilakukan pada bagian atas wajah (region of interest) untuk menghindari false positive dan meningkatkan efisiensi. |
| 4 | **Head Tilt Angle Calculation** | Menghitung kemiringan kepala berdasarkan posisi dua mata menggunakan fungsi `atan2(dy, dx)`. Sudut positif berarti miring ke kanan, negatif berarti miring ke kiri. |
| 5 | **Real-Time Presence Tracking** | Menghitung durasi kehadiran pengguna di depan kamera secara kontinu. Waktu diakumulasi selama wajah terdeteksi. |
| 6 | **Auto Reset Timer** | Jika wajah tidak terdeteksi selama lebih dari 10 detik, sistem otomatis mereset waktu sesi. |
| 7 | **Auto Close Application** | Aplikasi akan menutup otomatis ketika durasi target (misalnya 1 menit) tercapai dan wajah masih terdeteksi. |
| 8 | **Visual Feedback System** | Menyediakan indikator visual langsung untuk wajah, mata, dan orientasi kepala, membantu pengguna memahami status deteksi secara real-time. |


# Teknologi yang digunakan

# Diagram Alur

# Hasil Tampilan 

# PPT Presentasi
Berikut PPT hasil diskusi kami

# Video Demo
Link Video:
