package httpapi

import (
	"context"
	"encoding/json"
	"net/http"

	"fixture/internal/ordering"
)

type Handler struct {
	Load func(ctx context.Context, id ordering.OrderID) (ordering.Order, error)
	Save func(ctx context.Context, o ordering.Order) error
}

type orderRequest struct {
	OrderID string `json:"order_id"`
	Reason  string `json:"reason"`
}

func (h Handler) Place(w http.ResponseWriter, r *http.Request) {
	var req orderRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	id, err := ordering.NewOrderID(req.OrderID)
	if err != nil {
		http.Error(w, "invalid order id", http.StatusBadRequest)
		return
	}
	order, err := h.Load(r.Context(), id)
	if err != nil {
		http.Error(w, "not found", http.StatusNotFound)
		return
	}
	draft, ok := order.(ordering.DraftOrder)
	if !ok {
		http.Error(w, "order is not a draft", http.StatusConflict)
		return
	}
	if len(draft.Items) == 0 {
		http.Error(w, "order has no items", http.StatusUnprocessableEntity)
		return
	}
	placed := ordering.Place(draft)
	if err := h.Save(r.Context(), placed); err != nil {
		http.Error(w, "could not save", http.StatusInternalServerError)
		return
	}
	_ = json.NewEncoder(w).Encode(placed)
}

func (h Handler) Cancel(w http.ResponseWriter, r *http.Request) {
	var req orderRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	id, err := ordering.NewOrderID(req.OrderID)
	if err != nil {
		http.Error(w, "invalid order id", http.StatusBadRequest)
		return
	}
	order, err := h.Load(r.Context(), id)
	if err != nil {
		http.Error(w, "not found", http.StatusNotFound)
		return
	}
	cancelled, err := ordering.Cancel(order, req.Reason)
	if err != nil {
		http.Error(w, err.Error(), http.StatusConflict)
		return
	}
	if err := h.Save(r.Context(), cancelled); err != nil {
		http.Error(w, "could not save", http.StatusInternalServerError)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
