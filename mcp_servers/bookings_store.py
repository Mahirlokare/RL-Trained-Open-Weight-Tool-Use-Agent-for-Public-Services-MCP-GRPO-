"""
Persistent Bookings & Citizen Session Store for Civic AI.
Persists all confirmed appointments to data/bookings.json and manages citizen sign-in sessions.
"""
import os
import json
import time
from typing import List, Dict, Any, Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
BOOKINGS_FILE = os.path.join(DATA_DIR, "bookings.json")
SESSION_FILE = os.path.join(DATA_DIR, "active_session.json")

def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(BOOKINGS_FILE):
        # Seed with initial verified sample booking
        initial_bookings = [
            {
                "booking_id": "BK-SEVA-68079",
                "citizen_name": "Ramesh Devidas Patil",
                "mobile": "9876543210",
                "center_id": "SEVA_PUNE_NORTH",
                "center_name": "SEVA KENDRA PUNE NORTH (CENTRAL REGISTRY)",
                "slot_time": "2026-12-01 10:00 AM",
                "scheme_id": "PM_KISAN",
                "scheme_name": "PM-KISAN (Farmer Direct Assistance)",
                "confirmation_token": "CONFIRM-DF037992399C",
                "status": "CONFIRMED",
                "booked_at": "2026-11-24 10:15:00",
                "pass_file": "docs/Seva_Kendra_Appointment_Slip.png"
            }
        ]
        with open(BOOKINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(initial_bookings, f, indent=2, ensure_ascii=False)

def save_booking_record(booking_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Persists an appointment booking record to data/bookings.json."""
    _ensure_data_dir()
    bookings = load_all_bookings()
    
    # Ensure mandatory fields
    bid = booking_dict.get("booking_id") or f"BK-SEVA-{abs(hash(str(time.time()))) % 100000}"
    record = {
        "booking_id": bid,
        "citizen_name": booking_dict.get("citizen_name", "Citizen Beneficiary"),
        "mobile": booking_dict.get("mobile", "9876543210"),
        "center_id": booking_dict.get("center_id", "SEVA_PUNE_NORTH"),
        "center_name": booking_dict.get("center_name", booking_dict.get("center_id", "SEVA KENDRA PUNE NORTH")),
        "slot_time": booking_dict.get("slot_time", "2026-12-01 10:00 AM"),
        "scheme_id": booking_dict.get("scheme_id", "PM_KISAN"),
        "scheme_name": booking_dict.get("scheme_name", booking_dict.get("scheme_id", "PM_KISAN")),
        "confirmation_token": booking_dict.get("confirmation_token", "CONFIRM-DIRECT"),
        "status": "CONFIRMED",
        "booked_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pass_file": "docs/Seva_Kendra_Appointment_Slip.png"
    }

    # Check for existing record to update or append
    existing_idx = next((i for i, b in enumerate(bookings) if b.get("booking_id") == bid), None)
    if existing_idx is not None:
        bookings[existing_idx] = record
    else:
        bookings.insert(0, record)  # Newest first

    with open(BOOKINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(bookings, f, indent=2, ensure_ascii=False)

    return record

def load_all_bookings(filter_citizen: Optional[str] = None) -> List[Dict[str, Any]]:
    """Loads all saved bookings, optionally filtered by citizen name."""
    _ensure_data_dir()
    try:
        with open(BOOKINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                return []
            if filter_citizen and filter_citizen.strip():
                fc = filter_citizen.strip().lower()
                return [b for b in data if fc in str(b.get("citizen_name", "")).lower() or fc in str(b.get("booking_id", "")).lower()]
            return data
    except Exception:
        return []

def get_bookings_table_rows(filter_citizen: Optional[str] = None) -> List[List[str]]:
    """Returns formatted 2D table rows for Gradio Dataframe."""
    bookings = load_all_bookings(filter_citizen)
    rows = []
    for b in bookings:
        rows.append([
            b.get("booking_id", ""),
            b.get("citizen_name", ""),
            b.get("scheme_id", ""),
            b.get("center_id", ""),
            b.get("slot_time", ""),
            b.get("confirmation_token", ""),
            b.get("status", "CONFIRMED"),
            b.get("booked_at", "")
        ])
    return rows

# --- Citizen Session Authentication Store ---
DEFAULT_SESSION = {
    "signed_in": True,
    "citizen_name": "Ramesh Devidas Patil",
    "mobile": "9876543210",
    "role": "citizen",
    "district": "Pune, Maharashtra",
    "signed_in_at": "2026-11-24 10:00:00"
}

def get_current_session() -> Dict[str, Any]:
    """Retrieves current user sign-in profile."""
    _ensure_data_dir()
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return dict(DEFAULT_SESSION)

def set_current_session(citizen_name: str, mobile: str, role: str, district: str) -> Dict[str, Any]:
    """Saves updated user sign-in session."""
    _ensure_data_dir()
    session = {
        "signed_in": True,
        "citizen_name": citizen_name.strip() if citizen_name else "Citizen Beneficiary",
        "mobile": mobile.strip() if mobile else "9876543210",
        "role": role if role in ["citizen", "official"] else "citizen",
        "district": district.strip() if district else "Pune, Maharashtra",
        "signed_in_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(session, f, indent=2, ensure_ascii=False)
    return session
