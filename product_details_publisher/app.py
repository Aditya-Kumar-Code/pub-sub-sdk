

from dapr.clients import DaprClient

from fastapi import FastAPI, HTTPException,status
import json
import logging
from pydantic import BaseModel,Field,ValidationError
logging.basicConfig(level=logging.INFO)
publisher_order_id=0

app = FastAPI()
class allordersconstraints(BaseModel):

    order_sender_name: str =Field(..., description="Order Sender Name", max_length=50)
    order_sender_id: int =Field(..., description="Order Sender id", gt=0, le=1000)
    product_id: int =Field(..., description="Product Id", gt=0  , le=1000)
    productName: str =Field(..., description="Product Name", max_length=50)
    quantity: int =Field(..., description="Quantity", gt=0,le=1000)
    price: float = Field(..., description="Price of the product", gt=0, le=1000)

@app.post("/publish-orders")
async def publish_orders(product_details: dict):
    try:
        
        
        order_received = {
                    'order_sender_name': product_details["order_sender_name"],
                    'order_sender_id':product_details["order_sender_id"],
                    'product_id': product_details["product_id"],
                    'productName': product_details["productName"],
                    'quantity': product_details["quantity"],
                    'price': product_details["price"],
                    
                }
        
        
        try:
            global publisher_order_id
            publisher_order_id+=1
            model_validation=allordersconstraints(**order_received)
            publisher_order={
                'publisher_order_id':publisher_order_id,
                'productName':model_validation.productName,
                'quantity':model_validation.quantity,
                'price':model_validation.price,

            }




        

            with DaprClient() as client:
                

                # Publish an event/message using Dapr PubSub
                result = client.publish_event(
                    pubsub_name='pubsub',
                    topic_name='any_topic',
                    data=json.dumps(publisher_order),
                    data_content_type='application/json',
                )
                logging.info('Published data: ' + json.dumps(publisher_order))
                return {"message": f"Order with orderId {publisher_order_id} and product {model_validation.productName} published successfully"}
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST , detail=f"{e} is required in the JSON payload")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
