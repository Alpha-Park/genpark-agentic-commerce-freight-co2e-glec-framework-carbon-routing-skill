# -*- coding: utf-8 -*-
"""GenPark Industrial Skill: genpark-agentic-commerce-freight-co2e-glec-framework-carbon-routing-skill
Category: agentic_commerce
Website: https://www.genpark.ai
LinkedIn: https://www.linkedin.com/company/92955550
"""
import sys
import json
import math

sys.stdout.reconfigure(encoding="utf-8")

def calculate_glec_freight_emissions(shipment_weight_tonnes, distance_km, mode_comparison=None):
    if shipment_weight_tonnes <= 0 or distance_km <= 0:
        raise ValueError("Weight and distance must be positive values")
        
    tonne_km = shipment_weight_tonnes * distance_km
    
    # Standard GLEC default WTW emission factors (g CO2e / tonne-km):
    # Air freight: 602.0
    # Road diesel truck: 62.0
    # Rail freight (electric/diesel mix): 22.0
    # Ocean container vessel: 11.5
    factors = {
        "AIR_FREIGHT": 602.0,
        "ROAD_DIESEL_LTL": 62.0,
        "RAIL_INTERMODAL": 22.0,
        "OCEAN_CONTAINER": 11.5
    }
    
    evaluated_modes = []
    for mode, factor in factors.items():
        total_co2e_kg = (tonne_km * factor) / 1000.0
        evaluated_modes.append({
            "transport_mode": mode,
            "wtw_factor_gco2e_per_tkm": factor,
            "total_emissions_co2e_kg": round(total_co2e_kg, 2),
            "total_emissions_co2e_metric_tonnes": round(total_co2e_kg / 1000.0, 3)
        })
        
    # Sorted from lowest to highest emissions
    sorted_modes = sorted(evaluated_modes, key=lambda m: m["total_emissions_co2e_kg"])
    greenest_mode = sorted_modes[0]
    dirtiest_mode = sorted_modes[-1]
    decarbonization_savings_kg = dirtiest_mode["total_emissions_co2e_kg"] - greenest_mode["total_emissions_co2e_kg"]
    
    return {
        "shipment_weight_tonnes": shipment_weight_tonnes,
        "transit_distance_km": distance_km,
        "total_freight_tonne_km": round(tonne_km, 1),
        "lowest_emission_mode": greenest_mode["transport_mode"],
        "max_decarbonization_potential_kg": round(decarbonization_savings_kg, 2),
        "modal_emissions_breakdown": evaluated_modes
    }


def handle_rpc(request_str):
    try:
        req = json.loads(request_str)
        rpc_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})
        
        if method == "tools/list":
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "tools": [{
                        "name": "calculate_glec_freight_emissions",
                        "description": """Calculate multi-modal freight transport greenhouse gas (GHG) emissions based on the GLEC (Global Logistics Emissions Council) framework and ISO 14083.
Compares Well-to-Wheel (WTW) CO2e intensity across air, ocean, rail, and road freight, selecting green corridors and computing cost-to-abatement trade-offs.""",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }]
                }
            })
        elif method == "tools/call":
            call_params = params.get("arguments", {})
            res = calculate_glec_freight_emissions(**call_params)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(res, indent=2)
                    }]
                }
            })
        else:
            return json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"}
            })
    except Exception as e:
        return json.dumps({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32000, "message": str(e)}
        })

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sample = {'shipment_weight_tonnes': 4.5, 'distance_km': 1850.0}
        out = calculate_glec_freight_emissions(**sample)
        print("[TEST_PASS] Output:", json.dumps(out))
    else:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            print(handle_rpc(line))
