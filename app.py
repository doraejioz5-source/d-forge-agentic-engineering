from __future__ import annotations

import os

from dotenv import load_dotenv
import streamlit as st

from dforge.agents import (
    answer_project_question,
    route_message,
    run_planner_agent,
    run_requirement_agent,
    run_reviewer_agent,
    run_system_agent,
    run_verification_agent,
)
from dforge.schemas import ProjectState
from dforge.validator import check_traceability
from dforge.workflow import run_dforge

load_dotenv()

st.set_page_config(
    page_title="D-FORGE",
    page_icon="🛠️",
    layout="wide",
)

WELCOME = """
안녕하세요. **D-FORGE Engineering Agent**입니다.

개발하고 싶은 제품·시스템·기술을 자연스럽게 설명해주세요.
제가 필요한 정보를 확인한 뒤 **요구사항 → 시스템 설계 → 시험·검증 → 개발계획** 순서로 도와드리겠습니다.

예:
공장 내부를 자율 이동하면서 설비 상태를 점검하는 소형 이동 시스템을 개발하고 싶어.
"""


def new_state() -> ProjectState:
    return ProjectState(project_goal="")


def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": WELCOME}
        ]
    if "project_state" not in st.session_state:
        st.session_state.project_state = new_state()
    if "project_context" not in st.session_state:
        st.session_state.project_context = ""
    if "awaiting_clarification" not in st.session_state:
        st.session_state.awaiting_clarification = False


def clear_downstream(state: ProjectState, from_stage: str):
    order = ["requirements", "architecture", "verification", "review", "planning"]
    idx = order.index(from_stage)

    if idx <= 0:
        state.architecture = None
    if idx <= 1:
        state.verification = None
        state.traceability = None
    if idx <= 2:
        state.review = None
    if idx <= 3:
        state.development_plan = None


def clarification_reply():
    state = st.session_state.project_state
    questions = state.requirements.clarification_questions
    body = "\n".join(f"{i}. {q}" for i, q in enumerate(questions, 1))
    return (
        "🧭 Router → **Requirement Agent**\n\n"
        "요구사항을 확정하기 전에 정보가 조금 더 필요합니다.\n\n"
        f"{body}\n\n"
        "위 질문에 편하게 한 번에 답해주세요."
    )


def requirements_reply():
    state = st.session_state.project_state
    lines = ["🧭 Router → **Requirement Agent**", "", "### 요구사항을 정리했습니다."]
    for req in state.requirements.requirements:
        lines.append(f"- **{req.id}** · {req.description}")
    lines += [
        "",
        "이제 '시스템 설계해줘'라고 입력하면 다음 단계로 진행할 수 있습니다.",
    ]
    return "\n".join(lines)


def architecture_reply():
    state = st.session_state.project_state
    lines = ["🧭 Router → **System Design Agent**", "", "### 기능 구조를 만들었습니다."]
    for module in state.architecture.modules:
        refs = ", ".join(module.related_requirements) or "-"
        lines.append(
            f"- **{module.id} · {module.name}** — {module.purpose}  \n"
            f"  ↳ 연계 요구사항: {refs}"
        )
    lines += [
        "",
        "다음으로 '시험계획 만들어줘'라고 입력할 수 있습니다.",
    ]
    return "\n".join(lines)


def verification_reply():
    state = st.session_state.project_state
    lines = ["🧭 Router → **Verification Agent**", "", "### 시험·검증 계획을 만들었습니다."]
    for test in state.verification.tests:
        refs = ", ".join(test.requirement_ids) or "-"
        lines.append(
            f"- **{test.id}** · {test.objective}  \n"
            f"  ↳ REQ: {refs}  \n"
            f"  ↳ 판정기준: {test.pass_criteria}"
        )

    trace = state.traceability
    lines += ["", "### Traceability Check"]
    if trace.coverage_ok:
        lines.append("✅ 모든 요구사항이 설계 모듈과 시험 항목에 연결되어 있습니다.")
    else:
        if trace.missing_module_mapping:
            lines.append(
                "⚠️ 설계 연결 누락: " + ", ".join(trace.missing_module_mapping)
            )
        if trace.missing_test_mapping:
            lines.append(
                "⚠️ 시험 연결 누락: " + ", ".join(trace.missing_test_mapping)
            )
    return "\n".join(lines)


def review_reply():
    state = st.session_state.project_state
    lines = [
        "🧭 Router → **Reviewer Agent**",
        "",
        "### Engineering Review",
        state.review.summary,
    ]
    if state.review.issues:
        lines += ["", "**확인할 항목**"]
        lines += [f"- {item}" for item in state.review.issues]
    if state.review.recommended_actions:
        lines += ["", "**권장 수정**"]
        lines += [f"- {item}" for item in state.review.recommended_actions]
    return "\n".join(lines)


def planning_reply():
    state = st.session_state.project_state
    lines = ["🧭 Router → **Development Planner**", "", "### R&D 개발계획"]
    for phase in state.development_plan.phases:
        lines.append(f"**{phase.phase}** — {phase.goal}")
        lines.extend(f"- {item}" for item in phase.outputs)
        lines.append("")
    return "\n".join(lines)


def status_reply():
    state = st.session_state.project_state

    req = len(state.requirements.requirements) if state.requirements else 0
    mods = len(state.architecture.modules) if state.architecture else 0
    tests = len(state.verification.tests) if state.verification else 0

    stages = [
        ("요구사항", state.requirements is not None and not state.requirements.needs_clarification),
        ("시스템 설계", state.architecture is not None),
        ("시험·검증", state.verification is not None),
        ("Traceability", state.traceability is not None),
        ("Engineering Review", state.review is not None),
        ("개발계획", state.development_plan is not None),
    ]

    lines = ["🧭 Router → **Project Status**", "", "### 현재 진행 상태"]
    lines.extend(
        f"{'✅' if done else '○'} {name}" for name, done in stages
    )
    lines += [
        "",
        f"요구사항 **{req}개** · 모듈 **{mods}개** · 시험 **{tests}개**",
    ]
    return "\n".join(lines)


def ensure_requirements():
    state = st.session_state.project_state
    if state.requirements and not state.requirements.needs_clarification:
        return True

    state.requirements = run_requirement_agent(st.session_state.project_context)
    if state.requirements.needs_clarification:
        st.session_state.awaiting_clarification = True
        return False
    return True


def ensure_architecture():
    state = st.session_state.project_state
    if not ensure_requirements():
        return False
    if state.architecture is None:
        state.architecture = run_system_agent(
            st.session_state.project_context,
            state.requirements,
        )
    return True


def ensure_verification():
    state = st.session_state.project_state
    if not ensure_architecture():
        return False
    if state.verification is None:
        state.verification = run_verification_agent(
            st.session_state.project_context,
            state.requirements,
            state.architecture,
        )
        state.traceability = check_traceability(
            state.requirements,
            state.architecture,
            state.verification,
        )
    return True


def fallback_action(message: str) -> str:
    text = message.lower()
    if any(word in text for word in ["전체", "끝까지", "보고서", "다 진행", "계속 진행"]):
        return "run_all"
    if any(word in text for word in ["시험", "검증", "테스트"]):
        return "verification"
    if any(word in text for word in ["설계", "구성", "아키텍처", "architecture"]):
        return "architecture"
    if any(word in text for word in ["리뷰", "검토", "누락", "추적"]):
        return "review"
    if any(word in text for word in ["개발계획", "일정", "로드맵", "플랜"]):
        return "planning"
    if any(word in text for word in ["상태", "어디까지", "진행 상황"]):
        return "status"
    return "question"


def handle_message(message: str) -> str:
    state = st.session_state.project_state

    if not state.project_goal:
        st.session_state.project_context = message
        state.project_goal = message
        state.requirements = run_requirement_agent(st.session_state.project_context)

        if state.requirements.needs_clarification:
            st.session_state.awaiting_clarification = True
            return clarification_reply()

        return requirements_reply()

    if st.session_state.awaiting_clarification:
        st.session_state.project_context += f"\n추가 정보: {message}"
        state.project_goal = st.session_state.project_context
        state.requirements = run_requirement_agent(st.session_state.project_context)
        clear_downstream(state, "requirements")

        if state.requirements.needs_clarification:
            return clarification_reply()

        st.session_state.awaiting_clarification = False
        return requirements_reply()

    try:
        decision = route_message(message, state)
        action = decision.action
    except Exception:
        action = fallback_action(message)

    if action == "requirements":
        st.session_state.project_context += f"\n사용자 변경사항: {message}"
        state.project_goal = st.session_state.project_context
        state.requirements = run_requirement_agent(st.session_state.project_context)
        clear_downstream(state, "requirements")

        if state.requirements.needs_clarification:
            st.session_state.awaiting_clarification = True
            return clarification_reply()

        return requirements_reply()

    if action == "architecture":
        if not ensure_requirements():
            return clarification_reply()

        state.architecture = run_system_agent(
            st.session_state.project_context,
            state.requirements,
        )
        clear_downstream(state, "architecture")
        return architecture_reply()

    if action == "verification":
        if not ensure_architecture():
            return clarification_reply()

        state.verification = run_verification_agent(
            st.session_state.project_context,
            state.requirements,
            state.architecture,
        )
        state.traceability = check_traceability(
            state.requirements,
            state.architecture,
            state.verification,
        )
        state.review = None
        state.development_plan = None
        return verification_reply()

    if action == "review":
        if not ensure_verification():
            return clarification_reply()

        state.review = run_reviewer_agent(state)
        state.development_plan = None
        return review_reply()

    if action == "planning":
        if not ensure_verification():
            return clarification_reply()

        if state.review is None:
            state.review = run_reviewer_agent(state)
        state.development_plan = run_planner_agent(state)
        return planning_reply()

    if action == "run_all":
        result = run_dforge(st.session_state.project_context)
        st.session_state.project_state = result.state

        if result.stopped_for_clarification:
            st.session_state.awaiting_clarification = True
            return clarification_reply()

        st.session_state.awaiting_clarification = False
        return (
            "🧭 Router → **Full Engineering Workflow**\n\n"
            "✅ 요구사항 → 시스템 설계 → 시험·검증 → Traceability → "
            "Engineering Review → 개발계획까지 완료했습니다.\n\n"
            + status_reply()
        )

    if action == "status":
        return status_reply()

    advisor = answer_project_question(message, state)
    return (
        "🧭 Router → **Engineering Advisor**\n\n"
        + advisor.answer
    )


init_session()

state = st.session_state.project_state

with st.sidebar:
    st.title("D-FORGE")
    st.caption("Project Memory")

    if state.project_goal:
        st.markdown("**현재 프로젝트**")
        short_goal = state.project_goal.split("\n")[0]
        st.write(short_goal[:140])
    else:
        st.write("아직 프로젝트가 시작되지 않았습니다.")

    req_count = len(state.requirements.requirements) if state.requirements else 0
    mod_count = len(state.architecture.modules) if state.architecture else 0
    test_count = len(state.verification.tests) if state.verification else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("REQ", req_count)
    c2.metric("MOD", mod_count)
    c3.metric("TEST", test_count)

    if state.traceability:
        st.metric(
            "Traceability",
            "PASS" if state.traceability.coverage_ok else "CHECK",
        )

    st.divider()
    st.caption("예시 명령")
    st.write("• 시스템 설계해줘")
    st.write("• 시험계획 만들어줘")
    st.write("• 누락된 요구사항 있어?")
    st.write("• 개발계획까지 만들어줘")
    st.write("• 현재 어디까지 됐어?")
    st.write("• 전체 계속 진행해줘")

    st.divider()
    if st.button("새 프로젝트 시작", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": WELCOME}
        ]
        st.session_state.project_state = new_state()
        st.session_state.project_context = ""
        st.session_state.awaiting_clarification = False
        st.rerun()

    with st.expander("ProjectState 보기"):
        st.json(state.model_dump())

st.title("D-FORGE Engineering Agent")
st.caption(
    "R&D 개발자와 대화하면서 현재 프로젝트 상태를 기억하고 "
    "필요한 Engineering Agent를 선택해 실행합니다."
)

if not os.getenv("OPENAI_API_KEY"):
    st.warning(
        "OPENAI_API_KEY가 설정되지 않았습니다. "
        "로컬의 .env 파일에 키를 추가한 뒤 실행해주세요."
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input(
    "개발 아이디어 또는 Engineering 요청을 입력하세요..."
)

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("D-FORGE가 현재 프로젝트 상태를 확인하고 있습니다..."):
            try:
                response = handle_message(prompt)
            except Exception as exc:
                response = (
                    "실행 중 오류가 발생했습니다. API 키와 네트워크 상태를 확인해주세요.\n\n"
                    f"오류: {type(exc).__name__}"
                )

        st.markdown(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )
