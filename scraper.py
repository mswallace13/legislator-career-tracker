import sqlite3
import re
import requests
from bs4 import BeautifulSoup

def scrape_and_populate_bio(legislator_id, bio_url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        response = requests.get(bio_url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {bio_url}: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract visible text paragraphs
    paragraphs = [p.get_text() for p in soup.find_all(["p", "li"])]
    full_text = " ".join(paragraphs)

    conn = sqlite3.connect("legislators.db")
    cursor = conn.cursor()

    # --- 1. Education Extraction ---
    degree_patterns = [
        r"(B\.A\.|B\.S\.|M\.A\.|M\.S\.|Ph\.D\.|J\.D\.|Bachelor|Master|Doctorate)[^,\.]*?(?:from|at)\s+([A-Z][a-zA-Z\s]+(?:University|College|State))",
        r"(Degree in [^,\.]+? from [A-Z][a-zA-Z\s]+(?:University|College))"
    ]
    
    for pattern in degree_patterns:
        matches = re.findall(pattern, full_text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                degree, institution = match[0].strip(), match[1].strip()
            else:
                degree, institution = match.strip(), "Unknown Institution"
            
            cursor.execute("""
                INSERT INTO education (legislator_id, degree, institution) 
                VALUES (?, ?, ?)
            """, (legislator_id, degree, institution))

    # --- 2. Military Service Extraction ---
    military_branches = ["Army", "Navy", "Air Force", "Marines", "Coast Guard", "National Guard"]
    branch_found = None
    
    for branch in military_branches:
        if re.search(r"\b" + branch + r"\b", full_text, re.IGNORECASE):
            branch_found = branch
            break

    if branch_found:
        rank_match = re.search(r"\b(Captain|Major|Colonel|General|Commander|Sergeant|Lieutenant)\b", full_text, re.IGNORECASE)
        rank = rank_match.group(0) if rank_match else "Veteran"
        
        cursor.execute("""
            INSERT OR REPLACE INTO military_service (legislator_id, branch, highest_rank, veteran_status)
            VALUES (?, ?, ?, 1)
        """, (legislator_id, branch_found, rank))

    conn.commit()
    conn.close()
    print(f"Successfully processed bio for {legislator_id}")


if __name__ == "__main__":
    # Add legislators to scrape into your database
    legislators = [
        {"id": "AL-105", "name": "Chip Brown", "state": "AL", "chamber": "lower", "party": "Republican", "url": "https://en.wikipedia.org/wiki/Chip_Brown"},
        {"id": "AL-20", "name": "Linda Coleman-Madison", "state": "AL", "chamber": "upper", "party": "Democratic", "url": "https://en.wikipedia.org/wiki/Linda_Coleman-Madison"},
        {"id": "AR-45", "name": "Aaron Pilkington", "state": "AR", "chamber": "lower", "party": "Republican", "url": "https://en.wikipedia.org/wiki/Aaron_Pilkington"},
        {"id": "AL-53", "name": "Anthony Daniels", "state": "AL", "chamber": "lower", "party": "Democratic", "url": "https://en.wikipedia.org/wiki/Anthony_Daniels_(politician)"},
        {"id": "AL-24", "name": "Nathaniel Ledbetter", "state": "AL", "chamber": "lower", "party": "Republican", "url": "https://en.wikipedia.org/wiki/Nathaniel_Ledbetter"}
    ]

    conn = sqlite3.connect("legislators.db")
    cursor = conn.cursor()

    for leg in legislators:
        # Insert base legislator record
        cursor.execute("""
            INSERT OR REPLACE INTO legislators (id, name, state, chamber, party)
            VALUES (?, ?, ?, ?, ?)
        """, (leg["id"], leg["name"], leg["state"], leg["chamber"], leg["party"]))
        conn.commit()

        # Scrape and populate bio details
        scrape_and_populate_bio(leg["id"], leg["url"])

    conn.close()
    print("All legislators scraped and inserted successfully!")