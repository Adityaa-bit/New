import mysql.connector
from database_manager import DatabaseManager
from file_scanner import FileScanner
import sys
import os

# function for handling allowwed threat
def handle_allowed_threats():
    allowed_threats = DatabaseManager.get_allowed_threats()
    
    if not allowed_threats:
        print("\nNo allowed threats found.")
        return
    
    print("\n✅ **Allowed Threats** ✅")
    print("----------------------------------------")
    for i, threat in enumerate(allowed_threats, 1):
        print(f"{i}. File: {threat['allowed_file_path'] or threat['file_path']}")
        print(f"   Threat Type: {threat['threat_type']}")
        print(f"   Allowed On: {threat['allowed_on']}")
        print("----------------------------------------")
    
    try:
        choice = int(input("\nSelect a threat to take action (0 to cancel): "))
        if 0 < choice <= len(allowed_threats):
            selected_threat = allowed_threats[choice-1]
            threat_id = selected_threat['id']
            file_path = selected_threat['allowed_file_path'] or selected_threat['file_path']
            
            print("\n1. Move to Quarantine")
            print("2. Delete")
            action = int(input("Choose an action: "))
            
            if action == 1:
                DatabaseManager.move_allowed_to_quarantine(threat_id, file_path)
            elif action == 2:
                DatabaseManager.delete_allowed_threat(threat_id)
            else:
                print("Invalid action.")
    except ValueError:
        print("Invalid input.")
#function to handle quarintine threat
def handle_quarantine_files():
    quarantine_files = DatabaseManager.get_quarantine_files()
    
    if not quarantine_files:
        print("\nNo quarantine files found.")
        return
    
    print("\n🚫 **Quarantine Files** 🚫")
    print("----------------------------------------")
    for i, threat in enumerate(quarantine_files, 1):
        print(f"{i}. File: {threat['quarantine_file_path'] or threat['file_path']}")
        print(f"   Threat Type: {threat['threat_type']}")
        print(f"   Quarantined On: {threat['quarantined_on']}")
        print("----------------------------------------")
    
    try:
        choice = int(input("\nSelect a file to take action (0 to cancel): "))
        if 0 < choice <= len(quarantine_files):
            selected_threat = quarantine_files[choice-1]
            threat_id = selected_threat['id']
            
            print("\n1. Move to Allowed")
            print("2. Delete")
            action = int(input("Choose an action: "))
            
            if action == 1:
                DatabaseManager.move_quarantine_to_allowed(threat_id)
            elif action == 2:
                DatabaseManager.delete_quarantine_threat(threat_id)
            else:
                print("Invalid action.")
    except ValueError:
        print("Invalid input.")

def main():
    
    # Initialize database with updated schema
    DatabaseManager.initialize_database()
    
    # Load signatures from a text file
    signature_file_path = "C:/Users/adity/OneDrive/Desktop/New folder (2)/Malse.txt"
    if os.path.exists(signature_file_path):
        DatabaseManager.load_signatures_from_file(signature_file_path)
    else:
        print(f"Signature file not found at: {signature_file_path}")
    
    while True:
        print("\n=== Antivirus Menu ===")
        print("1️⃣ Scan for threats")
        print("2️⃣ View Protection History")
        print("3️⃣ Manage Allowed Threats")
        print("4️⃣ Manage Quarantine Files")
        print("5️⃣ Quit")
        
        try:
            choice = int(input("Choose an option: "))
            
            if choice == 1:
                FileScanner.scan_for_threats()
            elif choice == 2:
                DatabaseManager.view_protection_history()
            elif choice == 3:
                handle_allowed_threats()
            elif choice == 4:
                handle_quarantine_files()
            elif choice == 5:
                print("Exiting the antivirus...")
                sys.exit()
            else:
                print("Invalid option. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

if __name__ == "__main__":
    main()