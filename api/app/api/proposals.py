from api.app.api import router


@router.get("/proposals", summary="List proposals")
def list_proposals(dao: str):
    pass
