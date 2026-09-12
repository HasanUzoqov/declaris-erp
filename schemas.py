from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Auth Schemas
class UserCreate(BaseModel):
    phone: str
    password: str
    full_name: Optional[str] = None
    company_id: Optional[int] = None

class UserLogin(BaseModel):
    phone: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    company_id: Optional[int] = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    token: str
    message: str

# Company Schemas
class CompanyCreate(BaseModel):
    name: str
    inn: str
    tax_id: Optional[str] = None

class CompanyResponse(BaseModel):
    id: int
    name: str
    inn: Optional[str] = None
    tax_id: Optional[str] = None

    class Config:
        from_attributes = True

# Tax Schemas
class TaxCodeResponse(BaseModel):
    id: int
    code: str
    name: str
    name_uz: str
    treasury_account: str
    rate: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class TaxPaymentCreate(BaseModel):
    tax_code: str
    amount: float
    period: str
    company_inn: Optional[str] = None

class TaxPaymentResponse(BaseModel):
    id: int
    amount: float
    period: str
    payment_purpose: str
    status: str

    class Config:
        from_attributes = True

class PaymentGenerateRequest(BaseModel):
    tax_code: str
    inn: str
    amount: float
    period: str

class PaymentGenerateResponse(BaseModel):
    payment_purpose: str
    treasury_account: str
    tax_name: str
    amount: float

# Transaction Schemas
class TransactionCreate(BaseModel):
    type: str
    currency: str
    amount: float
    rate: float
    mfo: Optional[str] = None
    account: Optional[str] = None
    counterparty: Optional[str] = None
    counterparty_inn: Optional[str] = None
    description: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    type: str
    currency: str
    amount: float
    rate: float
    uzs_amount: float
    status: str

    class Config:
        from_attributes = True

class TransactionSummary(BaseModel):
    total_import_usd: float
    total_export_usd: float
    total_import_uzs: float
    total_export_uzs: float
    import_count: int
    export_count: int

# Customs Schemas
class CustomsCreate(BaseModel):
    declaration_number: str
    regime: str
    goods_description: str
    amount_usd: float
    currency: str
    entry_date: str
    expiry_date: str

class CustomsResponse(BaseModel):
    id: int
    declaration_number: str
    regime: str
    goods_description: str
    amount_usd: float
    days_remaining: int
    status: str

    class Config:
        from_attributes = True

# Import Calculator History
class ImportCalcCreate(BaseModel):
    item_name: str
    invoice_usd: float
    usd_rate: float
    duty: float
    fee: float
    transport: float
    qty: float

class ImportCalcResponse(BaseModel):
    id: int
    item_name: str
    total_cost: float
    unit_cost: float

    class Config:
        from_attributes = True

# Risk Analytics
class RiskAlertResponse(BaseModel):
    id: int
    title: str
    description: str
    severity: str
    resolved: bool

    class Config:
        from_attributes = True

class GapAnalysisItem(BaseModel):
    counterparty: str
    inn: str
    gap_percent: float
    severity: str

class RiskSummary(BaseModel):
    overall_risk: float
    qqs_risk: float
    currency_risk: float
    customs_risk: float

# Dashboard
class DashboardStats(BaseModel):
    total_tax_liability: float
    total_import: float
    total_export: float
    risk_index: float
    pending_alerts: int
    active_customs: int
    import_calculations: int
    urgent_deadlines: int

class DashboardData(BaseModel):
    stats: DashboardStats
    gap_analysis: List[GapAnalysisItem] = []
    recent_transactions: List[TransactionResponse] = []
    risk_alerts: List[RiskAlertResponse] = []
    customs_deadlines: List[CustomsResponse] = []
    upcoming_deadlines: List[str] = []
    recent_calculations: List[ImportCalcResponse] = []
