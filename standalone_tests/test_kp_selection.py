# Minimal standalone test logic for kpi_return selection

from custom_components.noaa_space_weather.sensor import kpi_return


class Dummy:
    def __init__(self, data):
        self.data = data


def test_prefers_estimated_kp():
    c = Dummy({"kp_index_data": {"estimated_kp": 2.67, "kp_index": 3}})
    assert kpi_return(c) == 2.67


def test_fallback_to_integer_kp():
    c = Dummy({"kp_index_data": {"kp_index": 3}})
    assert kpi_return(c) == 3
