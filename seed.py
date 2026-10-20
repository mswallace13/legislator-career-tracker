import sqlite3

conn = sqlite3.connect("legislators.db")
cursor = conn.cursor()

with open("schema.sql", "r") as f:
    cursor.executescript(f.read())

cursor.executescript("""
INSERT OR REPLACE INTO legislators VALUES ('AL-105', 'Chip Brown', 'AL', 'lower', 'Republican');
INSERT OR REPLACE INTO legislators VALUES ('AL-20', 'Linda Coleman-Madison', 'AL', 'upper', 'Democratic');

INSERT INTO education (legislator_id, degree, institution) VALUES 
('AL-105', 'B.S. Business', 'University of Alabama'),
('AL-20', 'M.A. Education', 'University of Alabama at Birmingham');

INSERT INTO professions (legislator_id, job_title, category) VALUES 
('AL-105', 'Small Business Owner', 'Business'),
('AL-20', 'Educator', 'Education');

INSERT OR REPLACE INTO military_service VALUES ('AL-105', 'Navy', 'Commander', 1);
""")

conn.commit()
conn.close()
print("Sample career and education data inserted!")