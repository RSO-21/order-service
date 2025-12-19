# order_service/server.py
import grpc
from concurrent import futures
from app import models, database
import app.order_pb2, app.order_pb2_grpc
from sqlalchemy.orm import Session

class OrderServicer(app.order_pb2_grpc.OrderServiceServicer):

    def CreateOrder(self, request, context):
        db = database.get_db_session()
        order = models.Order(user_id=request.user_id)
        order.items = [models.OrderItem(offer_id=i.offer_id, quantity=i.quantity) for i in request.items]
        db.add(order)
        db.commit()
        db.refresh(order)
        return app.order_pb2.OrderResponse(order_id=order.id, user_id=order.user_id, payment_id=0, payment_status="PENDING")

    def UpdatePayment(self, request, context):
        db = database.get_db_session()
        order = db.query(models.Order).filter(models.Order.id == request.order_id).first()
        if not order:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Order not found")
            return app.order_pb2.OrderResponse()
        order.payment_id = request.payment_id
        order.payment_status = request.payment_status
        db.commit()
        db.refresh(order)
        return app.order_pb2.OrderResponse(
            order_id=order.id,
            user_id=order.user_id,
            payment_id=order.payment_id,
            payment_status=order.payment_status
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    app.order_pb2_grpc.add_OrderServiceServicer_to_server(OrderServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
