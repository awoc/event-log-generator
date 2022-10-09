import os
from copy import deepcopy
from pm4py.objects.log.obj import EventLog, Trace, Event
import pm4py


def convert_dir_to_file(dir_path: str, file_name: str) -> None:
    """
    Merges all .xes files in a directory to a single .xes file.

    Parameters
    ----------
    dir_path
        Path to the folder
    file_name
        Output name of the resulting .xes file.

    Returns
    -------

    """
    for root, _, files in os.walk(dir_path):
        file_paths = [
            os.path.join(root, file) for file in files if file.endswith(".xes")
        ]
        convert_files(file_paths, file_name)


def convert_files(file_paths: list[str], file_name: str) -> None:
    """
    Merges a list of .xes files to a single .xes file.

    Parameters
    ----------
    file_paths
        List of xes files.
    file_name
        Output name of the resulting .xes file.

    Returns
    -------
    """
    traces = []
    extensions = {}
    properties = {}

    for idx, file_path in enumerate(file_paths):
        log = pm4py.read_xes(file_path)

        if idx == 0:
            extensions = create_extensions(log)
            properties = deepcopy(log.properties)

        for trace in log:
            traces.append(convert_trace(trace))

    traces.sort(key=lambda x: x[0]["time:timestamp"])

    event_log = EventLog(traces, extensions=extensions, properties=properties)
    pm4py.write_xes(event_log, file_name)


def create_extensions(log: EventLog) -> dict[str, str]:
    """
    Copies all extensions of an event log and adds message extension to it.

    Parameters
    ----------
    log
        Input event log.

    Returns
    -------
    extensions
        A dictionary of all extensions.
    """
    extensions = deepcopy(log.extensions)
    extensions["Message"] = {
        "prefix": "message",
        "uri": "https://cpee.org/~demo/corrins/message.xesext",
    }

    return extensions


def convert_trace(trace: Trace) -> Trace:
    """
    Converts a trace including events to valid trace with the message xes extension.

    Parameters
    ----------
    trace
        The trace that should be converted.

    Returns
    -------
    trace
        The converted trace.

    """
    # Add participant attribute from first event
    participant = trace[0]["org:group"]

    attributes = deepcopy(trace.attributes)
    properties = deepcopy(trace.properties)
    events = [convert_event(event) for event in trace]

    if participant is not None:
        attributes["message:participant"] = participant

    return Trace(events, attributes=attributes, properties=properties)


def convert_event(event: Event) -> Event:
    """
    Converts an event to valid event with the message xes extension.

    Parameters
    ----------
    event
        The event that should be converted.

    Returns
    -------
    event
        The converted event.
    """
    new_event = Event()
    message_type = None
    content = {"value": None}

    for key, value in event.items():
        match key:
            case "concept:name" | "time:timestamp":
                new_event[key] = value
            case "msgType":
                message_type = "message:sent" if value == "send" else "message:received"
                if len(content) > 0:
                    new_event[message_type] = content
            case "msgFlow":
                content["children"] = [("message:content", value)]
                if message_type is not None:
                    new_event[message_type] = content

    return new_event


if __name__ == "__main__":
    convert_dir_to_file("./input/real1", "./output/1_healthcare.xes")
