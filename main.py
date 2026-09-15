"""Declaris ERP - Main Application"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
import schemas
import auth
from datetime import datetime

# ===================== CREATE TABLES =====================
Base.metadata.create_all(bind=engine)

# ===================== APP INIT =====================
app = FastAPI(
    title="Declaris ERP",
    description="O'zbekiston Soliq, TIF va Risk Analitika Platformasi",
    version="1.0.0"
)

# ===================== CORS =====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da aniq domainni ko'rsating
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== AUTH ENDPOINTS =====================
@app.post("/auth/register", response_model=schemas.TokenResponse)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Ro'yxatdan o'tish"""
    # Mavjud foydalanuvchini tekshirish
    db_user = db.query(models.User).filter(models.User.phone == user_data.phone).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Bu telefon raqam allaqachon ro'yxatdan o'tgan")
    
    # Parolni xeshlovchi xavfsiz funksiya
    hashed_pw = auth.get_password_hash(user_data.password)
    
    # User obyektini xatosiz yaratish
    new_user = models.User(
        username=user_data.phone,  # username bo'sh qolmasligi uchun phone beriladi
        phone=user_data.phone,
        full_name=user_data.full_name or "Foydalanuvchi",
        hashed_password=hashed_pw,
        role="ACCOUNTANT",
        company_id=None
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Baza xatoligi: {str(e)}")
    
    token = auth.create_access_token(data={"sub": str(new_user.id)})
    return {
        "token": token,
        "message": f"Xush kelibsiz, {new_user.full_name}!"
    }
# ===================== COMPANY ENDPOINTS =====================

@app.get("/companies", response_model=list[schemas.CompanyResponse])
def get_companies(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Barcha kompaniyalar"""
    return db.query(models.Company).all()


@app.post("/companies", response_model=schemas.CompanyResponse)
def create_company(
    company: schemas.CompanyCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Yangi kompaniya qo'shish"""
    db_company = db.query(models.Company).filter(models.Company.inn == company.inn).first()
    if db_company:
        raise HTTPException(status_code=400, detail="Bu INN bilan kompaniya allaqachon mavjud")
    
    db_company = models.Company(**company.model_dump())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


# ===================== TAX ENDPOINTS =====================

@app.get("/tax/codes", response_model=list[schemas.TaxCodeResponse])
def get_tax_codes(db: Session = Depends(get_db)):
    """Soliq kodlari ro'yxati"""
    codes = db.query(models.TaxCode).all()
    
    # Agar bo'sh bo'lsa, default kodlarni yaratish
    if not codes:
        default_codes = [
            models.TaxCode(code="101", name="JSHDS", name_uz="JSHDS", treasury_account="23402000300100001010", rate="4% / 5%", description="Yagona soliq"),
            models.TaxCode(code="102", name="Foyda Soliqi", name_uz="Foyda solig'i", treasury_account="23402000300100002010", rate="15%", description="Korxona foydasi solig'i"),
            models.TaxCode(code="103", name="QQS", name_uz="QQS 12%", treasury_account="23402000300100003010", rate="12%", description="Qo'shilgan qiymat solig'i"),
            models.TaxCode(code="104", name="Aylanma Soliq", name_uz="Aylanma soliq", treasury_account="23402000300100004010", rate="4% / 25%", description="Aylanma soliq"),
            models.TaxCode(code="105", name="Bojxona Yig'imlari", name_uz="Bojxona yig'imlari", treasury_account="23402000300100005010", rate="O'zgaruvchan", description="Bojxona yig'imlari"),
        ]
        for code in default_codes:
            db.add(code)
        db.commit()
        codes = db.query(models.TaxCode).all()
    
    return codes


@app.post("/tax/payments", response_model=schemas.TaxPaymentResponse)
def create_tax_payment(
    payment: schemas.TaxPaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Soliq to'lovini saqlash"""
    tax_code = db.query(models.TaxCode).filter(models.TaxCode.code == payment.tax_code).first()
    if not tax_code:
        raise HTTPException(status_code=404, detail="Soliq kodi topilmadi")
    
    purpose = f"Soliq to'lovi: {tax_code.name_uz} bo'yicha {payment.period} davri uchun. INN: {payment.company_inn or 'N/A'}. KOD: {tax_code.code}. Summa: {payment.amount:,.0f} so'm."
    
    db_payment = models.TaxPayment(
        company_id=current_user.company_id,
        tax_code_id=tax_code.id,
        amount=payment.amount,
        period=payment.period,
        payment_purpose=purpose,
        status="pending"
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


@app.get("/tax/payments", response_model=list[schemas.TaxPaymentResponse])
def get_tax_payments(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Soliq to'lovlari tarixi"""
    return db.query(models.TaxPayment).filter(
        models.TaxPayment.company_id == current_user.company_id
    ).all()


@app.post("/tax/generate-payment", response_model=schemas.PaymentGenerateResponse)
def generate_payment(req: schemas.PaymentGenerateRequest, db: Session = Depends(get_db)):
    """Avtomatik to'lov maqsadi generatsiyasi"""
    tax_code = db.query(models.TaxCode).filter(models.TaxCode.code == req.tax_code).first()
    if not tax_code:
        raise HTTPException(status_code=404, detail="Soliq kodi topilmadi")
    
    purpose = f"Soliq to'lovi: {tax_code.name_uz} bo'yicha {req.period} davri uchun. INN: {req.inn}. KOD: {tax_code.code}. Summa: {req.amount:,.0f} so'm. Majburiyatni bajarish maqsadida."
    
    return schemas.PaymentGenerateResponse(
        payment_purpose=purpose,
        treasury_account=tax_code.treasury_account,
        tax_name=tax_code.name_uz,
        amount=req.amount
    )


# ===================== TRANSACTIONS (IMPORT/EXPORT) =====================

@app.post("/transactions", response_model=schemas.TransactionResponse)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Yangi valyuta operatsiyasi"""
    uzs_amount = transaction.amount * transaction.rate
    
    db_transaction = models.Transaction(
        company_id=current_user.company_id,
        type=transaction.type,
        currency=transaction.currency,
        amount=transaction.amount,
        rate=transaction.rate,
        uzs_amount=uzs_amount,
        mfo=transaction.mfo,
        account=transaction.account,
        counterparty=transaction.counterparty,
        counterparty_inn=transaction.counterparty_inn,
        description=transaction.description,
        date=datetime.utcnow(),
        status="completed"
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@app.get("/transactions", response_model=list[schemas.TransactionResponse])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Barcha operatsiyalar"""
    return db.query(models.Transaction).filter(
        models.Transaction.company_id == current_user.company_id
    ).order_by(models.Transaction.date.desc()).all()


@app.get("/transactions/summary", response_model=schemas.TransactionSummary)
def get_transaction_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Operatsiyalar xulosasi"""
    transactions = db.query(models.Transaction).filter(
        models.Transaction.company_id == current_user.company_id
    ).all()
    
    imports = [t for t in transactions if t.type == models.TransactionType.IMPORT]
    exports = [t for t in transactions if t.type == models.TransactionType.EXPORT]
    
    return schemas.TransactionSummary(
        total_import_usd=sum(t.amount for t in imports if t.currency == "USD"),
        total_export_usd=sum(t.amount for t in exports if t.currency == "USD"),
        total_import_uzs=sum(t.uzs_amount for t in imports),
        total_export_uzs=sum(t.uzs_amount for t in exports),
        import_count=len(imports),
        export_count=len(exports)
    )


# ===================== CUSTOMS DECLARATIONS =====================

@app.post("/customs", response_model=schemas.CustomsResponse)
def create_customs(
    customs: schemas.CustomsCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Yangi bojxona deklaratsiyasi"""
    from datetime import datetime as dt
    
    entry_date = dt.strptime(customs.entry_date, "%Y-%m-%d")
    expiry_date = dt.strptime(customs.expiry_date, "%Y-%m-%d")
    days_remaining = max(0, (expiry_date - dt.utcnow()).days)
    
    db_customs = models.CustomsDeclaration(
        company_id=current_user.company_id,
        declaration_number=customs.declaration_number,
        regime=customs.regime,
        goods_description=customs.goods_description,
        amount_usd=customs.amount_usd,
        currency=customs.currency,
        entry_date=entry_date,
        expiry_date=expiry_date,
        days_remaining=days_remaining,
        status="active"
    )
    db.add(db_customs)
    db.commit()
    db.refresh(db_customs)
    return db_customs


@app.get("/customs", response_model=list[schemas.CustomsResponse])
def get_customs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Barcha deklaratsiyalar"""
    customs = db.query(models.CustomsDeclaration).filter(
        models.CustomsDeclaration.company_id == current_user.company_id
    ).all()
    
    for c in customs:
        c.days_remaining = max(0, (c.expiry_date - datetime.utcnow()).days)
        if c.days_remaining == 0 and c.status == "active":
            c.status = "expired"
    
    db.commit()
    return customs


# ===================== IMPORT CALCULATOR HISTORY =====================

@app.post("/calculations", response_model=schemas.ImportCalcResponse)
def save_calculation(
    calc: schemas.ImportCalcCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Import kalkulyator tarixini saqlash"""
    total_cost = (calc.invoice_usd * calc.usd_rate) + calc.duty + calc.fee + calc.transport
    unit_cost = total_cost / calc.qty if calc.qty > 0 else 0
    
    db_calc = models.ImportCalculation(
        company_id=current_user.company_id,
        item_name=calc.item_name,
        invoice_usd=calc.invoice_usd,
        usd_rate=calc.usd_rate,
        duty=calc.duty,
        fee=calc.fee,
        transport=calc.transport,
        qty=calc.qty,
        total_cost=total_cost,
        unit_cost=unit_cost
    )
    db.add(db_calc)
    db.commit()
    db.refresh(db_calc)
    return db_calc


@app.get("/calculations", response_model=list[schemas.ImportCalcResponse])
def get_calculations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Kalkulyator tarixi"""
    return db.query(models.ImportCalculation).filter(
        models.ImportCalculation.company_id == current_user.company_id
    ).order_by(models.ImportCalculation.created_at.desc()).all()


# ===================== RISK ANALYTICS =====================

@app.get("/risks/alerts", response_model=list[schemas.RiskAlertResponse])
def get_risk_alerts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Aktiv ogohlantirishlar"""
    return db.query(models.RiskAlert).filter(
        models.RiskAlert.company_id == current_user.company_id,
        models.RiskAlert.resolved == False
    ).order_by(models.RiskAlert.created_at.desc()).all()


@app.get("/risks/gap-analysis", response_model=list[schemas.GapAnalysisItem])
def gap_analysis(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """QQS Gap-Analiz"""
    counterparties = db.query(models.Counterparty).filter(
        models.Counterparty.company_id == current_user.company_id
    ).all()
    
    result = []
    for cp in counterparties:
        if cp.qqs_input > 0:
            cp.gap_percent = abs(((cp.qqs_input - cp.qqs_output) / cp.qqs_input) * 100)
            cp.risk_score = min(100, cp.gap_percent * 3)
        
        severity = "low"
        if cp.gap_percent > 20: severity = "high"
        elif cp.gap_percent > 10: severity = "medium"
        
        result.append(schemas.GapAnalysisItem(
            counterparty=cp.name,
            inn=cp.inn,
            gap_percent=round(cp.gap_percent, 1),
            severity=severity
        ))
    
    db.commit()
    return sorted(result, key=lambda x: x.gap_percent, reverse=True)


@app.get("/risks/summary", response_model=schemas.RiskSummary)
def risk_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Risk xulosasi"""
    alerts = db.query(models.RiskAlert).filter(
        models.RiskAlert.company_id == current_user.company_id,
        models.RiskAlert.resolved == False
    ).all()
    
    qqs_alerts = [a for a in alerts if a.type in [models.RiskType.QQS_BREAK, models.RiskType.TAX_GAP]]
    currency_alerts = [a for a in alerts if a.type == models.RiskType.CURRENCY_DELAY]
    customs_alerts = [a for a in alerts if a.type == models.RiskType.CUSTOMS_EXPIRY]
    
    def calc_risk(alert_list):
        if not alert_list: return 0.0
        severity_scores = {"low": 25, "medium": 50, "high": 100}
        total = sum(severity_scores.get(a.severity.value, 50) for a in alert_list)
        return min(100, total / max(len(alert_list), 1))
    
    overall = (calc_risk(qqs_alerts) * 0.4 + calc_risk(currency_alerts) * 0.35 + calc_risk(customs_alerts) * 0.25)
    
    return schemas.RiskSummary(
        overall_risk=round(overall, 1),
        qqs_risk=round(calc_risk(qqs_alerts), 1),
        currency_risk=round(calc_risk(currency_alerts), 1),
        customs_risk=round(calc_risk(customs_alerts), 1)
    )


# ===================== DASHBOARD =====================

@app.get("/analytics/dashboard", response_model=schemas.DashboardData)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Dashboard ma'lumotlari"""
    company_id = current_user.company_id
    
    # Tax stats
    tax_payments = db.query(models.TaxPayment).filter(
        models.TaxPayment.company_id == company_id
    ).all()
    total_tax = sum(p.amount for p in tax_payments if p.status != "cancelled")
    
    # Transaction stats
    transactions = db.query(models.Transaction).filter(
        models.Transaction.company_id == company_id
    ).all()
    total_import = sum(t.uzs_amount for t in transactions if t.type == models.TransactionType.IMPORT)
    total_export = sum(t.uzs_amount for t in transactions if t.type == models.TransactionType.EXPORT)
    
    # Risk alerts
    alerts = db.query(models.RiskAlert).filter(
        models.RiskAlert.company_id == company_id,
        models.RiskAlert.resolved == False
    ).all()
    
    severity_scores = {"low": 25, "medium": 50, "high": 100}
    if alerts:
        risk_index = sum(severity_scores.get(a.severity.value, 50) for a in alerts) / len(alerts)
        risk_index = min(100, risk_index)
    else:
        risk_index = 0.0
    
    # Calculations count
    calc_count = db.query(models.ImportCalculation).filter(
        models.ImportCalculation.company_id == company_id
    ).count()
    
    # Customs
    customs = db.query(models.CustomsDeclaration).filter(
        models.CustomsDeclaration.company_id == company_id,
        models.CustomsDeclaration.status == "active"
    ).all()
    
    for c in customs:
        c.days_remaining = max(0, (c.expiry_date - datetime.utcnow()).days)
    
    urgent_customs = len([c for c in customs if c.days_remaining <= 7])
    
    return schemas.DashboardData(
        stats=schemas.DashboardStats(
            total_tax_liability=total_tax,
            total_import=total_import,
            total_export=total_export,
            risk_index=round(risk_index, 1),
            pending_alerts=len(alerts),
            active_customs=len(customs),
            import_calculations=calc_count,
            urgent_deadlines=urgent_customs
        ),
        gap_analysis=[],  # Will be populated separately
        recent_transactions=[],  # Will be populated separately
        risk_alerts=[],  # Will be populated separately
        customs_deadlines=[],  # Will be populated separately
        upcoming_deadlines=[],
        recent_calculations=[]
    )


# ===================== ROOT & HEALTH =====================

@app.get("/")
def root():
    return {
        "message": "Declaris ERP API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# ===================== RUN =====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
