"""Cenários adicionais para regras que os testes originais não isolam."""

import csv
import json
from pathlib import Path

import pytest

from helpers import run_cli
from onfly_report.cli import main


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _write_inputs(tmp_path, rows):
    """Cria arquivos de entrada para chamadas diretas ao CLI."""
    from helpers import BASE, COLUMNS

    input_path = tmp_path / "reservas.csv"
    rates_path = tmp_path / "rates.csv"
    with input_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows({**BASE, **row} for row in rows)
    rates_path.write_text(
        "currency,rate_to_brl\nBRL,1.000000\nUSD,5.420000\nEUR,5.880000\n",
        encoding="utf-8",
    )
    return input_path, rates_path


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


def test_readme_validation_sample_matches_expected_report(tmp_path):
    """A amostra oficial valida totais, mês do check-in e ranking consolidado."""
    output_path = tmp_path / "nested" / "sample-report.json"

    exit_code = main(
        [
            "--input",
            str(PROJECT_ROOT / "data" / "exemplo-validacao.csv"),
            "--rates",
            str(PROJECT_ROOT / "data" / "taxas_cambio.csv"),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert output_path.is_file()
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["summary"] == {
        "total_reservations": 12,
        "confirmed_reservations": 9,
        "cancelled_reservations": 2,
        "no_show_reservations": 1,
        "total_room_nights": 28,
        "total_amount_brl": "7566.00",
        "average_nightly_rate_brl": "270.21",
    }
    assert report["by_month"] == [
        {"month": "2025-01", "reservations": 8, "room_nights": 25, "total_brl": "6684.00"},
        {"month": "2025-02", "reservations": 1, "room_nights": 3, "total_brl": "882.00"},
    ]
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == [
        "H01",
        "H02",
        "H12",
        "H10",
        "H09",
    ]


def test_cli_rejects_top_less_than_one_with_exit_code_2(tmp_path):
    """--top inválido deve ser tratado como erro de argumento."""
    with pytest.raises(SystemExit) as error:
        main(["--input", "unused.csv", "--rates", "unused-rates.csv", "--top", "0"])

    assert error.value.code == 2


def test_cli_defaults_to_five_hotels_and_creates_output_directory(tmp_path):
    """Sem --top, o CLI usa cinco e cria diretórios de saída ausentes."""
    rows = [
        {
            "reservation_id": f"R-{index}",
            "hotel_id": f"H{index:02}",
            "hotel_name": f"Hotel {index}",
            "amount": f"{100 + index}.00",
        }
        for index in range(6)
    ]
    input_path, rates_path = _write_inputs(tmp_path, rows)
    output_path = tmp_path / "new" / "nested" / "report.json"

    exit_code = main(
        ["--input", str(input_path), "--rates", str(rates_path), "--output", str(output_path)]
    )

    assert exit_code == 0
    assert output_path.is_file()
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert len(report["top_hotels"]) == 5


def test_money_is_rounded_half_up_to_two_decimal_places(tmp_path):
    """Valores são somados com Decimal e arredondados half-up ao serializar."""
    report = run_cli(tmp_path, [{"reservation_id": "R-1", "amount": "1.005"}])

    assert report["summary"]["total_amount_brl"] == "1.01"
    assert report["summary"]["average_nightly_rate_brl"] == "1.01"
    assert report["by_month"][0]["total_brl"] == "1.01"
    assert report["top_hotels"][0]["total_brl"] == "1.01"


def test_average_nightly_rate_is_zero_when_there_are_no_room_nights(tmp_path):
    """Sem noites, a média deve ser serializada como 0.00."""
    report = run_cli(
        tmp_path,
        [
            {
                "reservation_id": "R-1",
                "checkin_date": "2025-01-10",
                "checkout_date": "2025-01-10",
                "rooms": "1",
                "amount": "100.00",
            }
        ],
    )

    assert report["summary"]["total_room_nights"] == 0
    assert report["summary"]["total_amount_brl"] == "100.00"
    assert report["summary"]["average_nightly_rate_brl"] == "0.00"


def test_months_are_sorted_and_use_checkin_month(tmp_path):
    """A agregação mensal usa o check-in e ordena os meses cronologicamente."""
    report = run_cli(
        tmp_path,
        [
            {
                "reservation_id": "R-1",
                "checkin_date": "2025-02-28",
                "checkout_date": "2025-03-02",
                "amount": "30.00",
            },
            {
                "reservation_id": "R-2",
                "checkin_date": "2024-12-31",
                "checkout_date": "2025-01-02",
                "amount": "20.00",
            },
            {
                "reservation_id": "R-3",
                "checkin_date": "2025-01-15",
                "checkout_date": "2025-01-16",
                "amount": "10.00",
            },
        ],
    )

    assert report["by_month"] == [
        {"month": "2024-12", "reservations": 1, "room_nights": 2, "total_brl": "20.00"},
        {"month": "2025-01", "reservations": 1, "room_nights": 1, "total_brl": "10.00"},
        {"month": "2025-02", "reservations": 1, "room_nights": 2, "total_brl": "30.00"},
    ]
