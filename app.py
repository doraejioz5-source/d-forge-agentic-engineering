from __future__ import annotations

import os
from dotenv import load_dotenv
import streamlit as st

from dforge.workflow import run_dforge

load_dotenv()

st.set_page_config(page_title="D-FORGE", page_icon="🛠️", layout="wide")

st.title("D-FORGE")
st.caption("Agentic Engineering LLM MVP — R&D 개발 프로세스 초안 자동화")

st.info(
    "데모 범위: 점검·정비·센서·로봇·모니터링 등 안전한 R&D의 요구사항, "
    "기능 설계, 시험계획, 추적성, 개발계획을 구조화합니다."
)

if not os.getenv("OPENAI_API_KEY"):
    st.warning("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

sample = (
    "공장 내부를 자율 이동하면서 설비 상태를 점검하는 소형 이동 시스템을 개발하고 싶다. "
    "영상 저장은 하지 않고, 위치·장애물·설비 상태 센서만 사용하고 싶다."
)

project_goal = st.text_area(
    "개발 목표",
    value=sample,
    height=140,
    help="처음에는 개발자가 실제로 말하듯 자연어로 입력하면 됩니다.",
)

run = st.button("Engineering 시작", type="primary", use_container_width=True)

if run:
    status = st.status("D-FORGE Engineering Workflow 실행 중", expanded=True)

    def on_progress(step: str, message: str):
        status.write(f"**{step.upper()}** — {message}")

    try:
        result = run_dforge(project_goal, on_progress=on_progress)
        state = result.state

        if result.stopped_for_clarification:
            status.update(label="추가 정보가 필요합니다", state="complete")
            st.subheader("추가 질문")
            for q in state.requirements.clarification_questions:
                st.write(f"- {q}")
            st.stop()

        status.update(label="Engineering Report 완료", state="complete")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("요구사항", len(state.requirements.requirements))
        c2.metric("기능 모듈", len(state.architecture.modules))
        c3.metric("시험 항목", len(state.verification.tests))
        c4.metric("Traceability", "PASS" if state.traceability.coverage_ok else "CHECK")

        tabs = st.tabs([
            "01 요구사항",
            "02 시스템 설계",
            "03 시험·검증",
            "04 추적성",
            "05 리뷰",
            "06 개발계획",
            "JSON",
        ])

        with tabs[0]:
            for req in state.requirements.requirements:
                st.markdown(f"**{req.id} · {req.category}**")
                st.write(req.description)

        with tabs[1]:
            for module in state.architecture.modules:
                st.markdown(f"**{module.id} · {module.name}**")
                st.write(module.purpose)
                st.caption("연계 요구사항: " + ", ".join(module.related_requirements))

        with tabs[2]:
            for test in state.verification.tests:
                st.markdown(f"**{test.id}** — {test.objective}")
                st.write(f"연계 요구사항: {', '.join(test.requirement_ids)}")
                st.write(f"방법: {test.method}")
                st.write(f"판정기준: {test.pass_criteria}")

        with tabs[3]:
            for rid in state.traceability.requirement_ids:
                module_ok = rid in state.traceability.mapped_to_module
                test_ok = rid in state.traceability.mapped_to_test
                st.write(
                    f"{'✅' if module_ok else '⚠️'} {rid} → Module | "
                    f"{'✅' if test_ok else '⚠️'} {rid} → Test"
                )

        with tabs[4]:
            st.write(state.review.summary)
            for item in state.review.issues:
                st.write(f"- {item}")

        with tabs[5]:
            for phase in state.development_plan.phases:
                st.markdown(f"**{phase.phase}**")
                st.write(phase.goal)
                for output in phase.outputs:
                    st.write(f"- {output}")

        with tabs[6]:
            st.json(state.model_dump())

    except Exception as exc:
        status.update(label="실행 오류", state="error")
        st.exception(exc)
