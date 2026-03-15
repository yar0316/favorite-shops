import json
from typing import Any, Dict

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    # TODO: Implement auth and routing for menus
    return {
        "statusCode": 501,
        "body": json.dumps({"error": "Not Implemented"})
    }
