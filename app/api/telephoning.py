from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.models.user import UserRole
from app.telephoning.main import Telephoning


router = APIRouter(prefix="/telephoning", tags=["telephoning"])


@router.get("/types")
def get_phone_types(user: CurrentUser):
    schemas = {}
    for flavor in Telephoning.instance().flavors.values():
        if flavor.is_public() or user.role == UserRole.ADMIN:
            print(flavor)
            schema = flavor.get_schema()
            if schema is not None:
                for phone_type in flavor.PHONE_TYPES:
                    schemas.update({phone_type: schema})
    return schemas
