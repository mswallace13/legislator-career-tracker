from flask import Flask, render_template_string
import sqlite3

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Legislator Background Tracker</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.css">
    <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.js"></script>
</head>
<body class="bg-gray-50 p-8">
    <div class="max-w-6xl mx-auto bg-white p-6 rounded-lg shadow">
        <h1 class="text-3xl font-bold mb-6 text-gray-800">State Legislator Career & Background Tracker</h1>
        <table id="legislatorsTable" class="w-full text-left border-collapse">
            <thead>
                <tr class="bg-gray-100 border-b">
                    <th class="p-3">State</th>
                    <th class="p-3">Name</th>
                    <th class="p-3">Party</th>
                    <th class="p-3">Education</th>
                    <th class="p-3">Profession</th>
                    <th class="p-3">Military</th>
                </tr>
            </thead>
            <tbody>
                {% for row in rows %}
                <tr class="border-b hover:bg-gray-50">
                    <td class="p-3">{{ row[0] }}</td>
                    <td class="p-3 font-semibold">{{ row[1] }}</td>
                    <td class="p-3">{{ row[2] }}</td>
                    <td class="p-3">{{ row[3] or 'N/A' }}</td>
                    <td class="p-3">{{ row[4] or 'N/A' }}</td>
                    <td class="p-3">{{ row[5] or 'None' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <script>
        $(document).ready(function() {
            $('#legislatorsTable').DataTable({
                "pageLength": 25,
                "order": [[0, "asc"]]
            });
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    conn = sqlite3.connect("legislators.db")
    cursor = conn.cursor()
    query = """
    SELECT 
        l.state, 
        l.name, 
        l.party, 
        GROUP_CONCAT(DISTINCT e.degree || ' (' || e.institution || ')') AS education,
        GROUP_CONCAT(DISTINCT p.job_title) AS profession,
        COALESCE(m.branch || ' - ' || m.highest_rank, 'None') AS military
    FROM legislators l
    LEFT JOIN education e ON l.id = e.legislator_id
    LEFT JOIN professions p ON l.id = p.legislator_id
    LEFT JOIN military_service m ON l.id = m.legislator_id
    GROUP BY l.id
    """
    rows = cursor.execute(query).fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, rows=rows)

if __name__ == "__main__":
    app.run(port=5000, debug=True)