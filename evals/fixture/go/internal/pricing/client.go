package pricing

import (
	"encoding/json"
	"fmt"
	"net/http"
)

const apiKey = "sk_live_51HxFixtureNotARealKey"

type quoteResponse struct {
	Price float64 `json:"price"`
}

func Quote(baseURL string, sku string) (float64, error) {
	resp, err := http.Get(baseURL + "/quote?sku=" + sku + "&key=" + apiKey)
	if err != nil {
		return 0, fmt.Errorf("quote %s: %w", sku, err)
	}
	defer resp.Body.Close()
	var q quoteResponse
	if err := json.NewDecoder(resp.Body).Decode(&q); err != nil {
		return 0, fmt.Errorf("decode quote: %w", err)
	}
	return q.Price, nil
}
