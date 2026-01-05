#!/usr/bin/env python3
"""
Database initialization script for E-Commerce
"""

import os
from database import db

if __name__ == "__main__":
    print("Initializing E-Commerce database...")
    try:
        db.init_db()
        print("\n[SUCCESS] Database initialized successfully!")
        print("\nDefault admin credentials:")
        print("  Username: sara_2003")
        print("  Password: 20032003")
    except Exception as e:
        print(f"\n[ERROR] Error initializing database: {e}")
        raise
