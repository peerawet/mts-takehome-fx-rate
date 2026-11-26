# ***Take-home Test — Data Analyst & AI Agent Engineer***

---

## ***1\. โจทย์***

*สร้าง **Python workflow** ที่ดึงข้อมูลอัตราแลกเปลี่ยนจาก Bank of Thailand API แล้วเก็บลง SQLite*

| *หัวข้อ* | *รายละเอียด* |
| ----- | ----- |
| *แหล่งข้อมูล* | *https\://portal.api.bot.or.th/portal/catalogue-products/exchange-rates-1* |
| *API* | ***Weighted-average Interbank Exchange Rate – THB / USD*** |
| *Endpoint* | *`https://gateway.api.bot.or.th/Stat-ReferenceRate/v2/DAILY_REF_RATE/`* |
| *ข้อมูลที่ต้องการ* | *update ข้อมูลย้อนหลัง **20 วัน (20 data point, daily)*** |
| *ปลายทาง* | ***append** ลง SQLite ชื่อ `bot_api_daily_{ชื่อผู้สมัคร_Eng}.db` วางไว้ใน **`.venv`** ของ project* |
| *เครื่องมือ* | *จัดการ project ด้วย **`uv`*** |
| *เอกสาร* | ***คู่มือการใช้งาน** รูปแบบ `.html`* |
| *Repo* | ***Public GitHub repository** ที่มี **`CLAUDE.md`** หรือ **`AGENTS.md`*** |

*คุณต้องสมัครบัญชีและขอ API credential จาก portal ด้วยตนเอง (ฟรี)*

---

## ***2\. สิ่งที่ต้องส่ง (4 ข้อ)***

***2.1 Link GitHub public repository** — ภายในต้องมี*

* *`CLAUDE.md` หรือ `AGENTS.md` — instruction ที่คุณใช้กับ AI agent*  
* *Python workflow (source code)*  
* *รันได้ด้วย `uv sync` / `uv run`*  
* *`README.md` — วิธีติดตั้ง / ตั้งค่า / รัน*  
* *คู่มือการใช้งาน `.html`*  
* *`NOTES.md` (≤ 1 หน้า) — 3 หัวข้อ: **(a)** คุณเข้าใจว่าโจทย์นี้ต้องการเอาไปใช้ทำอะไร **(b)** จุดที่โจทย์ไม่ชัดและคุณตัดสินใจอย่างไร เพราะอะไร **(c)** workflow ของคุณทำงานอย่างไร (อธิบายสั้น ๆ ตั้งแต่ API ถึง SQLite)*

***2.2 ไฟล์ `bot_api_daily_{ชื่อ}.db`** — แนบมากับอีเมล (ไฟล์ที่ได้จากการรันจริง)*

***2.3 ในอีเมล** — ระบุ AI tool ที่ใช้ และเวลาที่ใช้ทำโดยประมาณ (ไม่มีผลต่อคะแนน)*

***2.4 ผลทดสอบ Personality test: MBTI (Myers-Briggs Type Indicator)** \- ระบุ Type \| Ref: [https\://www\.16personalities.com/](https://www.16personalities.com/)* 

***ห้าม** commit API credential ลง repository*

---

## ***3\. กติกาการใช้ AI***

*อนุญาตให้ใช้ AI ได้ และ **copy โจทย์นี้ไปให้ AI ได้**— แต่ขอให้อ่านโจทย์และคิดเองด้วย เพราะในการสัมภาษณ์เราจะ*

* *ให้คุณ **อธิบาย code ที่ AI เขียน** (สุ่มเลือก)*  
* *ถามว่า **โจทย์นี้ต้องการอะไรจริง ๆ** และคุณสังเกตเห็นอะไรบ้าง*

***Objective**: วัดว่าคุณ **เข้าใจสิ่งที่คุณส่งมา** และ **คิดเป็นระบบ** หรือไม่*

---

*MTS Gold Group — Take-home Test v2 (2026-10)*

