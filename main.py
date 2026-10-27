import html
import re
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="파이썬 코드 형광 블록 & 3줄 스크롤 분석기",
    page_icon="🐍",
    layout="wide",
)

st.title("🐍 파이썬 소스코드 역할별 형광 블록 분석기")
st.markdown(
    "파이썬 코드를 **역할별 뭉텅이(블록)로 분리 및 요약**하고, "
    "**선명한 형광색 바탕**과 **3줄 고정 스크롤 창**으로 시각화합니다."
)
st.markdown("---")

# 기본 제공 예시 코드
DEFAULT_PYTHON_CODE = """# 1. 데이터 처리 및 합산 함수 정의
def analyze_scores(scores):
    valid_scores = []
    total_sum = 0
    
    # 2. 점수 반복 순회 및 유효성 조건 검사
    for score in scores:
        if score >= 60:
            valid_scores.append(score)
            total_sum += score
            print(f"합격 점수 포함: {score}점")
        else:
            print(f"불합격 점수 제외: {score}점")
            
    # 3. 평균 계산 및 결과 반환
    average = total_sum / len(valid_scores) if valid_scores else 0
    return valid_scores, total_sum, average

# 4. 메인 데이터 정의 및 함수 호출
student_scores = [45, 75, 88, 52, 95]
passed, total, avg = analyze_scores(student_scores)

# 5. 최종 결과 리포트 출력
print(f"합격자 수: {len(passed)}명")
print(f"합격자 총점: {total}점, 평균: {avg:.1f}점")"""

# 코드 입력창
code_input = st.text_area(
    "📝 분석할 파이썬 소스코드를 입력하세요 (최소 4줄 이상):",
    value=DEFAULT_PYTHON_CODE,
    height=260,
)


# 라인별 카테고리 분류 함수
def classify_python_line(line):
  stripped = line.strip()
  if not stripped:
    return "BLANK"
  if stripped.startswith("#"):
    return "COMMENT"
  if stripped.startswith("def ") or stripped.startswith("class "):
    return "HEADER"
  if re.search(
      r"\b(if|elif|else|for|while|try|except|finally|with)\b", stripped
  ):
    return "LOGIC"
  if "print(" in stripped or stripped.startswith("return "):
    return "OUTPUT"
  return "GENERAL"


# 블록별 자동 요약 생성기
def generate_block_summary(lines, category):
  full_text = "\n".join(lines)

  if category == "COMMENT":
    return "코드의 목적, 동작 방식, 또는 작성자의 메타설명이 기재된 주석 구간입니다."
  elif category == "HEADER":
    if "def " in full_text:
      func_names = re.findall(r"def\s+(\w+)", full_text)
      return f"새로운 함수(`{', '.join(func_names)}`)의 진입점 및 매개변수를 선언하는 구간입니다."
    return "클래스(Class) 또는 구조적 프레임워크를 선언하는 진입점 구간입니다."
  elif category == "LOGIC":
    has_loop = "for " in full_text or "while " in full_text
    has_cond = "if " in full_text or "elif " in full_text or "else:" in full_text
    if has_loop and has_cond:
      return "데이터를 순차적으로 반복(loop)하면서 조건문(if)에 따라 다르게 처리하는 핵심 제어 로직입니다."
    elif has_loop:
      return "리스트나 범위(range) 데이터를 순회하며 반복 작업을 수행하는 구문입니다."
    elif has_cond:
      return "조건의 참/거짓을 판별하여 실행 흐름을 분기시키는 구문입니다."
    return "코드 실행의 조건 판단 및 예외 처리가 진행되는 제어 구간입니다."
  elif category == "OUTPUT":
    if "return " in full_text and "print(" in full_text:
      return "계산된 최종 데이터 결과를 상위 호출부로 반환함과 동시에 콘솔에 출력합니다."
    elif "return " in full_text:
      return "함수의 실행을 종료하고 계산된 처리 결과를 호출한 곳으로 반환(return)합니다."
    return (
        "처리된 결과 데이터나 안내 메시지를 화면 콘솔(print)에 출력합니다."
    )
  else:
    if "=" in full_text:
      return (
          "변수에 새로운 값을 할당하거나 연산을 수행하여 데이터를 저장하는"
          " 일반 실행 구간입니다."
      )
    return "일반 명령문 실행 및 데이터 처리 구간입니다."


# 코드 뭉텅이 그룹화 함수
def parse_python_blocks(code_text):
  lines = code_text.split("\n")
  blocks = []
  current_block_lines = []
  current_cat = None
  start_idx = 1

  for idx, line in enumerate(lines, 1):
    cat = classify_python_line(line)

    if current_cat is None:
      current_cat = cat
      start_idx = idx
      current_block_lines.append((idx, line))
    elif cat == current_cat or cat == "BLANK":
      current_block_lines.append((idx, line))
    else:
      raw_lines = [l_str for _, l_str in current_block_lines]
      summary = generate_block_summary(raw_lines, current_cat)
      blocks.append({
          "category": current_cat,
          "start": start_idx,
          "end": idx - 1,
          "lines": current_block_lines,
          "summary": summary,
      })
      current_cat = cat
      start_idx = idx
      current_block_lines = [(idx, line)]

  if current_block_lines:
    raw_lines = [l_str for _, l_str in current_block_lines]
    summary = generate_block_summary(raw_lines, current_cat)
    blocks.append({
        "category": current_cat,
        "start": start_idx,
        "end": len(lines),
        "lines": current_block_lines,
        "summary": summary,
    })

  return blocks


# 🎨 선명한 형광색 (Neon/Fluorescent) 테마 설정
FLUORESCENT_THEMES = {
    "COMMENT": {
        "title": "💡 주석 및 코드 설명 뭉텅이",
        "bg_color": "#EAFF00",  # 형광 노랑
        "border_color": "#B3C400",
        "text_color": "#000000",
    },
    "HEADER": {
        "title": "🔧 함수 / 클래스 선언 뭉텅이",
        "bg_color": "#FF007F",  # 형광 핫핑크
        "border_color": "#CC0066",
        "text_color": "#FFFFFF",
    },
    "LOGIC": {
        "title": "⚡ 조건 판단 및 반복 제어 뭉텅이",
        "bg_color": "#00E5FF",  # 형광 시안(파랑)
        "border_color": "#00B3CC",
        "text_color": "#000000",
    },
    "OUTPUT": {
        "title": "🖥️ 데이터 출력 및 결과 반환 뭉텅이",
        "bg_color": "#00FF66",  # 형광 초록
        "border_color": "#00CC52",
        "text_color": "#000000",
    },
    "GENERAL": {
        "title": "📦 변수 선언 및 일반 연산 뭉텅이",
        "bg_color": "#FF7700",  # 형광 주황
        "border_color": "#CC5F00",
        "text_color": "#FFFFFF",
    },
}

# 실행 버튼
if st.button("🚀 파이썬 코드 역할 분리 & 요약 분석 실행", type="primary"):
  lines = code_input.split("\n")

  if len(lines) < 4:
    st.warning(
        f"⚠️ 코드가 너무 짧습니다! 현재 {len(lines)}줄입니다. 최소 4줄 이상의 코드를 입력해주세요."
    )
  else:
    st.success("✨ 파이썬 소스코드 역할 분리 및 블록 요약 완료!")
    st.markdown("---")

    blocks = parse_python_blocks(code_input)

    st.subheader("🎨 1. 파이썬 역할별 형광 블록 & 3줄 고정 스크롤 뷰어")
    st.caption(
        "※ 각 코드 뭉텅이는 역할에 따른 **형광색 바탕**으로 구분되며, 코드 박스는 **정확히 3줄 크기(66px)**로 고정되어 내부 스크롤을 통해 전체 코드를 확인할 수 있습니다."
    )

    for block_num, block in enumerate(blocks, 1):
      theme = FLUORESCENT_THEMES.get(
          block["category"], FLUORESCENT_THEMES["GENERAL"]
      )

      # 블록 내부 코드 라인 HTML 변환 (줄당 22px 고정)
      line_html_list = []
      for l_num, l_text in block["lines"]:
        safe_line = html.escape(l_text).replace(" ", "&nbsp;") or "&nbsp;"
        line_html_list.append(
            f'<div style="height: 22px; line-height: 22px; white-space:'
            ' pre;"><span style="color: #888888; font-size: 11px; margin-right:'
            ' 12px; display: inline-block; width: 22px; user-select:'
            f' none;">{l_num:2d}</span><span style="color: #ffffff;'
            f' font-weight: 500;">{safe_line}</span></div>'
        )
      code_html = "".join(line_html_list)

      # 카드 렌더링 (형광 배경 + 요약 박스 + 3줄 고정 height: 66px 스크롤 창)
      st.markdown(
          f"""
            <div style="
                background-color: {theme['bg_color']};
                border: 3px solid {theme['border_color']};
                border-radius: 12px;
                padding: 14px 16px;
                margin-bottom: 22px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.12);
            ">
                <!-- 블록 타이틀 & 범위 뱃지 -->
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 8px;
                ">
                    <span style="
                        font-weight: 900;
                        font-size: 16px;
                        color: {theme['text_color']};
                    ">
                        📌 [블록 #{block_num}] {theme['title']}
                    </span>
                    <span style="
                        background-color: #000000;
                        color: #FFFFFF;
                        font-size: 11px;
                        font-weight: bold;
                        padding: 3px 10px;
                        border-radius: 12px;
                    ">
                        Lines {block['start']} ~ {block['end']}
                    </span>
                </div>

                <!-- 뭉텅이 역할 요약 카드 -->
                <div style="
                    background-color: rgba(255, 255, 255, 0.9);
                    border-left: 5px solid #000000;
                    padding: 8px 12px;
                    margin-bottom: 10px;
                    border-radius: 4px;
                    font-size: 13px;
                    color: #111111;
                    line-height: 1.5;
                ">
                    <b>💡 블록 역할 요약:</b> {block['summary']}
                </div>

                <!-- 3줄 크기 고정 (22px * 3줄 = 66px) & 내부 스크롤 창 -->
                <div style="
                    background-color: #1E1E1E;
                    border: 2px solid #000000;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-family: 'Consolas', 'Courier New', monospace;
                    font-size: 13px;
                    height: 66px;
                    overflow-y: scroll;
                    box-sizing: border-box;
                ">
                    {code_html}
                </div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    st.markdown("---")

    # 2. 블록 분석 상세 리포트
    st.subheader("🔍 2. 코드 뭉텅이별 원문 및 상세 요약")
    for block_num, block in enumerate(blocks, 1):
      theme = FLUORESCENT_THEMES.get(
          block["category"], FLUORESCENT_THEMES["GENERAL"]
      )
      raw_text = "\n".join([l_text for _, l_text in block["lines"]])

      with st.expander(
          f"🔹 [블록 #{block_num}] Lines {block['start']}~{block['end']} :"
          f" {theme['title']}",
          expanded=False,
      ):
        st.code(raw_text, language="python")
        st.write(f"• **역할 요약:** {block['summary']}")
