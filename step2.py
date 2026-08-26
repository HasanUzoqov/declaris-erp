"""
Declaris ERP - API Test Script (step2.py)
Server ishga tushgach, tekshirish uchun: python step2.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, token=None):
    """Yordamchi funksiya - endpointni tekshirish"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=5)
        
        status = "✅" if response.status_code == 200 else "❌"
        print(f"   {status} {method} {endpoint} - {response.status_code}")
        return response.json() if response.status_code == 200 else None
        
    except requests.exceptions.ConnectionError:
        print(f"   ❌ {method} {endpoint} - Server bilan aloqa yo'q!")
        return None
    except Exception as e:
        print(f"   ❌ {method} {endpoint} - {str(e)}")
        return None

def main():
    print("🚀 Declaris ERP API Tekshiruvi")
    print("=" * 40)
    
    # 1. Server holati
    print("\n📡 Server holati:")
    test_endpoint("GET", "/")
    test_endpoint("GET", "/health")
    
    # 2. Login
    print("\n🔐 Login:")
    login_data = {"phone": "+998901234567", "password": "admin123"}
    result = test_endpoint("POST", "/auth/login", login_data)
    
    if not result or "token" not in result:
        print("\n❌ Login amalga oshmadi! Server ishlayotganini tekshiring.")
        return
    
    token = result["token"]
    print(f"   📝 Token olindi: {token[:20]}...")
    
    # 3. Joriy foydalanuvchi
    print("\n👤 Foydalanuvchi ma'lumotlari:")
    test_endpoint("GET", "/auth/me", token=token)
    
    # 4. Kompaniyalar
    print("\n🏢 Kompaniyalar:")
    test_endpoint("GET", "/companies", token=token)
    
    # 5. Soliq kodlari
    print("\n💰 Soliq kodlari:")
    test_endpoint("GET", "/tax/codes", token=token)
    
    # 6. Soliq to'lovlari
    print("\n📝 Soliq to'lovlari:")
    test_endpoint("GET", "/tax/payments", token=token)
    
    # 7. Valyuta operatsiyalari
    print("\n🌍 Operatsiyalar:")
    test_endpoint("GET", "/transactions", token=token)
    test_endpoint("GET", "/transactions/summary", token=token)
    
    # 8. Bojxona
    print("\n📦 Bojxona deklaratsiyalari:")
    test_endpoint("GET", "/customs", token=token)
    
    # 9. Risk analitika
    print("\n⚠️ Risk analitika:")
    test_endpoint("GET", "/risks/alerts", token=token)
    test_endpoint("GET", "/risks/gap-analysis", token=token)
    test_endpoint("GET", "/risks/summary", token=token)
    
    # 10. Dashboard
    print("\n📊 Dashboard:")
    test_endpoint("GET", "/analytics/dashboard", token=token)
    
    # 11. Kalkulyator tarixi
    print("\n🧮 Kalkulyator:")
    test_endpoint("GET", "/calculations", token=token)
    
    print("\n" + "=" * 40)
    print("✅ Tekshiruv yakunlandi!")

if __name__ == "__main__":
    main()