# Bank Marketing Term Deposit Prediction

Predicting whether a customer will subscribe to a term deposit based on direct marketing campaign data from a Portuguese banking institution — built end-to-end from EDA to a deployed REST API.

## Business Problem

Bank memiliki budget terbatas untuk telemarketing dan tidak bisa menelepon seluruh basis nasabah. Tujuan project ini adalah membangun model yang membantu bank memprioritaskan nasabah mana yang paling berpotensi subscribe term deposit, sehingga campaign menjadi lebih efisien dibanding menelepon secara acak.
 
Karena kehilangan nasabah potensial (false negative) dianggap lebih merugikan dibanding biaya satu panggilan yang sia-sia (false positive), metric utama yang diprioritaskan dalam project ini adalah **recall**, bukan accuracy.

## Dataset

- 45.211 baris, 17 kolom, tidak ada missing value maupun duplikat
- Target `y`: apakah nasabah subscribe term deposit (`yes`/`no`)
- **Distribusi target sangat imbalanced**: 88.3% `no` vs 11.7% `yes` (base rate)
- Sumber: [Bank Marketing Dataset (UCI)](https://archive.ics.uci.edu/dataset/222/bank+marketing)

## Key Insights (EDA)

Semua insight dihitung sebagai *subscribe rate* per kategori (proporsi `yes` di dalam grup), dibandingkan terhadap base rate 11.7%:

- **`poutcome = success` → 64.7% subscribe rate** (~5.5x base rate), predictor terkuat di dataset — nasabah yang sukses di campaign sebelumnya jauh lebih reseptif.
- **Age berpola U-shaped, bukan linear**: usia 65+ (42.6%) dan di bawah 25 tahun (24%) jauh di atas base rate, sementara usia produktif 35-55 tahun justru di bawah base rate (~9%).
- Konsisten dengan temuan usia, **`job = student` (28.7%)** dan **`job = retired` (22.8%)** adalah dua kategori pekerjaan dengan rate tertinggi.
- **Month sangat musiman**: Maret (52%), Desember (46.7%), September (46.5%) jauh di atas base rate — meski volume kontaknya kecil. Sebaliknya, Mei (6.7%) terendah meski volume kontaknya paling besar — kuantitas kontak tidak menjamin kualitas hasil.
- `education = tertiary` dan `marital = single` punya rate sedikit di atas rata-rata, tapi efeknya jauh lebih lemah dibanding `poutcome`, `month`, atau `age`.

## Methodology

**Data leakage handling**
- `duration` (lama panggilan) **didrop** — nilainya baru diketahui setelah panggilan selesai, di titik waktu yang sama dengan target itu sendiri. Memasukkannya sebagai fitur akan menghasilkan model yang terlihat sangat baik di evaluasi, tapi tidak valid untuk dipakai memprediksi *sebelum* panggilan terjadi.
- `pdays`, `previous`, `poutcome` **dipertahankan** — ini fitur historis dari campaign sebelumnya yang valid diketahui sebelum keputusan kontak baru dibuat, bukan leakage.

**Feature engineering**
- `pdays = -1` (kode untuk "belum pernah dikontak") dipecah menjadi dua fitur: `was_contacted_before` (biner) dan `pdays_clean` (nilai -1 diganti 0), agar model tidak salah menginterpretasikan -1 sebagai skala numerik biasa.
- `day` (tanggal kontak) **didrop** — visualisasi rate per tanggal tidak menunjukkan pola linear maupun siklikal yang jelas, mengindikasikan ini lebih merupakan faktor operasional dibanding sinyal perilaku nasabah.

**Model comparison**

| Model | Threshold | Recall | Precision | AUC-ROC | Lift |
|---|---|---|---|---|---|
| Logistic Regression | 0.62 | 0.62 | 0.27 | 0.77 | 2.28x |
| Random Forest | 0.5 | 0.40 | 0.49 | 0.80 | 4.14x |
| **Random Forest (final)** | **0.3** | **0.60** | **0.31** | **0.7704** | **2.66x** |

Threshold default (0.5) terbukti terlalu konservatif untuk goal recall-first kita. Threshold di-tuning menggunakan precision-recall curve untuk menyeimbangkan antara menangkap sebanyak mungkin nasabah potensial dan menjaga efisiensi campaign.

## Results

- **Model final**: Random Forest (`n_estimators=100`), custom threshold **0.3**
- **Recall: 0.60** | **Precision: 0.31** | **AUC-ROC: 0.7704** | **Lift: 2.66x**
- **Business impact**: dengan merekomendasikan nasabah menggunakan model (alih-alih menelepon secara acak), bank dapat memperoleh jumlah subscriber yang sama dengan jumlah panggilan yang lebih sedikit — secara langsung menghemat waktu staf dan biaya operasional campaign.

> Model dipilih bukan berdasarkan AUC-ROC tertinggi, melainkan berdasarkan recall yang sesuai dengan definisi business cost yang ditetapkan di awal project: kehilangan nasabah potensial (false negative) dianggap lebih mahal daripada satu panggilan yang sia-sia (false positive).

## Deployment

Model dan preprocessing pipeline digabung menjadi satu objek `sklearn.Pipeline`, 
di-serialize dengan `joblib`, dan dibungkus sebagai REST API menggunakan **FastAPI**. 
Threshold custom (0.3) disimpan terpisah sebagai metadata karena tidak otomatis 
ter-embed ke dalam pipeline sklearn. Containerized dengan **Docker** untuk local testing.

API berhasil dijalankan secara lokal via Docker dan uvicorn — deployment ke platform 
publik akan ditambahkan pada iterasi berikutnya.

### Menjalankan secara lokal

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
uv run fastapi dev app/main.py
# buka http://127.0.0.1:8000/docs
```

### Menjalankan dengan Docker

```bash
docker build -t bank-marketing-api .
docker run -p 8000:8000 bank-marketing-api
# buka http://localhost:8000/docs
```

## Lessons Learned

Salah satu temuan paling berharga dari project ini bukan soal model, tapi soal proses: notebook eksplorasi yang dijalankan tidak berurutan (cell di-edit dan di-run ulang secara manual, tidak top-to-bottom) dapat menghasilkan angka evaluasi yang tidak konsisten antar sesi, meskipun kode yang tersimpan terlihat benar. Akar masalahnya adalah reuse objek `ColumnTransformer`/`Pipeline` yang sudah pernah di-fit, dan variabel yang ter-overwrite tanpa disadari di antara eksperimen.

Solusi yang diterapkan: selalu validasi angka final dengan **Restart Kernel & Run All** sebelum melaporkan hasil, dan membangun objek preprocessing/model baru di setiap eksperimen alih-alih meng-reuse objek yang sudah pernah di-fit.

## Tech Stack

Python · pandas · scikit-learn · FastAPI · Docker · Render

## Project Structure

```
project/
├── data/
│   └── bank-full.csv
├── models/
│   ├── bank_marketing_model.joblib
│   └── model_metadata.json
├── notebooks/
│   └── 03_Modelling.ipynb
├── app/
│   ├── main.py
│   ├── schemas.py
│   └── predict.py
├── Dockerfile
├── requirements.txt
└── README.md
```
