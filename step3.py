"""
Declaris ERP - Data Export Utility (step3.py)
Ma'lumotlarni eksport qilish: python step3.py
"""
import json
from datetime import datetime
from database import SessionLocal
import models

def export_to_json():
    """Barcha ma'lumotlarni JSON ga eksport qilish"""
    db = SessionLocal()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"declaris_backup_{timestamp}.json"
    
    try:
        print("📦 Ma'lumotlar eksport qilinmoqda...")
        
        data = {
            "export_date": datetime.now().isoformat(),
            "companies": [],
            "users": [],
            "tax_payments": [],
            "transactions": [],
            "customs": [],
            "counterparties": [],
            "risk_alerts": [],
            "calculations": []
        }
        
        # Kompaniyalar
        companies = db.query(models.Company).all()
        for c in companies:
            data["companies"].append({
                "id": c.id, "name": c.name, "inn": c.inn,
                "address": c.address, "bank_account": c.bank_account,
                "mfo": c.mfo, "bank_name": c.bank_name,
                "created_at": str(c.created_at)
            })
        
        # Foydalanuvchilar (parolsiz!)
        users = db.query(models.User).all()
        for u in users:
            data["users"].append({
                "id": u.id, "username": u.username, "phone": u.phone,
                "full_name": u.full_name, "role": u.role.value,
                "company_id": u.company_id, "is_active": u.is_active
            })
        
        # Soliq to'lovlari
        payments = db.query(models.TaxPayment).all()
        for p in payments:
            data["tax_payments"].append({
                "id": p.id, "company_id": p.company_id,
                "tax_code": p.tax_code, "amount": p.amount,
                "period": p.period, "status": p.status,
                "payment_purpose": p.payment_purpose,
                "created_at": str(p.created_at)
            })
        
        # Operatsiyalar
        transactions = db.query(models.Transaction).all()
        for t in transactions:
            data["transactions"].append({
                "id": t.id, "type": t.type.value, "currency": t.currency,
                "amount": t.amount, "rate": t.rate, "uzs_amount": t.uzs_amount,
                "counterparty": t.counterparty, "description": t.description,
                "date": str(t.date)
            })
        
        # Bojxona
        customs = db.query(models.CustomsDeclaration).all()
        for c in customs:
            data["customs"].append({
                "id": c.id, "declaration_number": c.declaration_number,
                "regime": c.regime, "goods_description": c.goods_description,
                "amount_usd": c.amount_usd, "entry_date": str(c.entry_date),
                "expiry_date": str(c.expiry_date), "status": c.status
            })
        
        # JSON ga yozish
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Eksport tayyor: {filename}")
        print(f"   📊 Kompaniyalar: {len(data['companies'])}")
        print(f"   👤 Foydalanuvchilar: {len(data['users'])}")
        print(f"   💰 Soliq to'lovlari: {len(data['tax_payments'])}")
        print(f"   🌍 Operatsiyalar: {len(data['transactions'])}")
        print(f"   📦 Bojxona: {len(data['customs'])}")
        
    except Exception as e:
        print(f"❌ Xatolik: {e}")
    finally:
        db.close()

def show_statistics():
    """Bazadagi umumiy statistika"""
    db = SessionLocal()
    
    try:
        print("\n" + "=" * 40)
        print("📊 DECLARIS ERP - Umumiy Statistika")
        print("=" * 40)
        
        stats = {
            "Kompaniyalar": db.query(models.Company).count(),
            "Foydalanuvchilar": db.query(models.User).count(),
            "Soliq kodlari": db.query(models.TaxCode).count(),
            "Soliq to'lovlari": db.query(models.TaxPayment).count(),
            "Valyuta operatsiyalari": db.query(models.Transaction).count(),
            "Kontragentlar": db.query(models.Counterparty).count(),
            "Risk ogohlantirishlari": db.query(models.RiskAlert).count(),
            "Bojxona deklaratsiyalari": db.query(models.CustomsDeclaration).count(),
            "Import kalkulyatsiyalari": db.query(models.ImportCalculation).count(),
        }
        
        for key, value in stats.items():
            print(f"   {key:25} {value:>5} ta")
        
        print("=" * 40)
        
    except Exception as e:
        print(f"❌ Xatolik: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "export":
            export_to_json()
        elif sys.argv[1] == "stats":
            show_statistics()
        else:
            print("Foydalanish:")
            print("   python step3.py export   - JSON ga eksport")
            print("   python step3.py stats    - Statistikani ko'rish")
    else:
        # Default: ikkisini ham bajarish
        show_statistics()
        print()
        export_to_json()