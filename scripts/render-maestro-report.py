#!/usr/bin/env python3
"""Render a portable HTML + Markdown summary from Maestro JUnit and artifacts."""
from __future__ import annotations

import argparse
import html
import os
from pathlib import Path
import xml.etree.ElementTree as ET


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--junit', required=True)
    parser.add_argument('--artifacts', required=True)
    parser.add_argument('--html', required=True, dest='html_output')
    parser.add_argument('--markdown', required=True)
    parser.add_argument('--platform', required=True)
    return parser.parse_args()


def platform_label(value: str) -> str:
    return {'ios': 'iOS', 'android': 'Android'}.get(value.lower(), value)


def fmt_duration(value: float) -> str:
    if value < 1:
        return f"{value * 1000:.0f} ms"
    if value < 60:
        return f"{value:.1f}s"
    return f"{int(value // 60)}m {value % 60:.1f}s"


def suite_roots(root: ET.Element):
    if root.tag == 'testsuite':
        return [root]
    return root.findall('.//testsuite')


def collect_cases(junit_path: Path):
    if not junit_path.exists() or junit_path.stat().st_size == 0:
        return []
    root = ET.parse(junit_path).getroot()
    cases = []
    for suite in suite_roots(root):
        suite_name = suite.attrib.get('name', '')
        suite_props = {}
        suite_props_node = suite.find('properties')
        if suite_props_node is not None:
            for prop in suite_props_node.findall('property'):
                key = prop.attrib.get('name', '')
                if key:
                    suite_props[key] = prop.attrib.get('value', '')
        for tc in suite.findall('testcase'):
            failure = tc.find('failure')
            error = tc.find('error')
            skipped = tc.find('skipped')
            status = 'passed'
            detail = ''
            if failure is not None:
                status = 'failed'
                detail = failure.attrib.get('message') or (failure.text or '').strip()
            elif error is not None:
                status = 'failed'
                detail = error.attrib.get('message') or (error.text or '').strip()
            elif skipped is not None:
                status = 'skipped'
                detail = skipped.attrib.get('message') or (skipped.text or '').strip()
            props = dict(suite_props)
            props_node = tc.find('properties')
            if props_node is not None:
                for prop in props_node.findall('property'):
                    props[prop.attrib.get('name', '')] = prop.attrib.get('value', '')
            cases.append({
                'suite': suite_name,
                'name': tc.attrib.get('name', 'Unnamed flow'),
                'classname': tc.attrib.get('classname', ''),
                'time': float(tc.attrib.get('time', '0') or 0),
                'status': status,
                'detail': detail,
                'properties': props,
            })
    return cases


def collect_artifacts(artifact_dir: Path):
    if not artifact_dir.exists():
        return []
    files = []
    for p in sorted(artifact_dir.rglob('*')):
        if p.is_file():
            files.append(p)
    return files


def relative_href(path: Path, html_output: Path) -> str:
    return Path(os.path.relpath(path, start=html_output.parent)).as_posix()


def write_markdown(path: Path, platform: str, cases, artifacts):
    total = len(cases)
    passed = sum(c['status'] == 'passed' for c in cases)
    failed = sum(c['status'] == 'failed' for c in cases)
    skipped = sum(c['status'] == 'skipped' for c in cases)
    duration = sum(c['time'] for c in cases)
    lines = [
        f"## Maestro {platform_label(platform)} test report",
        '',
        f"**Result:** {'✅ Passed' if failed == 0 and total else '❌ Failed' if failed else '⚠️ No test cases parsed'}  ",
        f"**Tests:** {total} | **Passed:** {passed} | **Failed:** {failed} | **Skipped:** {skipped} | **Duration:** {fmt_duration(duration)}",
        '',
        '| Status | Flow | Duration |',
        '|---|---|---:|',
    ]
    icon = {'passed': '✅', 'failed': '❌', 'skipped': '⏭️'}
    for c in cases:
        name = c['name'].replace('|', '\\|')
        lines.append(f"| {icon[c['status']]} | {name} | {fmt_duration(c['time'])} |")
    failures = [c for c in cases if c['status'] == 'failed']
    if failures:
        lines += ['', '### Failures', '']
        for c in failures:
            detail = (c['detail'] or 'No failure message supplied').strip().replace('\n', ' ')
            if len(detail) > 700:
                detail = detail[:697] + '...'
            lines += [f"**{c['name']}**", '', f"> {detail}", '']
    lines += ['', f"Artifacts captured: **{len(artifacts)}** file(s).", '']
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines), encoding='utf-8')


def write_html(path: Path, platform: str, cases, artifacts):
    total = len(cases)
    passed = sum(c['status'] == 'passed' for c in cases)
    failed = sum(c['status'] == 'failed' for c in cases)
    skipped = sum(c['status'] == 'skipped' for c in cases)
    duration = sum(c['time'] for c in cases)
    pass_rate = (passed / total * 100) if total else 0
    rows = []
    for c in cases:
        detail = html.escape(c['detail'] or '')
        props = ' '.join(
            f'<span class="pill">{html.escape(k)}: {html.escape(v)}</span>'
            for k, v in c['properties'].items() if k
        )
        rows.append(f'''<tr>
<td><span class="status {c['status']}">{c['status'].upper()}</span></td>
<td><strong>{html.escape(c['name'])}</strong><div class="meta">{html.escape(c['suite'])}</div>{props}</td>
<td class="duration">{fmt_duration(c['time'])}</td>
<td>{f'<details><summary>Failure</summary><pre>{detail}</pre></details>' if detail else ''}</td>
</tr>''')

    artifact_items = []
    screenshots = []
    for f in artifacts:
        href = relative_href(f, path)
        suffix = f.suffix.lower()
        rel_name = html.escape(f.name)
        if suffix in {'.png', '.jpg', '.jpeg', '.webp'}:
            screenshots.append((href, rel_name))
        artifact_items.append(f'<li><a href="{html.escape(href)}">{html.escape(str(f.name))}</a> <span>{f.stat().st_size / 1024:.1f} KB</span></li>')

    screenshot_html = ''
    if screenshots:
        cards = ''.join(
            f'<a class="shot" href="{html.escape(href)}"><img src="{html.escape(href)}" alt="{name}"><span>{name}</span></a>'
            for href, name in screenshots[:12]
        )
        screenshot_html = f'<section><h2>Screenshots</h2><div class="shots">{cards}</div></section>'

    overall = 'PASSED' if total and failed == 0 else ('FAILED' if failed else 'NO RESULTS')
    overall_class = 'passed' if overall == 'PASSED' else ('failed' if overall == 'FAILED' else 'skipped')
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Maestro {html.escape(platform_label(platform))} Report</title>
<style>
:root{{--bg:#f8fafc;--card:#fff;--text:#111827;--muted:#64748b;--border:#e2e8f0;--green:#15803d;--greenbg:#dcfce7;--red:#b91c1c;--redbg:#fee2e2;--amber:#a16207;--amberbg:#fef3c7;--blue:#2563eb}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}main{{max-width:1180px;margin:0 auto;padding:36px 24px 72px}}h1{{font-size:32px;margin:0}}h2{{margin-top:36px}}.subtitle{{color:var(--muted);margin-top:5px}}.summary{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin:28px 0}}.card{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:18px}}.value{{font-size:26px;font-weight:750}}.label{{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.05em}}table{{width:100%;border-collapse:separate;border-spacing:0;background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden}}th,td{{padding:13px 14px;border-bottom:1px solid var(--border);vertical-align:top;text-align:left}}th{{font-size:12px;text-transform:uppercase;color:var(--muted);background:#f8fafc}}tr:last-child td{{border-bottom:0}}.status{{font-size:11px;font-weight:800;border-radius:999px;padding:5px 9px}}.status.passed{{color:var(--green);background:var(--greenbg)}}.status.failed{{color:var(--red);background:var(--redbg)}}.status.skipped{{color:var(--amber);background:var(--amberbg)}}.meta{{color:var(--muted);font-size:12px;margin-top:2px}}.pill{{display:inline-block;background:#eff6ff;color:#1d4ed8;border-radius:999px;font-size:11px;padding:3px 7px;margin:6px 4px 0 0}}.duration{{white-space:nowrap}}details summary{{cursor:pointer;color:var(--red);font-weight:600}}pre{{white-space:pre-wrap;max-width:500px;background:#111827;color:#f8fafc;padding:12px;border-radius:8px;overflow:auto;font-size:12px}}.shots{{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:14px}}.shot{{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;text-decoration:none;color:var(--text)}}.shot img{{width:100%;height:300px;object-fit:contain;background:#eef2f7;display:block}}.shot span{{display:block;padding:9px 11px;font-size:12px}}.artifacts{{columns:2;background:var(--card);border:1px solid var(--border);border-radius:14px;padding:16px 34px}}.artifacts li{{margin:5px 0;break-inside:avoid}}.artifacts span{{color:var(--muted);font-size:12px}}a{{color:var(--blue)}}@media(max-width:800px){{.summary{{grid-template-columns:repeat(2,1fr)}}.artifacts{{columns:1}}table{{font-size:13px}}}}
</style>
</head>
<body><main>
<header><span class="status {overall_class}">{overall}</span><h1>Maestro {html.escape(platform_label(platform))} test report</h1><div class="subtitle">Generated from the Maestro JUnit result and local test artifacts.</div></header>
<div class="summary">
<div class="card"><div class="label">Tests</div><div class="value">{total}</div></div>
<div class="card"><div class="label">Passed</div><div class="value">{passed}</div></div>
<div class="card"><div class="label">Failed</div><div class="value">{failed}</div></div>
<div class="card"><div class="label">Pass rate</div><div class="value">{pass_rate:.0f}%</div></div>
<div class="card"><div class="label">Duration</div><div class="value">{fmt_duration(duration)}</div></div>
</div>
<section><h2>Test results</h2><table><thead><tr><th>Status</th><th>Flow</th><th>Duration</th><th>Details</th></tr></thead><tbody>{''.join(rows)}</tbody></table></section>
{screenshot_html}
<section><h2>Artifacts</h2><ul class="artifacts">{''.join(artifact_items) if artifact_items else '<li>No artifacts found.</li>'}</ul></section>
</main></body></html>'''
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc, encoding='utf-8')


def main():
    args = parse_args()
    junit = Path(args.junit)
    artifacts_dir = Path(args.artifacts)
    html_output = Path(args.html_output)
    md_output = Path(args.markdown)
    cases = collect_cases(junit)
    artifacts = collect_artifacts(artifacts_dir)
    write_html(html_output, args.platform, cases, artifacts)
    write_markdown(md_output, args.platform, cases, artifacts)
    print(f"HTML report: {html_output}")
    print(f"Markdown summary: {md_output}")
    print(f"JUnit report: {junit}")
    print(f"Artifacts: {artifacts_dir}")


if __name__ == '__main__':
    main()
