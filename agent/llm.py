from typing import List, Dict, Any

def reason(goal: str, inputs: Dict[str, Any]) -> List[str]:
    if "order_id" in inputs:
        oid = inputs["order_id"]
        return [
            f"Check inventory for items in order {oid}",
            f"Process payment for order {oid}",
            f"Notify user of order {oid} status",
        ]
    return [
        f"Break down goal '{goal}' into actionable steps",
        "Call appropriate service APIs",
        "Return summarized result",
    ]
