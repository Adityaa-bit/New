import os
import send2trash
import hashlib
import datetime
from database_manager import DatabaseManager
from heuristic_scanner import HeuristicScanner
from signature_scanner import SignatureScanner
from behaviour_scanner import BehaviourScanner
from ml_scanner import MLScanner



class FileScanner:
    QUICK_SCAN_DIRECTORIES = [
        os.path.join(os.path.expanduser("~"), "Downloads"),
        os.path.join(os.path.expanduser("~"), "Desktop"),
        os.path.join(os.path.expanduser("~"), "Documents"),
        os.getenv("TEMP")
    ]

    detected_threats = []  # ⬅️ This stores all threats found during scanning

    @staticmethod
    def scan_for_threats():
        print("\n=== Scan Options ===")
        print("1️⃣ Quick Scan")
        print("2️⃣ Custom Scan")
        print("3️⃣ Full Scan")
        
        try:
            scan_choice = int(input("Choose an option: "))
            if scan_choice == 1:
                FileScanner.quick_scan()
            elif scan_choice == 2:
                FileScanner.custom_scan()
            elif scan_choice == 3:
                FileScanner.full_scan()
            else:
                print("Invalid option.")
        except ValueError:
            print("Invalid input.")

    @staticmethod
    def quick_scan():
        print("\n🚀 Starting Quick Scan...")
        for directory in FileScanner.QUICK_SCAN_DIRECTORIES:
            if directory and os.path.exists(directory):
                print(f"\n🔍 Scanning directory: {directory}")
                FileScanner.scan_directory(directory)
            else:
                print(f"⚠️ Directory not found: {directory}")
        print("\n✅ Quick Scan completed.")

    @staticmethod
    def custom_scan():
        path = input("\nEnter file or directory path: ").strip()
        if os.path.exists(path):
            print(f"\n🔍 Scanning path: {path}")
            if os.path.isdir(path):
                FileScanner.scan_directory(path)
            else:
                FileScanner.scan_file(path)
                FileScanner.show_threat_summary()
        else:
            print("❌ Error: Path does not exist.")
            return

    @staticmethod
    def full_scan():
        print("\n🚀 Starting Full Scan...")
        FileScanner.scan_directory("/")
        print("\n✅ Full Scan completed.")

    @staticmethod
    def scan_directory(directory_path):
        FileScanner.detected_threats = []  # Clear previous threats

        try:
            print(f"\n🔍 Scanning directory: {directory_path}")
            for root, _, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        FileScanner.scan_file(file_path)
                    except Exception as e:
                        print(f"⚠️ Error scanning {file_path}: {str(e)}")
        except PermissionError:
            print(f"⛔ Permission denied for directory: {directory_path}")
        except Exception as e:
            print(f"❌ Unexpected error scanning directory: {str(e)}")

        FileScanner.show_threat_summary()

    @staticmethod
    def scan_file(file_path):
        is_heuristic_threat = HeuristicScanner.scan(file_path)
        is_signature_threat = SignatureScanner.scan(file_path)
        is_behavior_threat = BehaviourScanner.scan(file_path)
        is_ml_threat = MLScanner().scan(file_path)
        
        if is_heuristic_threat or is_signature_threat or is_behavior_threat or is_ml_threat:
            threat_type = FileScanner.determine_threat_type(
                is_heuristic_threat, is_signature_threat, is_behavior_threat, is_ml_threat
            )
            FileScanner.detected_threats.append({
                "file_path": file_path,
                "threat_type": threat_type
            })
            DatabaseManager.log_threat_info(file_path, threat_type)

    @staticmethod
    def show_threat_summary():
        if not FileScanner.detected_threats:
            print("\n✅ No threats detected.")
            return

        print("\n⚠️ Detected Threats ⚠️")
        print("----------------------------------------")
        for idx, threat in enumerate(FileScanner.detected_threats, 1):
            print(f"{idx}. File: {threat['file_path']}")
            print(f"   Type: {threat['threat_type']}")
            print("----------------------------------------")

        for idx, threat in enumerate(FileScanner.detected_threats, 1):
            print(f"\n➡️ Action for Threat {idx}: {threat['file_path']}")
            print("1️⃣ Allow")
            print("2️⃣ Delete")
            print("3️⃣ Quarantine")

            try:
                action_choice = int(input("Choose an action: "))
                if action_choice == 1:
                    FileScanner.allow_threat(threat["file_path"], threat["threat_type"])
                elif action_choice == 2:
                    FileScanner.delete_threat(threat["file_path"])
                elif action_choice == 3:
                    FileScanner.quarantine_threat(threat["file_path"], threat["threat_type"])
                else:
                    print("Invalid choice. Skipping.")
            except ValueError:
                print("Invalid input. Skipping.")

    @staticmethod
    def determine_threat_type(is_heuristic_threat, is_signature_threat, is_behavior_threat, is_ml_threat):
        if is_signature_threat:
            return "Signature Threat"
        if is_heuristic_threat:
            return "Heuristic Threat"
        if is_behavior_threat:
            return "Behavior Threat"
        if is_ml_threat:
            return "ML Threat"
        return "Unknown Threat"

    @staticmethod
    def allow_threat(file_path, threat_type):
        threat_id = DatabaseManager.add_threat(file_path, "Allowed", threat_type)
        DatabaseManager.allow_threat(threat_id)
        print("✅ Threat allowed and logged.")

    @staticmethod
    def delete_threat(file_path):
        if FileScanner.move_to_recycle_bin(file_path):
            print("✅ Threat deleted and moved to Recycle Bin.")
        else:
            print("❌ Failed to delete the file.")

    @staticmethod
    def quarantine_threat(file_path, threat_type):
        quarantine_folder = "quarantine_folder"
        if not os.path.exists(quarantine_folder):
            os.makedirs(quarantine_folder)

        file_name = os.path.basename(file_path)
        quarantined_path = os.path.join(quarantine_folder, file_name)

        try:
            threat_id = DatabaseManager.add_threat(file_path, "Quarantined", threat_type)
            DatabaseManager.quarantine_threat(threat_id, quarantined_path)
            os.rename(file_path, quarantined_path)
            print("✅ Threat quarantined and logged successfully.")
        except Exception as e:
            print(f"❌ Failed to quarantine threat: {e}")

    @staticmethod
    def move_to_recycle_bin(file_path):
        try:
            send2trash.send2trash(file_path)
            return True
        except Exception as e:
            print(f"❌ Error moving file to Recycle Bin: {e}")
            return False
