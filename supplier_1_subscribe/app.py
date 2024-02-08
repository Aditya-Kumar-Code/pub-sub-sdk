import uvicorn
from fastapi import Body, FastAPI,HTTPException,status
from dapr.ext.fastapi import DaprApp
from pydantic import BaseModel,Field,ValidationError

subscriber_order_id=0
class OrderEvent(BaseModel):
    orderId: int = Field(..., description="ID of the order", gt=0, lt=10000)
    productName: str = Field(..., description="Name of the product", max_length=50)
    quantity: int = Field(..., description="Quantity of the product", gt=0)
    price: float = Field(..., description="Price of the product", gt=0, le=1000)

    
app = FastAPI()
dapr_app = DaprApp(app)
@dapr_app.subscribe(pubsub='pubsub', topic='any_topic')
def any_event_handler(order_event = Body()):
    try:
        event=order_event['data']
        order = {
            'orderId': event['publisher_order_id'],
            'productName': event['productName'],
            'quantity': event['quantity'],
            'price': event['price']
        }

        
        # Check if required keys are present
        if any(v is None for v in order.values()):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail="Invalid data format. Make sure all required fields are present.")

        try:
            model_validation = OrderEvent(**order)
            print('Order details')
            print('OrderId : %s' % model_validation.orderId, flush=True)
            print('productName : %s' % model_validation.productName, flush=True)
            print('quantity : %s' % model_validation.quantity, flush=True)
            print('price : %s' % model_validation.price, flush=True)
        except ValidationError as e:
            # Handle validation error
            print(f"Validation error: {e}")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
            
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail=str(e))



uvicorn.run(app,port=50051)