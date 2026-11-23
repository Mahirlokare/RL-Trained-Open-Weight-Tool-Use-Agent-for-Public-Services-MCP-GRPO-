"""
Public Services MCP Servers:
1. Scheme Service: Search & query government welfare schemes and criteria.
2. Document Service: Verify citizen documents and check eligibility rules.
3. Appointment Service: Slot availability and appointment bookings at Seva Kendra.
4. Notification Service: Dispatch SMS / WhatsApp confirmation tokens.
"""
from typing import Dict, Any, List
from mcp_servers.registry import MCPToolServer, MCPHub

# --- Database Mock Data ---
SCHEMES_DB = {
    "PMMVY": {
        "id": "PMMVY",
        "name": "Pradhan Mantri Matru Vandana Yojana",
        "category": "Maternal Health & Nutrition",
        "min_age": 19,
        "max_income_annual": 800000,
        "benefit_amount": 5000,
        "required_docs": ["Aadhaar", "MCP_Card", "Bank_Passbook"],
        "description": "Cash incentive for pregnant women and lactating mothers for health and nutrition."
    },
    "PM_KISAN": {
        "id": "PM_KISAN",
        "name": "PM Kisan Samman Nidhi",
        "category": "Agriculture & Farmer Support",
        "min_age": 18,
        "max_land_hectares": 2.0,
        "benefit_amount": 6000,
        "required_docs": ["Aadhaar", "Land_Record_7_12", "Bank_Passbook"],
        "description": "Income support of Rs. 6,000 per year in three equal installments to small farmers."
    },
    "VAYO_SHRESTHA": {
        "id": "VAYO_SHRESTHA",
        "name": "Senior Citizen Welfare & Assistive Devices",
        "category": "Elderly Care",
        "min_age": 60,
        "max_income_annual": 300000,
        "benefit_amount": 8000,
        "required_docs": ["Aadhaar", "Age_Proof", "Income_Certificate"],
        "description": "Assistance and physical aid devices for senior citizens from low-income households."
    }
}

SLOTS_DB = {
    "SEVA_PUNE_NORTH": ["2026-12-01 10:00 AM", "2026-12-01 02:00 PM", "2026-12-02 11:30 AM"],
    "SEVA_MUMBAI_CENTRAL": ["2026-12-01 09:30 AM", "2026-12-03 03:00 PM"],
    "SEVA_NAGPUR_EAST": ["2026-12-02 10:00 AM", "2026-12-04 01:00 PM"]
}

# --- Server 1: Scheme Service ---
def build_scheme_server() -> MCPToolServer:
    server = MCPToolServer("scheme-service", "Welfare scheme eligibility and database search")

    def search_schemes(query: str, category: str = None) -> Dict[str, Any]:
        results = []
        q = query.lower()
        for s in SCHEMES_DB.values():
            if q in s["name"].lower() or q in s["category"].lower() or q in s["id"].lower():
                if not category or category.lower() in s["category"].lower():
                    results.append(s)
        return {"total_matches": len(results), "schemes": results}

    def get_scheme_details(scheme_id: str) -> Dict[str, Any]:
        sid = scheme_id.upper()
        if sid in SCHEMES_DB:
            return {"found": True, "scheme": SCHEMES_DB[sid]}
        return {"found": False, "error": f"Scheme {scheme_id} not found."}

    server.register_tool(
        name="search_schemes",
        description="Search government welfare schemes by keyword or target sector",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term like 'farmer', 'maternal', 'pension'"},
                "category": {"type": "string", "description": "Optional category filter"}
            },
            "required": ["query"]
        },
        handler=search_schemes
    )

    server.register_tool(
        name="get_scheme_details",
        description="Retrieve full eligibility criteria and mandatory documents for a specific scheme ID",
        input_schema={
            "type": "object",
            "properties": {
                "scheme_id": {"type": "string", "description": "Unique scheme code (e.g. 'PMMVY', 'PM_KISAN')"}
            },
            "required": ["scheme_id"]
        },
        handler=get_scheme_details
    )
    return server

# --- Server 2: Document & Eligibility Service ---
def build_document_server() -> MCPToolServer:
    server = MCPToolServer("document-service", "Citizen document verification and eligibility checking")

    def verify_eligibility(scheme_id: str, citizen_age: int, annual_income: float, documents_available: List[str]) -> Dict[str, Any]:
        sid = scheme_id.upper()
        if sid not in SCHEMES_DB:
            return {"eligible": False, "reason": f"Unknown scheme {scheme_id}"}
        scheme = SCHEMES_DB[sid]
        
        # Age check
        if citizen_age < scheme.get("min_age", 0):
            return {"eligible": False, "reason": f"Age {citizen_age} is below minimum requirement of {scheme['min_age']} years."}
        
        # Income check
        if scheme.get("max_income_annual") and annual_income > scheme["max_income_annual"]:
            return {"eligible": False, "reason": f"Income Rs. {annual_income} exceeds ceiling of Rs. {scheme['max_income_annual']}."}
        
        # Document completeness check
        missing = [doc for doc in scheme["required_docs"] if doc not in documents_available]
        if missing:
            return {
                "eligible": True,
                "documentation_ready": False,
                "missing_documents": missing,
                "message": f"Eligible in principle, but missing required proofs: {', '.join(missing)}"
            }

        return {
            "eligible": True,
            "documentation_ready": True,
            "benefit_amount": scheme["benefit_amount"],
            "message": "Citizen fulfills all age, income, and documentation criteria."
        }

    server.register_tool(
        name="verify_eligibility",
        description="Validate if a citizen qualifies for a scheme based on age, income, and available documents",
        input_schema={
            "type": "object",
            "properties": {
                "scheme_id": {"type": "string", "description": "Scheme code (e.g. 'PMMVY')"},
                "citizen_age": {"type": "integer", "description": "Citizen age in years"},
                "annual_income": {"type": "number", "description": "Annual household income in INR"},
                "documents_available": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of documents present (e.g. ['Aadhaar', 'MCP_Card', 'Bank_Passbook'])"
                }
            },
            "required": ["scheme_id", "citizen_age", "annual_income", "documents_available"]
        },
        handler=verify_eligibility
    )
    return server

# --- Server 3: Appointment Service ---
def build_appointment_server() -> MCPToolServer:
    server = MCPToolServer("appointment-service", "Seva Kendra center appointment management")

    def check_center_slots(center_id: str) -> Dict[str, Any]:
        cid = center_id.upper()
        if cid in SLOTS_DB:
            return {"center_id": cid, "available_slots": SLOTS_DB[cid]}
        return {"center_id": cid, "available_slots": [], "error": "Center ID not found. Use SEVA_PUNE_NORTH, SEVA_MUMBAI_CENTRAL, or SEVA_NAGPUR_EAST."}

    def book_appointment(center_id: str, slot_time: str, citizen_name: str, scheme_id: str) -> Dict[str, Any]:
        cid = center_id.upper()
        if cid not in SLOTS_DB or slot_time not in SLOTS_DB[cid]:
            return {"success": False, "error": f"Slot '{slot_time}' is not available at {center_id}."}
        
        # Book and remove slot
        SLOTS_DB[cid].remove(slot_time)
        booking_ref = f"BK-{cid[:4]}-{abs(hash(citizen_name + slot_time)) % 100000}"
        return {
            "success": True,
            "booking_reference": booking_ref,
            "center": cid,
            "slot_time": slot_time,
            "citizen_name": citizen_name,
            "scheme_id": scheme_id
        }

    server.register_tool(
        name="check_center_slots",
        description="Query available appointment timeslots for a designated public service center",
        input_schema={
            "type": "object",
            "properties": {
                "center_id": {"type": "string", "description": "Service center ID (e.g. 'SEVA_PUNE_NORTH')"}
            },
            "required": ["center_id"]
        },
        handler=check_center_slots
    )

    server.register_tool(
        name="book_appointment",
        description="Book a verified verification slot at a Seva Kendra center",
        input_schema={
            "type": "object",
            "properties": {
                "center_id": {"type": "string", "description": "Service center ID"},
                "slot_time": {"type": "string", "description": "Exact chosen slot time from check_center_slots"},
                "citizen_name": {"type": "string", "description": "Full citizen name"},
                "scheme_id": {"type": "string", "description": "Scheme code"}
            },
            "required": ["center_id", "slot_time", "citizen_name", "scheme_id"]
        },
        handler=book_appointment
    )
    return server

# --- Server 4: Notification Service ---
def build_notification_server() -> MCPToolServer:
    server = MCPToolServer("notification-service", "Citizen SMS and alert dispatch")

    def send_confirmation_sms(phone_number: str, booking_reference: str, message: str) -> Dict[str, Any]:
        if len(phone_number.replace("+", "").replace("-", "")) < 10:
            return {"sent": False, "error": "Invalid phone number format. Minimum 10 digits required."}
        return {
            "sent": True,
            "dispatch_id": f"SMS-TX-{abs(hash(booking_reference)) % 999999}",
            "recipient": phone_number,
            "booking_reference": booking_reference,
            "status": "DELIVERED"
        }

    server.register_tool(
        name="send_confirmation_sms",
        description="Send an SMS booking confirmation and instruction ticket to the citizen's mobile phone",
        input_schema={
            "type": "object",
            "properties": {
                "phone_number": {"type": "string", "description": "10-digit mobile number"},
                "booking_reference": {"type": "string", "description": "Appointment reference token"},
                "message": {"type": "string", "description": "Brief confirmation text with date/location"}
            },
            "required": ["phone_number", "booking_reference", "message"]
        },
        handler=send_confirmation_sms
    )
    return server

def create_default_mcp_hub() -> MCPHub:
    """Builds and wires all 4 standard MCP tool servers into a unified hub."""
    hub = MCPHub()
    hub.add_server(build_scheme_server())
    hub.add_server(build_document_server())
    hub.add_server(build_appointment_server())
    hub.add_server(build_notification_server())
    return hub
