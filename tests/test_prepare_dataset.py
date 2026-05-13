from pathlib import Path

from geoshield_mllm.datasets.prepare import prepare_dataset_from_config


def test_prepare_dataset_filters_dataset_and_writes_manifest(tmp_path: Path) -> None:
    image = tmp_path / "a.jpg"
    image.write_bytes(b"fake")
    source = tmp_path / "source.csv"
    source.write_text(
        "dataset,source_path,true_lat,true_lon,true_city,true_country,source_id\n"
        f"gsv,{image},31.2,121.4,Shanghai,China,gsv_a\n"
        f"im2gps3k,{image},1.0,2.0,Other,Country,im_a\n",
        encoding="utf-8",
    )
    config = tmp_path / "config.yaml"
    output = tmp_path / "manifest.csv"
    config.write_text(
        "\n".join(
            [
                "dataset_name: gsv",
                "subset_name: gsv_1_test",
                f"source_root: {tmp_path}",
                f"metadata_manifest: {source}",
                f"output_manifest: {output}",
                "seed: 1",
                "sample_size: 1",
                "split_name: test",
            ]
        ),
        encoding="utf-8",
    )
    report = prepare_dataset_from_config(config)
    assert report.discovered_rows == 1
    assert report.rows_with_coordinates == 1
    assert report.written_rows == 1
    assert "gsv_1_test" in output.read_text(encoding="utf-8")


def test_prepare_dataset_refuses_missing_coordinates(tmp_path: Path) -> None:
    image = tmp_path / "a.jpg"
    image.write_bytes(b"fake")
    source = tmp_path / "source.csv"
    source.write_text("dataset,source_path,source_id\n" f"gsv,{image},gsv_a\n", encoding="utf-8")
    config = tmp_path / "config.yaml"
    output = tmp_path / "manifest.csv"
    config.write_text(
        "\n".join(
            [
                "dataset_name: gsv",
                "subset_name: gsv_1_test",
                f"source_root: {tmp_path}",
                f"metadata_manifest: {source}",
                f"output_manifest: {output}",
                "seed: 1",
                "sample_size: 1",
                "split_name: test",
            ]
        ),
        encoding="utf-8",
    )
    report = prepare_dataset_from_config(config)
    assert report.discovered_rows == 1
    assert report.rows_with_coordinates == 0
    assert report.written_rows == 0
    assert not output.exists()


def test_prepare_dataset_handles_uppercase_im2gps3k_metadata(tmp_path: Path) -> None:
    image = tmp_path / "abc.jpg"
    image.write_bytes(b"fake")
    source = tmp_path / "source.csv"
    source.write_text("IMG_ID,LAT,LON\nabc.jpg,12.5,99.1\n", encoding="utf-8")
    config = tmp_path / "config.yaml"
    output = tmp_path / "manifest.csv"
    config.write_text(
        "\n".join(
            [
                "dataset_name: im2gps3k",
                "subset_name: im2gps3k_1_test",
                f"source_root: {tmp_path}",
                f"metadata_manifest: {source}",
                f"output_manifest: {output}",
                "seed: 1",
                "sample_size: 1",
                "split_name: test",
            ]
        ),
        encoding="utf-8",
    )
    report = prepare_dataset_from_config(config)
    assert report.written_rows == 1
    text = output.read_text(encoding="utf-8")
    assert "12.5,99.1" in text
    assert "abc.jpg" in text
