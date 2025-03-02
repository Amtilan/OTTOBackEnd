from django.http import HttpRequest
from django.urls import path
from ninja import NinjaAPI
from django.contrib.admin.views.decorators import staff_member_required


from core.api.schemas import PingResponseSchema, VersionResponseSchema
from core.api.v1.urls import router as v1_router

api=NinjaAPI(
    title='OTTO',
    docs_decorator=staff_member_required
)

@api.get("/ping", response=PingResponseSchema)
def ping(request: HttpRequest) -> PingResponseSchema:
    return PingResponseSchema(result=True)

@api.get("/current_version", response=VersionResponseSchema)
def version(request: HttpRequest) -> VersionResponseSchema:
    return VersionResponseSchema(version=0.1)

api.add_router('v1/', v1_router)


urlpatterns=[
    path("", api.urls),    
]