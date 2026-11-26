# bot-fx

ดึงเรต **Weighted-average Interbank Exchange Rate – THB/USD** รายวันจาก API ของธนาคารแห่งประเทศไทย (ธปท.) ย้อนหลัง 20 วันทำการ แล้วบันทึกลง SQLite

```
uv run bot-fx
INFO Fetching 2026-10-26 .. 2026-11-26
INFO Fetching 2026-09-24 .. 2026-10-25
INFO Saved 20 rows (2026-10-30 .. 2026-11-26) to .../.venv/bot_api_daily_peerawet.db; table now holds 20 rows
```

รันซ้ำกี่ครั้งก็ได้ ข้อมูลไม่ซ้ำ ทุกรอบอัปเดต 20 วันทำการล่าสุด วันใหม่จะถูกเพิ่ม และแถวที่เก่ากว่านั้นยังเก็บไว้ ตารางจึงโตขึ้นวันละแถวเมื่อมีวันทำการใหม่ ถ้า ธปท. แก้เรตของวันที่บันทึกไว้แล้ว โปรแกรมจะเขียนค่าใหม่ทับและพิมพ์ WARNING บอกค่าเดิมกับค่าใหม่

## สิ่งที่ต้องมี

- **uv** สำหรับจัดการ Python และ dependency (ไม่ต้องลง Python เอง uv จะโหลด Python 3.12 ให้)
- **API key ของ ธปท.** ฟรี ขอได้จาก portal (ดูขั้นตอนด้านล่าง)
- อินเทอร์เน็ต

### ติดตั้ง uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# หรือถ้ามี Python อยู่แล้ว
pip install uv        # จากนั้นใช้ `python -m uv` แทน `uv` ถ้าคำสั่ง uv ไม่อยู่ใน PATH
```

### ขอ API key

1. เข้า https://portal.api.bot.or.th → Sign up → ยืนยันอีเมล
2. Catalogues → **Exchange Rates** → Access with this plan
3. ไอคอนตะกร้า → Create a new app → Submit Request
4. Profile → My apps → เลือก app → **Copy token** (ต้องรอให้คำขอได้รับอนุมัติก่อน)

## ติดตั้ง

```bash
git clone https://github.com/peerawet/mts-takehome-fx-rate.git
cd mts-takehome-fx-rate

cp .env.example .env            # Windows PowerShell: Copy-Item .env.example .env
```

เปิด `.env` แล้ววาง token หลัง `BOT_API_KEY=` (ไม่ต้องมีคำว่า `Bearer`)

```
BOT_API_KEY=<token ที่ copy มา>
```

จากนั้นติดตั้ง dependency

```bash
uv sync
```

## รัน

```bash
uv run bot-fx
```

- ไฟล์ผลลัพธ์อยู่ที่ `.venv/bot_api_daily_peerawet.db` ตามที่โจทย์กำหนด
- **ถ้าต้องการข้อมูลของวันนี้ ให้รันหลัง 18:00 น. เวลาไทย** ธปท. ประกาศเรตทุกวันทำการเวลานั้น รันก่อนหน้านั้นได้ปกติ แถวล่าสุดจะเป็นวันทำการก่อนหน้า
- วันที่นับตามเวลาไทยเสมอ ไม่ว่าเครื่องจะตั้ง timezone อะไร

### ตั้งค่าเพิ่มเติม

| ตัวแปร | ค่า default | ใช้ทำอะไร |
|---|---|---|
| `BOT_API_KEY` | (บังคับ) | token จาก portal ของ ธปท. ใส่ใน `.env` หรือ environment ก็ได้ |
| `BOT_DB_PATH` | `.venv/bot_api_daily_peerawet.db` | เปลี่ยนที่วางไฟล์ SQLite เช่น `BOT_DB_PATH=data/rates.db` |

## ดูข้อมูลที่ได้

```bash
uv run python -c "import sqlite3; [print(r) for r in sqlite3.connect('.venv/bot_api_daily_peerawet.db').execute('SELECT * FROM rates ORDER BY period')]"
```

หรือเปิดไฟล์ด้วยโปรแกรมอ่าน SQLite เช่น DB Browser for SQLite

ตาราง `rates` มี 3 คอลัมน์

| คอลัมน์ | ชนิด | ความหมาย |
|---|---|---|
| `period` | TEXT, PRIMARY KEY | วันที่ของเรต `YYYY-MM-DD` |
| `rate` | REAL | บาทต่อ 1 USD เช่น `34.014` (API ส่งมาเป็น `"34.0140000"`) แสดงครบ 7 ตำแหน่งได้ด้วย `printf('%.7f', rate)` |
| `fetched_at` | TEXT | เวลาที่ดึงแถวนั้นล่าสุด ISO 8601 เวลาไทย เช่น `2026-11-26T23:43:10+07:00` (อัปเดตทุกรอบที่แถวอยู่ใน 20 วันล่าสุด ไม่ได้บอกว่าค่าเปลี่ยนเมื่อไหร่) |

## Test

```bash
uv run pytest
```

test ทั้งหมดใช้ response จริงที่บันทึกไว้ใน `tests/fixtures/` ไม่ต้องใช้ API key และไม่ต้องต่อเน็ต

## แก้ปัญหา

| ข้อความ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `BOT_API_KEY is not set` | ยังไม่มี `.env` หรือยังไม่ได้ใส่ token | ทำตามขั้นตอนติดตั้งด้านบน |
| `403 Forbidden: the token was rejected` | token ผิด ไม่ครบ หรือคำขอยังไม่ได้รับอนุมัติ | copy token ใหม่จาก Profile → My apps และเช็กว่า app ได้รับอนุมัติแล้ว |
| `401 Unauthorized` | API ไม่ได้รับ token | เช็กว่าไม่มีช่องว่างหรือเครื่องหมายคำพูดครอบ token ใน `.env` |
| `WARNING Got N business days, expected 20` | ช่วงที่ดึงมีวันหยุดยาวมากจนได้ไม่ครบ 20 วันทำการ | ข้อมูลที่ได้ถูกบันทึกแล้ว รันใหม่ภายหลังได้ |
| `WARNING Rate for <วันที่> changed: <ค่าเดิม> -> <ค่าใหม่>` | ธปท. แก้เรตของวันที่บันทึกไว้แล้ว ตารางถูกอัปเดตเป็นค่าใหม่แล้ว | ถ้าเคยใช้ค่าเดิมในรายงาน ให้แจ้งผู้เกี่ยวข้อง ค่าเดิมดูได้จากข้อความนี้ |
| `Could not reach the BOT API` | ต่อเน็ตไม่ได้หรือ API ล่ม | ลองใหม่ภายหลัง |
| `uv: command not found` | ติดตั้ง uv แล้วแต่ไม่อยู่ใน PATH | เปิด terminal ใหม่ หรือใช้ `python -m uv` แทน |

## โครง project

```
src/bot_fx/
  cli.py         # จุดเริ่ม `bot-fx`: ร้อยทุกขั้นเข้าด้วยกัน
  config.py      # อ่าน BOT_API_KEY และ BOT_DB_PATH
  fetch.py       # เรียก API เป็น 2 ช่วง ช่วงละไม่เกิน 31 วัน
  transform.py   # กรองแถวว่าง แปลงเป็นตัวเลข เลือก 20 วันทำการล่าสุด
  store.py       # upsert ลง SQLite
tests/           # pytest + response จริงใน fixtures/
docs/            # โจทย์ ข้อสังเกต และ OpenAPI spec ของ ธปท.
```

## เอกสารอื่น

- [manual.html](manual.html): คู่มือการใช้งานแบบทีละขั้น พร้อมคำสั่ง SQL และวิธีส่งออกเป็น CSV (ดาวน์โหลดแล้วเปิดในเบราว์เซอร์ ใช้ได้แบบออฟไลน์)
- [NOTES.md](NOTES.md): เข้าใจโจทย์ว่าอย่างไร จุดที่ไม่ชัดและการตัดสินใจ และ workflow โดยสรุป
- [CLAUDE.md](CLAUDE.md): คำสั่งสำหรับ AI agent ที่ใช้พัฒนา repo นี้
- [observations.html](observations.html): ข้อสังเกตระหว่างศึกษาโจทย์ เอกสาร API และผลการทดลองยิง API จริง (ฉบับข้อความ: [docs/observations.md](docs/observations.md))
