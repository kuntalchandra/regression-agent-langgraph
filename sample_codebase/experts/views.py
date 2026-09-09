from fastapi import APIRouter

router = APIRouter(prefix="/experts")


@router.post("/onboard")
def onboard_expert(payload: dict):
    """Onboard a new expert - the endpoint we'll simulate changing."""
    result = validate_and_create(payload)
    return result


@router.get("/{expert_id}")
def get_expert(expert_id: str):
    """Fetch expert details."""
    return {"expert_id": expert_id}


def validate_and_create(payload: dict):
    """Helper used by onboard_expert - not itself an endpoint."""
    return {"status": "created"}
