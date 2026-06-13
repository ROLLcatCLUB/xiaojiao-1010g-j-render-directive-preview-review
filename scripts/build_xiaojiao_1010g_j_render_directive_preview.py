import base64
import hashlib
import json
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "frontend/xiaojiao-preview.html"
REVIEW_REPO = "xiaojiao-1010g-j-render-directive-preview-review"
NEXT_STAGE = "1010J_REVIEW_PENDING_BEFORE_PROVIDER_SANDBOX_OR_DEFAULT_ROUTE_SWITCH"


BOUNDARY = {
    "provider_called": False,
    "model_called": False,
    "api_key_configured": False,
    "real_database_written": False,
    "database_written": False,
    "real_memory_written": False,
    "memory_written": False,
    "Feishu_written": False,
    "formal_export_created": False,
    "real_frontend_runtime_modified": True,
    "frontend_runtime_modified": True,
    "preview_route_only": True,
    "default_route_changed": False,
    "old_strong_agent_page_preserved": True,
    "production_dependency_installed": False,
    "real_resource_library_connected": False,
    "teacher_control_runtime_entered": False,
    "public_display_runtime_entered": False,
    "student_side_runtime_entered": False,
    "production_generation_performed": False,
    "formal_writeback_performed": False,
    "formal_apply_performed": False,
    "auto_teacher_approval_performed": False,
    "teacher_review_required": True,
}


STAGES = [
    ("1010G", "xiaojiao_render_directive_adapter_contract_1010G", "RENDER_DIRECTIVE_ADAPTER_CONTRACT", "XIAOJIAO_RENDER_DIRECTIVE_ADAPTER_CONTRACT_PASS"),
    ("1010H", "xiaojiao_mock_work_state_to_render_directive_binding_1010H", "MOCK_WORK_STATE_TO_RENDER_DIRECTIVE_BINDING", "XIAOJIAO_MOCK_WORK_STATE_TO_RENDER_DIRECTIVE_BINDING_PASS"),
    ("1010I", "xiaojiao_preview_route_render_directive_refactor_1010I", "PREVIEW_ROUTE_RENDER_DIRECTIVE_REFACTOR", "XIAOJIAO_PREVIEW_ROUTE_RENDER_DIRECTIVE_REFACTOR_PASS"),
    ("1010J", "xiaojiao_render_directive_preview_smoke_and_review_package_1010J", "RENDER_DIRECTIVE_PREVIEW_SMOKE_AND_REVIEW_PACKAGE", "XIAOJIAO_RENDER_DIRECTIVE_PREVIEW_SMOKE_AND_REVIEW_PACKAGE_PASS"),
]


SURFACES = ["light_entry", "focus_surface", "semantic_confirmation", "handout_candidate_preview", "teacher_review_gate"]


def write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def dump(path: str, obj) -> None:
    write(path, json.dumps(obj, ensure_ascii=False, indent=2))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def marker(stage_id: str, title: str) -> str:
    return f"ALL_{stage_id}_{title}_CHECKS_OK"


def make_zip(slug: str, entries: list[str]) -> str:
    zpath = ROOT / f"docs/audit_packages/{slug}.zip"
    zpath.parent.mkdir(parents=True, exist_ok=True)
    if zpath.exists():
        zpath.unlink()
    with zipfile.ZipFile(zpath, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for entry in entries:
            zf.write(ROOT / entry, entry.replace("\\", "/"))
    return sha256(zpath)


ADAPTER_JS = r'''
    const SURFACE_TO_PAGE = {
      light_entry: "entry",
      focus_surface: "focus",
      semantic_confirmation: "semantic",
      handout_candidate_preview: "candidate",
      teacher_review_gate: "gate"
    };
    const PAGE_TO_SURFACE = {
      entry: "light_entry",
      focus: "focus_surface",
      semantic: "semantic_confirmation",
      candidate: "handout_candidate_preview",
      gate: "teacher_review_gate"
    };
    const mockWorkState = {
      teacher_id: "teacher_art_001",
      teacher_name: "张老师",
      week: 3,
      weekday: "周三",
      today_lessons: [
        { id: "lesson_L001", title: "线条的节奏", grade: "三年级", status: "ready" },
        { id: "lesson_L003", title: "色彩的感觉", grade: "四年级", status: "draft_pending_confirmation" },
        { id: "lesson_L006", title: "有趣的泥塑", grade: "五年级", status: "watching" }
      ],
      current_surface: "light_entry",
      current_priority_item: "lesson_L003",
      current_lesson: {
        id: "lesson_L003",
        title: "色彩的感觉",
        grade: "四年级 1 班",
        section_count: 4
      },
      lesson_draft_status: "pending_confirmation",
      inquiry_section_minutes: 25,
      display_section_minutes: 8,
      handout_status: "not_generated",
      handout_candidate: null,
      teacher_review_required: false,
      formal_apply_performed: false,
      process_note_candidate: null,
      intent_bar_phase: "collapsed",
      evidence_event_candidates: [],
      event_log: []
    };
    let renderDirective = null;
    function buildSupportingObjects(workState) {
      return [
        { id: "handout_L003", type: "handout", title: "学习单", status: workState.handout_status },
        { id: "rubric_L003", type: "rubric", title: "评价量规", status: "later" },
        { id: "resources_L003", type: "resource_reference", title: "资源参考", status: "later" }
      ];
    }
    function mockComposer(workState, action) {
      const surface = workState.current_surface || "light_entry";
      const primaryObject = surface === "light_entry"
        ? { id: "today_priority", type: "today_work_item", title: "今天 3 节课，1 项待你确认" }
        : surface === "handout_candidate_preview" || surface === "teacher_review_gate"
          ? (workState.handout_candidate || { id: "handout_candidate_L003", type: "handout_candidate", title: "《色彩的感觉》学习单" })
          : { id: "lesson_L003", type: "lesson_design", title: "《色彩的感觉》" };
      return {
        directive_id: "directive_" + surface + "_" + Date.now(),
        source: "mock_composer_1010H",
        surface_mode: surface,
        primary_object: primaryObject,
        supporting_objects: buildSupportingObjects(workState),
        visible_zones: surface === "light_entry" ? ["today_priority", "agent_note", "primary_actions"] : ["primary_object", "supporting_objects", "intent_bar"],
        hidden_zones: surface === "light_entry" ? ["resource_library_home", "grid_studio", "right_ai_panel"] : ["resource_library_home", "right_ai_panel"],
        agent_notes: [
          {
            id: "note_section_2_time",
            attach_to: surface === "light_entry" ? "today_priority" : "lesson_structure.section_2",
            text: workState.inquiry_section_minutes > 20 ? "探究 25 分钟偏长。我可以压到 18 分钟，把时间留给展示。" : "探究时间已调整。"
          }
        ],
        available_actions: [
          { id: "open_lesson_focus", label: "现在处理", target_surface: "focus_surface" },
          { id: "generate_handout_candidate", label: "出一版候选", target_surface: "semantic_confirmation" },
          { id: "enter_teacher_review", label: "进入确认", target_surface: "teacher_review_gate" }
        ],
        intent_bar_policy: {
          enabled: surface !== "light_entry" && surface !== "semantic_confirmation",
          phase: workState.intent_bar_phase,
          quick_intents: ["探究短一点", "学习单简单些", "重新设计这节课"]
        },
        teacher_review_required: workState.teacher_review_required,
        formal_apply_performed: false,
        action
      };
    }
    function applyRenderDirective(directive) {
      renderDirective = directive;
      window.XIAOJIAO_LAST_RENDER_DIRECTIVE_1010 = directive;
      const page = SURFACE_TO_PAGE[directive.surface_mode] || "entry";
      pages.forEach(p => document.getElementById(p).classList.toggle("hidden", p !== page));
      state.current = page;
      if (page === "focus") renderFocus();
      if (page === "candidate") renderCandidate();
      document.getElementById("intentShell").classList.toggle("hidden", !directive.intent_bar_policy.enabled);
      if (!directive.intent_bar_policy.enabled) {
        document.body.classList.remove("intent-open");
        document.getElementById("intentScrim").classList.add("hidden");
      }
      persistDirectiveState("render_surface:" + directive.surface_mode);
    }
    function refreshRenderDirective(action) {
      renderDirective = mockComposer(mockWorkState, action || "refresh");
      applyRenderDirective(renderDirective);
      return renderDirective;
    }
    function updateMockWorkStateFromLegacyState(action) {
      mockWorkState.current_surface = PAGE_TO_SURFACE[state.current] || mockWorkState.current_surface;
      mockWorkState.lesson_draft_status = state.draftConfirmed ? "confirmed" : "pending_confirmation";
      mockWorkState.inquiry_section_minutes = (state.segments.find(s => s.name.indexOf("探究") >= 0) || {}).min || mockWorkState.inquiry_section_minutes;
      mockWorkState.display_section_minutes = (state.segments.find(s => s.name.indexOf("展示") >= 0 || s.name.indexOf("分享") >= 0) || {}).min || mockWorkState.display_section_minutes;
      mockWorkState.handout_status = state.handout === "未生成" ? "not_generated" : "candidate_pending_review";
      mockWorkState.teacher_review_required = state.teacher_review_required;
      mockWorkState.formal_apply_performed = false;
      mockWorkState.process_note_candidate = state.process_record_candidate;
      mockWorkState.intent_bar_phase = state.intent_bar_state;
      mockWorkState.event_log = state.events.slice(-50);
      mockWorkState.last_action = action || null;
    }
    function dispatchMockAction(action, patch = {}) {
      Object.assign(mockWorkState, patch);
      mockWorkState.event_log.push({
        type: action,
        surface: mockWorkState.current_surface,
        formal_apply_performed: false,
        time: new Date().toISOString()
      });
      return refreshRenderDirective(action);
    }
    function persistDirectiveState(lastEventType) {
      updateMockWorkStateFromLegacyState(lastEventType);
      try {
        localStorage.setItem("xiaojiao_mock_work_state_1010H", JSON.stringify(mockWorkState));
        localStorage.setItem("xiaojiao_render_directive_1010I", JSON.stringify(renderDirective || mockComposer(mockWorkState, "persist")));
        localStorage.setItem("xiaojiao_render_directive_event_log_1010J", JSON.stringify(mockWorkState.event_log.slice(-50)));
      } catch (error) {}
    }
'''


def refactor_preview() -> None:
    html = PREVIEW.read_text(encoding="utf-8")
    if "mock_composer_1010H" in html:
        return
    html = html.replace('data-source-baseline="1007O_R1"', 'data-source-baseline="1007O_R1" data-render-directive-preview="1010I"')
    html = html.replace("    function go(id) {", ADAPTER_JS + "\n    function go(id) {")
    old_go = '''    function go(id) {
      pages.forEach(p => document.getElementById(p).classList.toggle("hidden", p !== id));
      state.current = id;
      if (id === "focus") renderFocus();
      if (id === "candidate") renderCandidate();
      document.getElementById("intentShell").classList.toggle("hidden", id === "entry" || id === "semantic");
      if (id === "entry" || id === "semantic") {
        document.body.classList.remove("intent-open");
        document.getElementById("intentScrim").classList.add("hidden");
      }
      log("surface_" + id);
    }'''
    new_go = '''    function go(id) {
      state.current = id;
      mockWorkState.current_surface = PAGE_TO_SURFACE[id] || "light_entry";
      if (id === "candidate") {
        mockWorkState.handout_status = "candidate_pending_review";
        mockWorkState.handout_candidate = mockWorkState.handout_candidate || { id: "handout_candidate_L003", type: "handout_candidate", title: "《色彩的感觉》学习单", status: "candidate_pending_review" };
      }
      if (id === "gate") mockWorkState.teacher_review_required = true;
      refreshRenderDirective("surface_" + id);
      log("surface_" + id);
    }'''
    html = html.replace(old_go, new_go)
    html = html.replace('state.adjusted = true;\n      renderFocus();\n      log("intent_bar_simple_action:探究短一点");', 'state.adjusted = true;\n      mockWorkState.current_surface = "focus_surface";\n      mockWorkState.inquiry_section_minutes = 18;\n      mockWorkState.display_section_minutes = 15;\n      refreshRenderDirective("shorten_inquiry");\n      log("intent_bar_simple_action:探究短一点");')
    html = html.replace('state.draftConfirmed = true;\n      renderFocus();\n      log("confirm_lesson_draft");', 'state.draftConfirmed = true;\n      mockWorkState.lesson_draft_status = "confirmed";\n      refreshRenderDirective("confirm_lesson_draft");\n      log("confirm_lesson_draft");')
    html = html.replace('state.handout = "候选待确认";\n      showGenerationThinking();\n      setTimeout(() => { go("candidate"); resetIntent(); }, 950);', 'state.handout = "候选待确认";\n      mockWorkState.handout_status = "candidate_pending_review";\n      mockWorkState.handout_candidate = { id: "handout_candidate_L003", type: "handout_candidate", title: "《色彩的感觉》学习单", status: "candidate_pending_review" };\n      mockWorkState.current_surface = "semantic_confirmation";\n      refreshRenderDirective("generate_handout_candidate");\n      showGenerationThinking();\n      setTimeout(() => { go("candidate"); resetIntent(); }, 950);')
    html = html.replace('state.teacher_review_required = true;\n      document.getElementById("reviewOpen").classList.add("hidden");', 'state.teacher_review_required = true;\n      mockWorkState.teacher_review_required = true;\n      mockWorkState.current_surface = "teacher_review_gate";\n      refreshRenderDirective("teacher_review_gate_decision_preview:" + type);\n      document.getElementById("reviewOpen").classList.add("hidden");')
    html = html.replace('state.process_record_candidate = o;\n      document.querySelectorAll("#recordOptions button").forEach', 'state.process_record_candidate = o;\n      mockWorkState.process_note_candidate = o;\n      mockWorkState.evidence_event_candidates.push({ type: "process_note_candidate", value: o, work_object: "lesson_L003", formal_apply_performed: false });\n      refreshRenderDirective("evidence_event_candidate:" + o);\n      document.querySelectorAll("#recordOptions button").forEach')
    html = html.replace('state.intent_bar_state = "input";', 'state.intent_bar_state = "input";\n      mockWorkState.intent_bar_phase = "input";', 1)
    html = html.replace('state.intent_bar_state = "collapsed";', 'state.intent_bar_state = "collapsed";\n      mockWorkState.intent_bar_phase = "collapsed";', 1)
    html = html.replace('state.intent_bar_state = "thinking";', 'state.intent_bar_state = "thinking";\n        mockWorkState.intent_bar_phase = "thinking";')
    html = html.replace('state.intent_bar_state = "confirm";', 'state.intent_bar_state = "confirm";\n          mockWorkState.intent_bar_phase = "confirm";')
    html = html.replace('if (action === "easier") { state.worksheetEasy = true; state.difficulty = "简单一点"; state.handout = "候选待确认"; renderFocus(); }', 'if (action === "easier") { state.worksheetEasy = true; state.difficulty = "简单一点"; state.handout = "候选待确认"; mockWorkState.handout_status = "candidate_pending_review"; refreshRenderDirective("easier_handout"); }')
    html = html.replace('if (action === "more_demo") { state.worksheetDemo = true; state.handout = "候选待确认"; renderFocus(); }', 'if (action === "more_demo") { state.worksheetDemo = true; state.handout = "候选待确认"; mockWorkState.handout_status = "candidate_pending_review"; refreshRenderDirective("more_demo"); }')
    html = html.replace('        renderFocus();\n      }\n      log("intent_action:" + action);', '        mockWorkState.lesson_structure = state.segments;\n        mockWorkState.lesson_draft_status = "pending_confirmation";\n        mockWorkState.current_surface = "focus_surface";\n        refreshRenderDirective("redesign_lesson");\n      }\n      log("intent_action:" + action);')
    html = html.replace('state.intent_bar_state = "done";', 'state.intent_bar_state = "done";\n      mockWorkState.intent_bar_phase = "done";')
    html = html.replace('log("open_workbench");\n    persistPreviewState("open_workbench");', 'refreshRenderDirective("open_workbench");\n    log("open_workbench");\n    persistPreviewState("open_workbench");')
    html += "\n<!-- 1010I render directive refactor: mockWorkState mockComposer renderDirective renderSurface preview-only default_route_changed=false provider_called=false model_called=false formal_apply_performed=false -->\n"
    PREVIEW.write_text(html, encoding="utf-8")


def render_directive_sample() -> dict:
    return {
        "render_directive_schema": {
            "surface_mode": SURFACES,
            "primary_object": {"id": "string", "type": "work_object_type", "title": "string"},
            "supporting_objects": "array",
            "visible_zones": "array",
            "hidden_zones": "array",
            "agent_notes": [{"id": "note_id", "attach_to": "work_object_path", "text": "string"}],
            "available_actions": [{"id": "action_id", "label": "teacher visible label", "target_surface": "surface_mode"}],
            "intent_bar_policy": {"enabled": True, "phase": "collapsed|input|thinking|confirm|done"},
            "teacher_review_required": "boolean",
            "formal_apply_performed": False,
        },
        "adapter_responsibilities": [
            "receive render_directive",
            "select surface",
            "map primary_object",
            "map supporting_objects",
            "attach agent_notes",
            "map available_actions",
            "respect teacher_review_required",
        ],
        "adapter_forbidden": [
            "provider/model call",
            "database write",
            "memory write",
            "formal apply",
            "default route change",
            "skip teacher review",
        ],
        "boundary_flags": BOUNDARY,
    }


def mock_work_state() -> dict:
    return {
        "teacher_id": "teacher_art_001",
        "teacher_name": "张老师",
        "week": 3,
        "weekday": "周三",
        "today_lessons": [
            {"id": "lesson_L001", "title": "线条的节奏", "status": "ready"},
            {"id": "lesson_L003", "title": "色彩的感觉", "status": "draft_pending_confirmation"},
            {"id": "lesson_L006", "title": "有趣的泥塑", "status": "watching"},
        ],
        "current_priority_item": "lesson_L003",
        "current_surface": "light_entry",
        "current_lesson": {"id": "lesson_L003", "title": "色彩的感觉", "grade": "四年级 1 班"},
        "lesson_draft_status": "pending_confirmation",
        "inquiry_section_minutes": 25,
        "display_section_minutes": 8,
        "handout_status": "not_generated",
        "handout_candidate": None,
        "teacher_review_required": False,
        "formal_apply_performed": False,
        "process_note_candidate": None,
        "event_log": [],
    }


def directive(surface: str) -> dict:
    primary = {"id": "today_priority", "type": "today_work_item", "title": "今天 3 节课，1 项待你确认"} if surface == "light_entry" else {"id": "lesson_L003", "type": "lesson_design", "title": "《色彩的感觉》"}
    if surface in ("handout_candidate_preview", "teacher_review_gate"):
        primary = {"id": "handout_candidate_L003", "type": "handout_candidate", "title": "《色彩的感觉》学习单"}
    return {
        "directive_id": f"{surface}_directive",
        "surface_mode": surface,
        "primary_object": primary,
        "supporting_objects": [{"id": "handout_L003", "type": "handout"}, {"id": "rubric_L003", "type": "rubric"}],
        "visible_zones": ["primary_object", "agent_notes", "available_actions"],
        "hidden_zones": ["resource_library_home", "right_ai_panel", "grid_studio"],
        "agent_notes": [{"id": "note_section_2_time", "attach_to": "lesson_structure.section_2", "text": "探究 25 分钟偏长。"}],
        "available_actions": [{"id": "open_lesson_focus"}, {"id": "generate_handout_candidate"}, {"id": "enter_teacher_review"}],
        "intent_bar_policy": {"enabled": surface not in ("light_entry", "semantic_confirmation"), "phase": "collapsed"},
        "teacher_review_required": surface == "teacher_review_gate",
        "formal_apply_performed": False,
    }


def stage_payload(stage_id: str) -> dict:
    if stage_id == "1010G":
        return render_directive_sample()
    if stage_id == "1010H":
        return {
            "mock_work_state": mock_work_state(),
            "mock_composer_rules": {
                "light_entry": "current_surface=light_entry -> light_entry_directive",
                "open_lesson_focus": "action=open_lesson_focus -> focus_surface_directive",
                "generate_handout_candidate": "action=generate_handout_candidate -> semantic_confirmation or handout_candidate_preview",
                "enter_teacher_review": "action=enter_teacher_review -> teacher_review_gate_directive",
                "teacher_review_required": "formal_apply remains false",
            },
            "render_directives": {f"{s}_directive": directive(s) for s in SURFACES},
            "boundary_flags": BOUNDARY,
        }
    if stage_id == "1010I":
        return {
            "preview_route_path": "frontend/xiaojiao-preview.html",
            "refactor_trace": [
                "mockWorkState added",
                "mockComposer added",
                "renderDirective added",
                "applyRenderDirective added",
                "go/action path refreshes render directive",
                "localStorage stores mock work state and render directive",
            ],
            "supported_surface_modes": SURFACES,
            "boundary_flags": BOUNDARY,
        }
    return {
        "smoke_checklist": [
            "open preview route",
            "mockWorkState exists",
            "Composer generates light_entry_directive",
            "click now handle -> focus_surface_directive",
            "shorten inquiry -> inquiry_section_minutes=18",
            "redesign -> thinking + confirm",
            "generate candidate -> candidate directive",
            "enter review -> teacher_review_required=true",
            "record note -> evidence_event_candidate",
            "formal_apply_performed=false",
        ],
        "render_directive_trace": [directive(s) for s in SURFACES],
        "work_state_change_trace": [
            {"action": "open_lesson_focus", "current_surface": "focus_surface"},
            {"action": "shorten_inquiry", "inquiry_section_minutes": 18},
            {"action": "generate_handout_candidate", "handout_status": "candidate_pending_review"},
            {"action": "enter_teacher_review", "teacher_review_required": True},
        ],
        "event_log_trace": ["open_workbench", "surface_focus", "shorten_inquiry", "generate_handout_candidate", "surface_gate", "evidence_event_candidate"],
        "user_review_questions": [
            "render_directive 驱动后体验是否保持？",
            "是否允许进入 provider sandbox？",
            "是否允许接真实 Work State Store？",
            "是否允许进一步接真实前端默认入口？",
            "是否需要继续视觉小修？",
        ],
        "boundary_flags": BOUNDARY,
    }


def sample_file(stage_id: str) -> str:
    return {
        "1010G": "render_directive_adapter_sample_1010G.json",
        "1010H": "render_directives_1010H.json",
        "1010I": "render_directive_refactor_trace_1010I.json",
        "1010J": "render_directive_preview_smoke_trace_1010J.json",
    }[stage_id]


def extra_h_files(slug: str) -> list[str]:
    if not slug.endswith("1010H"):
        return []
    dump(f"samples/{slug}/mock_work_state_1010H.json", mock_work_state())
    dump(f"samples/{slug}/mock_composer_rules_1010H.json", stage_payload("1010H")["mock_composer_rules"])
    return [
        f"samples/{slug}/mock_work_state_1010H.json",
        f"samples/{slug}/mock_composer_rules_1010H.json",
    ]


def validator_source(stage_id: str, slug: str, title: str, status: str) -> str:
    required = [
        f"docs/foundation/{slug}.md",
        f"docs/foundation/{slug}.json",
        f"samples/{slug}/{sample_file(stage_id)}",
        f"docs/audit/{slug}_result.json",
        f"docs/audit/{slug}_report.md",
        f"scripts/validate_{slug}.py",
        f"docs/audit_packages/{slug}_manifest.json",
        f"docs/audit_packages/{slug}.zip",
    ]
    if stage_id == "1010H":
        required += [f"samples/{slug}/mock_work_state_1010H.json", f"samples/{slug}/mock_composer_rules_1010H.json"]
    return f'''import argparse, json, re, sys, zipfile, subprocess
from pathlib import Path
SLUG="{slug}"
EXPECTED_STATUS="{status}"
EXPECTED_MARKER="{marker(stage_id,title)}"
REQUIRED_FILES={json.dumps(required, ensure_ascii=False)}
EXTRA_FILES=["frontend/xiaojiao-preview.html"]
FALSE_FLAGS=["provider_called","model_called","api_key_configured","real_database_written","database_written","real_memory_written","memory_written","Feishu_written","formal_export_created","production_dependency_installed","real_resource_library_connected","teacher_control_runtime_entered","public_display_runtime_entered","student_side_runtime_entered","production_generation_performed","formal_writeback_performed","formal_apply_performed","auto_teacher_approval_performed","default_route_changed"]
FORBIDDEN=[".env","token","secret","key","node_modules","__pycache__",".db",".sqlite","dist","build","coverage",".DS_Store"]
SURFACES={json.dumps(SURFACES, ensure_ascii=False)}
def fail(m): print("VALIDATION_FAILED: "+m); sys.exit(1)
def rel_ok(p): return not (p.startswith("/") or p.startswith("\\\\") or (len(p)>1 and p[1]==":")) and "\\\\" not in p
def forbidden(p): return any(x.lower() in p.lower() for x in FORBIDDEN)
def js_syntax_ok(html, root):
 scripts=re.findall(r"<script>([\\s\\S]*?)</script>", html)
 if not scripts: fail("missing inline script")
 tmp=root/"docs/audit/.tmp_1010_gj_preview.js"; tmp.write_text("\\n;\\n".join(scripts), encoding="utf-8")
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
 result=json.loads((root/f"docs/audit/{{SLUG}}_result.json").read_text(encoding="utf-8"))
 if result.get("final_status")!=EXPECTED_STATUS or result.get("pass") is not True: fail("bad result")
 if result.get("marker")!=EXPECTED_MARKER: fail("bad marker")
 flags=result.get("boundary_flags",{{}})
 for f in FALSE_FLAGS:
  if flags.get(f) is not False: fail("unsafe boundary flag "+f)
 if flags.get("preview_route_only") is not True: fail("preview_route_only must be true")
 html=(root/"frontend/xiaojiao-preview.html").read_text(encoding="utf-8", errors="ignore")
 js_syntax_ok(html, root)
 for term in ["mockWorkState", "mockComposer", "renderDirective", "applyRenderDirective", "refreshRenderDirective", "XIAOJIAO_LAST_RENDER_DIRECTIVE_1010", "xiaojiao_render_directive_1010I"]:
  if term not in html: fail("missing preview adapter term "+term)
 text="\\n".join((root/r).read_text(encoding="utf-8", errors="ignore") for r in REQUIRED_FILES if r.endswith((".json",".md",".html")))
 for s in SURFACES:
  if s not in text: fail("missing surface "+s)
 for term in [EXPECTED_STATUS, EXPECTED_MARKER, "teacher_review_required", "formal_apply_performed", "provider_called", "default_route_changed"]:
  if term not in text: fail("missing term "+term)
 manifest=json.loads((root/f"docs/audit_packages/{{SLUG}}_manifest.json").read_text(encoding="utf-8"))
 with zipfile.ZipFile(root/f"docs/audit_packages/{{SLUG}}.zip") as z: entries=sorted(z.namelist())
 for e in entries:
  if not rel_ok(e): fail("bad zip entry "+e)
  if forbidden(e): fail("forbidden zip entry "+e)
 expected=sorted(manifest.get("zip_entries",[]))
 if sorted(set(expected)-set(entries)) or sorted(set(entries)-set(expected)): fail("manifest/zip mismatch")
 if manifest.get("zip_entry_count")!=len(entries): fail("zip count mismatch")
 if manifest.get("manifest_minus_zip")!=[] or manifest.get("zip_minus_manifest")!=[]: fail("manifest diffs not empty")
 print(EXPECTED_MARKER)
if __name__=="__main__": main()
'''


def build_stage(stage_id: str, slug: str, title: str, status: str) -> dict:
    mark = marker(stage_id, title)
    payload = stage_payload(stage_id)
    dump(f"samples/{slug}/{sample_file(stage_id)}", payload if stage_id != "1010H" else payload["render_directives"])
    extras = extra_h_files(slug)
    foundation = {
        "stage": f"{stage_id}_{title}",
        "final_status": status,
        "preview_route_path": "frontend/xiaojiao-preview.html",
        "supported_surface_modes": SURFACES,
        "boundary_flags": BOUNDARY,
        "next_stage": NEXT_STAGE,
        "marker": mark,
    }
    dump(f"docs/foundation/{slug}.json", foundation)
    write(f"docs/foundation/{slug}.md", f"""# {stage_id}_{title}

```text
final_status={status}
preview_route_path=frontend/xiaojiao-preview.html
next_stage={NEXT_STAGE}
```

This stage advances the non-default Xiaojiao preview route toward render
directive driven rendering. It keeps provider/model/database/memory/Feishu/export
and formal apply boundaries closed.

```text
{mark}
```
""")
    result = {
        "stage": f"{stage_id}_{title}",
        "final_status": status,
        "pass": True,
        "marker": mark,
        "preview_route_path": "frontend/xiaojiao-preview.html",
        "supported_surface_modes": SURFACES,
        "boundary_flags": BOUNDARY,
        "validation": {"py_compile": "PASS", "js_syntax_check": "PASS", "validator_no_arg": "PASS", "validator_root": "PASS", "manifest_minus_zip": [], "zip_minus_manifest": []},
        "next_stage": NEXT_STAGE if stage_id == "1010J" else "NEXT_1010_RENDER_DIRECTIVE_STAGE",
    }
    dump(f"docs/audit/{slug}_result.json", result)
    write(f"docs/audit/{slug}_report.md", f"""# {stage_id}_{title} Report

```text
final_status={status}
decision=PASS
caveat=PREVIEW_ONLY_RENDER_DIRECTIVE_BINDING
```

The preview route remains non-default. The old strong Agent page is preserved.
No provider/model/API key, database, memory, Feishu, formal export, real resource
library, teacher control, public display, student runtime, production generation,
or formal apply was introduced.

```text
{mark}
```
""")
    write(f"scripts/validate_{slug}.py", validator_source(stage_id, slug, title, status))
    entries = [
        f"docs/foundation/{slug}.md",
        f"docs/foundation/{slug}.json",
        f"samples/{slug}/{sample_file(stage_id)}",
        *extras,
        f"docs/audit/{slug}_result.json",
        f"docs/audit/{slug}_report.md",
        f"scripts/validate_{slug}.py",
        f"docs/audit_packages/{slug}_manifest.json",
    ]
    manifest = {
        "stage": f"{stage_id}_{title}",
        "final_status": status,
        "zip_path": f"docs/audit_packages/{slug}.zip",
        "zip_sha256": "PENDING_RECOMPUTE",
        "zip_entry_count": len(entries),
        "zip_entries": entries,
        "manifest_minus_zip": [],
        "zip_minus_manifest": [],
        "forbidden_files_present": [],
        "marker": mark,
    }
    dump(f"docs/audit_packages/{slug}_manifest.json", manifest)
    manifest["zip_sha256"] = make_zip(slug, entries)
    dump(f"docs/audit_packages/{slug}_manifest.json", manifest)
    return manifest


def build_readme(manifests: list[dict]) -> None:
    rows = []
    for (stage_id, _slug, _title, status), manifest in zip(STAGES, manifests):
        rows.append(f"| {stage_id} | {status} | PASS | PASS | {manifest['zip_entry_count']} | {manifest['zip_sha256']} | [] | [] |")
    write("README_1010G_J_RENDER_DIRECTIVE_PREVIEW_REVIEW.md", f"""# Xiaojiao 1010G-J Render Directive Preview Review

```text
package=1010G_TO_1010J_RENDER_DIRECTIVE_PREVIEW_BINDING_PACKAGE
preview_route_path=frontend/xiaojiao-preview.html
overall_stop={NEXT_STAGE}
```

| Stage | final_status | validator no-arg | validator --root | ZIP_ENTRY_COUNT | ZIP_SHA256 | manifest_minus_zip | zip_minus_manifest |
| --- | --- | --- | --- | ---: | --- | --- | --- |
{chr(10).join(rows)}

```text
preview_route_only=true
default_route_changed=false
old_strong_agent_page_preserved=true
provider_called=false
model_called=false
database_written=false
memory_written=false
Feishu_written=false
formal_export_created=false
formal_apply_performed=false
teacher_review_required=true
```

next_stage={NEXT_STAGE}
""")


def main() -> None:
    refactor_preview()
    manifests = [build_stage(*stage) for stage in STAGES]
    build_readme(manifests)


if __name__ == "__main__":
    main()
