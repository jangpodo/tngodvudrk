import html
import re
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="다국어 소스코드 블록 하이라이트 & { } 연관선 분석기",
    page_icon="🎨",
    layout="wide",
)

st.title("🎨 소스코드 블록 하이라이트 & { } 스코프 연결 분석 대시보드")
st.markdown(
    "각 코드 뭉텅이(블록)의 **상세 동작 해석을 제목으로 자동 생성**하고, "
    "**`{ }` (중괄호/대괄호) 영역에 묶인 코드 블록들을 얇은 연결선**으로 visual하게 이어 보여줍니다."
)
st.markdown("---")

# 1. 언어 선택 버튼
st.subheader("🌐 언어 선택")
selected_lang = st.radio(
    "분석할 프로그래밍 언어를 선택하세요:",
    ["C", "C++", "Java", "Python"],
    horizontal=True,
    index=0,
)

# 기본 제공 예시 코드 (최소 4줄 이상 및 { } 구문 포함)
default_codes = {
    "C": """// C언어 점수 판별 및 카운트다운 예제
#include <stdio.h>

void check_grade(int score) {
    // 점수 조건 판별 블록
    if (score >= 90) {
        printf("A학점입니다.\\n");
    } else {
        printf("B학점 이하입니다.\\n");
    }
    
    // 반복 카운트다운 블록
    for (int i = 0; i < 3; i++) {
        printf("카운트다운: %d\\n", i);
    }
}

int main() {
    check_grade(95);
    return 0;
}""",
    "C++": """// C++ 데이터 처리 예제
#include <iostream>
using namespace std;

void process_data(int count) {
    // 조건 판단 구간
    if (count > 5) {
        cout << "데이터가 충분합니다." << endl;
    } else {
        cout << "데이터가 부족합니다." << endl;
    }

    // 데이터 반복 처리 구간
    for (int i = 0; i < count; i++) {
        cout << "프로세스 실행 중... #" << i + 1 << endl;
    }
}

int main() {
    process_data(3);
    return 0;
}""",
    "Java": """// Java 권한 검사 예제
public class Main {
    public static void checkAge(int age) {
        // 연령 판별 조건문
        if (age >= 18) {
            System.out.println("성인입니다.");
        } else {
            System.out.println("미성년자입니다.");
        }

        // 반복 대기열 검사
        for (int i = 0; i < 3; i++) {
            System.out.println("대기 순번: " + (i + 1));
        }
    }

    public static void main(String[] args) {
        checkAge(20);
    }
}""",
    "Python": """# Python 데이터 처리 예제 (인덴트 블록 구조)
def process_scores(scores):
    total = 0
    
    # 반복 및 조건 검사
    for score in scores:
        if score >= 80:
            total += score
            print(f"합격점 추가: {score}")
        else:
            print(f"불합격점 제외: {score}")
            
    return total

# 메인 실행
data = [75, 85, 90, 60]
result = process_scores(data)
print(f"최종 합산 점수: {result}")""",
}

st.markdown("---")
st.subheader("📝 분석할 소스코드 (최소 4줄 이상)")
code_input = st.text_area(
    f"[{selected_lang}] 코드를 입력하거나 아래 예시를 수정하세요:",
    value=default_codes[selected_lang],
    height=280,
)


# --- 라인 유형 분류 함수 ---
def get_line_category(line, lang):
  stripped = line.strip()
  if not stripped:
    return "BLANK"

  # 주석
  if (lang == "Python" and stripped.startswith("#")) or (
      lang != "Python"
      and (
          stripped.startswith("//")
          or stripped.startswith("/*")
          or stripped.startswith("*")
      )
  ):
    return "COMMENT"

  # 함수 / 클래스 선언
  if lang == "Python" and (
      stripped.startswith("def ") or stripped.startswith("class ")
  ):
    return "HEADER"
  if lang in ["C", "C++"] and (
      re.search(
          r"\b(void|int|float|double|char|bool|auto)\s+\w+\s*\(", stripped
      )
      or "main(" in stripped
      or stripped.startswith("#include")
  ):
    return "HEADER"
  if lang == "Java" and (
      "class " in stripped
      or re.search(
          r"\b(public|private|protected|static|void)\s+\w+\s*\(", stripped
      )
  ):
    return "HEADER"

  # 조건 / 반복 제어구문
  if re.search(r"\b(if|else|elif|for|while|switch|case|do)\b", stripped):
    return "LOGIC"

  # 출력 구문
  if (
      ("print(" in stripped or "printf(" in stripped)
      or ("cout" in stripped)
      or ("System.out." in stripped)
  ):
    return "OUTPUT"

  return "GENERAL"


# --- 상세 동작 해석 기반 제목 생성기 ---
def generate_detailed_title(lines, category, lang):
  full_text = " ".join(lines)

  if category == "COMMENT":
    return "💡 코드 설명 및 주석 메타정보 구간"

  elif category == "HEADER":
    if "main" in full_text:
      return "🚀 메인(Main) 프로그램 진입점 및 실행 함수 정의"
    elif "class" in full_text:
      return "🏗️ 클래스(Class) 객체 데이터 구조 정의"
    elif "#include" in full_text or "import" in full_text:
      return "📦 외부 라이브러리 및 헤더 파일 포함 선언"
    else:
      return "🔧 핵심 기능 수행 전용 함수/메서드 선언"

  elif category == "LOGIC":
    has_loop = any(
        k in full_text
        for k in ["for", "while", "for (", "while (", "for ", "while "]
    )
    has_cond = any(
        k in full_text for k in ["if", "else", "switch", "case", "elif"]
    )
    if has_loop and has_cond:
      return "🔄⚡ 데이터 반복 순회 및 조건부 결과 판별 제어 로직"
    elif has_loop:
      return "🔄 데이터 연속 반복 처리 및 순회 제어 로직"
    elif has_cond:
      return "⚡ 분기 조건(If/Else) 비교 판단 및 흐름 제어 로직"
    return "⚙️ 핵심 연산 및 로직 제어 구간"

  elif category == "OUTPUT":
    if "return" in full_text:
      return "🖥️ 처리된 데이터 계산 결과 화면 출력 및 반환"
    return "🖥️ 콘솔 화면 결과 데이터 출력 및 메시지 로깅"

  else:
    if "return" in full_text:
      return "📤 상위 함수로 최종 결과값 반환(Return)"
    elif "=" in full_text:
      return "📝 변수 선언, 값 저장 및 데이터 초기화 연산"
    return "📦 일반 명령어 실행 및 연산 처리 구간"


# --- 코드 뭉텅이 그룹화 및 `{ }` 스코프 깊이 측정 ---
def group_code_with_brace_scope(code_text, lang):
  lines = code_text.split("\n")
  blocks = []
  current_block_lines = []
  current_cat = None
  start_idx = 1

  # 라인별 중괄호 Depth 측정
  current_depth = 0
  line_info = []

  for idx, line in enumerate(lines, 1):
    cat = get_line_category(line, lang)

    # 단순 문자열 내부 제외한 { } 개수 카운트
    open_braces = line.count("{")
    close_braces = line.count("}")

    # 현재 라인의 depth 정보 기록
    line_depth = current_depth
    current_depth += open_braces - close_braces
    if current_depth < 0:
      current_depth = 0

    line_info.append({
        "line_num": idx,
        "text": line,
        "category": cat,
        "depth": line_depth,
        "open_braces": open_braces,
        "close_braces": close_braces,
    })

  # 뭉텅이(블록) 단위로 묶기
  for item in line_info:
    cat = item["category"]

    if current_cat is None:
      current_cat = cat
      current_block_lines.append(item)
      start_idx = item["line_num"]
    elif cat == current_cat or cat == "BLANK":
      current_block_lines.append(item)
    else:
      # 대표 Depth 계산 (블록 내 최소 depth)
      min_depth = min(x["depth"] for x in current_block_lines)
      raw_lines = [x["text"] for x in current_block_lines]
      detailed_title = generate_detailed_title(raw_lines, current_cat, lang)

      blocks.append({
          "category": current_cat,
          "title": detailed_title,
          "start": start_idx,
          "end": item["line_num"] - 1,
          "depth": min_depth,
          "lines": current_block_lines,
      })
      current_cat = cat
      current_block_lines = [item]
      start_idx = item["line_num"]

  if current_block_lines:
    min_depth = min(x["depth"] for x in current_block_lines)
    raw_lines = [x["text"] for x in current_block_lines]
    detailed_title = generate_detailed_title(raw_lines, current_cat, lang)

    blocks.append({
        "category": current_cat,
        "title": detailed_title,
        "start": start_idx,
        "end": len(lines),
        "depth": min_depth,
        "lines": current_block_lines,
    })

  return blocks


# 블록 시각화 스타일
STYLE_CONFIG = {
    "COMMENT": {
        "bg": "#FFFBE6",
        "border": "#FAAD14",
        "color": "#8C6B00",
        "line_color": "#ffe58f",
    },
    "HEADER": {
        "bg": "#FFF0F0",
        "border": "#FF4D4F",
        "color": "#A8071A",
        "line_color": "#ffccc7",
    },
    "LOGIC": {
        "bg": "#F9F0FF",
        "border": "#9254DE",
        "color": "#391085",
        "line_color": "#d3ade6",
    },
    "OUTPUT": {
        "bg": "#F6FFED",
        "border": "#52C41A",
        "color": "#135200",
        "line_color": "#b7eb8f",
    },
    "GENERAL": {
        "bg": "#F0F5FF",
        "border": "#2F54EB",
        "color": "#10239E",
        "line_color": "#adc6ff",
    },
}

# 분석 실행
if st.button("🚀 소스코드 블록 하이라이트 & { } 스코프 분석 실행", type="primary"):
  lines = code_input.split("\n")

  if len(lines) < 4:
    st.warning(
        f"⚠️ 코드가 너무 짧습니다! 현재 {len(lines)}줄입니다. 최소 4줄 이상의 코드를 입력해주세요."
    )
  else:
    st.success(
        f"✨ [{selected_lang}] 코드를 동작 해석 제목과 {{ }} 연결선 포함하여 블록 분석을 완료했습니다!"
    )
    st.markdown("---")

    blocks = group_code_with_brace_scope(code_input, selected_lang)

    st.subheader("🎨 1. { } 스코프 연결선 및 동작 해석 블록 시각화")
    st.caption(
        "※ 상세 동작 해석이 블록 제목으로 지정되며, `{ }` (중괄호) 범위로 묶인 코드 블록은 좌측에 **얇은 스코프 연결선**이 생성됩니다."
    )

    for block_num, block in enumerate(blocks, 1):
      style = STYLE_CONFIG.get(block["category"], STYLE_CONFIG["GENERAL"])
      depth = block["depth"]

      # 블록 내부 코드 HTML 변환
      block_code_html = []
      for l_item in block["lines"]:
        safe_line = html.escape(l_item["text"]).replace(" ", "&nbsp;")
        if not safe_line:
          safe_line = "&nbsp;"

        # 중괄호 하이라이팅 강조
        safe_line = safe_line.replace(
            "{",
            '<b style="color:#d9d9d9; background:#262626; padding:0 3px; border-radius:3px;">{</b>',
        ).replace(
            "}",
            '<b style="color:#d9d9d9; background:#262626; padding:0 3px; border-radius:3px;">}</b>',
        )

        block_code_html.append(
            f'<div><span style="color: #bfbfbf; font-size: 11px;'
            f' margin-right: 15px; user-select:'
            f' none;">{l_item["line_num"]:2d}</span>{safe_line}</div>'
        )

      code_content = "".join(block_code_html)

      # { } 연결선 (Depth 계층에 따른 좌측 연결선 패딩 및 가이드선 생성)
      connector_lines_html = ""
      for d in range(depth):
        line_color = ["#1890FF", "#722ED1", "#FA8C16", "#52C41A"][d % 4]
        connector_lines_html += f"""
                <div style="
                    position: absolute;
                    left: {d * 14}px;
                    top: 0;
                    bottom: 0;
                    width: 3px;
                    background-color: {line_color};
                    border-radius: 2px;
                    opacity: 0.85;
                " title="{{ }} 스코프 연결선 (Level {d+1})"></div>
                """

      scope_badge = ""
      if depth > 0:
        scope_badge = f'<span style="font-size: 11px; background-color: #595959; color: white; padding: 2px 6px; border-radius: 4px; margin-left: 8px;">🔗 {{ }} Scope Level {depth}</span>'

      # HTML 카드 렌더링 (연결선 + 블록 테두리)
      st.markdown(
          f"""
            <div style="position: relative; padding-left: {depth * 14 + (10 if depth > 0 else 0)}px; margin-bottom: 16px;">
                {connector_lines_html}
                <div style="
                    background-color: {style['bg']};
                    border: 2px solid {style['border']};
                    border-radius: 8px;
                    padding: 12px 14px;
                ">
                    <div style="
                        font-weight: bold;
                        color: {style['color']};
                        font-size: 15px;
                        margin-bottom: 8px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    ">
                        <span>📌 [블록 #{block_num}] {block['title']} {scope_badge}</span>
                        <span style="font-size: 12px; background-color: {style['border']}; color: white; padding: 2px 8px; border-radius: 4px;">Lines {block['start']} ~ {block['end']}</span>
                    </div>
                    <div style="
                        background-color: #ffffff;
                        border: 1px solid #e8e8e8;
                        padding: 10px 12px;
                        border-radius: 6px;
                        font-family: 'Consolas', 'Courier New', monospace;
                        font-size: 13px;
                        line-height: 1.6;
                        color: #262626;
                    ">
                        {code_content}
                    </div>
                </div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    st.markdown("---")

    # 2. 블록 분석 리포트
    st.subheader("🔍 2. 코드 뭉텅이별 구조 상세 리포트")
    for block_num, block in enumerate(blocks, 1):
      raw_block_text = "\n".join([x["text"] for x in block["lines"]])
      with st.expander(
          f"🔹 [블록 #{block_num}] Lines {block['start']}~{block['end']} :"
          f" {block['title']}",
          expanded=False,
      ):
        st.code(raw_block_text, language=selected_lang.lower())
        st.write(f"• **상세 역할:** {block['title']}")
        st.write(
            f"• **중괄호 {{ }} 스코프 깊이:** Level {block['depth']} (깊이가 높을수록"
            " 내부 스코프에 중첩된 코드입니다)"
        )
