#!/usr/bin/env python3
"""Inject click-by-click native PresentationML animations into an existing PPTX.

Usage: python animate_pptx.py INPUT.pptx PLAN.json OUTPUT.pptx [--report REPORT.json]

Plan format:
  {"slides": [{"slide": 1, "steps": [
     [{"name": "explanation-1", "effect": "appear"}],
     [{"name": "ruler", "effect": "motion", "path": "M 0 0 L .1 0 E",
       "duration": 900},
      {"name": "new-line", "effect": "wipe", "direction": "right",
       "delay": 900, "duration": 650}]
  ]}]}

Each steps entry is one click. Events in one entry share the same click origin,
with optional delay in milliseconds. Durations are milliseconds. Each event
    targets the unique p:cNvPr name (or descr/alt) of a shape, picture, group, or graphic frame.
Appear/fade/wipe are entrance effects. Native entrance semantics hide their
targets before their first entrance. Motion targets should either be visible
on slide entry or have an entrance in an earlier step. "disappear" is an exit.

This module modifies only slide XML and validates target references, timing IDs,
click gates, and ZIP/XML integrity. This is structural validation, not a claim
that desktop PowerPoint playback has been inspected.

PresentationML references:
https://learn.microsoft.com/en-us/office/open-xml/presentation/working-with-animation
https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.presentation.animatemotion
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from decimal import Decimal
from pathlib import Path
import re
import tempfile
import zipfile

from lxml import etree as ET

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"p": P, "a": A}


def pe(tag: str, **attrs):
    return ET.Element(f"{{{P}}}{tag}", {k: str(v) for k, v in attrs.items()})


def sub(parent, tag: str, **attrs):
    node = pe(tag, **attrs)
    parent.append(node)
    return node


class Ids:
    def __init__(self):
        self.value = 0

    def __call__(self):
        self.value += 1
        return str(self.value)


def condition(parent, delay="0", evt=None, slide_target=False):
    attrs = {"delay": str(delay)}
    if evt is not None:
        attrs["evt"] = evt
    c = sub(parent, "cond", **attrs)
    if slide_target:
        sub(sub(c, "tgtEl"), "sldTgt")
    return c


def timing_node(ids, parent, *, dur=None, **attrs):
    values = {"id": ids(), **attrs}
    if dur is not None:
        values["dur"] = str(dur)
    return sub(parent, "cTn", **values)


def behavior(ids, parent, shape_id, attrs=(), duration=1, additive=None):
    cb_attrs = {"additive": additive} if additive else {}
    bhvr = sub(parent, "cBhvr", **cb_attrs)
    timing_node(ids, bhvr, dur=duration, fill="hold")
    sub(sub(bhvr, "tgtEl"), "spTgt", spid=shape_id)
    if attrs:
        names = sub(bhvr, "attrNameLst")
        for value in attrs:
            sub(names, "attrName").text = value
    return bhvr


def set_visibility(ids, parent, shape_id, visibility):
    node = sub(parent, "set")
    behavior(ids, node, shape_id, ["style.visibility"], 1)
    sub(sub(node, "to"), "strVal", val=visibility)


def normalize_motion_path(path):
    """Validate command arity and write decimals with the Office-required zero.

    MS-OE376 4.6.4 says Office may read '.1' as '1', not '0.1'. Do not
    pass through user/JS-generated number strings without normalizing them.
    """
    if not isinstance(path, str):
        raise ValueError("Motion path must be a string")
    token_pattern = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?|[MLCZEmlcze]"
    tokens = re.findall(token_pattern, path)
    if re.sub(token_pattern, "", path).strip(" ,\t\r\n"):
        raise ValueError("Motion path contains unsupported content")
    if not tokens or tokens[0].upper() != "M":
        raise ValueError("Motion path must begin with M")
    arity = {"M": 2, "L": 2, "C": 6, "Z": 0, "E": 0}
    output = []
    i = 0
    while i < len(tokens):
        command = tokens[i]
        if command.upper() not in arity:
            raise ValueError("Motion path coordinate count does not match its command")
        output.append(command)
        n = arity[command.upper()]
        if i + n >= len(tokens):
            raise ValueError("Motion path is missing coordinates")
        for token in tokens[i + 1:i + 1 + n]:
            if token.upper() in arity:
                raise ValueError("Motion path is missing coordinates")
            number = Decimal(token)
            if not number.is_finite():
                raise ValueError("Motion coordinates must be finite")
            output.append(format(number, "f"))
        i += n + 1
        if command.upper() == "E" and i != len(tokens):
            raise ValueError("Motion path contains data after E")
    if output[-1].upper() != "E":
        output.append("E")
    return " ".join(output)


def effect_node(ids, event, shape_id, first, text_shape=False):
    effect = event.get("effect", "appear")
    if effect not in {"appear", "fade", "wipe", "motion", "disappear"}:
        raise ValueError(f"Unsupported animation effect: {effect!r}")
    duration = int(event.get("duration", 1 if effect in {"appear", "disappear"} else 500))
    delay = int(event.get("delay", 0))
    if duration < 1 or delay < 0:
        raise ValueError("Animation duration must be positive and delay nonnegative")
    preset_id = {"appear": 1, "fade": 10, "wipe": 22, "motion": 0, "disappear": 1}[effect]
    preset_class = "path" if effect == "motion" else "exit" if effect == "disappear" else "entr"
    par = pe("par")
    ctn = timing_node(ids, par, presetID=preset_id, presetClass=preset_class,
                      presetSubtype="0", fill="hold",
                      nodeType="clickEffect" if first else "withEffect")
    if text_shape:
        ctn.set("grpId", "0")
    condition(sub(ctn, "stCondLst"), delay)
    children = sub(ctn, "childTnLst")
    if effect == "disappear":
        set_visibility(ids, children, shape_id, "hidden")
    elif effect in {"appear", "fade", "wipe"}:
        set_visibility(ids, children, shape_id, "visible")
        if effect in {"fade", "wipe"}:
            direction = event.get("direction", "right")
            if direction not in {"up", "down", "left", "right"}:
                raise ValueError(f"Unsupported wipe direction: {direction}")
            filter_value = "fade" if effect == "fade" else f"wipe({direction})"
            anim = sub(children, "animEffect", transition="in", filter=filter_value)
            behavior(ids, anim, shape_id, duration=duration)
    else:
        path = normalize_motion_path(event.get("path"))
        anim = sub(children, "animMotion", origin="layout", path=path,
                   pathEditMode="relative")
        behavior(ids, anim, shape_id, ["ppt_x", "ppt_y"], duration,
                 additive="base")
    return par


def build_timing(slide_root, spec):
    names = {}
    shape_ids = []
    text_shape_ids = set()
    # MS-OI29500 19.5.16(c): bldP may only point to an sp with valid t text.
    # Pictures (including SVGs), paths, lines, and groups use object timing only.
    for shape in slide_root.findall(".//p:sp", NS):
        prop = shape.find("p:nvSpPr/p:cNvPr", NS)
        if prop is not None and any((t.text or "").strip() for t in shape.findall(".//a:t", NS)):
            text_shape_ids.add(prop.get("id"))
    for prop in slide_root.findall(".//p:cNvPr", NS):
        shape_id = prop.get("id")
        shape_ids.append(shape_id)
        # Artifact Tool SVG/image exports preserve their alt text as descr.
        for name in {prop.get("name", ""), prop.get("descr", "")} - {""}:
            names.setdefault(name, []).append(shape_id)
    if len(shape_ids) != len(set(shape_ids)):
        raise ValueError("Slide has duplicate shape IDs")
    for old in slide_root.findall("p:timing", NS):
        slide_root.remove(old)
    ids = Ids()
    timing = pe("timing")
    root_par = sub(sub(timing, "tnLst"), "par")
    root_ctn = timing_node(ids, root_par, dur="indefinite", restart="never", nodeType="tmRoot")
    seq = sub(sub(root_ctn, "childTnLst"), "seq", concurrent="1", nextAc="seek")
    main = timing_node(ids, seq, dur="indefinite", nodeType="mainSeq")
    main_children = sub(main, "childTnLst")
    count = Counter()
    entrances = set()
    click_count = 0
    for step in spec.get("steps", []):
        if not isinstance(step, list) or not step:
            raise ValueError("Each animation step must be a nonempty event list")
        click_count += 1
        click_par = sub(main_children, "par")
        click_ctn = timing_node(ids, click_par, fill="hold")
        condition(sub(click_ctn, "stCondLst"), "indefinite")
        delay_par = sub(sub(click_ctn, "childTnLst"), "par")
        delay_ctn = timing_node(ids, delay_par, fill="hold")
        condition(sub(delay_ctn, "stCondLst"), 0)
        effect_list = sub(delay_ctn, "childTnLst")
        for i, event in enumerate(step):
            name = event.get("name")
            matching = names.get(name, [])
            if len(matching) != 1:
                raise ValueError(f"Animation target {name!r} matches {len(matching)} shapes")
            shape_id = matching[0]
            effect = event.get("effect", "appear")
            if effect in {"appear", "fade", "wipe"}:
                if shape_id in entrances:
                    raise ValueError(f"Duplicate entrance for {name!r}; use an exit before a separate entrance")
                entrances.add(shape_id)
            effect_list.append(effect_node(ids, event, shape_id, i == 0, shape_id in text_shape_ids))
            count[effect] += 1
    condition(sub(seq, "prevCondLst"), 0, "onPrev", True)
    condition(sub(seq, "nextCondLst"), 0, "onNext", True)
    text_entrances = entrances & text_shape_ids
    if text_entrances:
        builds = sub(timing, "bldLst")
        for shape_id in sorted(text_entrances, key=int):
            sub(builds, "bldP", spid=shape_id, grpId="0", animBg="1")
    ext = slide_root.find("p:extLst", NS)
    if ext is not None:
        slide_root.insert(slide_root.index(ext), timing)
    else:
        slide_root.append(timing)
    validate_timing(slide_root, click_count)
    return {"clicks": click_count, "events": sum(count.values()), "effects": dict(count),
            "entrance_targets": len(entrances), "timing_nodes": ids.value}


def validate_timing(root, expected_clicks=None):
    timings = root.findall("p:timing", NS)
    if len(timings) != 1:
        raise ValueError(f"Expected one timing element, got {len(timings)}")
    timing = timings[0]
    node_ids = [n.get("id") for n in timing.findall(".//p:cTn", NS)]
    if len(node_ids) != len(set(node_ids)):
        raise ValueError("Duplicate timing node IDs")
    shape_ids = {n.get("id") for n in root.findall(".//p:cSld//p:cNvPr", NS)}
    target_ids = {n.get("spid") for n in timing.findall(".//p:spTgt", NS)}
    target_ids.update(n.get("spid") for n in timing.findall(".//p:bldP", NS))
    if not target_ids <= shape_ids:
        raise ValueError(f"Unknown animation targets: {target_ids - shape_ids}")
    for bld in timing.findall(".//p:bldP", NS):
        targets = root.xpath('.//p:sp[p:nvSpPr/p:cNvPr/@id=$spid]', spid=bld.get("spid"), namespaces=NS)
        if len(targets) != 1 or not any((t.text or "").strip() for t in targets[0].findall(".//a:t", NS)):
            raise ValueError("bldP must target a text-bearing p:sp, never an image or empty line")
    mains = timing.xpath('.//p:cTn[@nodeType="mainSeq"]', namespaces=NS)
    if len(mains) != 1:
        raise ValueError("Expected exactly one mainSeq")
    gates = mains[0].findall("p:childTnLst/p:par", NS)
    click_nodes = timing.xpath('.//p:cTn[@nodeType="clickEffect"]', namespaces=NS)
    if len(gates) != len(click_nodes):
        raise ValueError("Each click gate must have exactly one first clickEffect")
    if expected_clicks is not None and len(gates) != expected_clicks:
        raise ValueError("Unexpected click gate count")
    for gate in gates:
        cond = gate.find("p:cTn/p:stCondLst/p:cond", NS)
        if cond is None or cond.get("delay") != "indefinite":
            raise ValueError("A click gate lacks its indefinite start condition")
    return {"targets": len(target_ids), "clicks": len(gates)}


def inject(input_path, plan_path, output_path):
    input_path, plan_path, output_path = map(Path, (input_path, plan_path, output_path))
    if input_path.resolve() == output_path.resolve():
        raise ValueError("Input and output must be distinct paths")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    specs = plan.get("slides", [])
    numbers = [int(x["slide"]) for x in specs]
    if len(numbers) != len(set(numbers)) or any(x < 1 for x in numbers):
        raise ValueError("Slide numbers must be unique positive integers")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    reports = []
    with zipfile.ZipFile(input_path) as zin:
        patches = {}
        for spec, number in zip(specs, numbers):
            key = f"ppt/slides/slide{number}.xml"
            if key not in zin.namelist():
                raise ValueError(f"No slide {number} in input PPTX")
            root = ET.fromstring(zin.read(key))
            report = build_timing(root, spec)
            reports.append({"slide": number, **report})
            patches[key] = ET.tostring(root, encoding="UTF-8", xml_declaration=True, standalone=True)
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                data = patches.get(info.filename)
                if data is None:
                    data = zin.read(info.filename)
                zout.writestr(info, data)
    with zipfile.ZipFile(output_path) as check:
        bad = check.testzip()
        if bad:
            raise ValueError(f"Bad ZIP member: {bad}")
        for name in check.namelist():
            if name.endswith(".xml") or name.endswith(".rels"):
                ET.fromstring(check.read(name))
        for report in reports:
            validate_timing(ET.fromstring(check.read(f'ppt/slides/slide{report["slide"]}.xml')), report["clicks"])
    return {"output": str(output_path), "animated_slides": len(reports),
            "clicks": sum(x["clicks"] for x in reports),
            "events": sum(x["events"] for x in reports), "slides": reports,
            "validation": "ZIP and XML well-formed; timing IDs and shape targets valid; click gate structure checked",
            "playback_validation": "Not inspected in desktop PowerPoint"}


def self_test():
    root = pe("sld")
    tree = sub(sub(root, "cSld"), "spTree")
    for i, name in enumerate(("text-1", "line", "ruler", "answer"), 2):
        sp = sub(tree, "sp")
        sub(sub(sp, "nvSpPr"), "cNvPr", id=i, name=name)
    report = build_timing(root, {"steps": [
        [{"name": "text-1"}],
        [{"name": "ruler", "effect": "motion", "path": "M 0 0 L .1 .02 E", "duration": 700},
         {"name": "line", "effect": "wipe", "delay": 700}],
        [{"name": "answer", "effect": "fade"}],
        [{"name": "ruler", "effect": "disappear"}],
    ]})
    assert report["clicks"] == 4 and report["events"] == 5
    assert report["effects"] == {"appear": 1, "motion": 1, "wipe": 1, "fade": 1, "disappear": 1}
    assert normalize_motion_path("M 0 0 L .1 -.02 E") == "M 0 0 L 0.1 -0.02 E"
    # Negative test ensures a misspelled target fails before any write.
    try:
        build_timing(root, {"steps": [[{"name": "does-not-exist"}]]})
    except ValueError:
        pass
    else:
        raise AssertionError("Unknown target was not rejected")
    return {"self_test": "passed", **report}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", nargs="?")
    parser.add_argument("plan", nargs="?")
    parser.add_argument("output", nargs="?")
    parser.add_argument("--report")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        report = self_test()
    else:
        if not all((args.input, args.plan, args.output)):
            parser.error("input, plan, and output are required")
        report = inject(args.input, args.plan, args.output)
    if args.report:
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
