"""Generate a realistic (fictional) employee handbook PDF for the demo.

Northwind Robotics is not a real company. The numbers are made up but specific, so
the chatbot has concrete facts to retrieve and cite. Run:

    python scripts/make_pdf.py
"""
from pathlib import Path

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

OUT = Path(__file__).resolve().parent.parent / "data" / "handbook.pdf"

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=16, spaceBefore=16, spaceAfter=6, textColor="#1f1e1c")
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12.5, spaceBefore=10, spaceAfter=3, textColor="#cc785c")
BODY = ParagraphStyle("BODY", parent=styles["BodyText"], fontSize=10.5, leading=15, alignment=TA_LEFT, spaceAfter=6)
TITLE = ParagraphStyle("TITLE", parent=styles["Title"], fontSize=24, textColor="#1f1e1c")
SUB = ParagraphStyle("SUB", parent=styles["Normal"], fontSize=11, textColor="#6b6862", spaceAfter=2)

# Each section: (heading, [paragraphs or ("bullets", [items])])
SECTIONS = [
    ("1. Working Hours & Time", [
        "Northwind Robotics operates on a flexible schedule. Core collaboration hours are 10:00 AM to 4:00 PM in your local time zone, during which employees are expected to be reachable. Outside core hours you may arrange your day as you see fit.",
        "The standard work week is 40 hours. Non-exempt employees are eligible for overtime at 1.5x for hours worked beyond 40 in a week, subject to prior manager approval.",
        "Full-time is defined as 30 or more scheduled hours per week. Part-time employees receive prorated benefits based on scheduled hours.",
    ]),
    ("2. Remote & Hybrid Work", [
        "Northwind Robotics is remote-first. Most roles may work fully remotely. Employees within 50 miles of the Austin or Rotterdam offices are asked to come in at least 4 days per month for team on-sites.",
        "Hardware-facing roles (robotics assembly, QA lab, field engineering) require on-site presence as specified in the role's offer letter.",
        "You may work from anywhere within your country of employment without prior approval. Working from another country for more than 21 consecutive days requires written approval from People Ops for tax and legal compliance.",
        "Northwind provides a one-time USD 750 home-office stipend for full-time employees to set up a desk, chair, and monitor, reimbursed via the expense system.",
    ]),
    ("3. Paid Time Off (Vacation)", [
        "Full-time employees accrue 20 days (160 hours) of paid vacation per year, accrued monthly at 1.67 days per month. Part-time employees accrue prorated vacation.",
        "You may carry over up to 5 unused vacation days into the next calendar year. Days beyond 5 are forfeited on December 31 and are not paid out, except where local law requires otherwise.",
        "Vacation requests should be submitted at least 2 weeks in advance for absences of 3 or more days. Manager approval is required and is normally granted within 3 business days.",
        "Upon leaving the company, accrued and unused vacation is paid out in the final paycheck where required by local law.",
    ]),
    ("4. Sick Leave & Health", [
        "Employees receive 10 paid sick days per year, separate from vacation. Sick days do not carry over and are not paid out.",
        "For absences of 3 or more consecutive sick days, a doctor's note may be requested by People Ops.",
        "Mental health days are considered sick days — no explanation is required beyond notifying your manager.",
    ]),
    ("5. Parental & Family Leave", [
        "Birthing parents receive 16 weeks of fully paid parental leave. Non-birthing and adoptive parents receive 12 weeks of fully paid leave, to be taken within 12 months of the birth or placement.",
        "Parental leave is available to employees after 90 days of employment. Leave may be taken continuously or, with manager agreement, split into up to two blocks.",
        "Northwind also provides up to 5 paid days of bereavement leave for an immediate family member.",
    ]),
    ("6. Expenses & Reimbursement", [
        "Business expenses are reimbursed when they are reasonable, necessary, and submitted with a receipt within 60 days. Submit expenses through the Ramp portal under your team's cost center.",
        "Purchases over USD 500 (including laptops and monitors beyond the standard issue) require manager pre-approval before purchase.",
        "Standard equipment (company laptop, keyboard, mouse, headset) is ordered through IT and does not require an expense claim.",
        "Meals during business travel are reimbursed up to USD 75 per day. Alcohol is not reimbursable. Ride-share and public transit for business purposes are reimbursable with a receipt.",
        "To expense a work laptop outside the standard issue, get written manager approval, purchase the device, then submit the itemized receipt in Ramp within 60 days under 'Equipment'.",
    ]),
    ("7. Equipment & IT", [
        "Every full-time employee is issued a company laptop. The standard refresh cycle is every 3 years, or sooner if the device fails.",
        "Report lost or stolen equipment to IT Security within 24 hours so the device can be remotely locked and wiped.",
        "Company devices must have full-disk encryption and automatic screen lock enabled. IT enforces these via device management.",
    ]),
    ("8. Information Security & Data Handling", [
        "Never share customer data, source code, or internal documents outside Northwind systems. Do not paste confidential data into third-party tools that are not on the approved-vendor list.",
        "Use the company password manager for all work credentials. Multi-factor authentication is mandatory on all company accounts.",
        "Report suspected phishing or a security incident immediately to security@northwind.example. There is no penalty for reporting in good faith, even if it turns out to be a false alarm.",
        "Customer robotics telemetry is classified as Confidential and may only be accessed on a need-to-know basis for a support or engineering task.",
    ]),
    ("9. Code of Conduct", [
        "Northwind Robotics is committed to a respectful, harassment-free workplace. Discrimination or harassment on the basis of any protected characteristic will not be tolerated.",
        "Conflicts of interest — including outside work that competes with Northwind — must be disclosed to People Ops.",
        "Concerns may be raised with your manager, People Ops, or anonymously through the ethics hotline. Retaliation for a good-faith report is itself a violation of this policy.",
    ]),
    ("10. Benefits Overview", [
        "Full-time employees are eligible for medical, dental, and vision insurance, with Northwind covering 90% of the employee premium and 60% of dependent premiums.",
        "Northwind matches 401(k)/pension contributions up to 4% of salary, vesting immediately.",
        "An annual learning & development budget of USD 1,500 per employee may be used for courses, books, and conferences, approved by your manager.",
        "The Employee Assistance Program offers free, confidential counseling sessions to all employees and their households.",
    ]),
]


def build():
    doc = SimpleDocTemplate(
        str(OUT), pagesize=LETTER,
        leftMargin=0.9 * inch, rightMargin=0.9 * inch,
        topMargin=0.9 * inch, bottomMargin=0.8 * inch,
        title="Northwind Robotics Employee Handbook",
    )
    flow = [
        Paragraph("Northwind Robotics", TITLE),
        Paragraph("Employee Handbook — Effective January 2026 · v3.1", SUB),
        Paragraph("Internal document. This handbook summarizes company policy for all employees. "
                  "Where local law is more generous, local law applies.", BODY),
        Spacer(1, 10),
    ]
    for heading, items in SECTIONS:
        flow.append(Paragraph(heading, H1))
        for item in items:
            if isinstance(item, tuple) and item[0] == "bullets":
                flow.append(ListFlowable(
                    [ListItem(Paragraph(b, BODY)) for b in item[1]],
                    bulletType="bullet", leftIndent=14))
            else:
                flow.append(Paragraph(item, BODY))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.build(flow)
    print(f"Wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build()
