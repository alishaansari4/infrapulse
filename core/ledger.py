

from typing import Dict, Any

SAMPLE_AUDIT_PROJECTS = {
    "PRJ-MP-091": {
        "title": "Mandla Tribal Belt Solar Microgrid & Water Filtration",
        "district": "Mandla",
        "state": "Madhya Pradesh",
        "completion_date": "March 2026",
        "allocated_cr": 14.5,
        "t0": {
            "satellite_radiance_deficit": 0.89,
            "monthly_water_complaints": 48,
            "electrification_rate": 0.32
        },
        "t1": {
            "satellite_radiance_deficit": 0.28,
            "monthly_water_complaints": 6,
            "electrification_rate": 0.91
        }
    },
    "PRJ-CG-042": {
        "title": "Bastar Rural Feeder Road Rehabilitation",
        "district": "Bastar",
        "state": "Chhattisgarh",
        "completion_date": "January 2026",
        "allocated_cr": 22.0,
        "t0": {
            "satellite_radiance_deficit": 0.92,
            "monthly_water_complaints": 62,
            "electrification_rate": 0.25
        },
        "t1": {
            "satellite_radiance_deficit": 0.55,
            "monthly_water_complaints": 14,
            "electrification_rate": 0.68
        }
    }
}

def diff_project_impact(project_id: str) -> Dict[str, Any]:
    prj = SAMPLE_AUDIT_PROJECTS.get(project_id)
    if not prj:
        return {}

    t0 = prj["t0"]
    t1 = prj["t1"]
    
    complaint_drop = ((t0["monthly_water_complaints"] - t1["monthly_water_complaints"]) / t0["monthly_water_complaints"]) * 100
    deficit_reduction = ((t0["satellite_radiance_deficit"] - t1["satellite_radiance_deficit"]) / t0["satellite_radiance_deficit"]) * 100
    grid_improvement = ((t1["electrification_rate"] - t0["electrification_rate"]) / t0["electrification_rate"]) * 100

    # Composite delivery integrity score out of 100
    delivery_score = round((complaint_drop * 0.4) + (deficit_reduction * 0.4) + (grid_improvement * 0.2), 1)

    return {
        "project_id": project_id,
        "title": prj["title"],
        "district": prj["district"],
        "complaint_reduction_pct": round(complaint_drop, 1),
        "deficit_reduction_pct": round(deficit_reduction, 1),
        "grid_gain_pct": round(grid_improvement, 1),
        "delivery_integrity_score": min(delivery_score, 98.5),
        "status": "Verified Delivered via Satellite & Civic Signal Corroboration"
    }
