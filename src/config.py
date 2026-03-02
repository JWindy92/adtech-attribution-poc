# TODO: How to calculate ideal values

DEFAULT_ADSTOCK_PARAMS = {
    "ctv_spend": {"decay": 0.7, "max_lag": 8},
    "linear_tv_spend": {"decay": 0.6, "max_lag": 6},
    "search_spend": {"decay": 0.3, "max_lag": 2},
    "social_spend": {"decay": 0.5, "max_lag": 4},
}


DEFAULT_SATURATION_PARAMS = {
    "ctv_spend": {"alpha": 1.2, "gamma": 100000},
    "linear_tv_spend": {"alpha": 1.0, "gamma": 150000},
    "search_spend": {"alpha": 1.5, "gamma": 40000},
    "social_spend": {"alpha": 1.3, "gamma": 25000},
}

# DEFAULT_MMM_PARAMS = {
#     "samples": 2000,
#     "tune": 1000,
#     "target_accept": 0.9,
# }


class AppConfig:
    def __init__(self):
        self.saturation_params = DEFAULT_SATURATION_PARAMS
        self.media_columns = [
            "ctv_spend",
            "linear_tv_spend",
            "search_spend",
            "social_spend",
        ]


APP_CONFIG = AppConfig()
