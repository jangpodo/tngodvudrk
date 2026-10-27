import html
import re
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="소스코드 형광 블록 & 3줄 스크롤 분석기",
    page_icon="🎨",
    layout="wide",
)

st.title("🎨 형광색 블록 구분 및 3줄 스크롤 코드 분석 대시보드")
st.markdown(
    "각 코드 뭉텅이를 **선명한 형광색 전체 블록**으로 구분하고, "
    "코드 상자는 **정확히 3줄 높이(66px)로 고정**하여 내부 스크롤로 조회하도록 구현했습니다."
)
st.markdown("---")

# 1. 언어 선택 라디오 버튼
st.subheader("🌐 프로그래밍 언어 선택")
selected_lang = st.radio(
    "분석할 언어를 선택하세요:",
    ["C", "C++", "Java", "Python"],
    horizontal=True,
    index=0,
)

# 기본 예시 코드
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
st.subheader("📝 소스코드 입력 (최소 4줄 이상)")
code_input = st.text_area(
    f"[{selected_lang}] 코드를 입력하거나 예시를 수정하세요:",
    value=default_codes[selected_lang],
    height=250,
)


# 라인 역할 분류
def get_line_category(line, lang):
  stripped = line.strip()
  if not stripped:
    return "BLANK"

  if (lang == "Python" and stripped.startswith("#")) or (
      lang != "Python"
      and (
          stripped.startswith("//")
          or stripped.startswith("/*")
          or stripped.startswith("*")
      )
  ):
    return "COMMENT"

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

  if re.search(r"\b(if|else|elif|for|while|switch|case|do)\b", stripped):
    return "LOGIC"

  if (
      ("print(" in stripped or "printf(" in stripped)
      or ("cout" in stripped)
      or ("System.out." in stripped)
  ):
    return "OUTPUT"

  return "GENERAL"


# 자동 제목 생성
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
    return (
        "🖥️ 처리 결과 화면 출력 및 반환"
        if "return" in full_text
        else "🖥️ 콘솔 화면 데이터 출력 및 메시지 로깅"
    )
  else:
    return (
        "📝 변수 선언, 값 저장 및 연산 구간"
        if "=" in full_text
        else "📦 일반 명령어 실행 및 연산 처리 구간"
    )


# 뭉텅이 그룹화 및 중괄호 Depth 계산
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


# 🎨 선명한 형광색(Neon/Fluorescent) 블록 스타일 정의
FLUORESCENT_STYLES = {
    "COMMENT": {
        "block_bg": "#EAFF00",  # 형광 노랑
        "text_color": "#000000",
        "badge_bg": "#000000",
        "badge_text": "#EAFF00",
        "border_color": "#B3C400",
    },
    "HEADER": {
        "block_bg": "#FF007F",  # 형광 핫핑크
        "text_color": "#FFFFFF",
        "badge_bg": "#FFFFFF",
        "badge_text": "#FF007F",
        "border_color": "#CC0066",
    },
    "LOGIC": {
        "block_bg": "#00E5FF",  # 형광 시안(블루)
        "text_color": "#000000",
        "badge_bg": "#000000",
        "badge_text": "#00E5FF",
        "border_color": "#00B3CC",
    },
    "OUTPUT": {
        "block_bg": "#00FF66",  # 형광 네온 그린
        "text_color": "#000000",
        "badge_bg": "#000000",
        "badge_text": "#00FF66",
        "border_color": "#00CC52",
    },
    "GENERAL": {
        "block_bg": "#BD00FF",  # 형광 보라(퍼플)
        "text_color": "#FFFFFF",
        "badge_bg": "#FFFFFF",
        "badge_text": "#BD00FF",
        "border_color": "#9900CC",
    },
}

# 분석 실행 버튼
if st.button("🚀 형광 블록 & 3줄 스크롤 시각화 분석 실행", type="primary"):
  lines = code_input.split("\n")

  if len(lines) < 4:
    st.warning(
        f"⚠️ 코드가 너무 짧습니다! 현재 {len(lines)}줄입니다. 최소 4줄 이상의 코드를 입력해주세요."
    )
  else:
    st.success(
        f"✨ [{selected_lang}] 형광색 블록 구분 및 3줄 제한 스크롤 뷰 분석 완료!"
    )
    st.markdown("---")

    blocks = group_code_with_brace_scope(code_input, selected_lang)

    st.subheader("🎨 1. 형광색 뭉텅이 블록 & 3줄 고정 스크롤 뷰어")
    st.caption(
        "※ 코드 박스는 **정확히 3줄 높이(66px)**로 고정되며, 3줄보다 긴 코드는 박스 내 스크롤을 내려서 확인할 수 있습니다."
    )

    for block_num, block in enumerate(blocks, 1):
      style = FLUORESCENT_STYLES.get(
          block["category"], FLUORESCENT_STYLES["GENERAL"]
      )
      depth = block["depth"]

      # 블록 내부 코드 HTML 변환 (각 줄 22px 높이 고정)
      block_code_html = []
      for l_item in block["lines"]:
        safe_line = html.escape(l_item["text"]).replace(" ", "&nbsp;")
        if not safe_line:
          safe_line = "&nbsp;"

        # 중괄호 하이라이팅
        safe_line = safe_line.replace(
            "{",
            '<b style="background:#000000; color:#00FF66; padding:0 4px;'
            ' border-radius:3px;">{</b>',
        ).replace(
            "}",
            '<b style="background:#000000; color:#00FF66; padding:0 4px;'
            ' border-radius:3px;">}</b>',
        )

        block_code_html.append(
            f'<div style="height: 22px; line-height: 22px;'
            ' white-space: nowrap;"><span style="color: #666666;'
            ' font-size: 11px; margin-right: 12px; display: inline-block;'
            f' width: 22px; user-select: none;">{l_item["line_num"]:2d}</span><span'
            f' style="color: #111111; font-weight: 600;">{safe_line}</span></div>'
        )

      code_content = "".join(block_code_html)

      # { } 스코프 연결선
      connector_lines_html = ""
      neon_lines = ["#FF007F", "#00E5FF", "#00FF66", "#EAFF00"]
      for d in range(depth):
        line_color = neon_lines[d % len(neon_lines)]
        connector_lines_html += f"""
                <div style="
                    position: absolute;
                    left: {d * 14}px;
                    top: 0;
                    bottom: 0;
                    width: 4px;
                    background-color: {line_color};
                    box-shadow: 0 0 8px {line_color};
                    border-radius: 2px;
                " title="Scope Level {d+1}"></div>
                """

      scope_badge = ""
      if depth > 0:
        scope_badge = f'<span style="font-size: 11px; background-color: #000000; color: #00E5FF; padding: 2px 7px; border-radius: 4px; margin-left: 8px;">🔗 Level {depth} Scope</span>'

      # HTML 형광 블록 렌더링 (height: 66px 로 정확히 3줄 세팅)
      st.markdown(
          f"""
            <div style="position: relative; padding-left: {depth * 14 + (10 if depth > 0 else 0)}px; margin-bottom: 22px;">
                {connector_lines_html}
                <div style="
                    background-color: {style['block_bg']};
                    border: 3px solid {style['border_color']};
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    border-radius: 10px;
                    padding: 12px 14px;
                ">
                    <!-- 형광 블록 헤더 -->
                    <div style="
                        font-weight: 800;
                        color: {style['text_color']};
                        font-size: 15px;
                        margin-bottom: 8px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    ">
                        <span>📌 [블록 #{block_num}] {block['title']} {scope_badge}</span>
                        <span style="
                            font-size: 12px;
                            background-color: {style['badge_bg']};
                            color: {style['badge_text']};
                            padding: 3px 10px;
                            border-radius: 12px;
                            font-weight: bold;
                        ">Lines {block['start']} ~ {block['end']}</span>
                    </div>

                    <!-- 정확히 3줄 크기 고정(22px * 3 = 66px) 및 내부 스크롤 창 -->
                    <div style="
                        background-color: #FFFFFF;
                        border: 2px solid rgba(0,0,0,0.2);
                        padding: 4px 10px;
                        border-radius: 6px;
                        font-family: 'Consolas', 'Courier New', monospace;
                        font-size: 13px;
                        height: 66px;
                        overflow-y: auto;
                        box-sizing: content-box;
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
        st.write(f"• **상세 동작 해석:** {block['title']}")
        st.write(f"• **중괄호 {{ }} 스코프 깊이:** Level {block['depth']}")
