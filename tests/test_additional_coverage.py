"""Cenários adicionais para regras que os testes originais não isolam."""

from helpers import run_cli

def test_top_hotels_sort_by_amount_then_hotel_id(tmp_path):
    """O valor define o ranking; o ID só desempata valores iguais."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H99", "hotel_name": "Hotel Maior", "amount": "1200.00"},
            {"reservation_id": "R-2", "hotel_id": "H01", "hotel_name": "Hotel Segundo", "amount": "1000.00"},
            {"reservation_id": "R-3", "hotel_id": "H03", "hotel_name": "Hotel Empate B", "amount": "900.00"},
            {"reservation_id": "R-4", "hotel_id": "H02", "hotel_name": "Hotel Empate A", "amount": "900.00"},
        ],
        top=4,
    )

    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H99", "H01", "H02", "H03"]
    assert [hotel["total_brl"] for hotel in report["top_hotels"]] == [
        "1200.00",
        "1000.00",
        "900.00",
        "900.00",
    ]


def test_reads_all_reservations_when_input_exceeds_200_rows(tmp_path):
    """O total deve incluir todas as linhas, sem truncar o CSV."""
    rows = [
        {"reservation_id": f"R-{index}", "amount": "1.00"}
        for index in range(201)
    ]

    report = run_cli(tmp_path, rows)

    assert report["summary"]["total_reservations"] == 201
    assert report["summary"]["confirmed_reservations"] == 201
    assert report["summary"]["total_room_nights"] == 201
    assert report["summary"]["total_amount_brl"] == "201.00"


def test_non_confirmed_reservations_are_excluded_from_aggregations(tmp_path):
    """Canceladas e no-show contam no resumo de status, mas não nos agrupamentos."""
    report = run_cli(
        tmp_path,
        [
            {
                "reservation_id": "R-1",
                "hotel_id": "H01",
                "hotel_name": "Hotel Confirmado",
                "status": "CONFIRMED",
                "checkin_date": "2025-01-10",
                "checkout_date": "2025-01-12",
                "amount": "100.00",
            },
            {
                "reservation_id": "R-2",
                "hotel_id": "H02",
                "hotel_name": "Hotel Cancelado",
                "status": "CANCELLED",
                "checkin_date": "2025-01-15",
                "checkout_date": "2025-01-18",
                "amount": "500.00",
            },
            {
                "reservation_id": "R-3",
                "hotel_id": "H03",
                "hotel_name": "Hotel No-show",
                "status": "NO_SHOW",
                "checkin_date": "2025-02-01",
                "checkout_date": "2025-02-05",
                "amount": "700.00",
            },
        ],
    )

    assert report["summary"]["total_reservations"] == 3
    assert report["summary"]["confirmed_reservations"] == 1
    assert report["summary"]["cancelled_reservations"] == 1
    assert report["summary"]["no_show_reservations"] == 1
    assert report["by_month"] == [
        {"month": "2025-01", "reservations": 1, "room_nights": 2, "total_brl": "100.00"}
    ]
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01"]
