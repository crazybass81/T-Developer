"""Domain Knowledge Database Setup - Day 33
Initialize domain-specific knowledge base for agent generation"""
import json
import sqlite3
from datetime import datetime


def setup_database():
    conn = sqlite3.connect("domain_knowledge.db")
    cursor = conn.cursor()

    # Create tables
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS domains (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS patterns (
        id INTEGER PRIMARY KEY,
        domain_id INTEGER,
        pattern_name TEXT,
        pattern_code TEXT,
        use_case TEXT,
        FOREIGN KEY (domain_id) REFERENCES domains(id)
    )"""
    )

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS requirements (
        id INTEGER PRIMARY KEY,
        domain_id INTEGER,
        requirement_type TEXT,
        requirement_data TEXT,
        FOREIGN KEY (domain_id) REFERENCES domains(id)
    )"""
    )

    # Insert domains
    domains = [
        ("finance", "Financial services and trading systems"),
        ("healthcare", "Medical and health management systems"),
        ("ecommerce", "Online retail and marketplace systems"),
    ]
    cursor.executemany("INSERT OR IGNORE INTO domains (name, description) VALUES (?, ?)", domains)

    # Insert finance patterns
    cursor.execute('SELECT id FROM domains WHERE name = "finance"')
    finance_id = cursor.fetchone()[0]

    finance_patterns = [
        (
            finance_id,
            "TransactionValidator",
            "validate_transaction(amount, account)",
            "Transaction validation",
        ),
        (finance_id, "RiskCalculator", "calculate_risk(portfolio)", "Risk assessment"),
        (finance_id, "ComplianceChecker", "check_compliance(transaction)", "Regulatory compliance"),
    ]
    cursor.executemany("INSERT INTO patterns VALUES (NULL, ?, ?, ?, ?)", finance_patterns)

    # Insert healthcare patterns
    cursor.execute('SELECT id FROM domains WHERE name = "healthcare"')
    healthcare_id = cursor.fetchone()[0]

    healthcare_patterns = [
        (
            healthcare_id,
            "PatientRecordManager",
            "manage_patient_record(patient_id)",
            "Patient data management",
        ),
        (healthcare_id, "PrivacyValidator", "validate_hipaa_compliance(data)", "HIPAA compliance"),
        (healthcare_id, "DiagnosisAssistant", "suggest_diagnosis(symptoms)", "Diagnosis support"),
    ]
    cursor.executemany("INSERT INTO patterns VALUES (NULL, ?, ?, ?, ?)", healthcare_patterns)

    # Insert ecommerce patterns
    cursor.execute('SELECT id FROM domains WHERE name = "ecommerce"')
    ecommerce_id = cursor.fetchone()[0]

    ecommerce_patterns = [
        (ecommerce_id, "InventoryManager", "manage_inventory(product_id)", "Stock management"),
        (ecommerce_id, "PricingEngine", "calculate_price(product, discounts)", "Dynamic pricing"),
        (
            ecommerce_id,
            "RecommendationEngine",
            "recommend_products(user_history)",
            "Product recommendations",
        ),
    ]
    cursor.executemany("INSERT INTO patterns VALUES (NULL, ?, ?, ?, ?)", ecommerce_patterns)

    # Insert requirements
    requirements = [
        (finance_id, "security", json.dumps({"encryption": "AES-256", "auth": "multi-factor"})),
        (healthcare_id, "compliance", json.dumps({"standards": ["HIPAA", "HL7"], "audit": True})),
        (
            ecommerce_id,
            "performance",
            json.dumps({"response_time": "200ms", "throughput": "1000rps"}),
        ),
    ]
    cursor.executemany("INSERT INTO requirements VALUES (NULL, ?, ?, ?)", requirements)

    conn.commit()
    conn.close()
    print(f"✅ Domain knowledge database created at {datetime.now()}")

    # Verify data
    conn = sqlite3.connect("domain_knowledge.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM domains")
    domain_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM patterns")
    pattern_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM requirements")
    req_count = cursor.fetchone()[0]
    conn.close()

    print(f"📊 Database statistics:")
    print(f"  - Domains: {domain_count}")
    print(f"  - Patterns: {pattern_count}")
    print(f"  - Requirements: {req_count}")


if __name__ == "__main__":
    setup_database()
