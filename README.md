# Chess Engine 4KB (Python) — make.fun bounty

Project folder untuk bounty [**Build the strongest chess engine in 4 KB of Python**](https://make.fun/bounty/strongest-chess-engine-in-4kb-of-python-01) (EZO Labs / make.fun).

## Ringkasan bounty (cek halaman resmi untuk aturan final)
- **Goal:** engine catur terkuat dalam **≤ 4.096 byte** Python 3.13, **standard library only** (payload terkompresi ikut dihitung).
- **Build/submit:** dibuat pakai AI coding agent; submit **public GitHub repo + session transcripts**. Engine **tidak boleh memanggil model/LLM** saat berjalan.
- **Penilaian:** gauntlet lawan 8 house engine tetap (dua warna), opening diundi setelah deadline; rating **Elo** (rata-rata 3 trial). Harus di atas baseline house (**sunfish 4 KB**) untuk lolos hadiah berbayar.
- **Hadiah:** $500 USDC (Solana), 20 posisi ($100 juara 1). Tutup **2026-11-24 17:00 UTC**.

## Struktur folder
```
chess-4kb/
├─ engine.py            # Engine UCI submission-ready (target ≤ 4096 bytes)
├─ src/
│  └─ engine_dev.py     # Versi pengembangan (lebih mudah dibaca/diubah)
├─ scripts/
│  └─ check_size.py     # Cek ukuran file engine (byte)
├─ transcripts/         # Tempat menyimpan session transcripts (wajib saat submit)
└─ README.md
```

## Cara pakai (UCI)
Jalankan sebagai proses UCI:
```bash
python3 engine.py
```
Contoh interaksi cepat:
```
uci
isready
position startpos moves e2e4 e7e5
go movetime 1000
quit
```

## Cek ukuran
```bash
python3 scripts/check_size.py engine.py
```
Target submission: **≤ 4096 bytes**.

## Catatan
- `engine.py` adalah kandidat submission; iterasi logic di `src/engine_dev.py` lalu salin/minify ke `engine.py` sambil menjaga ukuran & fungsionalitas.
- `transcripts/` harus diisi rekaman sesi agent sesuai ketentuan make.fun sebelum submit.
- Belum diuji penuh di arena resmi make.fun dari lingkungan ini; uji lokal (cutechess-cli/GUI UCI) direkomendasikan.
