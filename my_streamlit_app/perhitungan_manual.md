## Perhitungan Manual

Semua angka di bawah dihitung ulang dari output notebook (tabel split, classification report, confusion matrix, dan tabel luas).

### A. Pembagian data
*Sumber: tabel split (bagian 4 notebook).*

- Total titik = 6 kelas × 1.500 = **9.000**
- Data latih = 6 kelas × 1.080 = **6.480**
- Data uji = 6 kelas × 312 = **1.872** (312 per kelas, jadi seimbang)

### B. Menentukan TP, FP, dan FN
*Sumber: classification report dan confusion matrix (bagian 5 notebook).*

- TP (benar diprediksi) = recall × support, dengan support = 312 per kelas
- Total prediksi satu kelas = TP / precision
- FP = total prediksi - TP
- FN = support - TP

Contoh Sawah: TP = 0,923 × 312 = 288 (cocok dengan diagonal confusion matrix). Total prediksi Sawah = 288 / 0,772 = 373, sehingga FP = 373 - 288 = 85 dan FN = 312 - 288 = 24 (baris Sawah: 1 salah ke Mangrove + 23 salah ke Lahan Hijau = 24).

| Kelas | TP | FP | FN |
|---|---|---|---|
| Sawah | 288 | 85 | 24 |
| Bangunan | 289 | 76 | 23 |
| Mangrove | 300 | 8 | 12 |
| Lahan Hijau | 243 | 38 | 69 |
| Perairan Laut | 288 | 0 | 24 |
| Danau (Ranu) | 230 | 27 | 82 |
| **Total** | **1.638** | **234** | **234** |

Total FP sama dengan total FN (234), dan sama dengan jumlah data uji yang salah (1.872 - 1.638 = 234).

### C. Akurasi
$$\text{Akurasi} = \frac{\sum TP}{N} = \frac{1.638}{1.872} = 0{,}875 = 87{,}50\%$$

### D. Precision, Recall, dan F1 per kelas

$$\text{Precision} = \frac{TP}{TP+FP} \qquad \text{Recall} = \frac{TP}{TP+FN} \qquad F1 = \frac{2 \times P \times R}{P + R}$$

| Kelas | Precision | Recall | F1 |
|---|---|---|---|
| Sawah | 288/373 = 0,772 | 288/312 = 0,923 | 0,841 |
| Bangunan | 289/365 = 0,792 | 289/312 = 0,926 | 0,854 |
| Mangrove | 300/308 = 0,974 | 300/312 = 0,962 | 0,968 |
| Lahan Hijau | 243/281 = 0,865 | 243/312 = 0,779 | 0,820 |
| Perairan Laut | 288/288 = 1,000 | 288/312 = 0,923 | 0,960 |
| Danau (Ranu) | 230/257 = 0,895 | 230/312 = 0,737 | 0,808 |

Contoh F1 Sawah: 2 × 0,772 × 0,923 / (0,772 + 0,923) = 1,425 / 1,695 = **0,841**.

### E. Rata-rata makro
$$F1_{macro} = \frac{0{,}841 + 0{,}854 + 0{,}968 + 0{,}820 + 0{,}960 + 0{,}808}{6} = \frac{5{,}251}{6} = 0{,}875$$

Karena jumlah data uji tiap kelas sama (312), rata-rata makro dan rata-rata berbobot memberi hasil yang sama.

### F. Luas hasil prediksi per area
*Sumber: tabel luas (bagian 6 notebook).*

Satu piksel Sentinel-2 = 10 m × 10 m = 100 m² = 0,01 ha, sehingga:

$$\text{Luas kelas (ha)} = \text{jumlah piksel kelas} \times 0{,}01$$

$$\text{Proporsi} = \frac{\text{luas kelas}}{\text{total luas area}} \times 100\%$$

Contoh Malang: total = 351,2 + 2.751,0 + 3,6 + 532,6 + 0 + 3,8 = 3.642,2 ha, dan Bangunan = 2.751,0 / 3.642,2 = **75,5%**.

| Area | Total luas (ha) | Kelas dominan | Luas (ha) | Proporsi |
|---|---|---|---|---|
| Surabaya-Sidoarjo | 3.636,1 | Mangrove | 953,4 | 26,2% |
| Malang | 3.642,2 | Bangunan | 2.751,0 | 75,5% |
| Nganjuk | 3.624,1 | Sawah | 1.584,6 | 43,7% |
| Banyuwangi | 3.684,5 | Bangunan | 1.447,0 | 39,3% |
| Danau (Ranu) | 3.648,1 | Sawah | 1.836,5 | 50,3% |

Total tiap area sekitar 3.600 ha, sesuai area 6 km × 6 km = 36 km² = 3.600 ha (selisih kecil karena batas piksel dan konversi koordinat).
