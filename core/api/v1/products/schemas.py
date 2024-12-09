


from ninja import Schema


class ProductTakeSchema(Schema):
    access_token: str
    produtcs: list[str]
    cost: int
    
    
class RecieveMessage(Schema):
    message: str
    