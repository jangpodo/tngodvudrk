import html
import re
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="소스코드 형광 블록 & 3줄 스크롤 분석기",
    page_icon="🎨",
    layout="wide",
)

st.title("🎨 형광색 칸 구분 및 3줄 스크롤 코드 블록 분석 대시보드")
st.markdown(
    "각 코드 뭉텅이를 **화려한 형광색 테두리**로 직관적으로 구분하며, "
    "코드 상자는 **기본 3줄 높이로 고정**되어 스크롤을 통해 전체 코드를 확인할 수 있습니다."
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

# 기본 제공 예시 코드
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
    "Python": """# Python 데이터 처리 예제
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
    height=260,
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


# --- 동적 제목 생성기 ---
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
      return "📦 외부 라이브러리 선언 구간"
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


# --- 코드 뭉텅이 그룹화 및 중괄호 Depth 계측 ---
def group_code_with_brace_scope(code_text, lang):
  lines = code_text.split("\n")
  blocks = []
  current_block_lines = []
  current_cat = None
  start_idx = 1
  current_depth = 0
  line_info = []

  for idx, line in enumerate(lines, 1):
    cat = get_line_category(line, lang)
    open_braces = line.count("{")
    close_braces = line.count("}")

    line_depth = current_depth
    current_depth += open_braces - close_braces
    if current_depth < 0:
      current_depth = 0

    line_info.append({
        "line_num": idx,
        "text": line,
        "category": cat,
        "depth": line_depth,
    })

  for item in line_info:
    cat = item["category"]

    if current_cat is None:
      current_cat = cat
      current_block_lines.append(item)
      start_idx = item["line_num"]
    elif cat == current_cat or cat == "BLANK":
      current_block_lines.append(item)
    else:
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


# --- 형광 컬러 스타일 정의 (강렬한 형광색 테두리 및 뱃지 적용) ---
STYLE_CONFIG = {
    "COMMENT": {
        "bg": "#FAFDE8",
        "border": "#CCFF00",  # 형광 연두/노랑
        "color": "#556B00",
        "badge_bg": "#CCFF00",
        "badge_color": "#000000",
    },
    "HEADER": {
        "bg": "#FFF0F6",
        "border": "#FF007F",  # 형광 핑크/핫핑크
        "color": "#99004D",
        "badge_bg": "#FF007F",
        "badge_color": "#FFFFFF",
    },
    "LOGIC": {
        "bg": "#E6FFFF",
        "border": "#00E5FF",  # 형광 시안/파랑
        "color": "#005566",
        "badge_bg": "#00E5FF",
        "badge_color": "#000000",
    },
    "OUTPUT": {
        "bg": "#E6FFFA",
        "border": "#00FF66",  # 형광 네온 초록
        "color": "#006624",
        "badge_bg": "#00FF66",
        "badge_color": "#000000",
    },
    "GENERAL": {
        "bg": "#F9F0FF",
        "border": "#BF00FF",  # 형광 바이올렛/보라
        "color": "#590080",
        "badge_bg": "#BF00FF",
        "badge_color": "#FFFFFF",
    },
}

# 분석 실행
if st.button("🚀 형광 블록 & 3줄 스크롤 시각화 분석 실행", type="primary"):
  lines = code_input.split("\n")

  if len(lines) < 4:
    st.warning(
        f"⚠️ 코드가 너무 짧습니다! 현재 {len(lines)}줄입니다. 최소 4줄 이상의 코드를 입력해주세요."
    )
  else:
    st.success(
        f"✨ [{selected_lang}] 형광색 칸 구분 및 3줄 스크롤 창 적용 분석 완료!"
    )
    st.markdown("---")

    blocks = group_code_with_brace_scope(code_input, selected_lang)

    st.subheader("🎨 1. 형광색 뭉텅이 구분 & 3줄 스크롤 코드 뷰어")
    st.caption(
        "※ 코드 박스는 **기본 3줄 높이**로 설정되어 있으며, 코드가 길 경우 박스 안에서 스크롤하여 확인할 수 있습니다."
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

        # 중괄호 하이라이팅
        safe_line = safe_line.replace(
            "{",
            '<b style="color:#FF007F; background:#FFE6F0; padding:0 3px;'
            ' border-radius:3px;">{</b>',
        ).replace(
            "}",
            '<b style="color:#FF007F; background:#FFE6F0; padding:0 3px;'
            ' border-radius:3px;">}</b>',
        )

        block_code_html.append(
            f'<div style="line-height: 22px; height: 22px;"><span style="color:'
            f' #999999; font-size: 11px; margin-right: 15px; user-select:'
            f' none; display: inline-block;'
            f' width: 20px;">{l_item["line_num"]:2d}</span>{safe_line}</div>'
        )

      code_content = "".join(block_code_html)

      # { } 스코프 형광 연결선
      connector_lines_html = ""
      neon_scope_colors = ["#FF007F", "#00E5FF", "#00FF66", "#BF00FF"]
      for d in range(depth):
        line_color = neon_scope_colors[d % len(neon_scope_colors)]
        connector_lines_html += f"""
                <div style="
                    position: absolute;
                    left: {d * 14}px;
                    top: 0;
                    bottom: 0;
                    width: 4px;
                    background-color: {line_color};
                    box-shadow: 0 0 6px {line_color};
                    border-radius: 2px;
                " title="Scope Level {d+1}"></div>
                """

      scope_badge = ""
      if depth > 0:
        scope_badge = f'<span style="font-size: 11px; background-color: #333333; color: #00E5FF; padding: 2px 6px; border-radius: 4px; margin-left: 8px; font-weight: bold;">🔗 Level {depth} Scope</span>'

      # HTML 카드 렌더링 (3줄 고정 max-height: 78px & overflow-y: auto)
      st.markdown(
          f"""
            <div style="position: relative; padding-left: {depth * 14 + (10 if depth > 0 else 0)}px; margin-bottom: 20px;">
                {connector_lines_html}
                <div style="
                    background-color: {style['bg']};
                    border: 3px solid {style['border']};
                    box-shadow: 0 0 8px {style['border']}88;
                    border-radius: 10px;
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
                        <span style="font-size: 12px; background-color: {style['badge_bg']}; color: {style['badge_color']}; padding: 3px 10px; border-radius: 12px; font-weight: bold;">Lines {block['start']} ~ {block['end']}</span>
                    </div>
                    <!-- 3줄 크기로 제한된 스크롤 가능 코드 영역 -->
                    <div style="
                        background-color: #ffffff;
                        border: 1px solid #d9d9d9;
                        padding: 6px 10px;
                        border-radius: 6px;
                        font-family: 'Consolas', 'Courier New', monospace;
                        font-size: 13px;
                        max-height: 78px;
                        overflow-y: auto;
                        box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
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
        st.write(f"• **자동 생성 제목:** {block['title']}")
        st.write(
            f"• **중괄호 {{ }} 깊이:** Level {block['depth']} (깊이가 클수록 안쪽"
            " 스코프에 중첩된 코드 뭉텅이입니다)"
        )
