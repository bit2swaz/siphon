import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parents[2] / "proto/gen/python"))

from concurrent import futures
import grpc
import numpy as np

import model_server_pb2 as pb2
import model_server_pb2_grpc as pb2_grpc
from .scorer import score_batch, load_model, current_version
from .config import GRPC_PORT


class ModelServerServicer(pb2_grpc.ModelServerServicer):
    def Score(self, request, context):
        user_embed  = np.array(request.user_embed, dtype=np.float32)
        video_ids   = [item.video_id for item in request.items]
        item_embeds = [np.array(item.item_embed, dtype=np.float32) for item in request.items]

        if not video_ids:
            return pb2.ScoreResponse(scores=[], model_version=current_version())

        results = score_batch(user_embed, video_ids, item_embeds)
        scores  = [pb2.ItemScore(video_id=vid, score=sc) for vid, sc in results]
        return pb2.ScoreResponse(scores=scores, model_version=current_version())

    def Reload(self, request, context):
        ok = load_model(request.version)
        return pb2.ReloadResponse(success=ok, message="ok" if ok else "failed")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    pb2_grpc.add_ModelServerServicer_to_server(ModelServerServicer(), server)
    server.add_insecure_port(f"[::]:{GRPC_PORT}")
    server.start()
    print(f"gRPC model-server listening on :{GRPC_PORT}", flush=True)
    return server
