"""IPv4 address validation without the ``ipaddress`` or ``re`` modules."""

import unittest

_DIGITS = frozenset("0123456789")


def is_valid_ipv4(address):
    """Return True if ``address`` is a strict dotted-decimal IPv4 address.

    Rules:
      * Exactly four octets separated by single dots.
      * Each octet consists only of ASCII digits 0-9 (no signs, spaces,
        or Unicode digits such as '٣' or '²').
      * Each octet is in the range 0-255.
      * No leading zeros ("0" is fine, "01" / "00" are not).
    Non-string inputs return False.
    """
    if not isinstance(address, str):
        return False

    octets = address.split(".")
    if len(octets) != 4:
        return False

    for octet in octets:
        if not octet or len(octet) > 3:
            return False
        if not all(ch in _DIGITS for ch in octet):
            return False
        if len(octet) > 1 and octet[0] == "0":
            return False
        if int(octet) > 255:
            return False

    return True


class TestIsValidIPv4(unittest.TestCase):
    def assertValid(self, *addresses):
        for addr in addresses:
            with self.subTest(addr=addr):
                self.assertTrue(is_valid_ipv4(addr))

    def assertInvalid(self, *addresses):
        for addr in addresses:
            with self.subTest(addr=addr):
                self.assertFalse(is_valid_ipv4(addr))

    def test_valid_addresses(self):
        self.assertValid(
            "0.0.0.0",
            "255.255.255.255",
            "192.168.1.1",
            "127.0.0.1",
            "10.0.0.255",
            "1.2.3.4",
            "100.50.25.0",
            "249.250.251.252",
        )

    def test_leading_zeros(self):
        self.assertInvalid(
            "01.2.3.4",
            "1.02.3.4",
            "1.2.003.4",
            "1.2.3.00",
            "00.0.0.0",
            "192.168.01.1",
            "0255.1.1.1",
        )

    def test_out_of_range(self):
        self.assertInvalid(
            "256.0.0.0",
            "0.256.0.0",
            "0.0.0.256",
            "999.999.999.999",
            "300.1.1.1",
            "1.1.1.1000",
            "1234.1.1.1",
        )

    def test_wrong_number_of_octets(self):
        self.assertInvalid(
            "",
            "1",
            "1.2",
            "1.2.3",
            "1.2.3.4.5",
            "1.2.3.4.",
            ".1.2.3.4",
            "1..2.3",
            "1.2..3.4",
            "...",
            "....",
        )

    def test_invalid_characters(self):
        self.assertInvalid(
            "a.b.c.d",
            "1.2.3.a",
            "1.2.3.4a",
            "0x1.2.3.4",
            "1,2,3,4",
            "1.2.3.4/24",
            "1.2.3.4:80",
            "1.2.3.-4",
            "+1.2.3.4",
            "1.2.3.4e0",
            "1_0.2.3.4",
        )

    def test_whitespace(self):
        self.assertInvalid(
            " 1.2.3.4",
            "1.2.3.4 ",
            "1. 2.3.4",
            "1.2 .3.4",
            "1.2.3.4\n",
            "\t1.2.3.4",
            " ",
        )

    def test_unicode_digits(self):
        # str.isdigit()/int() accept these, so they must be rejected explicitly.
        self.assertInvalid(
            "١.٢.٣.٤",          # Arabic-Indic digits
            "1.2.3.²",          # superscript two
            "１.２.３.４",        # full-width digits
        )

    def test_non_string_input(self):
        self.assertInvalid(None, 1234, 1.2, ["1", "2", "3", "4"], b"1.2.3.4")


if __name__ == "__main__":
    unittest.main(verbosity=2)
