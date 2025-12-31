"""Script to clean up corrupted Excel file"""
import os
import time

file_path = 'data/master_register.xlsx'

if os.path.exists(file_path):
    try:
        # Try to validate the file
        from openpyxl import load_workbook
        wb = load_workbook(file_path)
        wb.close()
        print("File is valid, no cleanup needed")
    except Exception as e:
        print(f"File is corrupted: {e}")
        # Try to delete it
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                os.remove(file_path)
                print(f"Successfully deleted corrupted file on attempt {attempt + 1}")
                break
            except PermissionError:
                if attempt < max_attempts - 1:
                    print(f"File is locked, waiting... (attempt {attempt + 1}/{max_attempts})")
                    time.sleep(1)
                else:
                    print("Could not delete file - it may be open in Excel or locked by another process")
                    print("Please close Excel and any programs using this file, then try again")
            except Exception as e:
                print(f"Error deleting file: {e}")
                break
else:
    print("File does not exist")

