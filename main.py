import html
import re
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="다국어 소스코드 블록 하이라이트 & 분석기",
    page_icon="🎨",
    layout="wide",
)

st.title("🎨 소스코드 블록(뭉텅이) 하이라이트 및 상세 분석 대시보드")
st.markdown(
    "코드를 한 줄씩 칠하지 않고 **의미 있는 뭉텅이(블록) 단위**로 구별하여 색상을 입히고, 그 뒤에 각 블록의 작동 방식을 상세히 분석합니다."
)
st.markdown("---")

# 1. 언어 선택 버튼
st.subheader("🌐 🌐 언어 선택")
selected_lang = st.radio(
    "분석할 프로그래밍 언어를 선택하세요:",
    ["Python", "C", "C++", "Java"],
    horizontal=True,
    index=0,
)

# 기본 제공 예시 코드 (최소 4줄 이상)
default_codes = {
    "Python": """# 1. 점수 처리 함수 정의
def process_scores(scores):
    total = 0
    
    # 2. 반복 처리 및 조건 판별
    for score in scores:
        if score >= 80:
            total += score
            print(f"합격점 추가: {score}")
        else:
            print(f"불합격점 제외: {score}")
            
    return total

# 3. 메인 실행 및 결과 출력
data = [75, 85, 90, 60]
result = process_scores(data)
print(f"최종 합산 점수: {result}")""",
    "C": """// 1. 헤더 선언 및 함수 정의
#include <stdio.h>

void analyze_numbers(int arr[], int size) {
    // 2. 배열 조건 검색 및 반복문
    for (int i = 0; i < size; i++) {
        if (arr[i] % 2 == 0) {
            printf("짝수 발견: %d\\n", arr[i]);
        } else {
            printf("홀수 발견: %d\\n", arr[i]);
        }
    }
}

// 3. 메인 실행 함수
int main() {
    int data[] = {1, 2, 3, 4};
    analyze_numbers(data, 4);
    return 0;
}""",
    "C++": """// 1. 헤더 선언 및 함수 정의
#include <iostream>
#include <vector>
using namespace std;

void evaluate_grades(const vector<int>& grades) {
    // 2. 벡터 데이터 반복 및 등급 출력
    for (int score : grades) {
        if (score >= 90) {
            cout << "우수 등급: " << score << endl;
        } else {
            cout << "보통 등급: " << score << endl;
        }
    }
}

// 3. 메인 함수 실행
int main() {
    vector<int> student_scores = {95, 82, 88};
    evaluate_grades(student_scores);
    return 0;
}""",
    "Java": """// 1. 클래스 정의 및 메서드 선언
public class UserCheck {
    public static void checkPermissions(int level) {
        // 2. 권한 조건 분기 및 반복 구문
        if (level >= 5) {
            System.out.println("관리자 권한이 승인되었습니다.");
        } else {
            System.out.println("일반 사용자 권한입니다.");
        }
        
        for (int i = 1; i <= level; i++) {
            System.out.println("권한 슬롯 검사 중: " + i);
        }
    }

    // 3. 메인 진입점 메서드
    public static void main(String[] args) {
        checkPermissions(6);
    }
}""",
}

st.markdown("---")
st.subheader("📝 📝 분석할 소스코드 (최소 4줄 이상)")
code_input = st.text_area(
    f"[{selected_lang}] 코드를 붙여넣거나 수정하세요:",
    value=default_codes[selected_lang],
    height=260,
)


# --- 라인별 분류 함수 ---
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


# --- 뭉텅이(블록) 그룹화 함수 ---
def group_code_into_blocks(code_text, lang):
  lines = code_text.split("\n")
  raw_blocks = []
  current_block = []
  current_cat = None
  start_idx = 1

  for idx, line in enumerate(lines, 1):
    cat = get_line_category(line, lang)

    if current_cat is None:
      current_cat = cat
      current_block.append((idx, line))
      start_idx = idx
    elif cat == current_cat or cat == "BLANK":
      # 공백줄이나 같은 유형은 동일 뭉텅이로 흡수
      current_block.append((idx, line))
    else:
      raw_blocks.append({
          "category": current_cat,
          "start": start_idx,
          "end": idx - 1,
          "lines": current_block,
      })
      current_cat = cat
      current_block = [(idx, line)]
      start_idx = idx

  if current_block:
    raw_blocks.append({
        "category": current_cat,
        "start": start_idx,
        "end": len(lines),
        "lines": current_block,
    })

  return raw_blocks


# --- 블록 스타일 및 제목 정의 ---
BLOCK_STYLES = {
    "COMMENT": {
        "title": "💡 주석 및 설명 뭉텅이",
        "bg": "#FFFBE6",
        "border": "#FAAD14",
        "color": "#8C6B00",
        "desc": "코드의 목적이나 설명을 기록한 주석 구간입니다.",
    },
    "HEADER": {
        "title": "🔧 함수 및 구조 선언 뭉텅이",
        "bg": "#FFF0F0",
        "border": "#FF4D4F",
        "color": "#A8071A",
        "desc": "새로운 함수, 메서드, 클래스 등을 정의하여 진입점을 형성하는 구간입니다.",
    },
    "LOGIC": {
        "title": "⚡ 조건 분기 및 반복 로직 뭉텅이",
        "bg": "#F9F0FF",
        "border": "#9254DE",
        "color": "#391085",
        "desc": (
            "조건(if/else) 판단이나 반복(for/while) 처리가 진행되는 제어 흐름"
            " 핵심 구간입니다."
        ),
    },
    "OUTPUT": {
        "title": "🖥️ 데이터 출력 및 반환 뭉텅이",
        "bg": "#F6FFED",
        "border": "#52C41A",
        "color": "#135200",
        "desc": "결과 데이터를 화면에 출력하거나 상위 호출부로 전달하는 구간입니다.",
    },
    "GENERAL": {
        "title": "📦 일반 연산 및 실행 뭉텅이",
        "bg": "#F0F5FF",
        "border": "#2F54EB",
        "color": "#10239E",
        "desc": "변수 할당, 연산 수행, 함수 호출 등이 이루어지는 일반 실행 코드 구간입니다.",
    },
}


# 분석 실행
if st.button("🚀 코드 뭉텅이 하이라이트 & 블록 분석 실행", type="primary"):
  lines = code_input.split("\n")

  # 4줄 미만 검증
  if len(lines) < 4:
    st.warning(
        f"⚠️ 코드가 너무 짧습니다! 현재 {len(lines)}줄입니다. 최소 4줄 이상의 코드를 입력해주세요."
    )
  else:
    st.success(
        f"✨ [{selected_lang}] 총 {len(lines)}줄의 코드를 뭉텅이(블록) 단위로 하이라이팅 및 분석을 완료했습니다!"
    )
    st.markdown("---")

    blocks = group_code_into_blocks(code_input, selected_lang)

    # 1. 뭉텅이(블록) 하이라이트 시각화
    st.subheader("🎨 1. 코드 뭉텅이(블록) 하이라이트 뷰어")
    st.caption(
        "※ 한 줄씩 칠하지 않고, 역할이 같은 연속된 코드를 **하나의 통 뭉텅이(블록)**로 묶어서 하이라이팅했습니다."
    )

    for block_num, block in enumerate(blocks, 1):
      style = BLOCK_STYLES.get(block["category"], BLOCK_STYLES["GENERAL"])

      # 블록 내부 코드 HTML 변환
      block_code_html = []
      for l_num, line_str in block["lines"]:
        safe_line = html.escape(line_str).replace(" ", "&nbsp;")
        if not safe_line:
          safe_line = "&nbsp;"
        block_code_html.append(
            f'<div><span style="color: #bfbfbf; font-size: 11px;'
            f' margin-right: 15px; user-select:'
            f' none;">{l_num:2d}</span>{safe_line}</div>'
        )

      code_content = "".join(block_code_html)

      # 블록 뭉텅이 카드 렌더링
      st.markdown(
          f"""
            <div style="
                background-color: {style['bg']};
                border: 2px solid {style['border']};
                border-radius: 8px;
                margin-bottom: 18px;
                padding: 14px;
            ">
                <div style="
                    font-weight: bold;
                    color: {style['color']};
                    font-size: 15px;
                    margin-bottom: 8px;
                    display: flex;
                    justify-content: space-between;
                ">
                    <span>{style['title']} (블록 #{block_num})</span>
                    <span style="font-size: 13px; background-color: {style['border']}; color: white; padding: 2px 8px; border-radius: 4px;">Lines {block['start']} ~ {block['end']}</span>
                </div>
                <div style="
                    background-color: #ffffff;
                    border: 1px solid #e8e8e8;
                    padding: 12px;
                    border-radius: 6px;
                    font-family: 'Consolas', 'Courier New', monospace;
                    font-size: 13px;
                    line-height: 1.6;
                    color: #262626;
                ">
                    {code_content}
                </div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    st.markdown("---")

    # 2. 블록 단위 상세 코드 분석
    st.subheader("🔍 2. 코드 뭉텅이(블록)별 상세 해석 및 분석")
    st.markdown(
        "각 코드 뭉텅이가 **어떤 역할을 수행하는지 상세 분석한 결과**입니다."
    )

    for block_num, block in enumerate(blocks, 1):
      style = BLOCK_STYLES.get(block["category"], BLOCK_STYLES["GENERAL"])

      # 블록 코드 텍스트
      raw_block_text = "\n".join([line for _, line in block["lines"]])

      with st.expander(
          f"📌 [블록 #{block_num}] Lines {block['start']}~{block['end']} :"
          f" {style['title']}",
          expanded=True,
      ):
        c1, c2 = st.columns([1, 2])

        with c1:
          st.markdown("**코드 뭉텅이 원문:**")
          st.code(raw_block_text, language=selected_lang.lower())

        with c2:
          st.markdown("**🔍 상세 동작 해석:**")
          st.info(f"**구간 역할:** {style['desc']}")

          # 세부 분석 메시지 추출
          analysis_points = []
          for _, l in block["lines"]:
            stripped = l.strip()
            if "if" in stripped or "else" in stripped or "elif" in stripped:
              analysis_points.append(
                  "• 조건 판단문: 특정 조건의 만족 여부에 따라 실행 경로를 다르게 바꿉니다."
              )
            elif "for" in stripped or "while" in stripped:
              analysis_points.append(
                  "• 반복 제어문: 지정된 횟수나 조건 동안 내부 로직을 반복 수행합니다."
              )
            elif "def " in stripped or "main(" in stripped:
              analysis_points.append(
                  "• 진입점/함수 선언: 해당 코드 뭉텅이의 기능을 캡슐화하는 함수 시작 부분입니다."
              )
            elif (
                ("print" in stripped)
                or ("cout" in stripped)
                or ("System.out" in stripped)
            ):
              analysis_points.append(
                  "• 화면 출력: 처리된 데이터 결과를 콘솔 모니터에 출력합니다."
              )

          if not analysis_points:
            analysis_points.append(
                "• 일반 실행구문: 변수 선언, 값 저장 또는 외부 함수 호출을 수행하는 기본 실행 단계입니다."
            )

          # 중복 제거 후 출력
          for point in list(dict.fromkeys(analysis_points)):
            st.markdown(point)
