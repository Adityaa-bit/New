import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
import send2trash

class DatabaseManager:
    DB_HOST = "localhost"
    DB_NAME = "test12"
    DB_USER = "root"
    DB_PASSWORD = "root"

    @staticmethod
    def get_connection():
        try:
            return mysql.connector.connect(
                host=DatabaseManager.DB_HOST,
                database=DatabaseManager.DB_NAME,
                user=DatabaseManager.DB_USER,
                password=DatabaseManager.DB_PASSWORD
            )
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

    @staticmethod
    def initialize_database():
        conn = DatabaseManager.get_connection()
        if conn:
            try:
                cursor = conn.cursor()

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Threats (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        file_path VARCHAR(255) NOT NULL,
                        threat_type VARCHAR(50),
                        detected_on DATETIME,
                        status VARCHAR(20)
                    );
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Quarantine_Files (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        threat_id INT,
                        file_path VARCHAR(255) NOT NULL,
                        quarantined_on DATETIME,
                        FOREIGN KEY (threat_id) REFERENCES Threats(id)
                    );
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Allowed_Threats (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        threat_id INT,
                        file_path VARCHAR(255) NOT NULL,
                        allowed_on DATETIME,
                        FOREIGN KEY (threat_id) REFERENCES Threats(id)
                    );
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ThreatInfo (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        file_path VARCHAR(255) NOT NULL,
                        threat_type VARCHAR(50),
                        detected_on DATETIME
                    );
                """)
                  

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Protection_History (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        action VARCHAR(20),
                        file_path VARCHAR(255),
                        action_time DATETIME,
                        threat_type VARCHAR(50)
                    );
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS Malware_Signatures (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        signature VARCHAR(64) NOT NULL UNIQUE,
                        description TEXT,
                        added_on DATETIME
                    );
                """)

                conn.commit()
                print("✅ Database initialized successfully!")

            except Error as e:
                print(f"❌ Error initializing database: {e}")
                raise

            finally:
                if 'cursor' in locals():
                    cursor.close()
                if conn and conn.is_connected():
                    conn.close()

    @staticmethod
    def get_all_signatures():
        signatures = []
        conn = DatabaseManager.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT signature FROM Malware_Signatures")
                signatures = [row[0] for row in cursor.fetchall()]
            except Error as e:
                print(f"Error fetching signatures: {e}")
            finally:
                cursor.close()
                conn.close()
        return signatures

    @staticmethod
    def load_signatures_from_file(file_path):
        conn = DatabaseManager.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                sql = "INSERT IGNORE INTO Malware_Signatures (signature, added_on) VALUES (%s, NOW())"

                with open(file_path, 'r') as file:
                    for line in file:
                        signature = line.strip()
                        if signature:
                            cursor.execute(sql, (signature,))

                conn.commit()
                print("✅ Signatures loaded successfully!")
            except Error as e:
                print(f"Error loading signatures: {e}")
            finally:
                cursor.close()
                conn.close()

    @staticmethod
    def add_threat(file_path, status, threat_type):
        conn = DatabaseManager.get_connection()
        threat_id = -1
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Threats (file_path, detected_on, status, threat_type)
                    VALUES (%s, NOW(), %s, %s)
                """, (file_path, status, threat_type))

                threat_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO Protection_History (action, file_path, action_time, threat_type)
                    VALUES (%s, %s, NOW(), %s)
                """, (status, file_path, threat_type))

                conn.commit()
            except Error as e:
                print(f"Error adding threat: {e}")
            finally:
                cursor.close()
                conn.close()
        return threat_id
    
    @staticmethod
    def log_threat_info(file_path, threat_type):
        conn = DatabaseManager.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO ThreatInfo (file_path, threat_type, detected_on)
                    VALUES (%s, %s, NOW())
                """, (file_path, threat_type))
                conn.commit()
            except Error as e:
                print(f"Error logging threat info: {e}")
            finally:
                cursor.close()
                conn.close()

    @staticmethod
    def allow_threat(threat_id):
        conn = DatabaseManager.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT file_path FROM Threats WHERE id = %s", (threat_id,))
                file_path = cursor.fetchone()[0]

                cursor.execute("""
                    INSERT INTO Allowed_Threats (threat_id, file_path, allowed_on) 
                    VALUES (%s, %s, NOW())
                """, (threat_id, file_path))

                conn.commit()
                print("✅ Threat allowed successfully!")
            except Error as e:
                print(f"Error allowing threat: {e}")
            finally:
                cursor.close()
                conn.close()
    
    @staticmethod
    def remove_threat_info(file_path):
        conn = DatabaseManager.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM ThreatInfo WHERE file_path = %s", (file_path,))
                conn.commit()
            except Error as e:
                print(f"Error removing threat info: {e}")
            finally:
                cursor.close()
                conn.close()


    @staticmethod
    def quarantine_threat(threat_id, file_path):
        conn = DatabaseManager.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Quarantine_Files (threat_id, file_path, quarantined_on) 
                    VALUES (%s, %s, NOW())
                """, (threat_id, file_path))

                cursor.execute("UPDATE Threats SET status = 'Quarantined' WHERE id = %s", (threat_id,))
                conn.commit()
                print("✅ Threat quarantined successfully!")
            except Error as e:
                print(f"Error quarantining threat: {e}")
                raise
            finally:
                cursor.close()
                conn.close()

    @staticmethod
    def get_allowed_threats():
        allowed_threats = []
        conn = DatabaseManager.get_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT t.id, t.file_path, t.threat_type, a.allowed_on, a.file_path AS allowed_file_path
                    FROM Threats t
                    JOIN Allowed_Threats a ON t.id = a.threat_id
                """)
                allowed_threats = cursor.fetchall()
            except Error as e:
                print(f"Error fetching allowed threats: {e}")
            finally:
                cursor.close()
                conn.close()
        return allowed_threats

    @staticmethod
    def get_quarantine_files():
        quarantine_files = []
        conn = DatabaseManager.get_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT t.id, t.file_path, t.threat_type, q.quarantined_on, q.file_path AS quarantine_file_path
                    FROM Threats t
                    JOIN Quarantine_Files q ON t.id = q.threat_id
                """)
                quarantine_files = cursor.fetchall()
            except Error as e:
                print(f"Error fetching quarantine files: {e}")
            finally:
                cursor.close()
                conn.close()
        return quarantine_files

    @staticmethod
    def delete_allowed_threat(threat_id):
        conn = DatabaseManager.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT file_path FROM Allowed_Threats WHERE threat_id = %s", (threat_id,))
                result = cursor.fetchone()
                file_path = result[0] if result else None

                cursor.execute("DELETE FROM Allowed_Threats WHERE threat_id = %s", (threat_id,))
                cursor.execute("DELETE FROM Threats WHERE id = %s", (threat_id,))
                conn.commit()

                if file_path and os.path.exists(file_path):
                    send2trash.send2trash(file_path)
                    print("🗑️ File moved to Recycle Bin.")
                print("✅ Allowed threat deleted.")
            except Error as e:
                print(f"Error deleting allowed threat: {e}")
            finally:
                cursor.close()
                conn.close()

    @staticmethod
    def delete_quarantine_threat(threat_id):
        conn = DatabaseManager.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT file_path FROM Quarantine_Files WHERE threat_id = %s", (threat_id,))
                result = cursor.fetchone()
                file_path = result[0] if result else None

                cursor.execute("DELETE FROM Quarantine_Files WHERE threat_id = %s", (threat_id,))
                cursor.execute("DELETE FROM Threats WHERE id = %s", (threat_id,))
                conn.commit()

                if file_path and os.path.exists(file_path):
                    send2trash.send2trash(file_path)
                    print("🗑️ File moved from quarantine to Recycle Bin.")
                print("✅ Quarantine threat deleted.")
            except Error as e:
                print(f"Error deleting quarantined threat: {e}")
            finally:
                cursor.close()
                conn.close()

    @staticmethod
    def move_allowed_to_quarantine(threat_id, file_path):
        conn = DatabaseManager.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM Allowed_Threats WHERE threat_id = %s", (threat_id,))
                cursor.execute("""
                    INSERT INTO Quarantine_Files (threat_id, file_path, quarantined_on) 
                    VALUES (%s, %s, NOW())
                """, (threat_id, file_path))
                cursor.execute("UPDATE Threats SET status = 'Quarantined' WHERE id = %s", (threat_id,))

                quarantine_folder = "quarantine_folder"
                if not os.path.exists(quarantine_folder):
                    os.makedirs(quarantine_folder)
                file_name = os.path.basename(file_path)
                quarantined_path = os.path.join(quarantine_folder, file_name)
                os.rename(file_path, quarantined_path)

                cursor.execute("""
                    UPDATE Quarantine_Files SET file_path = %s WHERE threat_id = %s
                """, (quarantined_path, threat_id))
                conn.commit()
                print("✅ File moved from allowed to quarantine.")
            except (Error, OSError) as e:
                print(f"Error moving file: {e}")
            finally:
                cursor.close()
                conn.close()

    @staticmethod
    def move_quarantine_to_allowed(threat_id):
        conn = DatabaseManager.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT file_path FROM Quarantine_Files WHERE threat_id = %s", (threat_id,))
                quarantined_path = cursor.fetchone()[0]

                original_path = os.path.join(
                    os.path.dirname(os.path.dirname(quarantined_path)),
                    os.path.basename(quarantined_path)
                )

                cursor.execute("DELETE FROM Quarantine_Files WHERE threat_id = %s", (threat_id,))
                cursor.execute("""
                    INSERT INTO Allowed_Threats (threat_id, file_path, allowed_on) 
                    VALUES (%s, %s, NOW())
                """, (threat_id, original_path))
                cursor.execute("UPDATE Threats SET status = 'Allowed' WHERE id = %s", (threat_id,))
                conn.commit()

                os.rename(quarantined_path, original_path)
                print("✅ File moved from quarantine to allowed.")
            except (Error, OSError) as e:
                print(f"Error moving file: {e}")
            finally:
                cursor.close()
                conn.close()

    @staticmethod
    def view_protection_history():
        conn = DatabaseManager.get_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM Protection_History ORDER BY action_time DESC")

                print("\n📜 Protection History 📜")
                print("----------------------------------------")
                for row in cursor:
                    print(f"Action: {row['action']}")
                    print(f"File: {row['file_path']}")
                    print(f"Threat Type: {row['threat_type']}")
                    print(f"Time: {row['action_time']}")
                    print("----------------------------------------")
            except Error as e:
                print(f"Error viewing protection history: {e}")
            finally:
                cursor.close()
                conn.close()

if __name__ == "__main__":
    DatabaseManager.initialize_database()
