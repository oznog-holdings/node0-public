"""Every generic pattern must catch its fixture and leave the clean page alone; private names
and rules must be honoured, including across a line break; the allow-list must be scoped and
reasoned; images must be walked to the end; the walker must reach every file and refuse what
it cannot read. Fixtures that carry a refused shape are base64 or assembled at runtime, so
this file passes the gate itself.  Run: python3 -B -m unittest discover -s tests"""
import base64
import importlib.util
import os
import re
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, "..", "tools", "sanitize-check.py")
spec = importlib.util.spec_from_file_location("sc", TOOL)
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)

d = lambda s: base64.b64decode(s).decode()
NOALLOW = sc.Allow(tempfile.mkdtemp())
scan = lambda text, names=(), rules=(), allow=NOALLOW: {h[2] for h in sc.scan_text("f.md", text, list(names), list(rules), allow)}

DIRTY = [  # (rule expected, base64 of a synthetic offending line)
    ("ipv4-literal", "dGhlIHN0b3JhZ2UgaG9zdCBhbnN3ZXJzIG9uIDEwLjAuMTAuMTE="),
    ("ipv4-literal", "d2FuIHNpZGUgNDYuMjI0LjExMS42NS8yOQ=="),
    ("ipv4-literal", "aG9zdCBub2RlXzEwLjAuMC4xIGlzIHRoZSBvbmU="),                        # embedded after an underscore
    ("ipv4-literal", "c2VlIDEwLjAuMC4xLmV4YW1wbGUubmV0"),                                 # address-bearing hostname
    ("ipv6-literal", "cmVhY2hhYmxlIGF0IGZkMTI6MzQ1Njo3ODlhOjoxIG92ZXIgdGhlIHR1bm5lbA=="),
    ("ipv6-literal", "bGluayBsb2NhbCBmZTgwOjoxIGFuZCBmZDEyOjoxIGFuZCBbZmU4MDo6MSVldGgwXQ=="),  # compressed, zone id
    ("ipv6-literal", "bWFwcGVkIDo6ZmZmZjpjMDAwOjIwMQ=="),
    ("internal-hostname-suffix", "c3NoIGJveC5sYW4="),
    ("mac-address", "ZXRoMCBjaGFuZ2VkIHRvIGQ4OjNhOmRkOjUxOjYxOmE2"),
    ("mac-address", "Y2lzY28gc3R5bGUgMDAxMS4yMjMzLjQ0NTU="),
    ("cgnat-or-mesh-range", "bGFwdG9wIGF0IDEwMC4xMDEuMTAyLjEwMw=="),
    ("email-address", "d3JpdGUgdG8gc29tZW9uZUBleGFtcGxlLm5ldCBmb3IgYWNjZXNz"),
    ("url-credential", "Y3VybCBodHRwczovL2JvYjpodW50ZXIyMkBob3N0LmV4YW1wbGUvYXBp"),
    ("url-credential", "aHR0cHM6Ly9ib2I6JGVjcmV0MTIzQGxvY2FsaG9zdC8="),                  # $ but not a variable
    ("private-key-block", "LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0="),
    ("ssh-public-key", "c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUV4YW1wbGVFeGFtcGxlRXhhbXBsZUV4YW1wbGUgaG9zdA=="),
    ("api-token-shape", "R0lUSFVCX1RPS0VOPWdocF9hYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ejAxMjM="),
    ("api-token-shape", "dXNlIGdpdGh1Yl9wYXRfMTFBQUFBQUFBMGFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhIGZvciB0aGUgbWlycm9y"),
    ("api-token-shape", "YmVhcmVyIGV5SmhiR2NpT2lKSVV6STFOaUo5LmUzMC5BQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUE="),  # {} payload
    ("secret-assignment", "cGFzc3dvcmQ6IGh1bnRlcjIyaHVudGVy"),
    ("secret-assignment", "ZXhwb3J0IEFQSV9LRVk9YWJjZGVmZ2hpamtsbW5vcA=="),
    ("secret-assignment", "eyJwYXNzd29yZCI6ICJjb3JyZWN0aG9yc2ViYXR0ZXJ5In0="),
    ("secret-assignment", "REJfUEFTU1dPUkQ9aHVudGVyMjI="),                                  # prefixed key
    ("secret-assignment", "cGFzc3dvcmQ6ICJ0b3Agc2VjcmV0IHBocmFzZSI="),                      # quoted, with spaces
    ("secret-assignment", "cGFzc3dvcmQ6ICIkZWNyZXQxMjMi"),                                  # $ but not a variable
    ("secret-assignment", "cGFzc3dvcmQ6IHw="),                                              # a block scalar follows
    ("totp-or-recovery", "dGhlIHVuc2VhbCBrZXkgaXMga2VwdCBpbiBhIGRyYXdlcg=="),
    ("host-key-fingerprint", "U0hBMjU2Om5UaFhMeEp3cWZmVDBNMWVCSzBoSGtqbTk0U3hwNWZUblF1UGxYaE1Xb0k="),
    ("credential-store-path", "dGhlIGtleSBsaXZlcyBpbiB+Ly5zc2gvaWRfZWQyNTUxOQ=="),
    ("credential-store-name", "c3RvcmVkIGluIEtlZVBhc3MgdW5kZXIgdGhlIHVzdWFsIHRpdGxl"),
    ("bmc-or-ipmi-address", "dGhlIEJNQyBhbnN3ZXJzIGF0IDE5Mi4xNjguMy4xMDI="),
    ("unraid-flash-guid", "R1VJRCAwNzgxLTU1ODMtOEQ2NC0wMTAyMDMwNDA1MDYwNzA4"),
]

CLEAN = """---
title: "The seed"
---
The firewall sits at 192.0.2.1 and the storage box at 198.51.100.10, and the
documentation prefix 2001:db8::1 is fine, as is the BMC example bmc: 192.0.2.7.
A placeholder password: <the value>, a reference token: ${TOKEN}, a clone URL
https://token:${GITHUB_TOKEN}@forge.example/o/r.git and a shell $HOME are shapes,
not secrets. The version is 1.2, the time is 12:34:56, the host is
host.local.example.org, the ratio 123:456:789 is not an address, and the disk
is 12 TB. Send mail through the relay, not to an address on this page.
"""


class Patterns(unittest.TestCase):
    def test_each_dirty_line_is_caught_by_its_rule(self):
        for want, line in DIRTY:
            self.assertIn(want, scan(d(line)), f"{want}: {d(line)!r}")

    def test_hits_carry_a_length_never_the_value(self):
        for _, line in DIRTY:
            for h in sc.scan_text("f.md", d(line), [], [], NOALLOW):
                self.assertIsInstance(h[3], int)

    def test_clean_page_passes(self):
        self.assertEqual(scan(CLEAN), set())

    def test_private_names_fold_whitespace_and_case(self):
        names = sc.load_names_text = None  # placeholder to keep the API surface explicit
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("# a comment\nAlex Example\n")
        names = sc.load_names(f.name)
        self.assertEqual(scan("thanks to ALEX example", names), {"named"})
        self.assertEqual(scan("thanks to Alex\n   Example for it", names), {"named"})
        self.assertEqual(scan("thanks to Alexandra", names), set())

    def test_private_rules_keep_hash_and_report_by_position(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("# full-line comments only\nzone: \\b[a-z0-9-]+\\.corp\\.example\\b\ntag: public#tag|SecretProject\n")
        rules = sc.load_rules(f.name)
        self.assertEqual(scan("see web." + "corp.example", rules=rules), {"private-rule-1"})   # .corp mid-name is not the suffix rule
        self.assertEqual(scan("about SecretProject", rules=rules), {"private-rule-2"})
        self.assertEqual(scan("PRIVATE\nVALUE", rules=[("x", re.compile(r"PRIVATE\s+VALUE", re.S))]), {"private-rule-1"})

    def test_malformed_private_files_are_configuration_errors(self):
        for body in ("no colon here\n", "dup: a\ndup: b\n", "bad: (\n"):
            with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
                f.write(body)
            with self.assertRaises(sc.ConfigError):
                sc.load_rules(f.name)
        with self.assertRaises(sc.ConfigError):
            sc.load_names("/nonexistent/names/for/the/test")


class AllowList(unittest.TestCase):
    def _allow(self, text):
        t = tempfile.mkdtemp(); open(os.path.join(t, ".sanitize-allow"), "w").write(text); return sc.Allow(t)

    def test_entry_is_scoped_to_a_rule_and_the_whole_token(self):
        lab = "10.9."
        at = "@"   # assembled so this file carries no address
        a = self._allow(f"rule=ipv4-literal {lab}1.2 # the lab range on purpose\nrule=email-address re:.*{at}example\\.org # published address for the site\n")
        self.assertTrue(a.allows("ipv4-literal", lab + "1.2"))
        self.assertFalse(a.allows("ipv4-literal", "1" + lab + "1.2"))
        self.assertFalse(a.allows("named", lab + "1.2"))
        self.assertTrue(a.allows("email-address", "hello" + at + "example.org"))
        self.assertFalse(a.allows("email-address", "hello" + at + "example.org.private"))

    def test_allowed_token_is_the_surrounding_run(self):
        # allowing the bare public domain must not allow a subdomain of it
        a = self._allow("rule=named example.org # the public domain itself\n")
        names = [("example.org", re.compile(r"example\.org", re.I))]
        self.assertEqual(scan("see example.org today", names, allow=a), set())
        self.assertEqual(scan("see secret.example.org today", names, allow=a), {"named"})

    def test_reason_scope_and_images_are_enforced(self):
        for bad in ("rule=ipv4-literal re:.*\n", "rule=ipv4-literal re:.* # ok\n", "re:.* # no rule scope given\n",
                    "rule=image-metadata a.png # cannot allow an image\n", "rule=ipv4-literal re:( # a bad regex here\n"):
            with self.assertRaises(sc.ConfigError, msg=bad):
                self._allow(bad)


class Images(unittest.TestCase):
    def _png(self, chunks, tail=b""):
        def chunk(t, dd):
            return struct.pack(">I", len(dd)) + t + dd + struct.pack(">I", zlib.crc32(t + dd) & 0xFFFFFFFF)
        return b"\x89PNG\r\n\x1a\n" + b"".join(chunk(t, dd) for t, dd in chunks) + tail

    def _jpeg(self, segments, scans=1, between=None, tail=b""):
        out = b"\xff\xd8"
        for marker, payload in segments:
            out += b"\xff" + bytes([marker]) + struct.pack(">H", len(payload) + 2) + payload
        for k in range(scans):
            out += b"\xff\xda\x00\x02" + b"\x12\xff\x00\x34\xff\xd0\x56" * 40   # entropy data with a stuffed byte and a restart
            if between and k < scans - 1:
                out += between
        return out + tail + b"\xff\xd9"

    def _webp(self, chunks):
        body = b"".join(t + struct.pack("<I", len(dd)) + dd + (b"\x00" if len(dd) & 1 else b"") for t, dd in chunks)
        return b"RIFF" + struct.pack("<I", 4 + len(body)) + b"WEBP" + body

    def test_jpeg(self):
        J = sc.scan_jpeg
        self.assertIsNone(J(self._jpeg([(0xE0, b"JFIF\x00"), (0xDB, b"\x00" * 65), (0xC2, b"\x08" * 15), (0xC4, b"\x00" * 20)], scans=3)))
        j = self._jpeg([(0xE0, b"JFIF\x00")]); self.assertIsNone(J(j[:2] + b"\xff\xff" + j[2:]))   # fill bytes are legal
        self.assertEqual(J(self._jpeg([(0xE1, b"Exif\x00\x00MM")])), "jpeg-app1")
        self.assertEqual(J(self._jpeg([(0xE1, b"http://ns.adobe.com/xmp/extension/\x00")])), "jpeg-app1")
        self.assertEqual(J(self._jpeg([(0xFE, b"shot on a phone")])), "jpeg-comment")
        self.assertEqual(J(self._jpeg([(0xE0, b"not jfif")])), "jpeg-app0-unknown")
        com = b"\xff\xfe\x00\x0e" + b"Alex Private"
        self.assertEqual(J(self._jpeg([(0xE0, b"JFIF\x00")], scans=2, between=com)), "jpeg-comment")   # between scans
        self.assertEqual(J(self._jpeg([(0xE0, b"JFIF\x00")], tail=com)), "jpeg-comment")               # before EOI
        self.assertEqual(J(self._jpeg([(0xE0, b"JFIF\x00")]) + b"Alex Private"), "jpeg-trailing-data")
        self.assertEqual(J(self._jpeg([(0xE0, b"JFIF\x00")])[:-2]), "jpeg-truncated")

    def test_png(self):
        P = sc.scan_png
        ok = [(b"IHDR", b"\x00" * 13), (b"IDAT", b"x"), (b"IEND", b"")]
        self.assertIsNone(P(self._png(ok)))
        for t in (b"tEXt", b"iTXt", b"zTXt", b"eXIf", b"tIME", b"prVt"):
            self.assertEqual(P(self._png(ok[:1] + [(t, b"x")] + ok[1:])), "png-chunk-" + t.decode(), t)
        self.assertEqual(P(self._png(ok, tail=b"Alex Private")), "png-trailing-data")
        self.assertEqual(P(self._png([(b"prVt", b"x")] + ok)), "png-ihdr-not-first")
        self.assertEqual(P(self._png([(b"IEND", b"")]) + b"secret"), "png-ihdr-not-first")
        bad = bytearray(self._png(ok)); bad[-1] ^= 1
        self.assertEqual(P(bytes(bad)), "png-bad-crc")

    def test_webp(self):
        W = sc.scan_webp
        self.assertIsNone(W(self._webp([(b"VP8 ", b"\x00" * 4)])))
        self.assertEqual(W(self._webp([(b"VP8 ", b"\x00" * 4), (b"EXIF", b"\x00" * 4)])), "webp-chunk-EXIF")
        self.assertEqual(W(self._webp([(b"VP8X", b"\x0c" + b"\x00" * 9), (b"VP8 ", b"\x00" * 4)])), "webp-vp8x-metadata-flag")
        self.assertEqual(W(self._webp([(b"VP8X", b"\x00" * 10)])), "webp-no-image-data")
        self.assertEqual(W(self._webp([(b"VP8 ", b"\x00" * 4)]) + b"tail"), "webp-size-mismatch")
        broken = b"RIFF" + struct.pack("<I", 12) + b"WEBP" + b"VP8 " + struct.pack("<I", 0xFFFFFFFF)
        self.assertEqual(W(broken), "webp-truncated")


class Cli(unittest.TestCase):
    def _run(self, tree, *args):
        return subprocess.run([sys.executable, "-B", TOOL, "--root", tree, *args, tree], capture_output=True, text=True)

    def test_every_file_kind_is_reached_and_nothing_is_skipped(self):
        with tempfile.TemporaryDirectory() as t:
            os.makedirs(os.path.join(t, "resources", "deep"))
            open(os.path.join(t, "resources", "deep", "x.svg"), "w").write("<svg><text>" + d("MTAuMC4xLjE=") + "</text></svg>")
            open(os.path.join(t, "y.yaml"), "w").write("host: " + d("bWFjIDAwOjExOjIyOjMzOjQ0OjU1"))
            open(os.path.join(t, "z.bin"), "wb").write(b"\x00\xff\xfe\x80")
            os.symlink("../../Alex-Private", os.path.join(t, "link"))
            r = self._run(t)
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn("resources/deep/x.svg:1: ipv4-literal", r.stdout)
            self.assertIn("y.yaml:1: mac-address", r.stdout)
            self.assertIn("z.bin:0: unscannable", r.stdout)
            self.assertIn("link:0: symlink", r.stdout)
            self.assertNotIn(d("MTAuMC4xLjE="), r.stdout)     # the value is never printed

    def test_a_private_name_in_a_path_is_found_and_redacted(self):
        with tempfile.TemporaryDirectory() as t, tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as nf:
            nf.write("Alex Private\n"); nf.close()
            open(os.path.join(t, "Alex Private.md"), "w").write("nothing here\n")
            os.symlink("../Alex Private/x", os.path.join(t, "l"))
            r = self._run(t, "--names", nf.name)
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertNotIn("Alex Private", r.stdout)
            self.assertIn("<path redacted", r.stdout)
            self.assertIn("l:0: named", r.stdout)               # the link target is published text too

    def test_configuration_errors_exit_2(self):
        with tempfile.TemporaryDirectory() as t:
            open(os.path.join(t, "page.md"), "w").write(CLEAN)
            self.assertEqual(self._run(t, "--names", "/nonexistent/for/the/test").returncode, 2)
            open(os.path.join(t, ".sanitize-allow"), "w").write("re:.* # no rule scope\n")
            self.assertEqual(self._run(t).returncode, 2)
        r = subprocess.run([sys.executable, "-B", TOOL, "/nonexistent/path/for/the/test"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)

    def test_clean_tree_passes_and_says_which_half_ran(self):
        with tempfile.TemporaryDirectory() as t:
            open(os.path.join(t, "page.md"), "w").write(CLEAN)
            r = self._run(t)
            self.assertEqual(r.returncode, 0, r.stdout)
            self.assertIn("pattern half only", r.stdout)

    def test_ignored_build_products_do_not_fail_a_checkout(self):
        with tempfile.TemporaryDirectory() as t:
            subprocess.run(["git", "-C", t, "init", "-q"], check=True)
            open(os.path.join(t, ".gitignore"), "w").write("*.pyc\n")
            open(os.path.join(t, "page.md"), "w").write(CLEAN)
            open(os.path.join(t, "junk.pyc"), "wb").write(b"\x00\xff")
            r = subprocess.run([sys.executable, "-B", TOOL, "--root", t], cwd=t, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == "__main__":
    unittest.main()
