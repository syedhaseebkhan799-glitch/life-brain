"""
Generate a sample life profile as a PDF, for testing Life Brain.

The person in it is invented. Nothing here describes a real human being -- it
exists so the app can be exercised end to end without anyone having to upload
their actual life to find out whether the upload works.

    python samples/make_sample_pdf.py

Writes samples/sample_life_profile.pdf
"""
from pathlib import Path

from fpdf import FPDF

OUT = Path(__file__).resolve().parent / "sample_life_profile.pdf"

# Deliberately varied: dates, places, numbers, opinions, relationships, health,
# money, regrets, plans. Each section supports a different kind of question, so
# a tester can find out what the app is and isn't good at.
SECTIONS = [
    ("SAMPLE LIFE PROFILE - Amara Okonkwo", [
        "This is fictional test data for the Life Brain app. Amara Okonkwo is",
        "not a real person. Replace this file with your own documents when you",
        "are finished testing.",
    ]),
    ("Basic facts", [
        "Full name: Amara Chidinma Okonkwo",
        "Born: 14 March 1994, in Enugu, Nigeria",
        "Currently living in: Manchester, United Kingdom (since August 2019)",
        "Languages: English (native), Igbo (fluent), Portuguese (conversational)",
        "Height 1.68 m. Left-handed. Blood type O+.",
    ]),
    ("Family", [
        "Mother: Ngozi, a secondary school maths teacher, retired in 2021.",
        "Father: Emeka, ran a small electrical supplies business until 2016.",
        "One older brother, Chidi, born 1990, lives in Abuja, works in logistics.",
        "One younger sister, Adaeze, born 1999, studying medicine in Lagos.",
        "Grandmother Ifeoma lived with the family until she died in 2012. She",
        "taught Amara to cook jollof rice and to never lend money she could not",
        "afford to lose.",
    ]),
    ("Education", [
        "2005-2011: Federal Government College, Enugu.",
        "2012-2016: BSc Computer Science, University of Nigeria, Nsukka.",
        "Graduated second class upper. Final year project was a bus timetable",
        "app that never worked properly on Android 4.",
        "2019-2020: MSc Data Science, University of Manchester. Distinction.",
        "Dissertation on detecting fraudulent mobile money transfers.",
    ]),
    ("Work history", [
        "2016-2017: NYSC placement at a secondary school in Kaduna, teaching",
        "computer studies. Hated the first three months, loved the last six.",
        "2017-2019: Junior developer at Paystack-adjacent fintech startup in",
        "Lagos. Left because the commute was two hours each way.",
        "2020-2022: Data analyst at a logistics firm in Manchester. Salary",
        "started at 32,000 pounds, ended at 41,000.",
        "2022-present: Senior data scientist at a healthcare analytics company.",
        "Current salary 68,000 pounds. Promoted in April 2024.",
        "Manager is called Priya. They get on well. Priya pushed for the",
        "promotion when Amara did not ask for it.",
    ]),
    ("Money", [
        "Mortgage on a two-bedroom flat in Chorlton, bought March 2023 for",
        "245,000 pounds with a 40,000 deposit saved over four years.",
        "Monthly mortgage payment: 1,180 pounds.",
        "Emergency fund: about 11,000 pounds, target is 18,000.",
        "Sends roughly 300 pounds home most months, more in December.",
        "Regrets buying a car in 2021 and selling it at a loss in 2022.",
    ]),
    ("Health", [
        "Diagnosed with iron deficiency anaemia in 2018, managed with",
        "supplements. Energy much better since.",
        "Broke left wrist falling off a bicycle in Amsterdam, July 2023.",
        "Runs three times a week. Personal best 10k: 54 minutes, set in 2024.",
        "Sleeps badly in the week before a deadline. Has tried and abandoned",
        "four different meditation apps.",
    ]),
    ("Relationships and friendships", [
        "Long relationship with Tunde, 2015 to 2021. Ended amicably. They",
        "still exchange birthday messages.",
        "Seeing someone called Joseph since late 2024. He is a nurse, works",
        "nights, which makes weekends complicated.",
        "Closest friend is Bisi, known since university, now lives in Toronto.",
        "They speak most Sundays.",
        "Finds it hard to make new friends in Manchester and says so often.",
    ]),
    ("Things she believes and wants", [
        "Wants to move into a role with more direct impact on patient outcomes",
        "rather than dashboards nobody reads.",
        "Has said for three years that she wants to learn to swim properly.",
        "Has not booked a lesson.",
        "Thinks she works too much and that nobody has ever asked her to.",
        "Wants to visit Nigeria for at least a month, not the usual ten days.",
        "Believes strongly that people should be paid what they ask for, and",
        "is bad at asking.",
    ]),
    ("Notable events by year", [
        "2012: Grandmother Ifeoma died. First time on a plane.",
        "2016: Graduated. First paid programming work.",
        "2019: Moved to the UK. Hardest year.",
        "2021: Relationship with Tunde ended. Bought and regretted the car.",
        "2023: Bought the flat. Broke her wrist. Best and worst year at once.",
        "2024: Promoted. Ran fastest 10k. Met Joseph.",
        "2025: Started saying no to weekend work.",
    ]),
]


def build() -> Path:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # An explicit width, and x reset before every block. Passing w=0 measures
    # from wherever the cursor happens to be, which after a wrapped line is not
    # the left margin -- and fpdf refuses to render into what is left.
    width = pdf.w - pdf.l_margin - pdf.r_margin

    def block(text, size, style="", gap=0.0):
        pdf.set_font("Helvetica", style, size)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(width, 6 if not style else 8, text)
        if gap:
            pdf.ln(gap)

    for index, (heading, lines) in enumerate(SECTIONS):
        # A heading orphaned at the foot of a page is one the reader -- and the
        # model quoting it back -- has to hunt for.
        if pdf.get_y() > 250:
            pdf.add_page()
        block(heading, 16 if index == 0 else 13, style="B", gap=1)

        for line in lines:
            block(line, 11)
        pdf.ln(4)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUT))
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"wrote {path} ({path.stat().st_size:,} bytes)")
