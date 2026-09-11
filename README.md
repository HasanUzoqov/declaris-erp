# 🚀 Declaris ERP

**O'zbekiston Soliq, TIF va Risk Analitika Platformasi**

&gt; AI yordamchi bilan soliq, import-eksport va bojxona boshqaruvi

---

## 🎯 Imkoniyatlar

| Modul | Tavsif |
|-------|--------|
| 🔐 **Auth** | JWT + OAuth2, 3 ta rol (Admin, Buxgalter, Manager) |
| 🤖 **AI Chat** | Tabiy tilda savollarga javob |
| 🔮 **Risk Bashorat** | Valyuta kechikishini oldindan aytadi |
| 📊 **Smart Hisobot** | "Eng ko'p import qilingan valyuta qaysi?" |
| 💰 **Soliq** | JSHDS, QQS, Foyda solig'i avtomatlashtirish |
| 🌍 **Valyuta** | Import/Eksport/Convert operatsiyalari |
| 📋 **Bojxona** | IM-70, ND-40, EK-40 deklaratsiyalari |
| 🧮 **Kalkulyator** | Import narxini hisoblash |

---

## 🛠 Texnologiyalar

- **Backend:** FastAPI + SQLAlchemy + SQLite/PostgreSQL
- **AI:** OpenAI GPT-4o-mini (ixtiyoriy)
- **Frontend:** HTML/CSS/JS
- **Auth:** JWT + OAuth2 + Passlib

---

## 🚀 Ishga tushirish

```bash
pip install -r requirements.txt
python step.py
uvicorn main:app --reload
