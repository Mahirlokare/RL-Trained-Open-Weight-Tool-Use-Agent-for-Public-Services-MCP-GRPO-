"""
Synthetic trajectory generator for SFT warm-start and GRPO prompt generation.
Generates multi-turn public service scenarios with verified ground truth.
"""
import json
import random
from typing import List, Dict, Any

SCENARIOS = [
    {
        "type": "pmmvy_inquiry_and_check",
        "templates": [
            "I am pregnant and need to know about maternal assistance schemes. I am 24 years old with annual household income of 450000. I have my Aadhaar, MCP Card, and Bank Passbook.",
            "My wife is expecting our first child. She is 22. What benefits are available under PMMVY and can we apply? We have Aadhaar and MCP Card ready, plus bank details."
        ],
        "expected_tools": ["search_schemes", "verify_eligibility"],
        "scheme_id": "PMMVY",
        "age": 24,
        "income": 450000,
        "docs": ["Aadhaar", "MCP_Card", "Bank_Passbook"],
        "required_output_substrings": ["PMMVY", "eligible", "5000"]
    },
    {
        "type": "pm_kisan_full_booking",
        "templates": [
            "My father is a small farmer with 1.5 hectares of land. Does he qualify for PM-KISAN, and can you book an appointment for him at Pune North center? His name is Ramesh Patil, phone 9876543210.",
            "I want to check PM Kisan eligibility for farmer Devidas (age 52, 1.2 hectares land, Aadhaar and 7/12 land record available). If eligible, please book a slot at SEVA_PUNE_NORTH and send SMS to 9822334455."
        ],
        "expected_tools": ["get_scheme_details", "check_center_slots", "book_appointment", "send_confirmation_sms"],
        "scheme_id": "PM_KISAN",
        "center_id": "SEVA_PUNE_NORTH",
        "phone": "9822334455",
        "required_output_substrings": ["PM_KISAN", "BK-", "SEVA_PUNE_NORTH"]
    },
    {
        "type": "senior_ineligible_income",
        "templates": [
            "Can my grandfather (age 68) get aid under VAYO_SHRESTHA? His pension and business income is 550,000 annually. He has all identity documents.",
            "Check senior citizen assistance for Anant Rao (age 72). Annual income is 600,000 INR."
        ],
        "expected_tools": ["verify_eligibility"],
        "scheme_id": "VAYO_SHRESTHA",
        "age": 68,
        "income": 550000,
        "docs": ["Aadhaar", "Age_Proof", "Income_Certificate"],
        "required_output_substrings": ["exceeds", "ceiling", "not eligible"]
    }
]

def generate_synthetic_dataset(num_samples: int = 50) -> List[Dict[str, Any]]:
    dataset = []
    for i in range(num_samples):
        scen = random.choice(SCENARIOS)
        prompt = random.choice(scen["templates"])
        
        sample = {
            "task_id": f"task-synth-{i:03d}",
            "prompt": prompt,
            "ground_truth": {
                "expected_tools": scen["expected_tools"],
                "required_output_substrings": scen["required_output_substrings"],
                "scheme_id": scen.get("scheme_id")
            }
        }
        dataset.append(sample)
    return dataset

if __name__ == "__main__":
    data = generate_synthetic_dataset(20)
    print(f"Generated {len(data)} synthetic evaluation tasks.")
    print("Sample task:", json.dumps(data[0], indent=2))
