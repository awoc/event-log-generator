import os
import html
from datetime import datetime
from pathlib import Path
from typing import TextIO

from yaml import Loader, load_all
from classes.activity import Activity
from classes.trace import Trace
from classes.message import Message, MessageSent, MessageReceived


def convert_yaml_dir_to_xml(dir_path: str, file_name) -> None:
    """
    Merges all .yaml files in a directory that are in the CPEE format to a single .xes file.

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
        files = [os.path.join(root, file) for file in files if file.endswith(".yaml")]
        convert_yaml_to_xml(sorted(files), file_name)


def convert_yaml_to_xml(file_paths: list[str], file_name) -> None:
    """
    Merges a list of .yaml files in a directory that are in the CPEE format to a single .xes file.

    Parameters
    ----------
    file_paths
        List of .yaml files.
    file_name
        Output name of the resulting .xes file.

    Returns
    -------
    """
    event_log = []

    for file_path in file_paths:
        trace = {}
        events = []

        with open(file_path, encoding="UTF-8") as file:
            for data in load_all(file, Loader=Loader):
                if "log" in data:
                    log = data["log"]
                    if "trace" in log:
                        trace = log["trace"]
                if "event" in data:
                    event = data["event"]
                    if "concept:name" in event and event["id:id"] != "external":
                        events.append(event)

        trace["event"] = events
        event_log.append(trace)

    traces: list[Trace] = []

    for trace in event_log:
        activities = filter_events(trace["event"])
        trace_obj = Trace(
            activities,
            activities[0].date,
            {k: v for k, v in trace.items() if k != "event"},
        )
        traces.append(trace_obj)

    with open(file_name, "w+", encoding="UTF-8") as file:
        write_event_log(file, sorted(traces))


def filter_events(events: list) -> list[Activity]:
    """
    Maps events in the CPEE format to a list of activities.
    This function also removes lifecycle information.

    Parameters
    ----------
    events
        List of events in the CPEE format

    Returns
    -------
    activities
        List of activities.

    """
    activities: dict[Activity] = {}
    for event in events:
        # check if message is sent or received
        cpee_lifecycle = event["cpee:lifecycle:transition"]
        lifecycle_transition = event["lifecycle:transition"]
        event_uuid = event["cpee:activity_uuid"]

        if "data" in event and cpee_lifecycle == "activity/calling":
            event_data = event["data"]
            if "data_send" in event_data:
                request = event_data["data_send"][0]

                if event_uuid not in activities:
                    activities[event_uuid] = Activity()

                activity = activities[event_uuid]
                # Message sent
                if request["name"] == "file":
                    # Handle multiple parameter sent
                    content = request["value"].split(",")
                    activity.message = MessageSent(content)
                # Message received
                elif request["name"] == "value":
                    content = request["value"].split(",")
                    activity.message = MessageReceived(content)

        if cpee_lifecycle == "activity/done" and lifecycle_transition == "complete":
            if event_uuid not in activities:
                activities[event_uuid] = Activity()

            activity = activities[event_uuid]

            activity.attributes = {
                k: v
                for k, v in event.items()
                if k in ["time:timestamp", "concept:name", "concept:instance"]
            }

            activity.date = datetime.fromisoformat(
                activity.attributes["time:timestamp"]
            )

    return list(activities.values())


def write_event_log(file_obj: TextIO, traces: list[Trace]) -> None:
    """
    Writes a list of traces to an .xes event log.

    Parameters
    ----------
    file_obj
        Open file handler.
    traces
        List of traces.
    Returns
    -------

    """
    file_obj.write("""<?xml version="1.0" encoding="UTF-8"?>\n""")
    file_obj.write(
        """<log xes.version="1849-2016" xes.features="nested-attributes" xmlns="http://www.xes-standard.org/">\n"""
    )
    # Add extensions
    file_obj.write(
        """\t<extension name="Concept" prefix="concept" uri="http://www.xes-standard.org/concept.xesext" /> \n"""
    )
    file_obj.write(
        """\t<extension name="Time" prefix="time" uri="http://www.xes-standard.org/time.xesext" /> \n"""
    )
    file_obj.write(
        """\t<extension name="Message" prefix="message" uri="https://raw.githubusercontent.com/awoc/distributed-discovery/main/message.xesext" /> \n"""
    )

    for trace in traces:
        write_trace(file_obj, trace)

    file_obj.write("</log>\n")


def write_trace(file_obj: TextIO, trace: Trace) -> None:
    """
    Writes one trace to a file handler.

    Parameters
    ----------
    file_obj
        Open file handler.
    trace
        The trace.

    Returns
    -------

    """
    file_obj.write("\t<trace>\n")

    for name, value in trace.attributes.items():
        if name == "concept:name":
            file_obj.write(f"""\t\t<string key="{name}" value="{value}" />\n""")
        elif name == "cpee:name":
            file_obj.write(
                f"""\t\t<string key="message:participant" value="{value}" />\n"""
            )

    write_events(file_obj, trace.activities)

    file_obj.write("\t</trace>\n")


def write_events(file_obj: TextIO, activities: list[Activity]) -> None:
    """
    Writes events to a file handler.

    Parameters
    ----------
    file_obj
        Open file handler.
    activities
        List of activities.

    Returns
    -------

    """
    for activity in activities:
        file_obj.write("\t\t<event>\n")

        for name, value in activity.attributes.items():
            tag = "date" if name == "time:timestamp" else "string"
            file_obj.write(f"""\t\t\t<{tag} key="{name}" value="{value}" />\n""")

        if activity.message is not None:
            write_messages(file_obj, activity.message)

        file_obj.write("\t\t</event>\n")


def write_messages(file_obj: TextIO, message: Message) -> None:
    """
    Writes messages that are sent or received to a file handler.

    Parameters
    ----------
    file_obj
        Open file handler.
    message
        Content of the message.

    Returns
    -------

    """
    attribute_key = (
        "message:sent" if isinstance(message, MessageSent) else "message:received"
    )

    file_obj.write(f"""\t\t\t<list key="{attribute_key}">\n""")
    file_obj.write("\t\t\t\t<values>\n")

    for content in message.content:
        file_path = f"../../correlator/message-templates/{content}"

        text = Path(file_path).read_text(encoding="UTF-8")
        # Remove newlines
        text = " ".join(text.splitlines())
        escaped_text = html.escape(text)

        file_obj.write(
            f"""\t\t\t\t\t<string key="message:content" value="{escaped_text}"/>\n"""
        )

    file_obj.write("\t\t\t\t</values>\n")
    file_obj.write("\t\t\t</list>\n")


if __name__ == "__main__":
    convert_yaml_dir_to_xml(
        "./input/one-to-many-duplicate-messages",
        "output/one-to-many-duplicate-messages.xes",
    )
