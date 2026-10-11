"""Strict IPv4 validation and unit tests.

Run the tests with:
    python sol_filename.py
"""

import unittest


def is_valid_ipv4(value: object) -> bool:
    """Return whether value is an IPv4 address in strict dotted-decimal form."""
    if not isinstance(value, str):
        return False

    octets = value.split(".")
    if len(octets) != 4:
        return False

    for octet in octets:
        # Checking ASCII explicitly avoids accepting Unicode numerals via
        # str.isdigit(), while the length check rejects empty/oversized parts.
        if not 1 <= len(octet) <= 3:
            return False
        if any(character < "0" or character > "9" for character in octet):
            return False
        if len(octet) > 1 and octet[0] == "0":
            return False
        if int(octet) > 255:
            return False

    return True


class TestIPv4Validation(unittest.TestCase):
    def test_valid_addresses(self) -> None:
        valid_addresses = (
            "0.0.0.0",
            "1.2.3.4",
            "10.0.0.1",
            "127.0.0.1",
            "192.168.1.1",
            "255.255.255.255",
            "0.10.100.255",
        )
        for address in valid_addresses:
            with self.subTest(address=address):
                self.assertTrue(is_valid_ipv4(address))

    def test_leading_zeros(self) -> None:
        for address in (
            "00.0.0.0",
            "01.2.3.4",
            "1.02.3.4",
            "1.2.003.4",
            "1.2.3.00",
            "000.000.000.000",
        ):
            with self.subTest(address=address):
                self.assertFalse(is_valid_ipv4(address))

    def test_out_of_range_octets(self) -> None:
        for address in (
            "256.0.0.0",
            "0.256.0.0",
            "0.0.256.0",
            "0.0.0.256",
            "999.1.1.1",
            "1.2.3.1000",
        ):
            with self.subTest(address=address):
                self.assertFalse(is_valid_ipv4(address))

    def test_invalid_characters_and_whitespace(self) -> None:
        for address in (
            "a.b.c.d",
            "192.168.1.a",
            "1.2.3.-4",
            "1.2.3.+4",
            "1.2.3.4 ",
            " 1.2.3.4",
            "1.2.3.4\n",
            "1.2.3.４",  # Unicode full-width digit
            "1,2,3,4",
            "1.2.3.4/24",
            "1.2.3.4:80",
        ):
            with self.subTest(address=address):
                self.assertFalse(is_valid_ipv4(address))

    def test_wrong_octet_count_or_empty_octets(self) -> None:
        for address in (
            "",
            "1",
            "1.2.3",
            "1.2.3.4.5",
            ".1.2.3",
            "1.2.3.",
            "1..2.3",
            "...",
        ):
            with self.subTest(address=address):
                self.assertFalse(is_valid_ipv4(address))

    def test_non_string_values(self) -> None:
        for value in (None, 1234, 1.2, True, b"1.2.3.4", ["1", "2", "3", "4"]):
            with self.subTest(value=value):
                self.assertFalse(is_valid_ipv4(value))


if __name__ == "__main__":
    unittest.main()
