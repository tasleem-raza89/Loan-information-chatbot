from flask import Flask, render_template, request, jsonify
import requests
import re

app = Flask(__name__)

LOAN_KNOWLEDGE = """
Personal Loan: A personal loan can be used for medical expenses, travel, education, emergencies, or other personal needs. Approval, interest rates, and loan amounts depend on the lender, income, credit history, and eligibility.
Home Loan: A home loan is used to purchase, construct, or renovate a house. Lenders generally evaluate income, credit history, property documents, and repayment capacity.
Education Loan: An education loan helps students pay tuition fees and eligible education-related expenses. Requirements vary by lender, course, institution, and applicant.
Business Loan: A business loan helps eligible businesses cover working capital, equipment, expansion, and other business expenses.
Car Loan: A car loan helps finance the purchase of a vehicle. Eligibility, down payment, interest rate, and tenure vary by lender and vehicle.
Eligibility: Common factors include age, income, employment or business stability, credit history, existing debts, and lender rules. Exact requirements differ between lenders.
Documents: Common documents include identity proof, address proof, PAN, bank statements, income proof, and photographs. Additional documents may be required for specific loans.
Interest Rate: Interest rates depend on the lender, loan type, credit profile, income, loan amount, and tenure. Check the lender's official website for current rates.
EMI: EMI means Equated Monthly Instalment. It includes principal and interest paid monthly.
EMI Formula: EMI = P * r * (1+r)^n / ((1+r)^n - 1), where P is principal, r is monthly interest rate as a decimal, and n is the number of monthly instalments.
Credit Score: A credit score helps lenders assess creditworthiness. A stronger credit profile may improve loan approval chances and available terms, but approval is not guaranteed.
Loan Application: Compare interest rates, processing fees, repayment terms, prepayment conditions, and the total repayment amount. Apply through a lender's official website or branch.
"""

LOAN_KEYWORDS = [
    "loan", "emi", "interest rate", "interest", "lending", "borrow",
    "borrower", "lender", "credit score", "cibil", "repayment", "mortgage",
    "personal loan", "home loan", "education loan", "student loan",
    "business loan", "car loan", "vehicle loan", "eligibility", "collateral",
    "tenure", "principal", "down payment", "bank statement", "loan amount",
    "loan application", "processing fee", "foreclosure", "prepayment",
    "credit history", "pan card", "income proof", "documents required",
    "loan approval"
]

def is_loan_related(question):
    q = question.lower()
    if any(k in q for k in LOAN_KEYWORDS):
        return True
    patterns = [r"\bwhat is emi\b", r"\bcalculate emi\b",
                r"\bhow to calculate emi\b", r"\bloan documents\b",
                r"\bloan process\b", r"\btypes of loans\b"]
    return any(re.search(pattern, q) for pattern in patterns)

def get_local_ai_response(question):
    prompt = f"""You are a helpful Loan Information Assistant.
Rules:
1. Answer ONLY questions related to loans and borrowing.
2. Use clear, simple English.
3. Explain loan types, eligibility, documents, interest rates, credit scores and EMI.
4. Never invent current interest rates or lender-specific policies.
5. If information is unavailable, tell the user to check the lender's official website.
6. Provide general information, not guaranteed financial advice.
7. If the question is unrelated to loans, politely refuse.
Loan reference information:
{LOAN_KNOWLEDGE}
User question: {question}
Answer in English:"""
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3.2", "prompt": prompt, "stream": False},
        timeout=90
    )
    response.raise_for_status()
    return response.json().get("response", "").strip()

def generate_response(question):
    if not is_loan_related(question):
        return ("I can only answer questions related to loans. Please ask me about "
                "loan types, eligibility, interest rates, documents, or EMI.")
    try:
        answer = get_local_ai_response(question)
        if answer:
            return answer
    except (requests.RequestException, ValueError, KeyError):
        pass

    q = question.lower()
    if "emi" in q or "instalment" in q or "installment" in q:
        return ("EMI stands for Equated Monthly Instalment. It is the amount paid every "
                "month toward a loan. EMI depends on the loan amount, interest rate, "
                "and tenure. Use your lender's EMI calculator for an exact estimate.")
    if "interest" in q or "rate" in q:
        return ("Loan interest rates depend on the loan type, lender, credit profile, "
                "income, and tenure. Rates can change. Check the lender's official "
                "website for current rates and applicable charges.")
    if "eligibility" in q or "eligible" in q or "qualify" in q:
        return ("Loan eligibility commonly depends on age, income, employment stability, "
                "credit history, existing debts, and lender requirements. Criteria vary.")
    if "document" in q or "paper" in q:
        return ("Common loan documents include identity proof, address proof, PAN, bank "
                "statements, and income proof. Some loans need additional documents.")
    if "personal loan" in q:
        return ("A personal loan can be used for medical expenses, travel, education, "
                "emergencies, or other personal needs. Approval and terms depend on the lender.")
    if "home loan" in q or "mortgage" in q:
        return ("A home loan helps finance the purchase, construction, or renovation of a "
                "house. Lenders commonly check income, credit history, repayment capacity, "
                "and property documents.")
    if "education loan" in q or "student loan" in q:
        return ("An education loan can help cover tuition fees and eligible education "
                "expenses. Terms depend on the lender, course, institution, and applicant.")
    if "business loan" in q:
        return ("A business loan can help fund working capital, equipment, or expansion. "
                "Eligibility and rates depend on the lender and business.")
    if "car loan" in q or "vehicle loan" in q:
        return ("A car loan helps finance a vehicle purchase. Down payment, rate, tenure, "
                "and eligibility depend on the lender and applicant.")
    if "credit score" in q or "cibil" in q:
        return ("Lenders use credit history and credit scores to assess repayment risk. "
                "A stronger profile may help, but approval is not guaranteed.")
    return ("I can help with personal, home, education, business and car loans, eligibility, "
            "interest rates, documents, credit scores, and EMI. Please ask a more specific question.")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = str(data.get("message", "")).strip()
    if not question:
        return jsonify({"error": "Please type a question first."}), 400
    if len(question) > 1000:
        return jsonify({"error": "Please keep your question under 1000 characters."}), 400
    try:
        return jsonify({"answer": generate_response(question)})
    except Exception:
        app.logger.exception("Chat response failed")
        return jsonify({"error": "Something went wrong. Please try again."}), 500

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
