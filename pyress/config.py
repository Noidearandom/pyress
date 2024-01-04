import yaml


class Config:
    """A class to describe the configuration"""

    def __init__(self, config_file=None):
        if not config_file:
            self.conf_file = "~/config/pyress/config"
        else:
            self.conf_file = config_file
        self.list_of_links = []
        self.list_of_feeds = []
        self.conf = None

    def _get_feeds(self) -> None:
        if self.conf:
            self.list_of_links = list(self.conf.get("feeds"))

    def load(self) -> None:
        with open(self.conf_file, encoding="utf-8") as fd:
            self.conf = yaml.safe_load(fd)
        self._get_feeds()

    def save(self) -> None:
        pass
