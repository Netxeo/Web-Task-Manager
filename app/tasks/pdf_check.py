import base64
import re
import zlib

MAX_DECODED = 20 * 1024 * 1024
ESCAPED_NAME = re.compile(rb"#([0-9A-Fa-f]{2})")
STREAM = re.compile(rb"(?<!end)stream\r?\n(.*?)endstream", re.S)
FILTER = re.compile(rb"/Filter\s*(\[[^\]]*\]|/[A-Za-z0-9]+)")
NAME = re.compile(rb"/([A-Za-z0-9]+)")
OBJECT_STREAM = re.compile(rb"/Type\s*/ObjStm(?![A-Za-z0-9])")
ACTIVE_CONTENT = re.compile(rb"/(JavaScript|JS|Launch|EmbeddedFile|RichMedia|XFA)(?![A-Za-z0-9])")
ENCRYPTED = re.compile(rb"/Encrypt(?![A-Za-z0-9])")

BROKEN = "Ce PDF est incomplet ou abîmé."
UNREADABLE = "Ce PDF est chiffré ou compressé d'une façon qui empêche de le vérifier. Il a été refusé."
ACTIVE = "Ce PDF contient du code ou des fichiers cachés. Il a été refusé."


def unescape(data):
    return ESCAPED_NAME.sub(lambda match: bytes.fromhex(match.group(1).decode()), data)


def inflate(data, budget):
    decoder = zlib.decompressobj()
    output = decoder.decompress(data, budget + 1)
    if len(output) > budget:
        raise ValueError(UNREADABLE)
    return output


def decode(data, dictionary, budget):
    if b"/Predictor" in dictionary or b"/DecodeParms" in dictionary:
        raise ValueError(UNREADABLE)
    found = FILTER.search(dictionary)
    for name in NAME.findall(found.group(1)) if found else []:
        if name in (b"FlateDecode", b"Fl"):
            data = inflate(data, budget)
        elif name in (b"ASCIIHexDecode", b"AHx"):
            data = bytes.fromhex(re.sub(rb"[^0-9A-Fa-f]", b"", data.split(b">")[0]).decode().ljust(2, "0"))
        elif name in (b"ASCII85Decode", b"A85"):
            data = base64.a85decode(data.strip().removesuffix(b"~>"))
        else:
            raise ValueError(UNREADABLE)
    return data


def object_streams(content):
    body, decoded, position, budget = [], [], 0, MAX_DECODED
    for match in STREAM.finditer(content):
        body.append(content[position:match.start()])
        position = match.end()
        dictionary = unescape(content[max(content.rfind(b"obj", 0, match.start()), 0):match.start()])
        if OBJECT_STREAM.search(dictionary):
            try:
                data = decode(match.group(1), dictionary, budget)
            except (zlib.error, ValueError):
                raise ValueError(UNREADABLE) from None
            budget -= len(data)
            decoded.append(data)
    body.append(content[position:])
    return unescape(b"".join(body)), unescape(b"".join(decoded)), len(decoded)


def check_pdf(content):
    if not content.startswith(b"%PDF-") or b"%%EOF" not in content[-2048:]:
        raise ValueError(BROKEN)
    body, decoded, count = object_streams(content)
    if ENCRYPTED.search(body) or len(OBJECT_STREAM.findall(body)) != count:
        raise ValueError(UNREADABLE)
    if ACTIVE_CONTENT.search(body) or ACTIVE_CONTENT.search(decoded):
        raise ValueError(ACTIVE)
    return content
