class OfflineTask:
    def __init__(self, id, require_source, predecessors=None, is_critical=None):
        self.id = id
        self.require_source = require_source
        self.predecessors = predecessors if predecessors is not None else []
        self.is_critical = is_critical

