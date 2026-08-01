package ranking

import (
	"math"
	"sort"

	"github.com/bit2swaz/siphon/feed-api/internal/retrieval"
)

const _freshnessHalfLifeHours = 48.0

func Rerank(candidates []retrieval.Candidate, flagged map[string]bool, nowMs int64) []retrieval.Candidate {
	// safety filter + aggressive freshness decay past 48h (score *= exp(-0.1*age))
	var eligible []retrieval.Candidate
	for _, c := range candidates {
		if flagged[c.VideoID] {
			continue
		}
		ageHours := float64(nowMs-c.CreatedAt) / float64(3600*1000)
		if ageHours > _freshnessHalfLifeHours {
			c.Score *= math.Exp(-0.1 * ageHours)
		}
		eligible = append(eligible, c)
	}

	sort.Slice(eligible, func(i, j int) bool {
		return eligible[i].Score > eligible[j].Score
	})

	// diversity: greedily place the highest remaining candidate that doesnt make
	// 3 consecutive from the same creator.O(n²) greedy, fine for ~500
	result := make([]retrieval.Candidate, 0, len(eligible))
	remaining := eligible
	for len(remaining) > 0 {
		placed := false
		for i, c := range remaining {
			n := len(result)
			if n < 2 || result[n-1].CreatorID != c.CreatorID || result[n-2].CreatorID != c.CreatorID {
				result = append(result, c)
				remaining = append(remaining[:i], remaining[i+1:]...)
				placed = true
				break
			}
		}
		if !placed {
			// cant satisfy diversity, so append the remainder as-is
			result = append(result, remaining...)
			break
		}
	}
	return result
}
