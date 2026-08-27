"""Moudle that manages all incidents in the database."""

import xml.etree.ElementTree as ET
import json
import re
from datetime import datetime
from typing import List, Tuple, Dict, Optional
import os
import html
from bs4 import BeautifulSoup

from config.incident_config import (
    INCIDENT_TYPE,
    INCIDENT_STATE,
    INCIDENT_COLORS,
    INCIDENT_ARGUMENTS,
    INCIDENT_ARGUMENTS_V2
)
from util.file_util import get_xml_file
from util.time_util import convert_timestamp_to_readable
from config.constants import DATA_FOLDER_PATH
from data.database_manager import DatabaseManager


class IncidentManager:
    """Manages all incidents in the database."""

    def __init__(self):

        self.db_entries = (
            []
        )  # Raw database entries {"timestamp": "", "tidx": "", "type": "", "state": "", "args": []}
        self.xml_file_path = None
        self.text_dic: Dict[int, str] = {}
        self.true_incidents = (
            []
        )  # Clean incidents from database entries {"timestamp": "", "text": "", "label_color": "", "text_color": ""}

    def set_xml_file(self) -> None:
        """Set text dic for the incident manager."""
        self.xml_file_path = get_xml_file() if get_xml_file() is not None else None

    def load_text_dic(self) -> None:
        """Load text dictionary from XML file."""

        try:
            tree = ET.parse(self.xml_file_path)
            root = tree.getroot()

            for item in root.findall(".//item"):
                index_elem = item.find("index")
                text_elem = item.find("text")

                if index_elem is not None and text_elem is not None:
                    try:
                        index_num = int(index_elem.text)
                        text_content = text_elem.text or ""
                        self.text_dic[index_num] = text_content
                    except ValueError:
                        continue

        except Exception as e:
            pass

    def _get_text_by_index(self, index: int) -> Optional[str]:
        """
        Get text content by index number.

        Parameters:
            index (int): Index of text.
        """
        return self.text_dic.get(index)

    def _insert_arguments(self, base_text: str, args: List) -> str | None:
        """
        Insert arguments into base text.

        Parameters:
            base_text (str): Base string
            args (List): Arguments to insert into base string

        Returns:
            str: String with inserted arguments
        """
        if not base_text:
            return None

        words = base_text.split(" ")  # Splits on a single space
        new_words = []
        count = 0

        for word in words:
            if "%" in word:
                pattern = r"%[^%]*"
                # Pattern: % followed by any characters until the next %
                ########## or to the end of the string

                parts = re.findall(pattern, word)
                temp_parts = []

                for part in parts:

                    if "d" in part or "s" in part or "f" in part:

                        match = re.search(r"%.*?([a-zA-Z])(\d+)", part)
                        # Pattern: % followed by any characters and then letter(s), then capture digits
                        if match:
                            numerical_part = int(match.group(2))
                            if numerical_part == count:

                                # Remove numerical portion after part if its just
                                # a representation of the position of the argument in the argument list
                                if part.endswith(str(numerical_part)):
                                    part = part[: -len(str(numerical_part))]

                                elif part.endswith(
                                    f"{str(numerical_part)}."
                                ):  # Part ends with argument position with a "." after it
                                    numerical_part = (
                                        str(numerical_part) + "."
                                    )  # Temporarily add "." to number so you remove correct length
                                    part = (
                                        part[: -len(str(numerical_part))] + "."
                                    )  # Re-add the "." back into the part
                                count += 1

                        if "d" in part:

                            digit_len = None
                            match = re.search(r"%(\d+)d", part)
                            # Pattern: % followed by captured digits, then d
                            if match:

                                digit_len = match.group(1)
                                part = part.replace(digit_len, "")

                            if digit_len is not None:
                                digit_len = int(digit_len)

                                # longValue argument from arguments list filled to match the correct length
                                # Differs between DB versions
                                # Check V1 first, than V2
                                digit_to_insert = None
                                if INCIDENT_ARGUMENTS["d"] in args[0]:
                                    digit_to_insert = str(
                                        args[0][INCIDENT_ARGUMENTS["d"]]
                                    ).zfill(digit_len)
                                elif "_d" in args[0] and INCIDENT_ARGUMENTS_V2["d"] == args[0]["_d"]:
                                    digit_to_insert = str(
                                        args[0]["value"]
                                    ).zfill(digit_len)

                            else:
                                digit_to_insert = None
                                if INCIDENT_ARGUMENTS["d"] in args[0]:
                                    digit_to_insert = str(args[0][INCIDENT_ARGUMENTS["d"]])
                                elif "_d" in args[0] and INCIDENT_ARGUMENTS_V2["d"] == args[0]["_d"]:
                                    digit_to_insert = str(args[0]["value"])

                            part = part.replace("%d", digit_to_insert)
                            args.pop(0)

                        elif "s" in part:

                            # Find text to insert from text dic, then replace the %s with it
                            if INCIDENT_ARGUMENTS["s"] in args[0]:
                                part = part.replace(
                                    "%s",
                                    self._get_text_by_index(
                                        args[0][INCIDENT_ARGUMENTS["s"]]
                                    ),
                                )
                            elif "_d" in args[0] and INCIDENT_ARGUMENTS_V2["s"] == args[0]["_d"]:
                                part = part.replace(
                                    "%s",
                                    self._get_text_by_index(
                                        args[0]["value"]
                                    ),
                                )
                            args.pop(0)
                        else:

                            match = re.search(r"%\.(\d+)f", part)
                            # Pattern: Caputures digits between %. and f
                            if match:

                                precision = int(match.group(1))
                                # Replaces %.2f or similar with formatted number from argument

                                if INCIDENT_ARGUMENTS["f"] in args[0]:
                                    part = part.replace(
                                        f"%.{precision}f",
                                        f"{args[0][INCIDENT_ARGUMENTS["f"]]:.{precision}f}",
                                    )
                                elif "_d" in args[0] and INCIDENT_ARGUMENTS_V2["f"] == args[0]["_d"]:
                                    part = part.replace(
                                        f"%.{precision}f",
                                        f"{args[0]["value"]:.{precision}f}",
                                    )

                                args.pop(0)
                            else:

                                if INCIDENT_ARGUMENTS["f"] in args[0]:
                                    part = part.replace(
                                        "%f", str(args[0][INCIDENT_ARGUMENTS["f"]])
                                    )
                                elif "_d" in args[0] and INCIDENT_ARGUMENTS_V2["f"] == args[0]["_d"]:
                                    part = part.replace(
                                        "%f", str(args[0]["value"])
                                    )

                                args.pop(0)

                    else:
                        pass

                    temp_parts.append(part)

                injected_word = "".join(temp_parts)
                new_words.append(injected_word)

            else:

                new_words.append(word)

        final_text = self._check_for_user(" ".join(new_words))

        return final_text

    def _check_for_user(self, text: str) -> str:
        """
        Checks text for anywhere there needs to be a username filled in - and fills it in.

        Parameters:
            text (str): Original text

        Returns:
            str: Original text if no replacement needed, otherwise the original text with replacement.
        """

        pattern = r"User \d+"
        matches = re.findall(pattern, text)

        if matches:
            database_manager = DatabaseManager(
                os.path.join(DATA_FOLDER_PATH, "fbhmi.db")
            )
            digit_pattern = r"\d+"

            for match in matches:

                digits = re.findall(digit_pattern, match)
                query_results = database_manager.find_user_id(digits)
                if query_results:
                    user_name = query_results[0]["user_name"]
                    text = text.replace(str(digits[0]), user_name)
                else:
                    pass
                    # text = text.replace(str(digits[0]), "UNKNOWN")

            return text

        else:
            return text

    def _parse_help_text(self, base_help_text: str) -> str | None:
        """
        Parse help text and extract text.

        Parameters:
            base_help_text (str): Encoded help text

        Returns:
            str: Readable help text
        """

        if base_help_text:
            decoded_help_text = html.unescape(base_help_text)
            soup = BeautifulSoup(decoded_help_text, "html.parser")

            return soup.get_text(separator="/n")

        return None

    def add_db_entry(self, entry: dict) -> None:
        """Add an incident entry to the list."""

        try:
            self.db_entries.append(
                {
                    "timestamp": entry["timestamp"],
                    "tidx": entry["tidx"],
                    "help_tidx": entry["help_tidx"],
                    "type": entry["type"],
                    "state": entry["state"],
                    "args": json.loads(entry["args"]),
                }
            )
        except Exception as e:
            print(f"WARNING: BAD ENTRY {entry}")
            print(f"ERROR: {e}")

    def get_db_entries(self) -> List:
        """Get the list of db entries."""
        return self.db_entries[0]

    def get_incident_color(self, entry: dict) -> Tuple:
        """
        Get the color for the label and text of an incident.

        Parameters:
            entry (dict): Incident entry

        Returns:
            Tuple: Color for the label, color for the text
        """

        if entry["state"] in INCIDENT_STATE["clear"]:

            if (
                entry["type"] in INCIDENT_TYPE["event"]
            ):  # Incident is an event: return grey/green
                return INCIDENT_COLORS["clear"], INCIDENT_COLORS["event"]

            elif (
                entry["type"] in INCIDENT_TYPE["warning"]
            ):  # Incident is a warning: return grey/orange
                return INCIDENT_COLORS["clear"], INCIDENT_COLORS["warning"]

            else:  # Incident is an alarm: return grey/red
                return INCIDENT_COLORS["clear"], INCIDENT_COLORS["alarm"]

        else:

            if (
                entry["type"] in INCIDENT_TYPE["event"]
            ):  # Incident is an event: return green/black
                return INCIDENT_COLORS["event"], INCIDENT_COLORS["black_text"]

            elif (
                entry["type"] in INCIDENT_TYPE["warning"]
            ):  # Incident is a warning: return orange/black
                return INCIDENT_COLORS["warning"], INCIDENT_COLORS["black_text"]

            else:  # Incident is an alarm: return red/black
                return INCIDENT_COLORS["alarm"], INCIDENT_COLORS["black_text"]

    def clean_data(self) -> None:
        """
        Clean up all raw database entries into readable incidents.
        """

        for entry in self.db_entries:

            clean_incident = {}

            clean_incident["timestamp"] = convert_timestamp_to_readable(
                entry["timestamp"]
            )

            # Process text from text dic
            base_text = self._get_text_by_index(entry["tidx"])
            base_help_text = self._get_text_by_index(entry["help_tidx"])

            clean_incident["help_text"] = self._parse_help_text(base_help_text)

            clean_incident["text"] = self._insert_arguments(base_text, entry["args"])

            clean_incident["label_color"], clean_incident["text_color"] = (
                self.get_incident_color(entry)
            )

            self.true_incidents.append(clean_incident)

    def get_clean_incidents(self) -> List[Dict]:
        """
        Get all clean incidents.

        Returns:
            List: List of dictionaries containing readable timestamp, text, label_color, and text_color
        """
        return self.true_incidents
