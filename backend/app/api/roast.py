from fastapi import APIRouter
from pydantic import BaseModel

from app.services.roast.pipeline import roast_pipeline

router = APIRouter()


class RoastRequest(BaseModel):
    user_data: dict


@router.post("/roast")
def roast_user(req: RoastRequest):

    result = roast_pipeline(req.user_data)

    return result