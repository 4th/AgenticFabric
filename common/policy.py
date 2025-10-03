import os, requests
OPA_URL = os.getenv("OPA_URL", "http://opa:8181/v1/data/agent/allow")

def check_action(input_payload: dict) -> bool:
    try:
        r = requests.post(OPA_URL, json={"input": input_payload}, timeout=2.0)
        r.raise_for_status()
        data = r.json().get("result")
        return bool(data.get("allow", False) if isinstance(data, dict) else data)
    except Exception:
        return True  # demo default; set False for fail-closed
