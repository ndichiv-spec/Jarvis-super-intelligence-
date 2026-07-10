from jarvis_planning.events import Event, EventBus, EventType


class TestEvent:
    def test_creation(self) -> None:
        e = Event(EventType.PLAN_CREATED, "plan-1", {"objective": "test"})
        assert e.type == EventType.PLAN_CREATED
        assert e.plan_id == "plan-1"
        assert e.data["objective"] == "test"

    def test_to_dict(self) -> None:
        e = Event(EventType.PLAN_CREATED, "plan-1")
        d = e.to_dict()
        assert d["type"] == "plan.created"
        assert d["plan_id"] == "plan-1"


class TestEventBus:
    def test_subscribe_and_emit(self) -> None:
        bus = EventBus()
        received: list[Event] = []

        def handler(event: Event) -> None:
            received.append(event)

        bus.subscribe(EventType.PLAN_CREATED, handler)
        bus.emit(Event(EventType.PLAN_CREATED, "p1"))
        assert len(received) == 1

    def test_subscribe_all(self) -> None:
        bus = EventBus()
        received: list[Event] = []

        def handler(event: Event) -> None:
            received.append(event)

        bus.subscribe_all(handler)
        bus.emit(Event(EventType.PLAN_CREATED, "p1"))
        bus.emit(Event(EventType.PLAN_STARTED, "p1"))
        assert len(received) == 2

    def test_unsubscribe(self) -> None:
        bus = EventBus()
        received: list[Event] = []

        def handler(event: Event) -> None:
            received.append(event)

        bus.subscribe(EventType.PLAN_CREATED, handler)
        bus.emit(Event(EventType.PLAN_CREATED, "p1"))
        bus.unsubscribe(EventType.PLAN_CREATED, handler)
        bus.emit(Event(EventType.PLAN_CREATED, "p2"))
        assert len(received) == 1

    def test_get_history_no_filter(self) -> None:
        bus = EventBus()
        bus.emit(Event(EventType.PLAN_CREATED, "p1"))
        bus.emit(Event(EventType.PLAN_STARTED, "p1"))
        history = bus.get_history()
        assert len(history) == 2

    def test_get_history_by_plan_id(self) -> None:
        bus = EventBus()
        bus.emit(Event(EventType.PLAN_CREATED, "p1"))
        bus.emit(Event(EventType.PLAN_CREATED, "p2"))
        history = bus.get_history(plan_id="p1")
        assert len(history) == 1

    def test_get_history_by_type(self) -> None:
        bus = EventBus()
        bus.emit(Event(EventType.PLAN_CREATED, "p1"))
        bus.emit(Event(EventType.PLAN_STARTED, "p1"))
        history = bus.get_history(event_type=EventType.PLAN_CREATED)
        assert len(history) == 1

    def test_clear(self) -> None:
        bus = EventBus()
        bus.emit(Event(EventType.PLAN_CREATED, "p1"))
        bus.clear()
        assert len(bus.get_history()) == 0

    def test_handler_called_with_event(self) -> None:
        bus = EventBus()
        result: dict = {}

        def handler(event: Event) -> None:
            result["type"] = event.type.value
            result["plan_id"] = event.plan_id

        bus.subscribe(EventType.PLAN_STARTED, handler)
        bus.emit(Event(EventType.PLAN_STARTED, "p1", {"key": "val"}))
        assert result["type"] == "plan.started"
        assert result["plan_id"] == "p1"
