<div align="center">
  <img src="" width="700">
</div>

# MICRO BREAK
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
## 🧠 Haar Cascade Classifier (Metode Viola–Jones)
Proyek ini menggunakan **algoritma Viola–Jones** dengan pendekatan **Haar Cascade Classifier** sebagai inti dari sistem deteksi wajah real-time.  
Metode ini merupakan salah satu algoritma paling klasik dan efisien dalam *computer vision* untuk mendeteksi objek seperti wajah, mata, atau ekspresi dengan kecepatan tinggi.

**Komponen utama yang digunakan dalam algoritma ini:**
- **Haar-like Features** → Pola persegi sederhana yang digunakan untuk mengenali tepi, garis, dan tekstur wajah.  
- **Integral Image** → Teknik perhitungan cepat yang memungkinkan evaluasi ribuan fitur dalam waktu singkat.  
- **AdaBoost Algorithm** → Metode *machine learning* untuk memilih fitur terbaik dan membangun *strong classifier* dari banyak *weak classifier*.  
- **Cascade Classifier** → Struktur bertingkat yang memungkinkan deteksi efisien; hanya area yang lolos tahap awal akan diperiksa lebih lanjut.

Metode Haar Cascade (Viola–Jones) ini menjadi dasar untuk semua fitur yang diimplementasikan, seperti **deteksi mata, pengukuran sudut kemiringan kepala, serta pelacakan kehadiran real-time**.

## Diagram Alur
<div align="center">
  <img src="https://github.com/Rizz129/Micro_Break/blob/726d451253cc166974a2fa56e7ca085e238d98dd/image.png" width="700">
</div>

Flowchart di atas menjelaskan proses kerja sistem **real-time face detection & presence tracking**.  
Proses dimulai ketika kamera diaktifkan untuk menangkap frame video secara berkelanjutan. Sistem kemudian memeriksa apakah terdapat **wajah yang terdeteksi** dalam frame.

Jika wajah terdeteksi, program akan menghitung **selisih waktu (ΔT)** antar frame dan menambahkannya ke dalam **total waktu kehadiran pengguna**. Perhitungan ini terus berlanjut selama wajah masih terlihat di depan kamera.

Apabila wajah tidak terdeteksi, sistem akan mulai menghitung durasi kehilangan. Jika kondisi ini berlangsung lebih dari **10 detik**, maka **waktu sesi akan direset secara otomatis**, dan penghitungan dimulai ulang.

Sistem juga melakukan pengecekan apakah **total waktu kehadiran telah mencapai target** (misalnya 1 menit). Jika sudah tercapai dan wajah masih terdeteksi, maka program akan **berhenti otomatis**.

Secara keseluruhan, flowchart ini menggambarkan mekanisme **pemantauan kehadiran otomatis berbasis deteksi wajah**, yang mampu:
- Menghitung durasi kehadiran pengguna secara real-time  
- Melakukan reset saat wajah tidak terdeteksi selama 10 detik  
- Mengakhiri sesi otomatis ketika waktu target tercapai  

## Hasil Tampilan 
Berikut Tampilan dari Program :
<div align="center">
  <img src="https://github.com/Rizz129/Micro_Break/blob/a73ad392202562ec4a469de377cebab40aa96f61/WhatsApp%20Image%202025-11-12%20at%2017.54.42.jpeg" width="700">
</div>

## PPT Presentasi
Berikut PPT hasil diskusi kami :
(https://www.canva.com/design/DAG4eoIGsBo/0m97N4Xe-pMMDhgKLspoGw/edit?utm_content=DAG4eoIGsBo&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)

## Video Demo
Link Video:
https://youtu.be/eMaV0exm4vY?si=GOEUj-h-cfak8Ri1
