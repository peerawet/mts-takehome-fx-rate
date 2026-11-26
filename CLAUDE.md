# CLAUDE.md

คำสั่งสำหรับ AI agent ที่ทำงานใน repo นี้ อ่านให้จบก่อนแก้โค้ด

## งานนี้คืออะไร

สคริปต์ Python ที่ดึงเรต **Weighted-average Interbank Exchange Rate – THB/USD** รายวันจาก API ของธนาคารแห่งประเทศไทย (ธปท.) ย้อนหลัง 20 วันทำการ แล้วบันทึกลง SQLite รันด้วย `uv`

ข้อกำหนดเต็มอยู่ที่ `docs/brief.md` ข้อเท็จจริงเรื่อง API ที่ยืนยันด้วยการยิงจริงอยู่ที่ `docs/observations.md` (ข้อ 17–20 สำคัญที่สุด) และ spec อยู่ที่ `docs/api-specs/`
**เมื่อ spec กับ `docs/observations.md` ขัดกัน ให้เชื่อ `docs/observations.md`** เพราะ spec ของ ธปท. มีจุดผิด

## คำสั่ง

```bash
uv sync                 # ติดตั้ง dependency
uv run bot-fx           # ดึงข้อมูลแล้วบันทึกลง SQLite
uv run pytest           # รัน test (ห้ามยิง API จริงใน test)
```

## API ที่ใช้ (ห้ามใช้ตัวอื่น)

```
GET https://gateway.api.bot.or.th/Stat-ReferenceRate/v2/DAILY_REF_RATE/
    ?start_period=YYYY-MM-DD&end_period=YYYY-MM-DD
Authorization: <BOT_API_KEY>
```

- header คือ `Authorization: <token>` **ไม่มี** `Bearer` และ **ไม่ใช่** `X-IBM-Client-Id` (ระบบเก่า ตัวอย่างบนเน็ตส่วนใหญ่ยังใช้ตัวนี้)
- **ห้ามใช้** `Stat-ExchangeRate` / `DAILY_AVG_EXG_RATE` ถึง key เดียวกันจะใช้ได้ `mid_rate` ของ API นั้นใกล้เรตที่ต้องการแต่ไม่ใช่ตัวเดียวกัน (ต่างกันได้ถึง 0.03 บาท)
- ข้อมูลที่ใช้มีแค่ `result.data.data_detail` (array ของ `{"period": "YYYY-MM-DD", "rate": "34.0140000"}`)
- **ห้ามใช้** `data_header` และ `result.api` ระบุว่าข้อมูลมาจากไหน ชื่อในฟิลด์เหล่านี้สลับกับ API อีกตัวในของจริง

## พฤติกรรมของ API ที่ต้องรองรับ (spec ไม่ได้บอก)

| เรื่อง | พฤติกรรมจริง | สิ่งที่โค้ดต้องทำ |
|---|---|---|
| ช่วงวันที่ต่อครั้ง | `end - start` เกิน 31 วันได้ 400 `Exceed limit period` | แบ่งยิงเป็นช่วง ช่วงละไม่เกิน 31 วัน |
| วันที่ไม่มีข้อมูล | เสาร์อาทิตย์ วันหยุด และวันในอนาคต ได้ 200 กับ `[{"period": "", "rate": ""}]` | กรองแถวที่ `period` หรือ `rate` ว่างทิ้ง **ก่อน** แปลงชนิด |
| ลำดับข้อมูล | ใหม่ไปเก่า | sort เองตาม `period` อย่าพึ่งลำดับจาก API |
| ชนิดของ `rate` | string ทศนิยม 7 ตำแหน่ง | แปลงเป็น `float` หลังกรองแถวว่าง |
| เวลาประกาศ | ทุกวันทำการ 18:00 น. เวลาไทย | `end_period` = วันนี้ (เวลาไทย) ได้เสมอ วันในอนาคตไม่ error |
| Error body | 401/403 เป็น `{"error"}`, 400 เป็น `{"httpCode", "moreInformation": [{"message"}]}`, 404 เป็น `{"Message"}` | ตัดสินจาก **status code** แล้วแนบ body ไว้ใน log อย่า parse body หาสาเหตุ |
| Rate limit | 200 ครั้ง/ชั่วโมง header `X-RateLimit-Remaining` เป็น 0 แม้ยิงผ่าน | **ห้าม** อ่าน header `X-RateLimit-*` |

ข้อความ error ที่ต้องแยกให้คนอ่านเข้าใจ: 401 = ไม่ได้ตั้ง `BOT_API_KEY`, 403 = key ใช้ไม่ได้หรือยังไม่ได้รับอนุมัติ

## Flow ที่ต้องเป็น

1. อ่าน `BOT_API_KEY` จาก environment (โหลด `.env` อัตโนมัติถ้ามี) ถ้าไม่มี ให้หยุดพร้อมข้อความที่บอกวิธีตั้งค่า
2. คำนวณวันนี้ตามเวลาไทย (UTC+07:00 คงที่ ไทยไม่มี daylight saving จึงไม่ต้องใช้ `zoneinfo` ซึ่งบน Windows ต้องลง `tzdata` เพิ่ม)
3. ยิง **2 ช่วงต่อกัน** แต่ละช่วงไม่เกิน 31 วัน (รวมราว 60 วัน) เผื่อช่วงที่มีวันหยุดยาว
4. รวมผล → กรองแถวว่าง → ตัดแถวซ้ำ → sort ตาม `period` → เอา **20 แถวล่าสุด**
5. ถ้าได้ไม่ถึง 20 แถว ให้ log warning แล้วบันทึกเท่าที่ได้ ห้ามปล่อยผ่านเงียบๆ
6. upsert ลง SQLite แล้ว log สรุป (จำนวนแถว ช่วงวันที่ path ของไฟล์)

ยิง API แค่ 2 ครั้งต่อการรันหนึ่งรอบ timeout 30 วินาที ไม่ต้อง retry

## SQLite

- path default: `.venv/bot_api_daily_peerawet.db` ตามที่โจทย์กำหนด เปลี่ยนได้ด้วย env `BOT_DB_PATH` (สร้างโฟลเดอร์แม่ให้ถ้ายังไม่มี)
- โจทย์ใช้คำว่า "append" แต่ **ห้าม INSERT ตรงๆ** รันสองรอบจะได้แถวซ้ำ ต้องเป็น upsert ที่ทำให้รันกี่รอบผลก็เหมือนเดิม (idempotent)

```sql
CREATE TABLE IF NOT EXISTS rates (
    period      TEXT PRIMARY KEY,   -- 'YYYY-MM-DD'
    rate        REAL NOT NULL,      -- บาทต่อ 1 USD
    fetched_at  TEXT NOT NULL       -- ISO 8601 เวลาไทย เช่น 2026-11-26T21:20:23+07:00
);

INSERT INTO rates (period, rate, fetched_at) VALUES (?, ?, ?)
ON CONFLICT(period) DO UPDATE SET rate = excluded.rate, fetched_at = excluded.fetched_at;
```

ไม่ต้องเพิ่มคอลัมน์หรือตารางอื่น (เช่น `currency_pair`, `source`, log การรัน) เกินขอบเขตโจทย์

## โครง project

```
src/bot_fx/            # โค้ด แยก fetch / transform / store ให้ test แยกกันได้
tests/                 # pytest
tests/fixtures/        # response จริงที่บันทึกไว้ ใช้แทนการยิง API
docs/                  # โจทย์ ข้อสังเกต และ spec (อ้างอิงเท่านั้น ไม่ต้องแก้)
observations.html      # หน้าสรุปข้อสังเกต (ไม่ใช่คู่มือการใช้งานที่โจทย์ขอ)
```

- Python 3.12 dependency ให้น้อยที่สุด: `httpx` สำหรับ HTTP, `python-dotenv` สำหรับ `.env`, `pytest` เป็น dev dependency
- `sqlite3`, `datetime`, `logging` ใช้ของ standard library
- ประกาศ entry point `bot-fx` ใน `pyproject.toml`

## Test ที่ต้องมี

- response ปกติ: ได้แถวครบ ชนิดถูก เรียงถูก
- response ที่มีแถวว่าง `{"period": "", "rate": ""}`: ถูกกรองทิ้ง ไม่ error
- รวมสองช่วงที่มีวันซ้ำกัน: ไม่มีแถวซ้ำ
- ได้ไม่ถึง 20 แถว: มี warning
- upsert สองรอบด้วยข้อมูลเดียวกัน: จำนวนแถวเท่าเดิม
- status 400/401/403: ได้ error ที่อ่านเข้าใจ

ใช้ fixture จาก response จริง (ดูตัวอย่างใน `docs/observations.md` และ `observations.html` ส่วนที่ 3) ห้ามยิง API จริงใน test

## ห้ามทำ

- ห้าม commit `.env`, API key หรือไฟล์ `.db` และห้ามพิมพ์ key ลง log หรือ error message
- ห้ามเพิ่มของที่โจทย์ไม่ได้ขอ เช่น dashboard, scheduler, Docker, CLI option ที่ไม่จำเป็น
- ห้ามแก้ไฟล์ใน `docs/` ยกเว้นถูกสั่ง
- ถ้าพฤติกรรมของ API ที่เจอไม่ตรงกับไฟล์นี้ ให้หยุดแล้วรายงาน อย่าเดาแล้วแก้โค้ดให้ผ่าน

## ถือว่าเสร็จเมื่อ

- `uv sync` แล้ว `uv run bot-fx` ใน clone ใหม่ (มี `.env`) ได้ไฟล์ `.db` ที่มี 20 แถว
- รัน `uv run bot-fx` ซ้ำ จำนวนแถวยังเป็น 20 ถ้าไม่มีวันทำการใหม่
- `uv run pytest` ผ่านทั้งหมดโดยไม่ต่อเน็ต
