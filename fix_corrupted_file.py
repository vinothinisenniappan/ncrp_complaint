"""Utility script to fix corrupted Excel file"""
import os
import time
import zipfile
from openpyxl import load_workbook

master_file = 'data/master_register.xlsx'

print("=" * 60)
print("NCRP Complaint Organizer - Corrupted File Fixer")
print("=" * 60)

if not os.path.exists(master_file):
    print(f"\n[OK] File does not exist: {master_file}")
    print("  No action needed.")
    exit(0)

print(f"\nChecking file: {master_file}")

# Method 1: Check if it's a valid zip file
try:
    with zipfile.ZipFile(master_file, 'r') as zip_ref:
        if '[Content_Types].xml' not in zip_ref.namelist():
            print("\n[X] File is CORRUPTED: Missing [Content_Types].xml")
            raise KeyError("Missing [Content_Types].xml")
        print("[OK] File is a valid zip archive")
except (KeyError, zipfile.BadZipFile) as e:
    print(f"\n[X] File is CORRUPTED: {str(e)}")
    corrupted = True
except Exception as e:
    print(f"\n[?] Could not validate as zip: {str(e)}")
    corrupted = None
else:
    corrupted = False

# Method 2: Try openpyxl
if corrupted is not False:
    try:
        test_wb = load_workbook(master_file, read_only=True)
        test_wb.close()
        print("[OK] File can be opened with openpyxl")
        if corrupted:
            print("  (But zip validation failed - file may be partially corrupted)")
        corrupted = False
    except Exception as e:
        print(f"[X] File cannot be opened with openpyxl: {str(e)}")
        if corrupted is None:
            corrupted = True

# Fix corrupted file
if corrupted:
    print("\n" + "=" * 60)
    print("ATTEMPTING TO FIX...")
    print("=" * 60)
    
    backup_name = f"data/master_register_corrupted_{int(time.time())}.xlsx"
    
    try:
        os.rename(master_file, backup_name)
        print(f"[OK] Successfully renamed corrupted file to:")
        print(f"  {backup_name}")
        print("\n[OK] Corrupted file has been moved. System will create a new file.")
    except Exception as e:
        print(f"\n[X] Could not rename file: {str(e)}")
        print("\nTrying to delete...")
        try:
            os.remove(master_file)
            print("[OK] Successfully deleted corrupted file")
        except Exception as del_error:
            print(f"[X] Could not delete file: {str(del_error)}")
            print("\n[!] File may be locked by another program.")
            print("   Please:")
            print("   1. Close Excel if it's open")
            print("   2. Close any other programs using this file")
            print("   3. Run this script again")
            exit(1)
else:
    print("\n[OK] File is VALID - no action needed")

print("\n" + "=" * 60)
print("Done!")
print("=" * 60)

