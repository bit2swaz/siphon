package clients

import "testing"

// parity anchor: numpy float32 [1.5,-2.0,0.25].tobytes() base64. matches seed.py's
// item_vec_b64 encoding. guards against endianness/width drift in decodeVecB64
func TestDecodeVecB64_MatchesNumpy(t *testing.T) {
	got, err := decodeVecB64("AADAPwAAAMAAAIA+")
	if err != nil {
		t.Fatal(err)
	}
	want := []float32{1.5, -2.0, 0.25}
	if len(got) != len(want) {
		t.Fatalf("len: got %d want %d", len(got), len(want))
	}
	for i := range want {
		if got[i] != want[i] {
			t.Errorf("[%d]: got %v want %v", i, got[i], want[i])
		}
	}
}
