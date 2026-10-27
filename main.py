import html
import re
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="소스코드 형광 블록 & 3줄 스크롤 분석기",
    page_icon="🎨",
    layout="wide",
)

st.title("🎨 형광색 블록 구분 & 3줄 고정 스크롤 대시보드")
st.markdown("---")

# 1. 언어 선택 버튼
selected_lang = st.radio(
    "🌐 프로그래밍 언어 선택:",
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

code_input = st.text_area(
    f"[{selected_lang}] 분석할 소스코드 (최소 4줄 이상):",
    value=default_codes[selected_lang],
    height=240,
)


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


def generate_detailed_title(lines, category, lang):
  full_text = " ".join(lines)
  if category == "COMMENT":
    return "💡 주석 설명 구간"
  elif category == "HEADER":
    return (
        "🚀 메인(Main) 진입점 정의"
        if "main" in full_text
        else "🔧 핵심 기능 함수 선언"
    )
  elif category == "LOGIC":
    has_loop = any(k in full_text for k in ["for", "while"])
    has_cond = any(k in full_text for k in ["if", "else", "switch", "elif"])
    if has_loop and has_cond:
      return "🔄⚡ 반복 및 조건 판별 제어 로직"
    elif has_loop:
      return "🔄 데이터 반복 순회 로직"
    return "⚡ 조건 판단 분기 로직"
  elif category == "OUTPUT":
    return "🖥️ 결과 데이터 출력 및 메시지 출력"
  return "📝 데이터 연산 및 일반 실행 명령"


def group_code(code_text, lang):
  lines = code_text.split("\n")
  blocks, current_block_lines, current_cat, start_idx = [], [], None, 1
  current_depth = 0

  line_info = []
  for idx, line in enumerate(lines, 1):
    cat = get_line_category(line, lang)
    open_b, close_b = line.count("{"), line.count("}")
    line_depth = current_depth
    current_depth = max(0, current_depth + open_b - close_b)
    line_info.append({
        "line_num": idx,
        "text": line,
        "category": cat,
        "depth": line_depth,
    })

  for item in line_info:
    cat = item["category"]
    if current_cat is None:
      current_cat, start_idx = cat, item["line_num"]
      current_block_lines.append(item)
    elif cat == current_cat or cat == "BLANK":
      current_block_lines.append(item)
    else:
      min_depth = min(x["depth"] for x in current_block_lines)
      raw_lines = [x["text"] for x in current_block_lines]
      blocks.append({
          "category": current_cat,
          "title": generate_detailed_title(raw_lines, current_cat, lang),
          "start": start_idx,
          "end": item["line_num"] - 1,
          "depth": min_depth,
          "lines": current_block_lines,
      })
      current_cat, start_idx = cat, item["line_num"]
      current_block_lines = [item]

  if current_block_lines:
    min_depth = min(x["depth"] for x in current_block_lines)
    raw_lines = [x["text"] for x in current_block_lines]
    blocks.append({
        "category": current_cat,
        "title": generate_detailed_title(raw_lines, current_cat, lang),
        "start": start_idx,
        "end": len(lines),
        "depth": min_depth,
        "lines": current_block_lines,
    })
  return blocks


# 쨍한 형광색(Neon) 컬러 매핑
NEON_STYLES = {
    "COMMENT": {
        "bg": "#FFFF00",
        "text": "#000000",
        "border": "#CCCC00",
    },  # 형광 노랑
    "HEADER": {
        "bg": "#FF007F",
        "text": "#FFFFFF",
        "border": "#CC0066",
    },  # 형광 핫핑크
    "LOGIC": {
        "bg": "#00FFFF",
        "text": "#000000",
        "border": "#00CCCC",
    },  # 형광 시안(블루)
    "OUTPUT": {
        "bg": "#00FF00",
        "text": "#000000",
        "border": "#00CC00",
    },  # 형광 초록
    "GENERAL": {
        "bg": "#FF6600",
        "text": "#FFFFFF",
        "border": "#CC5200",
    },  # 형광 주황
}

if st.button("🚀 형광 블록 분석 실행", type="primary"):
  lines = code_input.split("\n")
  if len(lines) < 4:
    st.warning("⚠️ 코드가 너무 짧습니다. 4줄 이상 입력해주세요!")
  else:
    blocks = group_code(code_input, selected_lang)
    st.markdown("---")
    st.subheader("🎨 형광 블록 & 3줄 제한 스크롤 뷰")

    for idx, b in enumerate(blocks, 1):
      style = NEON_STYLES.get(b["category"], NEON_STYLES["GENERAL"])
      depth = b["depth"]

      # 각 코드 라인을 20px 고정 높이로 처리
      line_htmls = []
      for l in b["lines"]:
        safe_line = html.escape(l["text"]).replace(" ", "&nbsp;") or "&nbsp;"
        line_htmls.append(
            f'<div style="height: 20px; line-height: 20px;'
            ' white-space: nowrap;"><span style="color: #888; font-size: 11px;'
            ' margin-right: 10px; display: inline-block;'
            f' width: 20px;">{l["line_num"]:2d}</span><b>{safe_line}</b></div>'
        )
      code_html = "".join(line_htmls)

      # { } depth 연결선
      scope_line = ""
      if depth > 0:
        scope_line = f"""<div style="position: absolute; left: 0; top: 0; bottom: 0; width: 5px; background-color: #000000;"></div>"""

      # 3줄 시각 높이 제한: 20px * 3줄 + 여백 = 68px
      st.markdown(
          f"""
            <div style="position: relative; padding-left: {depth * 15}px; margin-bottom: 18px;">
                {scope_line}
                <div style="
                    background-color: {style['bg']};
                    border: 3px solid {style['border']};
                    border-radius: 8px;
                    padding: 10px 14px;
                ">
                    <div style="
                        font-weight: 900;
                        color: {style['text']};
                        font-size: 14px;
                        margin-bottom: 6px;
                        display: flex;
                        justify-content: space-between;
                    ">
                        <span>📌 [블록 #{idx}] {b['title']} (Depth: {depth})</span>
                        <span style="background: #000; color: #fff; padding: 2px 8px; border-radius: 10px; font-size: 11px;">Lines {b['start']}~{b['end']}</span>
                    </div>

                    <!-- 정확히 3줄 시각 제한 및 스크롤 영역 -->
                    <div style="
                        background-color: #FFFFFF;
                        border: 2px solid #000000;
                        padding: 4px 8px;
                        border-radius: 4px;
                        font-family: 'Consolas', monospace;
                        font-size: 13px;
                        height: 68px;
                        overflow-y: scroll;
                    ">
                        {code_html}
                    </div>
                </div>
            </div>
            """,
          unsafe_allow_html=True,
      )
