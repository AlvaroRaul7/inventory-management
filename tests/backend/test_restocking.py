"""
Tests for restocking (demand recommendations + purchase orders) API endpoints.
"""
import pytest


class TestDemandRecommendationsEndpoint:
    """Test suite for GET /api/demand/recommendations."""

    def test_zero_budget_returns_no_recommendations(self, client):
        """Test that a zero budget yields no recommendations."""
        response = client.get("/api/demand/recommendations?budget=0")
        assert response.status_code == 200

        data = response.json()
        assert data["recommendations"] == []
        assert data["total_cost"] == 0
        assert data["remaining_budget"] == 0

    def test_recommendations_respect_budget(self, client):
        """Test that recommended items never exceed the given budget."""
        response = client.get("/api/demand/recommendations?budget=500")
        assert response.status_code == 200

        data = response.json()
        assert data["total_cost"] <= 500
        assert data["remaining_budget"] >= 0

        calculated_total = sum(r["subtotal"] for r in data["recommendations"])
        assert abs(calculated_total - data["total_cost"]) < 0.01

    def test_recommendations_only_include_shortfall_items(self, client):
        """Test that only items with forecasted_demand > current_demand are recommended."""
        response = client.get("/api/demand/recommendations?budget=100000")
        assert response.status_code == 200

        data = response.json()
        assert len(data["recommendations"]) > 0

        for rec in data["recommendations"]:
            assert rec["shortfall"] > 0
            assert rec["recommended_quantity"] > 0
            assert rec["recommended_quantity"] <= rec["shortfall"]

    def test_recommendation_structure(self, client):
        """Test that each recommendation has the expected fields and types."""
        response = client.get("/api/demand/recommendations?budget=100000")
        data = response.json()

        first = data["recommendations"][0]
        for field in [
            "item_sku", "item_name", "current_demand", "forecasted_demand",
            "shortfall", "trend", "recommended_quantity", "unit_cost",
            "subtotal", "lead_time_days"
        ]:
            assert field in first

        assert isinstance(first["recommended_quantity"], int)
        assert isinstance(first["unit_cost"], (int, float))
        assert isinstance(first["lead_time_days"], int)


class TestPurchaseOrdersEndpoints:
    """Test suite for GET/POST /api/purchase-orders."""

    def test_get_purchase_orders_empty_or_list(self, client):
        """Test that purchase orders endpoint returns a list."""
        response = client.get("/api/purchase-orders")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_purchase_order_round_trip(self, client):
        """Test creating a restock order and reading it back."""
        payload = {
            "items": [
                {
                    "item_sku": "WDG-001",
                    "item_name": "Industrial Widget Type A",
                    "quantity": 25,
                    "unit_cost": 42.5,
                    "lead_time_days": 12,
                    "supplier_name": "Acme Supply"
                }
            ],
            "notes": "test restock order"
        }
        response = client.post("/api/purchase-orders", json=payload)
        assert response.status_code == 201

        created = response.json()
        assert len(created) == 1
        order = created[0]
        assert order["item_sku"] == "WDG-001"
        assert order["quantity"] == 25
        assert order["status"] == "Pending"
        assert "order_number" in order
        assert "T" in order["expected_delivery_date"]

        # Verify it now appears in the list endpoint
        list_response = client.get("/api/purchase-orders")
        all_orders = list_response.json()
        assert any(o["id"] == order["id"] for o in all_orders)

    def test_create_purchase_order_expected_delivery_matches_lead_time(self, client):
        """Test that expected_delivery_date is created_date + lead_time_days."""
        from datetime import datetime

        payload = {
            "items": [
                {
                    "item_sku": "GSK-203",
                    "item_name": "High-Temperature Gasket",
                    "quantity": 10,
                    "unit_cost": 6.25,
                    "lead_time_days": 7,
                    "supplier_name": "Acme Supply"
                }
            ]
        }
        response = client.post("/api/purchase-orders", json=payload)
        order = response.json()[0]

        created = datetime.fromisoformat(order["created_date"])
        expected = datetime.fromisoformat(order["expected_delivery_date"])
        assert (expected - created).days == 7

    def test_create_purchase_order_requires_items(self, client):
        """Test that submitting an empty items list is rejected."""
        response = client.post("/api/purchase-orders", json={"items": []})
        assert response.status_code == 400

    def test_create_purchase_order_rejects_invalid_quantity(self, client):
        """Test that non-positive quantity is rejected with a validation error."""
        payload = {
            "items": [
                {
                    "item_sku": "WDG-001",
                    "item_name": "Industrial Widget Type A",
                    "quantity": 0,
                    "unit_cost": 42.5,
                    "lead_time_days": 12,
                    "supplier_name": "Acme Supply"
                }
            ]
        }
        response = client.post("/api/purchase-orders", json=payload)
        assert response.status_code == 422

    def test_create_purchase_order_rejects_excessive_lead_time(self, client):
        """Test that an unreasonable lead_time_days is rejected instead of causing a 500."""
        payload = {
            "items": [
                {
                    "item_sku": "WDG-001",
                    "item_name": "Industrial Widget Type A",
                    "quantity": 5,
                    "unit_cost": 42.5,
                    "lead_time_days": 999999,
                    "supplier_name": "Acme Supply"
                }
            ]
        }
        response = client.post("/api/purchase-orders", json=payload)
        assert response.status_code == 422

    def test_recommendations_rejects_negative_budget(self, client):
        """Test that a negative budget is rejected."""
        response = client.get("/api/demand/recommendations?budget=-100")
        assert response.status_code == 422

    def test_recommendations_exclude_already_ordered_quantity(self, client):
        """Test that placing an order reduces the shortfall used for future recommendations."""
        before = client.get("/api/demand/recommendations?budget=100000").json()
        before_rec = next(r for r in before["recommendations"] if r["item_sku"] == "GSK-203")

        client.post("/api/purchase-orders", json={
            "items": [
                {
                    "item_sku": "GSK-203",
                    "item_name": "High-Temperature Gasket",
                    "quantity": before_rec["shortfall"],
                    "unit_cost": before_rec["unit_cost"],
                    "lead_time_days": before_rec["lead_time_days"],
                    "supplier_name": "Acme Supply"
                }
            ]
        })

        after = client.get("/api/demand/recommendations?budget=100000").json()
        assert all(r["item_sku"] != "GSK-203" for r in after["recommendations"])

    def test_create_multiple_line_items(self, client):
        """Test submitting a restock order with multiple items creates multiple orders."""
        payload = {
            "items": [
                {
                    "item_sku": "FLT-405",
                    "item_name": "Oil Filter Cartridge",
                    "quantity": 5,
                    "unit_cost": 9.5,
                    "lead_time_days": 8,
                    "supplier_name": "Acme Supply"
                },
                {
                    "item_sku": "VLV-506",
                    "item_name": "Pressure Relief Valve",
                    "quantity": 3,
                    "unit_cost": 54.0,
                    "lead_time_days": 14,
                    "supplier_name": "Acme Supply"
                }
            ]
        }
        response = client.post("/api/purchase-orders", json=payload)
        assert response.status_code == 201
        assert len(response.json()) == 2
