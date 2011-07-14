
from deft.tracker import UserError, load_with_storage
from deft.upgrade import create_upgrader
from deft.storage.overlay import OverlayStorage


class HistoricalBackend(object):
    def __init__(self, readonly_snapshot):
        self.readonly_snapshot = readonly_snapshot

    def init_tracker(warning_listener, **config_overrides):
        raise UserError("cannot initialise a tracker in a historical snapshot")
    
    def load_tracker(self, warning_listener):
        overlay = OverlayStorage(self.readonly_snapshot)
        create_upgrader().upgrade(overlay)
        return load_with_storage(overlay, warning_listener)

        
