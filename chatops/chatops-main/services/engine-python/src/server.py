#!/usr/bin/env python3
# services/engine-python/src/server.py
# gRPC Engine Server for chatops Multi-Agent AI Platform
"""
Engine gRPC Server implementation.
Processes requests from gateway-ts via gRPC.
"""
import os
import sys
import time
import json
import logging
from concurrent import futures

import grpc
from grpc_health.v1 import health_pb2, health_pb2_grpc
from grpc_health.v1.health import HealthServicer

# Add proto path for generated files
PROTO_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'proto', 'generated')
sys.path.insert(0, PROTO_PATH)

try:
    import engine_pb2
    import engine_pb2_grpc
    PROTO_AVAILABLE = True
except ImportError:
    PROTO_AVAILABLE = False
    engine_pb2 = None
    engine_pb2_grpc = None


# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper()),
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","service":"engine","message":"%(message)s"}',
    datefmt='%Y-%m-%dT%H:%M:%SZ'
)
logger = logging.getLogger(__name__)


class EngineServicer:
    """
    Engine gRPC Service implementation.
    Handles processing requests from the gateway.
    """

    def __init__(self):
        self.processor = Processor()
        logger.info('Engine service initialized')

    def Process(self, request, context):
        """Process a single request."""
        start_time = time.time()
        trace_id = getattr(request, 'trace_id', 'unknown')

        logger.info(f'Processing request: trace_id={trace_id}')

        try:
            input_data = request.input
            options = json.loads(request.options) if request.options else {}

            result = self.processor.process(input_data, options)
            processing_time = int((time.time() - start_time) * 1000)

            logger.info(f'Request processed: trace_id={trace_id}, time={processing_time}ms')

            if PROTO_AVAILABLE:
                return engine_pb2.ProcessResponse(
                    output=result['output'],
                    metadata=result['metadata'],
                    processing_time=processing_time
                )
            else:
                # Return mock response for development
                return type('MockResponse', (), {
                    'output': result['output'],
                    'metadata': result['metadata'],
                    'processing_time': processing_time
                })()

        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            logger.error(f'Processing failed: trace_id={trace_id}, error={str(e)}')
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            if PROTO_AVAILABLE:
                return engine_pb2.ProcessResponse(
                    output='',
                    metadata={},
                    processing_time=processing_time
                )
            else:
                # Return mock error response for development
                return type('MockResponse', (), {
                    'output': '',
                    'metadata': {},
                    'processing_time': processing_time
                })()
    def HealthCheck(self, request, context):
        """Health check endpoint."""
        if PROTO_AVAILABLE:
            return engine_pb2.HealthResponse(
                status='healthy',
                service='engine-python',
                timestamp=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            )
        else:
            return type('MockHealthResponse', (), {
                'status': 'healthy',
                'service': 'engine-python',
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            })()


class Processor:
    """
    Core processing logic for the engine.
    """

    def __init__(self):
        self.version = '0.1.0'

    def process(self, input_data: str, options: dict) -> dict:
        """
        Process input data with given options.

        Args:
            input_data: The input string to process
            options: Processing options

        Returns:
            Dictionary with output and metadata
        """
        # Simulate processing
        output = self._transform(input_data, options)

        return {
            'output': output,
            'metadata': {
                'version': self.version,
                'processed_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'input_length': str(len(input_data)),
                'output_length': str(len(output)),
            }
        }

    def _transform(self, input_data: str, options: dict) -> str:
        """Apply transformation to input data."""
        mode = options.get('mode', 'default')

        if mode == 'uppercase':
            return input_data.upper()
        elif mode == 'lowercase':
            return input_data.lower()
        elif mode == 'reverse':
            return input_data[::-1]
        else:
            return f'Processed: {input_data}'


def serve(port: int = 50051, max_workers: int = 10) -> grpc.Server:
    """Start the gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))

    # Add Engine service
    if PROTO_AVAILABLE:
        engine_pb2_grpc.add_EngineServiceServicer_to_server(
            EngineServicer(), server
        )
    else:
        logger.warning('Proto files not available, running in mock mode')

    # Add health service
    health_servicer = HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    health_servicer.set('', health_pb2.HealthCheckResponse.SERVING)
    health_servicer.set('chatops.engine.EngineService', health_pb2.HealthCheckResponse.SERVING)

    server.add_insecure_port(f'[::]:{port}')

    logger.info(f'Engine server starting on port {port}')
    server.start()

    return server


def main():
    """Main entry point."""
    port = int(os.getenv('GRPC_PORT', '50051'))
    max_workers = int(os.getenv('MAX_WORKERS', '10'))

    server = serve(port=port, max_workers=max_workers)

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info('Shutting down engine server')
        server.stop(grace=5)


if __name__ == '__main__':
    main()
