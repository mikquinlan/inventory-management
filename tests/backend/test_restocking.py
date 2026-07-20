"""
Tests for restocking API endpoints.
"""
import pytest


class TestRestockingEndpoints:
    """Test suite for restocking-related endpoints."""

    def test_get_recommendations_returns_list(self, client):
        """Test getting restock recommendations returns 200 and a list."""
        response = client.get("/api/restocking/recommendations?budget=30000")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_recommendations_stay_within_budget(self, client):
        """Test that total line_cost of selected rows never exceeds budget."""
        budget = 30000
        response = client.get(f"/api/restocking/recommendations?budget={budget}")
        assert response.status_code == 200

        data = response.json()
        total_selected_cost = sum(row["line_cost"] for row in data if row["selected"])
        assert total_selected_cost <= budget

    def test_zero_budget_selects_nothing(self, client):
        """Test that budget=0 selects no rows."""
        response = client.get("/api/restocking/recommendations?budget=0")
        assert response.status_code == 200

        data = response.json()
        for row in data:
            assert row["selected"] is False
            assert row["recommended_quantity"] == 0

    def test_recommendation_row_structure(self, client):
        """Test that every row exposes the new cost/supplier/lead-time fields."""
        response = client.get("/api/restocking/recommendations?budget=50000")
        assert response.status_code == 200

        data = response.json()
        for row in data:
            assert "item_sku" in row
            assert "item_name" in row
            assert "unit_cost" in row
            assert "supplier" in row
            assert "lead_time_days" in row
            assert "current_demand" in row
            assert "forecasted_demand" in row
            assert "shortfall" in row
            assert "trend" in row
            assert "recommended_quantity" in row
            assert "line_cost" in row
            assert "selected" in row

    def test_create_order_success(self, client):
        """Test that POST creates an order and returns order_number/expected_delivery/total_value."""
        response = client.post("/api/restocking/orders", json={
            "budget": 10000,
            "items": [
                {
                    "item_sku": "WDG-001",
                    "item_name": "Industrial Widget Type A",
                    "quantity": 10,
                    "unit_cost": 12.50,
                    "supplier": "Precision Parts Co",
                    "lead_time_days": 14
                }
            ]
        })
        assert response.status_code == 201

        data = response.json()
        assert "order_number" in data
        assert data["order_number"].startswith("RST-2025-")
        assert "expected_delivery" in data
        assert "total_value" in data
        assert data["total_value"] == pytest.approx(125.0)

    def test_create_order_over_budget_returns_400(self, client):
        """Test that POST over budget returns 400."""
        response = client.post("/api/restocking/orders", json={
            "budget": 10,
            "items": [
                {
                    "item_sku": "WDG-001",
                    "item_name": "Industrial Widget Type A",
                    "quantity": 10,
                    "unit_cost": 12.50,
                    "supplier": "Precision Parts Co",
                    "lead_time_days": 14
                }
            ]
        })
        assert response.status_code == 400

    def test_create_order_empty_items_returns_400(self, client):
        """Test that POST with empty items returns 400."""
        response = client.post("/api/restocking/orders", json={
            "budget": 10000,
            "items": []
        })
        assert response.status_code == 400

    def test_get_submitted_orders_includes_created_newest_first(self, client):
        """Test that GET submitted orders includes the created one, newest first."""
        first = client.post("/api/restocking/orders", json={
            "budget": 10000,
            "items": [{
                "item_sku": "GSK-203",
                "item_name": "High-Temperature Gasket",
                "quantity": 5,
                "unit_cost": 8.25,
                "supplier": "Ironclad Seals Ltd",
                "lead_time_days": 10
            }]
        })
        assert first.status_code == 201
        second = client.post("/api/restocking/orders", json={
            "budget": 10000,
            "items": [{
                "item_sku": "FLT-405",
                "item_name": "Oil Filter Cartridge",
                "quantity": 5,
                "unit_cost": 15.40,
                "supplier": "Clearflow Filtration",
                "lead_time_days": 7
            }]
        })
        assert second.status_code == 201

        response = client.get("/api/restocking/orders")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        order_numbers = [o["order_number"] for o in data]
        assert second.json()["order_number"] in order_numbers
        assert first.json()["order_number"] in order_numbers
        # Newest first
        assert order_numbers.index(second.json()["order_number"]) < order_numbers.index(first.json()["order_number"])

    def test_demand_still_returns_200_with_new_optional_fields(self, client):
        """Test that /api/demand still returns 200 with the new optional fields present."""
        response = client.get("/api/demand")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        for row in data:
            assert "unit_cost" in row
            assert "supplier" in row
            assert "lead_time_days" in row
