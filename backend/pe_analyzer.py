"""Static Portable Executable (.exe/.dll) header analysis. Files are never run."""
import datetime

try:
    import pefile
    HAS_PEFILE = True
except Exception:
    HAS_PEFILE = False

PACKED_ENTROPY = 7.2  # sections above this are often compressed/encrypted


def analyze_pe(path):
    if not HAS_PEFILE:
        raise RuntimeError("pefile is not installed (pip install pefile).")
    pe = pefile.PE(path)
    try:
        sections = []
        for s in pe.sections:
            name = s.Name.rstrip(b"\x00").decode("utf-8", "replace")
            entropy = round(s.get_entropy(), 2)
            sections.append({"name": name, "virtual_size": s.Misc_VirtualSize,
                             "entropy": entropy, "packed": entropy >= PACKED_ENTROPY})
        imports = [e.dll.decode("utf-8", "replace") for e in getattr(pe, "DIRECTORY_ENTRY_IMPORT", [])]
        return {
            "machine": hex(pe.FILE_HEADER.Machine),
            "compiled": datetime.datetime.fromtimestamp(pe.FILE_HEADER.TimeDateStamp).isoformat(sep=" "),
            "sections": sections,
            "imports": imports,
        }
    finally:
        pe.close()
