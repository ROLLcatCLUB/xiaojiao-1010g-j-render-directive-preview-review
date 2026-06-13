import argparse, json, re, sys, zipfile, subprocess
from pathlib import Path
SLUG="xiaojiao_mock_work_state_to_render_directive_binding_1010H"
EXPECTED_STATUS="XIAOJIAO_MOCK_WORK_STATE_TO_RENDER_DIRECTIVE_BINDING_PASS"
EXPECTED_MARKER="ALL_1010H_MOCK_WORK_STATE_TO_RENDER_DIRECTIVE_BINDING_CHECKS_OK"
REQUIRED_FILES=["docs/foundation/xiaojiao_mock_work_state_to_render_directive_binding_1010H.md", "docs/foundation/xiaojiao_mock_work_state_to_render_directive_binding_1010H.json", "samples/xiaojiao_mock_work_state_to_render_directive_binding_1010H/render_directives_1010H.json", "docs/audit/xiaojiao_mock_work_state_to_render_directive_binding_1010H_result.json", "docs/audit/xiaojiao_mock_work_state_to_render_directive_binding_1010H_report.md", "scripts/validate_xiaojiao_mock_work_state_to_render_directive_binding_1010H.py", "docs/audit_packages/xiaojiao_mock_work_state_to_render_directive_binding_1010H_manifest.json", "docs/audit_packages/xiaojiao_mock_work_state_to_render_directive_binding_1010H.zip", "samples/xiaojiao_mock_work_state_to_render_directive_binding_1010H/mock_work_state_1010H.json", "samples/xiaojiao_mock_work_state_to_render_directive_binding_1010H/mock_composer_rules_1010H.json"]
EXTRA_FILES=["frontend/xiaojiao-preview.html"]
FALSE_FLAGS=["provider_called","model_called","api_key_configured","real_database_written","database_written","real_memory_written","memory_written","Feishu_written","formal_export_created","production_dependency_installed","real_resource_library_connected","teacher_control_runtime_entered","public_display_runtime_entered","student_side_runtime_entered","production_generation_performed","formal_writeback_performed","formal_apply_performed","auto_teacher_approval_performed","default_route_changed"]
FORBIDDEN=[".env","token","secret","key","node_modules","__pycache__",".db",".sqlite","dist","build","coverage",".DS_Store"]
SURFACES=["light_entry", "focus_surface", "semantic_confirmation", "handout_candidate_preview", "teacher_review_gate"]
def fail(m): print("VALIDATION_FAILED: "+m); sys.exit(1)
def rel_ok(p): return not (p.startswith("/") or p.startswith("\\") or (len(p)>1 and p[1]==":")) and "\\" not in p
def forbidden(p): return any(x.lower() in p.lower() for x in FORBIDDEN)
def js_syntax_ok(html, root):
 scripts=re.findall(r"<script>([\s\S]*?)</script>", html)
 if not scripts: fail("missing inline script")
 tmp=root/"docs/audit/.tmp_1010_gj_preview.js"; tmp.write_text("\n;\n".join(scripts), encoding="utf-8")
 r=subprocess.run(["node","--check",str(tmp)], cwd=str(root), capture_output=True, text=True)
 try: tmp.unlink()
 except OSError: pass
 if r.returncode!=0: fail("js syntax check failed: "+(r.stderr or r.stdout).strip())
def main():
 p=argparse.ArgumentParser(); p.add_argument("--root",default="."); a=p.parse_args(); root=Path(a.root).resolve()
 for r in REQUIRED_FILES+EXTRA_FILES:
  if not rel_ok(r): fail("bad required path "+r)
  if forbidden(r): fail("forbidden required path "+r)
  if not (root/r).exists(): fail("missing required file "+r)
 result=json.loads((root/f"docs/audit/{SLUG}_result.json").read_text(encoding="utf-8"))
 if result.get("final_status")!=EXPECTED_STATUS or result.get("pass") is not True: fail("bad result")
 if result.get("marker")!=EXPECTED_MARKER: fail("bad marker")
 flags=result.get("boundary_flags",{})
 for f in FALSE_FLAGS:
  if flags.get(f) is not False: fail("unsafe boundary flag "+f)
 if flags.get("preview_route_only") is not True: fail("preview_route_only must be true")
 html=(root/"frontend/xiaojiao-preview.html").read_text(encoding="utf-8", errors="ignore")
 js_syntax_ok(html, root)
 for term in ["mockWorkState", "mockComposer", "renderDirective", "applyRenderDirective", "refreshRenderDirective", "XIAOJIAO_LAST_RENDER_DIRECTIVE_1010", "xiaojiao_render_directive_1010I"]:
  if term not in html: fail("missing preview adapter term "+term)
 text="\n".join((root/r).read_text(encoding="utf-8", errors="ignore") for r in REQUIRED_FILES if r.endswith((".json",".md",".html")))
 for s in SURFACES:
  if s not in text: fail("missing surface "+s)
 for term in [EXPECTED_STATUS, EXPECTED_MARKER, "teacher_review_required", "formal_apply_performed", "provider_called", "default_route_changed"]:
  if term not in text: fail("missing term "+term)
 manifest=json.loads((root/f"docs/audit_packages/{SLUG}_manifest.json").read_text(encoding="utf-8"))
 with zipfile.ZipFile(root/f"docs/audit_packages/{SLUG}.zip") as z: entries=sorted(z.namelist())
 for e in entries:
  if not rel_ok(e): fail("bad zip entry "+e)
  if forbidden(e): fail("forbidden zip entry "+e)
 expected=sorted(manifest.get("zip_entries",[]))
 if sorted(set(expected)-set(entries)) or sorted(set(entries)-set(expected)): fail("manifest/zip mismatch")
 if manifest.get("zip_entry_count")!=len(entries): fail("zip count mismatch")
 if manifest.get("manifest_minus_zip")!=[] or manifest.get("zip_minus_manifest")!=[]: fail("manifest diffs not empty")
 print(EXPECTED_MARKER)
if __name__=="__main__": main()
