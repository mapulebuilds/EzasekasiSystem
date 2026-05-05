#!/usr/bin/env python3
"""
Database Export Script
Exports the Ezasekasi database schema and data to a SQL file
"""

import mysql.connector
from datetime import datetime

def export_database(host, user, password, database, output_file):
    """Export database to SQL file"""
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"-- Database Export for '{database}'\n")
            f.write(f"-- Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-- Host: " + host + "\n")
            f.write("-- Database: " + database + "\n")
            f.write("-- -----------------------------------------------\n\n")
            
            # Drop database if exists
            f.write(f"DROP DATABASE IF EXISTS `{database}`;\n")
            f.write(f"CREATE DATABASE `{database}`;\n")
            f.write(f"USE `{database}`;\n\n")
            
            # Export each table
            for table in tables:
                table_name = table[0]
                print(f"Exporting table: {table_name}")
                
                # Get CREATE TABLE statement
                cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
                create_table = cursor.fetchone()[1]
                f.write(f"{create_table};\n\n")
                
                # Get table data
                cursor.execute(f"SELECT * FROM `{table_name}`")
                rows = cursor.fetchall()
                
                if rows:
                    # Get column names
                    cursor.execute(f"DESCRIBE `{table_name}`")
                    columns = [col[0] for col in cursor.fetchall()]
                    
                    # Write INSERT statements
                    col_names = ", ".join([f"`{col}`" for col in columns])
                    for row in rows:
                        values = []
                        for val in row:
                            if val is None:
                                values.append("NULL")
                            elif isinstance(val, str):
                                values.append(f"'{val.replace(chr(39), chr(39)*2)}'")
                            elif isinstance(val, (int, float)):
                                values.append(str(val))
                            else:
                                values.append(f"'{str(val)}'")
                        
                        insert_stmt = f"INSERT INTO `{table_name}` ({col_names}) VALUES ({', '.join(values)});"
                        f.write(insert_stmt + "\n")
                    
                    f.write("\n")
        
        print(f"✅ Database exported successfully to {output_file}")
        conn.close()
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
        return False
    except Exception as err:
        print(f"❌ Error: {err}")
        return False

if __name__ == "__main__":
    # Database connection details
    HOST = "127.0.0.1"
    USER = "root"
    PASSWORD = "Njabu@08"
    DATABASE = "ezasekasi_db"
    OUTPUT_FILE = "database.sql"
    
    print("Starting database export...")
    export_database(HOST, USER, PASSWORD, DATABASE, OUTPUT_FILE)
