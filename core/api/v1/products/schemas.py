from typing import Any, List, Dict
from ninja import Schema

class ProductTakeSchema(Schema):
    access_token: str
    products: List[str]
    cost: int

class ProductTakeOutSchema(Schema):
    title: str
    picture_url: str
    
class RecieveMessage(Schema):
    message: str


    
class OutputProductAnalysisResult(Schema):
    result: List[Dict[str, Any]] 
