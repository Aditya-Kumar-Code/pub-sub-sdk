from cloudevents.http import from_http
import json
import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, Field, ValidationError

app = FastAPI()

app_port = os.getenv('APP_PORT', 6002)


class OrderEvent(BaseModel):
    orderId: int = Field(..., description="ID of the order", gt=0, lt=1000)
    productName: str = Field(..., description="Name of the product", max_length=50)
    quantity: int = Field(..., description="Quantity of the product", gt=0)
    price: float = Field(..., description="Price of the product", gt=0, le=1000)

# Register Dapr pub/sub subscriptions
@app.get('/dapr/subscribe')
def subscribe():
    subscriptions = [{
        'pubsubname': 'orderpubsub',
        'topic': 'orders',
        'route': 'orders'
    }]
    print('Dapr pub/sub is subscribed to: ' + json.dumps(subscriptions))
    return subscriptions


# Dapr subscription in /dapr/subscribe sets up this route
@app.post('/orders')
async def orders_subscriber(request: Request):
    try:
        event = from_http(request.headers, await request.body())
        order = {
            'orderId': event.data.get('orderId'),
            'productName': event.data.get('productName'),
            'quantity': event.data.get('quantity'),
            'price': event.data.get('price')
        }
        
        # Check if required keys are present
        if any(v is None for v in order.values()):
            raise HTTPException(status_code=400, detail="Invalid data format. Make sure all required fields are present.")

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
            raise HTTPException(status_code=422, detail=str(e))
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {'success': True}

uvicorn.run(app, port=6002)
