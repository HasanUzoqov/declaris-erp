"""
Declaris ERP - Database Seeder (step.py)
Bir marta ishga tushiring: python step.py
"""
from database import engine, SessionLocal
import models
from auth import get_password_hash
from datetime import datetime, timedelta

def init_database():
    """Barcha jadvallarni yaratish"""
    print("📦 Jadvallar yaratilmoqda...")
    models.Base.metadata.create_all(bind=engine)
    print("✅ Jadvallar tayyor!")

def seed_data():
    """Demo ma'lumotlar yuklash"""
    db = SessionLocal()
    
    try:
        # === KOMPANIYA ===
        print("🏢 Kompaniya yaratilmoqda...")
        company = models.Company(
            name="Global Trade Uzbekistan MCHJ",
            inn="123456789",
            address="Toshkent sh., Chilonzor tumani",
            bank_account="20214000900012345678",
            mfo="00444",
            bank_name="Agrobank"
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        print(f"   ✅ {company.name}")

        # === ADMIN FOYDALANUVCHI ===
        print("👤 Admin foydalanuvchi yaratilmoqda...")
        admin = models.User(
            username="admin",
            phone="+998901234567",
            full_name="Admin Foydalanuvchi",
            hashed_password=get_password_hash("admin123"),
            role=models.UserRole.ADMIN,
            company_id=company.id,
            is_active=True
        )
        db.add(admin)

        # === BUXGALTER ===
        accountant = models.User(
            username="buxgalter",
            phone="+998907654321",
            full_name="Karimova Nodira",
            hashed_password=get_password_hash("bux123"),
            role=models.UserRole.ACCOUNTANT,
            company_id=company.id,
            is_active=True
        )
        db.add(accountant)
        db.commit()
        print("   ✅ Admin va Buxgalter yaratildi")

        # === SOLIQ KODLARI ===
        print("💰 Soliq kodlari yuklanmoqda...")
        tax_codes = [
            models.TaxCode(code="101", name="JSHDS", name_uz="JSHDS", 
                          treasury_account="23402000300100001010", 
                          rate="4% / 5%", description="Yagona soliq hisoblangan daromad solig'i"),
            models.TaxCode(code="102", name="Foyda Soliqi", name_uz="Foyda solig'i", 
                          treasury_account="23402000300100002010", 
                          rate="15%", description="Korxona foydasi solig'i"),
            models.TaxCode(code="103", name="QQS", name_uz="QQS 12%", 
                          treasury_account="23402000300100003010", 
                          rate="12%", description="Qo'shilgan qiymat solig'i"),
            models.TaxCode(code="104", name="Aylanma Soliq", name_uz="Aylanma soliq", 
                          treasury_account="23402000300100004010", 
                          rate="4% / 25%", description="Aylanmadan olinadigan soliq"),
            models.TaxCode(code="105", name="Bojxona Yig'imlari", name_uz="Bojxona yig'imlari", 
                          treasury_account="23402000300100005010", 
                          rate="O'zgaruvchan", description="Bojxona bo'yicha yig'imlar"),
        ]
        for tc in tax_codes:
            db.add(tc)
        db.commit()
        print("   ✅ 5 ta soliq kodi yuklandi")

        # === SOLIQ TO'LOVLARI ===
        print("📝 Soliq to'lovlari yuklanmoqda...")
        payments = [
            models.TaxPayment(company_id=company.id, tax_code_id=1, 
                            amount=45000000, period="Iyul 2026",
                            payment_purpose="JSHDS to'lovi", status="paid", 
                            paid_at=datetime.utcnow()),
            models.TaxPayment(company_id=company.id, tax_code_id=3, 
                            amount=128400000, period="Iyul 2026",
                            payment_purpose="QQS to'lovi", status="pending"),
            models.TaxPayment(company_id=company.id, tax_code_id=2, 
                            amount=35000000, period="Iyul 2026",
                            payment_purpose="Foyda solig'i", status="pending"),
        ]
        for p in payments:
            db.add(p)
        db.commit()
        print("   ✅ 3 ta soliq to'lovi yuklandi")

        # === VALYUTA OPERATSIYALARI ===
        print("🌍 Import/Eksport operatsiyalari yuklanmoqda...")
        transactions = [
            models.Transaction(
                company_id=company.id, type=models.TransactionType.IMPORT,
                currency="USD", amount=45000, rate=12650, uzs_amount=569250000,
                counterparty="China Electronics Ltd", 
                description="Smartfon va noutbuk importi",
                date=datetime.utcnow() - timedelta(days=2)
            ),
            models.Transaction(
                company_id=company.id, type=models.TransactionType.EXPORT,
                currency="EUR", amount=12300, rate=13800, uzs_amount=169740000,
                counterparty="EuroTrade GmbH", 
                description="Tekstil mahsulotlari eksporti",
                date=datetime.utcnow() - timedelta(days=5)
            ),
            models.Transaction(
                company_id=company.id, type=models.TransactionType.CONVERT,
                currency="USD", amount=8500, rate=12620, uzs_amount=107270000,
                description="Valyuta konvertatsiyasi",
                date=datetime.utcnow() - timedelta(days=7)
            ),
            models.Transaction(
                company_id=company.id, type=models.TransactionType.EXPORT,
                currency="USD", amount=25000, rate=12600, uzs_amount=315000000,
                counterparty="Turkish Textile Co", 
                description="Kiyim-kechak eksporti",
                date=datetime.utcnow() - timedelta(days=95)  # 90+ kun - kechikish xavfi
            ),
        ]
        for t in transactions:
            db.add(t)
        db.commit()
        print("   ✅ 4 ta operatsiya yuklandi")

        # === KONTRAGENTLAR (GAP ANALIZ) ===
        print("🏭 Kontragentlar yuklanmoqda...")
        counterparties = [
            models.Counterparty(
                company_id=company.id, name="Asia Textile LLC", 
                inn="987654321", country="Xitoy",
                qqs_input=12000000, qqs_output=10512000, 
                gap_percent=12.4, risk_score=37
            ),
            models.Counterparty(
                company_id=company.id, name="Global Import LLC", 
                inn="876543210", country="Turkiya",
                qqs_input=8500000, qqs_output=7811500, 
                gap_percent=8.1, risk_score=24
            ),
            models.Counterparty(
                company_id=company.id, name="Samarqand Agro", 
                inn="765432109", country="O'zbekiston",
                qqs_input=15000000, qqs_output=11445000, 
                gap_percent=23.7, risk_score=71
            ),
        ]
        for cp in counterparties:
            db.add(cp)
        db.commit()
        print("   ✅ 3 ta kontragent yuklandi")

        # === RISK OGOHLANTIRISHLARI ===
        print("⚠️ Risk ogohlantirishlari yuklanmoqda...")
        alerts = [
            models.RiskAlert(
                company_id=company.id, type=models.RiskType.CURRENCY_DELAY,
                severity=models.RiskSeverity.HIGH,
                title="Valyuta tushumi kechikishi: Turkish Textile Co",
                description="Eksport operatsiyasi (25000 USD) bo'yicha valyuta tushumi 95 kundan beri kelmagan. Jarima xavfi!",
                related_id=4
            ),
            models.RiskAlert(
                company_id=company.id, type=models.RiskType.TAX_GAP,
                severity=models.RiskSeverity.HIGH,
                title="QQS uzilishi: Samarqand Agro",
                description="Kontragent bilan QQS uzilishi 23.7%. Soliq tekshiruvi xavfi.",
                related_id=3
            ),
            models.RiskAlert(
                company_id=company.id, type=models.RiskType.CUSTOMS_EXPIRY,
                severity=models.RiskSeverity.MEDIUM,
                title="Bojxona rejimi tugayapti: CD-2026-001",
                description="IM-70 rejimi bo'yicha elektronika tovarlari saqlash muddati 5 kundan so'ng tugaydi.",
                related_id=1
            ),
        ]
        for a in alerts:
            db.add(a)
        db.commit()
        print("   ✅ 3 ta ogohlantirish yuklandi")

        # === BOJXONA DEKLARATSIYALARI ===
        print("📦 Bojxona deklaratsiyalari yuklanmoqda...")
        customs = [
            models.CustomsDeclaration(
                company_id=company.id, declaration_number="CD-2026-001",
                regime="IM-70", goods_description="Elektronika (smartfon, noutbuk)",
                amount_usd=45000, entry_date=datetime.utcnow() - timedelta(days=85),
                expiry_date=datetime.utcnow() + timedelta(days=5),
                days_remaining=5, status="active"
            ),
            models.CustomsDeclaration(
                company_id=company.id, declaration_number="CD-2026-002",
                regime="ND-40", goods_description="Kiyim-kechak",
                amount_usd=12000, entry_date=datetime.utcnow() - timedelta(days=42),
                expiry_date=datetime.utcnow() + timedelta(days=18),
                days_remaining=18, status="active"
            ),
            models.CustomsDeclaration(
                company_id=company.id, declaration_number="CD-2026-003",
                regime="IM-70", goods_description="Avto ehtiyot qismlar",
                amount_usd=28000, entry_date=datetime.utcnow() - timedelta(days=15),
                expiry_date=datetime.utcnow() + timedelta(days=45),
                days_remaining=45, status="active"
            ),
        ]
        for c in customs:
            db.add(c)
        db.commit()
        print("   ✅ 3 ta deklaratsiya yuklandi")

        # === IMPORT KALKULYATOR TARIXI ===
        print("🧮 Kalkulyator ma'lumotlari yuklanmoqda...")
        calculations = [
            models.ImportCalculation(
                company_id=company.id, item_name="Elektron komponentlar",
                invoice_usd=10000, usd_rate=12800, duty=6400000,
                fee=400000, transport=8000000, qty=100,
                total_cost=142800000, unit_cost=1428000
            ),
        ]
        for calc in calculations:
            db.add(calc)
        db.commit()
        print("   ✅ 1 ta kalkulyatsiya yuklandi")

        print("\n🎉 Baza to'liq yuklandi!")
        print("   🔑 Login: admin / admin123")
        print("   🔑 Login: buxgalter / bux123")

    except Exception as e:
        print(f"\n❌ Xatolik: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
    seed_data()