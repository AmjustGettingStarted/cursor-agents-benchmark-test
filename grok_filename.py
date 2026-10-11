"""Strict IPv4 address validation without ipaddress or regular expressions.

A string is a valid IPv4 address only when all of the following hold:

* It is a ``str`` made of exactly four dot-separated octets.
* Every octet is a decimal integer in the inclusive range 0..255.
* No octet has a leading zero. ``0`` itself is allowed; ``00`` and ``01`` are not.
* Every character of an octet is an ASCII digit (``0``-``9``). Signs, spaces,
  letters, hex prefixes, and non-ASCII digits are rejected.

This matches the strict dotted-decimal form. It does not accept CIDR suffixes,
ports, whitespace, or legacy octal/hex octet spellings.
"""

from __future__ import annotations

import unittest


def is_valid_ipv4(address: object) -> bool:
    """Return True if ``address`` is a strict dotted-decimal IPv4 string.

    Non-strings return False. The function never raises for bad input.
    """
    if not isinstance(address, str):
        return False

    # Four octets and three dots: "255.255.255.255" is 15 characters.
    # Anything longer cannot be a strict dotted-decimal address.
    if len(address) < 7 or len(address) > 15:
        return False

    octets = address.split(".")
    if len(octets) != 4:
        return False

    for octet in octets:
        if not _is_valid_octet(octet):
            return False
    return True


def _is_valid_octet(octet: str) -> bool:
    """Return True if ``octet`` is a decimal integer from 0 through 255.

    Leading zeros are rejected except for the single digit ``0``.
    """
    length = len(octet)
    if length == 0 or length > 3:
        return False

    # "0" is valid. "00", "01", and "001" are not.
    if length > 1 and octet[0] == "0":
        return False

    for character in octet:
        if character < "0" or character > "9":
            return False

    return int(octet) <= 255


class IPv4ValidationTests(unittest.TestCase):
    """Edge cases for strict dotted-decimal IPv4 validation."""

    def test_typical_valid_addresses(self) -> None:
        valid = (
            "0.0.0.0",
            "0.0.0.1",
            "1.2.3.4",
            "8.8.8.8",
            "10.0.0.1",
            "127.0.0.1",
            "172.16.0.1",
            "192.168.0.1",
            "192.168.1.1",
            "192.168.1.10",
            "203.0.113.5",
            "255.255.255.255",
            "255.255.255.0",
            "1.0.0.0",
            "0.0.0.255",
            "9.8.7.6",
            "100.100.100.100",
            "199.255.0.10",
        )
        for address in valid:
            with self.subTest(address=address):
                self.assertTrue(is_valid_ipv4(address))

    def test_leading_zeros_are_rejected(self) -> None:
        invalid = (
            "00.0.0.0",
            "0.00.0.0",
            "0.0.00.0",
            "0.0.0.00",
            "01.2.3.4",
            "1.02.3.4",
            "1.2.03.4",
            "1.2.3.04",
            "192.168.001.1",
            "192.168.1.01",
            "192.168.01.1",
            "010.1.1.1",
            "1.1.1.001",
            "000.000.000.000",
            "001.002.003.004",
            "08.08.08.08",
            "0.0.0.01",
        )
        for address in invalid:
            with self.subTest(address=address):
                self.assertFalse(is_valid_ipv4(address))

    def test_single_zero_octet_is_allowed(self) -> None:
        self.assertTrue(is_valid_ipv4("0.0.0.0"))
        self.assertTrue(is_valid_ipv4("10.0.0.0"))
        self.assertTrue(is_valid_ipv4("192.168.0.1"))
        self.assertTrue(is_valid_ipv4("1.2.3.0"))

    def test_out_of_range_octets(self) -> None:
        invalid = (
            "256.1.1.1",
            "1.256.1.1",
            "1.1.256.1",
            "1.1.1.256",
            "999.999.999.999",
            "256.256.256.256",
            "192.168.1.300",
            "300.168.1.1",
            "1.2.3.1000",
            "1234.1.1.1",
            "255.255.255.256",
            "1111.1.1.1",
            "1.999.1.1",
            "260.0.0.1",
        )
        for address in invalid:
            with self.subTest(address=address):
                self.assertFalse(is_valid_ipv4(address))

    def test_boundary_octets(self) -> None:
        self.assertTrue(is_valid_ipv4("0.0.0.0"))
        self.assertTrue(is_valid_ipv4("255.255.255.255"))
        self.assertTrue(is_valid_ipv4("0.255.0.255"))
        self.assertFalse(is_valid_ipv4("256.0.0.0"))
        self.assertFalse(is_valid_ipv4("0.0.0.256"))

    def test_invalid_characters(self) -> None:
        invalid = (
            "192.168.1.a",
            "192.168.a.1",
            "a.b.c.d",
            "abc.def.ghi.jkl",
            "192.168.1.1a",
            "192.168.1.1!",
            "192.168.1.1#",
            "192.168.1.-1",
            "-1.2.3.4",
            "1.2.-3.4",
            "+1.2.3.4",
            "1.+2.3.4",
            "1.2.3.+4",
            "0x1.2.3.4",
            "1.2.3.0x4",
            "1e2.3.4.5",
            "192.168.1.1/24",
            "192.168.1.1:80",
            "192,168,1,1",
            "192.168.1.1.",
            "192..168.1.1",
            "192.168.1.one",
            "192.168.1.１",  # fullwidth digit
            "１.2.3.4",
            "192.168.1.1\x00",
            "192.168.1.1\n",
            "192.168.1.1\t",
            "192.168.1.1\r",
        )
        for address in invalid:
            with self.subTest(address=address):
                self.assertFalse(is_valid_ipv4(address))

    def test_whitespace_is_rejected(self) -> None:
        invalid = (
            " 192.168.1.1",
            "192.168.1.1 ",
            "192.168.1.1  ",
            "192. 168.1.1",
            "192.168 .1.1",
            "192.168. 1.1",
            "192.168.1 .1",
            " 1.2.3.4",
            "1.2.3.4 ",
            "1.2.3. 4",
            "1.2. 3.4",
            "\t1.2.3.4",
            "1.2.3.4\n",
            "1. 2.3.4",
            "",
            " ",
            "   ",
            "\n",
            "1.2.3.4\t5",
        )
        for address in invalid:
            with self.subTest(address=repr(address)):
                self.assertFalse(is_valid_ipv4(address))

    def test_wrong_number_of_octets(self) -> None:
        invalid = (
            "",
            ".",
            "..",
            "...",
            "....",
            "1",
            "1.2",
            "1.2.3",
            "1.2.3.4.5",
            "1.2.3.4.5.6",
            "1.",
            ".1",
            "1.2.3.",
            ".1.2.3",
            "1..2.3",
            "1.2..3",
            "1...3",
            "...1",
            "1...",
            "192.168.1",
            "192.168.1.1.1",
            "1.2.3.4.",
            ".1.2.3.4",
            "1..2.3.4",
            "1.2.3..4",
            "1.2..3.4",
        )
        for address in invalid:
            with self.subTest(address=address):
                self.assertFalse(is_valid_ipv4(address))

    def test_non_string_inputs(self) -> None:
        invalid = (
            None,
            19216811,
            0,
            1.2,
            True,
            False,
            b"192.168.1.1",
            bytearray(b"1.2.3.4"),
            ["192", "168", "1", "1"],
            ("192", "168", "1", "1"),
            {"address": "1.2.3.4"},
            192.168,
        )
        for value in invalid:
            with self.subTest(value=value):
                self.assertFalse(is_valid_ipv4(value))

    def test_ipv6_and_other_lookalikes(self) -> None:
        invalid = (
            "::1",
            "2001:db8::1",
            "::ffff:192.168.1.1",
            "localhost",
            "example.com",
            "192.168.1.1/32",
            "[192.168.1.1]",
            "http://192.168.1.1",
            "192.168.1.1.",
            "192.168.1",
            "0",
            "255",
            "...",
            "....",
        )
        for address in invalid:
            with self.subTest(address=address):
                self.assertFalse(is_valid_ipv4(address))

    def test_does_not_interpret_octal_or_hex(self) -> None:
        # Legacy parsers treat a leading zero as octal (010 == 8). Strict
        # dotted-decimal rejects those spellings instead of converting them.
        self.assertFalse(is_valid_ipv4("010.010.010.010"))
        self.assertFalse(is_valid_ipv4("0x10.0x0.0x0.0x1"))
        self.assertTrue(is_valid_ipv4("10.10.10.10"))
        self.assertTrue(is_valid_ipv4("8.0.0.1"))


if __name__ == "__main__":
    unittest.main()
