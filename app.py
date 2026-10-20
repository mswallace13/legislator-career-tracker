import sqlite3
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# Progress API Route
@app.route('/api/progress')
def get_progress():
    conn = sqlite3.connect("legislators.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM legislators")
    total = cursor.fetchone()[0] or 1

    cursor.execute("""
        SELECT COUNT(DISTINCT l.id) 
        FROM legislators l
        LEFT JOIN education e ON l.id = e.legislator_id
        LEFT JOIN military_service m ON l.id = m.legislator_id
        WHERE e.legislator_id IS NOT NULL OR m.legislator_id IS NOT NULL
    """)
    scraped = cursor.fetchone()[0]
    conn.close()

    percentage = round((scraped / total) * 100, 1)

    return jsonify({
        "total": total,
        "scraped": scraped,
        "percentage": percentage
    })

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>State Legislator Career & Background Tracker</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.css">
    <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.js"></script>
</head>
<body class="bg-gray-50 p-8">
    <div class="max-w-6xl mx-auto bg-white p-6 rounded-lg shadow">
        <h1 class="text-3xl font-bold mb-4 text-gray-800">State Legislator Career & Background Tracker</h1>

        <div class="mb-6 p-4 bg-gray-100 rounded-lg border border-gray-200">
            <div class="flex justify-between mb-1">
                <span class="text-sm font-semibold text-gray-700">Scraping Progress</span>
                <span id="progressText" class="text-sm font-medium text-blue-600">0 / 0 (0%)</span>
            </div>
            <div class="w-full bg-gray-300 rounded-full h-4 overflow-hidden">
                <div id="progressBar" class="bg-blue-600 h-4 rounded-full transition-all duration-500" style="width: 0%"></div>
            </div>
        </div>

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

            function updateProgress() {
                $.getJSON('/api/progress', function(data) {
                    $('#progressText').text(data.scraped + ' / ' + data.total + ' (' + data.percentage + '%)');
                    $('#progressBar').css('width', data.percentage + '%');
                });
            }

            updateProgress();
            setInterval(updateProgress, 3000);
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    conn = sqlite3.connect("legislators.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.state, l.name, l.party,
               GROUP_CONCAT(DISTINCT e.degree || ' (' || e.institution || ')') AS education,
               GROUP_CONCAT(DISTINCT p.job_title) AS professions,
               GROUP_CONCAT(DISTINCT m.branch || ' - ' || m.highest_rank) AS military
        FROM legislators l
        LEFT JOIN education e ON l.id = e.legislator_id
        LEFT JOIN professions p ON l.id = p.legislator_id
        LEFT JOIN military_service m ON l.id = m.legislator_id
        GROUP BY l.id
        ORDER BY l.state, l.name
    """)
    rows = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, rows=rows)

if __name__ == "__main__":
    app.run(debug=True, port=5000)