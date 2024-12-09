from ninja import Router
from ninja_jwt.authentication import AsyncJWTAuth

from core.api.v1.customers.handlers import router as Customers_router
from core.api.v1.products.handlers import router as Products_router

router=Router(tags=['v1'], auth=AsyncJWTAuth())
router.add_router('Customers/', Customers_router)
router.add_router('Products/', Products_router)