#!/usr/bin/env python3
"""
Check database contents for history
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database import SessionLocal
from db.models import User, Analysis, Roadmap

def check_database_contents():
    """Check what's in the database"""
    
    print("🔍 Checking database contents...")
    
    db = SessionLocal()
    try:
        # Check users
        users = db.query(User).all()
        print(f"👥 Users: {len(users)}")
        for user in users:
            print(f"  - {user.name} ({user.email})")
        
        # Check analyses
        analyses = db.query(Analysis).all()
        print(f"\n📊 Analyses: {len(analyses)}")
        for analysis in analyses:
            print(f"  - {analysis.target_role} (Score: {analysis.match_score}%)")
            print(f"    User: {analysis.user_id}")
            print(f"    Created: {analysis.created_at}")
        
        # Check roadmaps
        roadmaps = db.query(Roadmap).all()
        print(f"\n🗺️ Roadmaps: {len(roadmaps)}")
        for roadmap in roadmaps:
            print(f"  - {roadmap.target_role} ({roadmap.total_days} days)")
            print(f"    User: {roadmap.user_id}")
            print(f"    Created: {roadmap.created_at}")
        
        if len(analyses) == 0 and len(roadmaps) == 0:
            print("\n❌ No history found in database!")
            print("💡 To create history:")
            print("   1. Login to the frontend app")
            print("   2. Complete a resume analysis")
            print("   3. Generate a roadmap")
            print("   4. Check history again")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_database_contents()
