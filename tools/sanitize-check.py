#!/usr/bin/env python3
"""sanitize-check: the mechanical half of a publication checklist.

    python3 tools/sanitize-check.py --names NAMES --rules RULES [PATH ...]

Walks the tree and refuses, by shape: IP literals outside the documentation
ranges (IPv4, and IPv6 validated by the standard library), carrier-grade NAT and
mesh-VPN ranges, MAC addresses in three notations, email addresses, credentials
in URLs, private keys, public keys, API-token shapes, password and token
assignments in the common syntaxes, recovery-material words, host-key material,
generic credential-store paths and product names, and images that carry
anything beyond pixels (a JPEG, PNG or WebP is walked segment by segment and
every segment must be on the list of pixel-carrying ones).

What is site-specific lives OUTSIDE this tool, in two private files that never
enter the repository: a names list (--names: literals that may not appear,
matched case-insensitively with whitespace folded, so a name wrapped across a
line break is still found) and a rules list (--rules: one `name: regex` per
line, full-line comments only). Both are required for a publication run;
without them the tool says it ran the pattern half only.

Every file is scanned, including this tool, the tests and every path name.
Text is scanned as text; the three image formats are parsed; anything else
that cannot be decoded, a symlink, a special file or an unreadable directory is
reported as a hit, never skipped. Only `.git` is skipped. A hit prints the rule,
the file, the line and the length of the match, never the match itself; a path
that itself carries a hit is printed redacted, and private rules are printed by
their position in the rules file, not their name.

Exceptions live in .sanitize-allow at the repository root, one per line:
`rule=<rule> <literal-or-re:regex> # reason`. The rule scope and the reason are
required; a literal must equal the whole matched token, a regex must match the
whole token. There are no exceptions for images: strip them.

Exit 0 is clean, 1 is at least one hit, 2 is a configuration error (a missing
path, an unreadable private file, a bad regex, a malformed allow entry). A green
run is necessary, never sufficient: it cannot read a label in a photograph,
decode a secret someone encoded, or know that an unlisted word is a name.
Stdlib only.
"""
import argparse
import ipaddress
import os
import re
import stat
import struct
import sys
import zlib


class ConfigError(Exception):
    pass


# ---------------------------------------------------------------- generic patterns
IPV4 = re.compile(r"(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?![\d]|\.\d)")
IPV6_CAND = re.compile(r"(?<![\w:.])((?:[0-9a-f]{0,4}:){2,7}[0-9a-f]{0,4}(?:%[\w-]+)?)(?![\w:])", re.I)
DOC_V4 = [ipaddress.ip_network(n) for n in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")]
DOC_V6 = [ipaddress.ip_network("2001:db8::/32")]

# a variable reference or a placeholder is a shape, not a value
# a variable reference or a placeholder is a shape, not a value: ${X}, $UPPER_CASE, <angle>, {{ moustache }},
# an ellipsis, or a run of x or *. A value that STARTS with one has no literal secret at its head.
_REF = r"(?:\$\{[\w.:-]+\}|(?-i:\$[A-Z_][A-Z0-9_]*(?![a-z]))|<[^<>]{1,60}>|\{\{[^{}]{1,60}\}\}|\.\.\.|x{4,}|\*{3,})"
_KEY = r"[\w-]*(?:password|passwd|secret|api[_-]?key|access[_-]?key|auth[_-]?token|token|private[_-]?key)[\w-]*"

PATTERNS = [
    ("internal-hostname-suffix", re.compile(r"\b[a-z0-9-]+\.(?:local|lan|internal|home\.arpa|corp)\b(?![.\w-])", re.I)),
    ("mac-address", re.compile(r"\b(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}\b|\b(?:[0-9a-f]{4}\.){2}[0-9a-f]{4}\b", re.I)),
    ("cgnat-or-mesh-range", re.compile(r"\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d{1,3}\.\d{1,3}\b|\bts\.net\b", re.I)),
    ("email-address", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("url-credential", re.compile(r"[a-z][a-z0-9+.-]*://[^\s/:@]+:(?!" + _REF + r"@)[^\s/@]+@", re.I)),
    ("unraid-flash-guid", re.compile(r"\b[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{16}\b")),
    ("private-key-block", re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY")),
    ("ssh-public-key", re.compile(r"\b(?:ssh-(?:rsa|ed25519|dss)|ecdsa-sha2-nistp\d+|sk-(?:ssh|ecdsa)[\w@.-]*)\s+AAAA[0-9A-Za-z+/]{20,}")),
    ("age-key", re.compile(r"\bAGE-SECRET-KEY-1[0-9A-Z]{50,}|\bage1[a-z0-9]{58}\b")),
    ("api-token-shape", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{20,}|\bglpat-[A-Za-z0-9_-]{20,}|\bsk-[A-Za-z0-9_-]{20,}|\bAKIA[0-9A-Z]{16}\b|\bxox[abp]-[0-9A-Za-z-]{10,}|\btskey-[a-z]+-[A-Za-z0-9]{10,}|\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{2,}\.[A-Za-z0-9_-]{10,}")),
    ("hex-token-near-secret-word", re.compile(r"(?i)\b(?:token|secret|key|password|passwd|pass)\b[^\n]{0,20}\b[0-9a-f]{32,}\b")),
    # yaml/ini/shell/json assignments; quoted values may hold spaces; a block scalar is flagged by its key alone
    ("secret-assignment", re.compile(r"[\"']?\b" + _KEY + r"\b[\"']?\s*[:=]\s*(?:\|[-+]?|>[-+]?|\"(?!" + _REF + r")[^\"\n]{4,}\"|'(?!" + _REF + r")[^'\n]{4,}'|(?!" + _REF + r")[^\s\"',;]{4,})", re.I)),
    ("totp-or-recovery", re.compile(r"(?i)\b(?:otpauth:[/]{2}|recovery[ ](?:share|key|code)s?|seed[ ]phrase|unseal[ ](?:key|share))\b")),
    ("known-hosts-line", re.compile(r"^\S+\s+(?:ssh-(?:rsa|ed25519|dss)|ecdsa-sha2-nistp\d+)\s+AAAA", re.M)),
    ("host-key-fingerprint", re.compile(r"\bSHA256:[0-9A-Za-z+/]{43}\b|\bMD5:(?:[0-9a-f]{2}:){15}[0-9a-f]{2}\b")),
    ("credential-store-path", re.compile(r"(?i)(?:\.sops\.yaml|secrets/[a-z0-9_.-]+\.(?:yaml|yml|json|age|env)|/root/\.ssh/|~/\.ssh/id_|/\.aws/credentials|/\.netrc\b|\.env\.(?:local|production)\b)")),
    ("credential-store-name", re.compile(r"(?i)\b(?:proton[ ]pass|standard[ ]notes|1pass[w]ord|bit[w]arden|kee[p]ass|last[p]ass|dash[l]ane)\b")),
]
BMC_NEAR = re.compile(r"(?i)\b(?:bmc|ipmi|ilo|idrac|redfish)\b[^\n]{0,40}\b(\d{1,3}(?:\.\d{1,3}){3})\b")
WORD_RUN = re.compile(r"[\w.:%-]+")


def is_doc(addr):
    return any(addr in n for n in (DOC_V4 if addr.version == 4 else DOC_V6)) or addr.is_loopback or addr.is_unspecified


# ---------------------------------------------------------------- allow-list
class Allow:
    """`rule=<rule> <literal|re:regex> # reason`; every part is required."""

    def __init__(self, root):
        self.entries = []
        p = os.path.join(root, ".sanitize-allow")
        if not os.path.exists(p):
            return
        with open(p, encoding="utf-8") as fh:
            raw_lines = fh.read().split("\n")
        for n, raw in enumerate(raw_lines, 1):
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if "#" not in line:
                raise ConfigError(f".sanitize-allow:{n}: no reason (append `# why`)")
            body, reason = line.split("#", 1)
            if len(reason.split()) < 3:
                raise ConfigError(f".sanitize-allow:{n}: the reason needs at least three words")
            body = body.strip()
            if not body.startswith("rule="):
                raise ConfigError(f".sanitize-allow:{n}: must start with rule=<rule>")
            parts = body[5:].split(None, 1)
            if len(parts) != 2:
                raise ConfigError(f".sanitize-allow:{n}: rule=<rule> <value> expected")
            rule, value = parts
            if rule == "image-metadata" or rule.startswith("image-"):
                raise ConfigError(f".sanitize-allow:{n}: no exceptions for images; strip the metadata")
            if value.startswith("re:"):
                try:
                    self.entries.append((rule, re.compile(value[3:].strip()).fullmatch))
                except re.error as e:
                    raise ConfigError(f".sanitize-allow:{n}: bad regex ({e})")
            else:
                self.entries.append((rule, lambda t, v=value: t == v))

    def allows(self, rule, token):
        return any(r == rule and f(token) for r, f in self.entries)


def token_at(text, start, end):
    """The whole [\\w.:%-] run around a match, so an exception must name the full token."""
    a, b = start, end
    while a > 0 and WORD_RUN.fullmatch(text[a - 1]): a -= 1
    while b < len(text) and WORD_RUN.fullmatch(text[b]): b += 1
    return text[a:b]


# ---------------------------------------------------------------- private half
def load_rules(path):
    rules = []
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().split("\n")
    except OSError as e:
        raise ConfigError(f"rules file: {e.strerror}: {path}")
    for n, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ConfigError(f"rules file line {n}: `name: regex` expected")
        name, rx = line.split(":", 1)
        name, rx = name.strip(), rx.strip()
        if not name or not rx:
            raise ConfigError(f"rules file line {n}: empty name or regex")
        if any(name == r[0] for r in rules):
            raise ConfigError(f"rules file line {n}: duplicate rule name")
        try:
            rules.append((name, re.compile(rx, re.I | re.S)))
        except re.error as e:
            raise ConfigError(f"rules file line {n}: bad regex ({e})")
    return rules


def load_names(path):
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().split("\n")
    except OSError as e:
        raise ConfigError(f"names file: {e.strerror}: {path}")
    names = []
    for line in lines:
        s = line.strip()
        if s and not s.startswith("#"):
            names.append((s, re.compile(r"\s+".join(re.escape(w) for w in s.split()), re.I)))
    return names


# ---------------------------------------------------------------- text
def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def scan_text(path, text, names, rules, allow):
    """Returns (path, line, rule, length) tuples. Private rules report as private-rule-N."""
    hits = []
    for m in IPV4.finditer(text):
        try:
            a = ipaddress.ip_address(m.group(1))
        except ValueError:
            continue
        if not is_doc(a) and not allow.allows("ipv4-literal", token_at(text, m.start(1), m.end(1))):
            hits.append((path, line_of(text, m.start()), "ipv4-literal", len(m.group(1))))
    for m in IPV6_CAND.finditer(text):
        cand = m.group(1)
        if ":" not in cand or cand.count(":") < 2:
            continue
        try:
            a = ipaddress.ip_address(cand.split("%")[0])
        except ValueError:
            continue
        if not is_doc(a) and not allow.allows("ipv6-literal", token_at(text, m.start(1), m.end(1))):
            hits.append((path, line_of(text, m.start()), "ipv6-literal", len(cand)))
    for m in BMC_NEAR.finditer(text):
        try:
            a = ipaddress.ip_address(m.group(1))
        except ValueError:
            continue
        if not is_doc(a):
            hits.append((path, line_of(text, m.start()), "bmc-or-ipmi-address", len(m.group(0))))
    for name, rx in PATTERNS:
        for m in rx.finditer(text):
            if not allow.allows(name, token_at(text, m.start(), m.end())):
                hits.append((path, line_of(text, m.start()), name, len(m.group(0))))
    for i, (name, rx) in enumerate(rules, 1):
        for m in rx.finditer(text):
            if not allow.allows(f"private-rule-{i}", token_at(text, m.start(), m.end())):
                hits.append((path, line_of(text, m.start()), f"private-rule-{i}", len(m.group(0))))
    for lit, rx in names:
        for m in rx.finditer(text):
            if not allow.allows("named", token_at(text, m.start(), m.end())):
                hits.append((path, line_of(text, m.start()), "named", len(lit)))
    return hits


# ---------------------------------------------------------------- images
# Every segment must be one of these; anything else is a place to hide text.
JPEG_OK = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,  # SOF
           0xC4, 0xDB, 0xDD, 0xDA, 0xD9, 0xD8}                                              # DHT DQT DRI SOS EOI SOI
JPEG_APP_OK = {0xE0: b"JFIF\x00", 0xE2: b"ICC_PROFILE\x00"}
PNG_OK = {b"IHDR", b"PLTE", b"IDAT", b"IEND", b"tRNS", b"gAMA", b"cHRM", b"sRGB", b"iCCP", b"sBIT", b"bKGD", b"pHYs", b"hIST", b"sPLT"}
WEBP_OK = {b"VP8 ", b"VP8L", b"VP8X", b"ALPH", b"ANIM", b"ANMF", b"ICCP"}


def scan_jpeg(b):
    """Returns None when clean, else a short reason code. Walks through every scan to EOI."""
    if b[:2] != b"\xff\xd8":
        return "jpeg-not-a-jpeg"
    i = 2
    n = len(b)
    while True:
        while i < n and b[i] == 0xFF:      # fill bytes are legal before a marker
            i += 1
        if i >= n:
            return "jpeg-truncated"
        if b[i - 1] != 0xFF:
            return "jpeg-malformed"
        marker = b[i]; i += 1
        if marker == 0xD9:                 # EOI
            return None if i == n else "jpeg-trailing-data"
        if 0xD0 <= marker <= 0xD7 or marker == 0x01:
            continue
        if i + 2 > n:
            return "jpeg-truncated"
        seglen = struct.unpack(">H", b[i:i + 2])[0]
        seg = b[i + 2:i + seglen]
        if seglen < 2 or i + seglen > n:
            return "jpeg-truncated"
        if marker in JPEG_APP_OK:
            if not seg.startswith(JPEG_APP_OK[marker]):
                return f"jpeg-app{marker - 0xE0}-unknown"
        elif 0xE0 <= marker <= 0xEF:
            return f"jpeg-app{marker - 0xE0}"
        elif marker == 0xFE:
            return "jpeg-comment"
        elif marker not in JPEG_OK:
            return f"jpeg-segment-{marker:02x}"
        i += seglen
        if marker == 0xDA:                 # entropy-coded data: skip to the next real marker
            while i < n:
                if b[i] == 0xFF and i + 1 < n and b[i + 1] not in (0x00,) and not 0xD0 <= b[i + 1] <= 0xD7 and b[i + 1] != 0xFF:
                    break
                i += 1
            if i >= n:
                return "jpeg-truncated"
            i += 1                         # now at the marker byte; the loop above consumes fills


def scan_png(b):
    if b[:8] != b"\x89PNG\r\n\x1a\n":
        return "png-not-a-png"
    i, n, first = 8, len(b), True
    while True:
        if i + 8 > n:
            return "png-truncated"
        ln, typ = struct.unpack(">I", b[i:i + 4])[0], b[i + 4:i + 8]
        if i + 12 + ln > n:
            return "png-truncated"
        data, crc = b[i + 8:i + 8 + ln], struct.unpack(">I", b[i + 8 + ln:i + 12 + ln])[0]
        if zlib.crc32(typ + data) & 0xFFFFFFFF != crc:
            return "png-bad-crc"
        if first and typ != b"IHDR":
            return "png-ihdr-not-first"
        first = False
        if typ == b"IEND":
            return None if i + 12 + ln == n else "png-trailing-data"
        if typ not in PNG_OK:
            return "png-chunk-" + typ.decode("latin1")
        i += 12 + ln


def scan_webp(b):
    if b[:4] != b"RIFF" or b[8:12] != b"WEBP":
        return "webp-not-a-webp"
    size = struct.unpack("<I", b[4:8])[0]
    if size + 8 != len(b):
        return "webp-size-mismatch"
    i, n, seen = 12, len(b), []
    while i < n:
        if i + 8 > n:
            return "webp-truncated"
        typ, ln = b[i:i + 4], struct.unpack("<I", b[i + 4:i + 8])[0]
        if i + 8 + ln > n:
            return "webp-truncated"
        if typ not in WEBP_OK:
            return "webp-chunk-" + typ.decode("latin1").strip()
        if typ == b"VP8X" and ln >= 1 and b[i + 8] & 0x0C:
            return "webp-vp8x-metadata-flag"
        seen.append(typ); i += 8 + ln + (ln & 1)
    if not any(t in seen for t in (b"VP8 ", b"VP8L", b"ANMF")):
        return "webp-no-image-data"
    return None


IMAGE_SCANNERS = {".jpg": scan_jpeg, ".jpeg": scan_jpeg, ".png": scan_png, ".webp": scan_webp}


# ---------------------------------------------------------------- walk
def walk(paths):
    """Yields (path, lstat). Traversal errors raise; nothing is skipped but .git."""
    def onerror(e):
        raise ConfigError(f"cannot read directory: {e.filename}")
    for p in paths:
        p = os.path.abspath(p)
        if not os.path.lexists(p):
            raise ConfigError(f"no such path: {p}")
        if not os.path.isdir(p) or os.path.islink(p):
            yield p, os.lstat(p)
            continue
        for d, dirs, files in os.walk(p, onerror=onerror):
            dirs[:] = sorted(x for x in dirs if x != ".git")
            for x in list(dirs):
                full = os.path.join(d, x)
                if os.path.islink(full):
                    dirs.remove(x); yield full, os.lstat(full)
            for f in sorted(files):
                full = os.path.join(d, f)
                yield full, os.lstat(full)


def git_files(root):
    """What git would publish: tracked plus untracked-not-ignored files (so an ignored build
    product does not fail the run, and nothing tracked is missed). None outside a checkout."""
    import subprocess
    try:
        out = subprocess.run(["git", "-C", root, "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                             capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    files = []
    for rel in out.decode("utf-8", "surrogateescape").split("\0"):
        if rel:
            full = os.path.join(root, rel)
            if os.path.lexists(full):
                files.append((full, os.lstat(full)))
    return files


def redact(rel, hits_on_path):
    return f"<path redacted, {len(rel)} chars>" if hits_on_path else rel.replace("\n", "\\n").replace("\r", "\\r")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", default=["."])
    ap.add_argument("--names", help="private file: literals that may not appear, one per line")
    ap.add_argument("--rules", help="private file: `name: regex` per line")
    ap.add_argument("--root", default=os.getcwd(), help="where .sanitize-allow lives; paths print relative to it")
    a = ap.parse_args(argv)
    try:
        names = load_names(a.names) if a.names else []
        rules = load_rules(a.rules) if a.rules else []
        allow = Allow(a.root)
        entries = list(git_files(a.root) if a.paths == ["."] and git_files(a.root) is not None else walk(a.paths))
    except ConfigError as e:
        print(f"sanitize-check: configuration error: {e}", file=sys.stderr)
        return 2
    hits, n = [], 0
    for path, st in entries:
        rel = os.path.relpath(path, a.root)
        n += 1
        path_hits = scan_text(rel, rel, names, rules, allow)      # the name of a file is published too
        shown = redact(rel, path_hits)
        hits += [(shown, 0, r, k) for (_, _, r, k) in path_hits]
        if stat.S_ISLNK(st.st_mode):
            target = os.readlink(path)
            hits += [(shown, 0, r, k) for (_, _, r, k) in scan_text(rel, target, names, rules, allow)]
            hits.append((shown, 0, "symlink", 0)); continue
        if not stat.S_ISREG(st.st_mode):
            hits.append((shown, 0, "not-a-regular-file", 0)); continue
        try:
            with open(path, "rb") as fh:
                b = fh.read()
        except OSError:
            hits.append((shown, 0, "unreadable", 0)); continue
        ext = os.path.splitext(path)[1].lower()
        if ext in IMAGE_SCANNERS:
            r = IMAGE_SCANNERS[ext](b)
            if r is not None:
                hits.append((shown, 0, "image-" + ("malformed" if any(w in r for w in ("truncated", "malformed", "not-a", "mismatch", "crc", "first")) else "metadata") + " (" + r + ")", 0))
            continue
        try:
            text = b.decode("utf-8")
        except UnicodeDecodeError:
            hits.append((shown, 0, "unscannable", 0)); continue
        hits += [(shown, l, r, k) for (_, l, r, k) in scan_text(rel, text, names, rules, allow)]
    for path, line, rule, k in hits:
        print(f"{path}:{line}: {rule}" + (f" (match of {k} chars)" if k else ""))
    half = "names and rules" if (names and rules) else ("names only" if names else ("rules only" if rules else "NO private half (pattern half only)"))
    print(f"sanitize-check: {n} files, {len(hits)} hits, {half}")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
