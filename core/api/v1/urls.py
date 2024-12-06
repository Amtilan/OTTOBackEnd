from ninja import Router
from ninja_jwt.authentication import JWTAuth

from core.api.v1.customers.handlers import router as Customers_router


router=Router(tags=['v1'], auth=JWTAuth())
router.add_router('Customers/', Customers_router)