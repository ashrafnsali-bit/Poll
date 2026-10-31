"""
Barber SaaS - Landing Page & Lead Collection Backend
Lightweight, Zero-Dependency Python HTTP Server with SQLite Database
"""

import http.server
import socketserver
import sqlite3
import json
import os
import re
import urllib.parse
from datetime import datetime

PORT = 8000
DB_FILE = os.path.join(os.path.dirname(__file__), "barber_leads.db")
BASE_DIR = os.path.dirname(__file__)

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                choice_type TEXT NOT NULL,  -- 'interested' | 'not_interested'
                phone TEXT,                 -- '05xxxxxxxx' or NULL
                ip_address TEXT,
                user_agent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

class BarberRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS and disable caching for API endpoints
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/" or path == "/index.html":
            self.serve_file(os.path.join(BASE_DIR, "index.html"), "text/html; charset=utf-8")
        elif path == "/admin" or path == "/admin.html":
            self.serve_file(os.path.join(BASE_DIR, "admin.html"), "text/html; charset=utf-8")
        elif path == "/api/leads":
            self.handle_api_get_leads()
        elif path == "/api/export":
            self.handle_api_export_csv()
        elif path == "/api/stats":
            self.handle_api_stats()
        else:
            # Fallback to static files
            super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/feedback":
            self.handle_api_feedback()
        else:
            self.send_error(404, "Endpoint not found")

    def serve_file(self, filepath, content_type):
        if not os.path.isfile(filepath):
            self.send_error(404, "File not found")
            return
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {e}")

    def handle_api_feedback(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data.decode("utf-8"))
        except Exception:
            self.send_json_response(400, {"success": False, "error": "بيانات غير صالحة (Invalid JSON)"})
            return

        choice = data.get("choice", "").strip()
        phone = data.get("phone", "").strip() if data.get("phone") else None

        # Validation logic
        if choice not in ("interested", "not_interested"):
            self.send_json_response(400, {"success": False, "error": "نوع الاختيار غير صحيح"})
            return

        if choice == "interested":
            if not phone:
                self.send_json_response(400, {"success": False, "error": "يرجى إدخال رقم الجوال"})
                return
            # Validation: exactly 10 digits starting with 05
            if not re.match(r"^05\d{8}$", phone):
                self.send_json_response(400, {
                    "success": False, 
                    "error": "رقم الجوال يجب أن يبدأ بـ 05 ويتكون من 10 أرقام بالضبط"
                })
                return
        else:
            phone = None

        ip_addr = self.headers.get("X-Forwarded-For", self.client_address[0])
        user_agent = self.headers.get("User-Agent", "Unknown")

        try:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO interactions (choice_type, phone, ip_address, user_agent) VALUES (?, ?, ?, ?)",
                    (choice, phone, ip_addr, user_agent)
                )
                conn.commit()
            
            self.send_json_response(200, {
                "success": True,
                "message": "تم تسجيل ردك بنجاح"
            })
        except Exception as e:
            self.send_json_response(500, {"success": False, "error": f"خطأ في قاعدة البيانات: {e}"})

    def handle_api_stats(self):
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM interactions")
                total = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM interactions WHERE choice_type = 'interested'")
                interested = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM interactions WHERE choice_type = 'not_interested'")
                not_interested = cursor.fetchone()[0]

                rate = round((interested / total * 100), 1) if total > 0 else 0

            self.send_json_response(200, {
                "total": total,
                "interested": interested,
                "not_interested": not_interested,
                "conversion_rate": rate
            })
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_api_leads(self):
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, choice_type, phone, ip_address, user_agent, created_at FROM interactions ORDER BY id DESC")
                rows = cursor.fetchall()

                leads = [
                    {
                        "id": row["id"],
                        "choice_type": row["choice_type"],
                        "phone": row["phone"] or "",
                        "ip_address": row["ip_address"] or "",
                        "user_agent": row["user_agent"] or "",
                        "created_at": row["created_at"]
                    }
                    for row in rows
                ]

            self.send_json_response(200, {"leads": leads})
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def handle_api_export_csv(self):
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, choice_type, phone, ip_address, user_agent, created_at FROM interactions ORDER BY id DESC")
                rows = cursor.fetchall()

            # UTF-8 BOM so Excel opens Arabic correctly
            bom = "\ufeff"
            csv_lines = [
                bom + "المعرف,نوع الاختيار,رقم الجوال,تاريخ التسجيل,عنوان IP,المتصفح"
            ]

            for row in rows:
                c_type = "مهتم" if row["choice_type"] == "interested" else "غير مهتم"
                # Prefix phone with single quote or text format in CSV so Excel doesn't drop leading 0
                phone_val = f'"{row["phone"]}"' if row["phone"] else '""'
                ua_clean = f'"{row["user_agent"].replace(chr(34), chr(39))}"' if row["user_agent"] else '""'
                ip_clean = f'"{row["ip_address"]}"' if row["ip_address"] else '""'
                date_clean = f'"{row["created_at"]}"'

                csv_lines.append(f'{row["id"]},{c_type},{phone_val},{date_clean},{ip_clean},{ua_clean}')

            csv_data = "\r\n".join(csv_lines).encode("utf-8")

            filename = f"barber_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.send_header("Content-Length", str(len(csv_data)))
            self.end_headers()
            self.wfile.write(csv_data)

        except Exception as e:
            self.send_error(500, f"Export error: {e}")

    def send_json_response(self, code, payload):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

def run(host='127.0.0.1', port=8000):
    init_db()
    server_address = (host, port)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(server_address, BarberRequestHandler) as httpd:
        print("=" * 60)
        print(f"[Barber SaaS] Server is running!")
        print(f"Landing Page:    http://{host or 'localhost'}:{port}/")
        print(f"Admin Dashboard: http://{host or 'localhost'}:{port}/admin")
        print("=" * 60)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")

if __name__ == "__main__":
    # Support custom port via command line argument if needed
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    # Use 0.0.0.0 if running standalone so other devices on local network can test
    run(host='0.0.0.0', port=port)
