import grpc
import logging
from concurrent import futures

from grpc.health.v1 import health, health_pb2_grpc


logger = logging.getLogger(__name__)


class GRPCServer:
    def __init__(self, threads: int, port: str) -> None:
        self.threads = threads
        self.port = port
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.threads))

    def add_servicer(self, method, servicer) -> None:
        method(servicer, self.server)

    def serve(self) -> None:
        self._configure_health_check()
        self.server.add_insecure_port(f"[::]:{self.port}")
        self.server.start()
        logger.info(f"GRPC Server listining on port: {self.port}")
        self.server.wait_for_termination()

    def _configure_health_check(self) -> None:
        # Health Check
        health_servicer = health.HealthServicer(
            experimental_non_blocking=True,
            experimental_thread_pool=futures.ThreadPoolExecutor(
                max_workers=self.threads
            ),
        )
        health_pb2_grpc.add_HealthServicer_to_server(health_servicer, self.server)
