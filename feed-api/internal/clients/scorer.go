// grpc-go NewClient + insecure creds, generated ModelServerClient
package clients

import (
	"context"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"

	"github.com/bit2swaz/siphon/feed-api/internal/retrieval"
	siphonpb "github.com/bit2swaz/siphon/proto/gen/go/siphon"
)

// itemVecFetcher supplies the 256-dim projected item embedding for a video_id.
// the model-server Score RPC computes cosine sim from the embeds we send so every
// candidate has to carry its vector. sending only video_id yields empty scores
type itemVecFetcher interface {
	ItemVec(ctx context.Context, videoID string) ([]float32, error)
}

type Scorer struct {
	client siphonpb.ModelServerClient
	items  itemVecFetcher
}

func NewScorer(addr string, items itemVecFetcher) (*Scorer, error) {
	conn, err := grpc.NewClient(addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return nil, err
	}
	return &Scorer{client: siphonpb.NewModelServerClient(conn), items: items}, nil
}

// ScoreBatch sends candidates (with item embeds) to model-server, overlays returned
// scores, and falls back to retrieval scores if the RPC fails so the feed still renders
func (s *Scorer) ScoreBatch(ctx context.Context, userEmbed []float32, cands []retrieval.Candidate) ([]retrieval.Candidate, int32, error) {
	items := make([]*siphonpb.ItemEmbed, 0, len(cands))
	for _, c := range cands {
		vec, err := s.items.ItemVec(ctx, c.VideoID)
		if err != nil || len(vec) == 0 {
			continue // no embed cached, so model-server cant score it; skip
		}
		items = append(items, &siphonpb.ItemEmbed{VideoId: c.VideoID, ItemEmbed: vec})
	}
	resp, err := s.client.Score(ctx, &siphonpb.ScoreRequest{UserEmbed: userEmbed, Items: items})
	if err != nil {
		return cands, 0, nil // fallback: keep retrieval order
	}
	scoreByID := make(map[string]float64, len(resp.Scores))
	for _, sc := range resp.Scores {
		scoreByID[sc.VideoId] = float64(sc.Score)
	}
	for i := range cands {
		if v, ok := scoreByID[cands[i].VideoID]; ok {
			cands[i].Score = v
		}
	}
	return cands, resp.ModelVersion, nil
}
