# order_service/grpc_server.py
import grpc
from concurrent import futures
import order_pb2
import order_pb2_grpc

from db import session
from models import Order

class OrderService(order_pb2_grpc.OrderServiceServicer):

    def MarkOrderPaid(self, request, context):
        order = session.query(Order).get(request.order_id)
        if not order:
            context.abort(grpc.StatusCode.NOT_FOUND, "Order not found")

        order.status = "PAID"
        session.commit()

        return order_pb2.MarkOrderPaidResponse(status="PAID")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    order_pb2_grpc.add_OrderServiceServicer_to_server(
        OrderService(), server
    )
    server.add_insecure_port("[::]:50052")
    server.start()
    server.wait_for_termination()