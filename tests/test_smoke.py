def test_package_version_exposed():
    import tradepulse

    assert tradepulse.__version__ == "0.1.0"
