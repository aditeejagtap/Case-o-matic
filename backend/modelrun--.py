from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, distinct
from models import Base, Detail, Summary
from datetime import date
import os



# Step 1: Add new detail entry
def add_detail_entry(date_entry, comId, region, programmer, casenum, status, comments, assigned, pending):
    #Pre-validations
    if date_entry > date.today():
        print("❌ You cannot enter data for dates in the future!")
        return
    
    # Add new detail entry
    new_detail = Detail(
        date=date_entry,
        comId=comId,
        region=region,
        programmer=programmer #current_user.comId
        casenum=casenum,
        status=status,
        comments=comments
    )
    session.add(new_detail)
    session.commit()
    print("Detail added!")

    # Update the summary table
    update_summary_table(date_entry, region, assigned, pending)

# Step 2: Update the summary table
    # write all summary logic here
    # Insert into summary
    summary_entry = Summary(
        date=date_entry,
        region=region,
        existing=existing,
        assigned=assigned,
        delivered=delivered,
        returned=returned,
        resources=resources,
        unassigned=unassigned,
        pending=pending
    )
    session.add(summary_entry)
    session.commit()
    print("Summary updated!")

if __name__ == "__main__":
    # Get user input for assigned and pending
    assigned = int(input("Enter the number of cases assigned today: "))
    pending = int(input("Enter the number of cases pending: "))

    add_detail_entry(
        date_entry=date.today(),
        comId="COM123",
        region="ASIA",
        programmer="Alice",
        casenum=1001,
        status="delivered",
        comments="First case",
        assigned=assigned,
        pending=pending
    )


