package clients

import (
	"encoding/base64"
	"encoding/binary"
	"math"
)

// decodeVecB64 decodes item_vec_b64: base64 of a numpy float32 array's raw bytes
// (little-endian, C-order) as written by seed.py and feature-service. the returned
// float32 slice is in the same 256-dim projected space stored in Qdrant
func decodeVecB64(b64 string) ([]float32, error) {
	raw, err := base64.StdEncoding.DecodeString(b64)
	if err != nil {
		return nil, err
	}
	vec := make([]float32, len(raw)/4)
	for i := range vec {
		vec[i] = math.Float32frombits(binary.LittleEndian.Uint32(raw[i*4:]))
	}
	return vec, nil
}
