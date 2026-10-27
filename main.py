import html
import re
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="다국어 소스코드 구간별 컬러 분석기",
    page_icon="🎨",
    layout="wide",
)

st.title("🎨 다국어 소스코드 요약 및 구간별 컬러 시각화 대시보드")
st.markdown(
    "파이썬, C, C++, Java 코드를 입력하면, **함수, 조건문, 반복문, 출력문, 주석** 등 코드의 역할과 구간별로 **배경색과 태그**를 입혀 보기 쉽게 분석해 드립니다."
)
st.markdown("---")

# 1. 언어 선택 버튼
st.subheader("🌐 1. 분석할 프로그래밍 언어 선택")
selected_lang = st.radio(
    "언어를 선택하세요:",
    ["Python", "C", "C++", "Java"],
    horizontal=True,
    index=0,
)

# 언어별 기본 예시 코드
default_codes = {
    "Python": """# 파이썬 할인 및 반복문 예제
def calculate_discount(price, is_vip):
    # VIP 할인 계산
    if is_vip:
        discount = price * 0.2
        print(f"VIP 할인 적용: {discount}원")
    else:
        discount = price * 0.05
        print(f"일반 할인 적용: {discount}원")
    
    for i in range(3):
        print(f"안내 메시지 반복 {i+1}회")
        
    return price - discount

# 메인 실행
final_price = calculate_discount(12000, True)
print(f"최종 금액: {final_price}")""",
    "C": """// C언어 점수 판별 및 카운트다운 예제
#include <stdio.h>

void check_grade(int score) {
    // 점수 조건 판별
    if (score >= 90) {
        printf("A학점입니다.\\n");
    } else {
        printf("B학점 이하입니다.\\n");
    }
    
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
    // 조건문 처리
    if (count > 5) {
        cout << "데이터가 충분합니다." << endl;
    } else {
        cout << "데이터가 부족합니다." << endl;
    }

    for (int i = 0; i < count; i++) {
        cout << "프로세스 실행 중... #" << i + 1 << endl;
    }
}

int main() {
    process_data(3);
    return 0;
}""",
    "Java": """// Java 연령 확인 예제
public class Main {
    public static void checkAge(int age) {
        // 연령 판별 조건문
        if (age >= 18) {
            System.out.println("성인입니다.");
        } else {
            System.out.println("미성년자입니다.");
        }

        for (int i = 0; i < 3; i++) {
            System.out.println("대기 순번: " + (i + 1));
        }
    }

    public static void main(String[] args) {
        checkAge(20);
    }
}""",
}

# 코드 입력란 (선택한 언어의 예시가 자동으로 로드됨)
st.markdown("---")
st.subheader("📝 2. 소스코드 입력")
code_input = st.text_area(
    f"[{selected_lang}] 분석할 소스코드를 이곳에 작성하거나 붙여넣으세요:",
    value=default_codes[selected_lang],
    height=280,
)


# --- [언어별 라인 역할 분류 분석기] ---
def classify_line(line, lang):
  stripped = line.strip()
  if not stripped:
    return "BLANK", "공백"

  # 1. 주석 (Comment)
  if lang == "Python":
    if stripped.startswith("#"):
      return "COMMENT", "주석"
  else:  # C, C++, Java
    if (
        stripped.startswith("//")
        or stripped.startswith("/*")
        or stripped.startswith("*")
        or stripped.endswith("*/")
    ):
      return "COMMENT", "주석"

  # 2. 출력문 (Output)
  if lang == "Python" and "print(" in stripped:
    return "OUTPUT", "출력문"
  elif lang == "C" and ("printf(" in stripped or "puts(" in stripped):
    return "OUTPUT", "출력문"
  elif lang == "C++" and (
      "cout" in stripped or "printf(" in stripped or "puts(" in stripped
  ):
    return "OUTPUT", "출력문"
  elif lang == "Java" and (
      "System.out.print" in stripped or "System.out.println" in stripped
  ):
    return "OUTPUT", "출력문"

  # 3. 함수/메서드 정의 (Function/Class)
  if lang == "Python":
    if stripped.startswith("def ") or stripped.startswith("class "):
      return "FUNCTION", "함수/클래스"
  elif lang in ["C", "C++"]:
    if re.search(
        r"\b(void|int|float|double|char|bool|auto|string)\s+\w+\s*\(", stripped
    ) or ("main(" in stripped):
      return "FUNCTION", "함수 정의"
  elif lang == "Java":
    if re.search(
        r"\b(public|private|protected|static|void|class|int|double|String|boolean)\s+\w+\s*\(",
        stripped,
    ) or ("class " in stripped):
      return "FUNCTION", "메서드/클래스"

  # 4. 조건문 (Condition)
  if re.search(r"\b(if|else if|elif|else)\b", stripped):
    return "CONDITION", "조건문"

  # 5. 반복문 (Loop)
  if re.search(r"\b(for|while|do)\b", stripped):
    return "LOOP", "반복문"

  # 6. 기타 일반 실행문
  return "GENERAL", "일반 코드"


# 실행 버튼
if st.button("🚀 코드 구간별 요약 및 컬러 시각화 실행", type="primary"):
  if not code_input.strip():
    st.warning("⚠️ 코드가 입력되지 않았습니다. 분석할 코드를 입력해주세요!")
  else:
    st.success(f"✨ [{selected_lang}] 분석 완료!")
    st.markdown("---")

    lines = code_input.split("\n")

    # 통계 집계
    role_counts = {
        "FUNCTION": 0,
        "CONDITION": 0,
        "LOOP": 0,
        "OUTPUT": 0,
        "COMMENT": 0,
        "GENERAL": 0,
        "BLANK": 0,
    }

    classified_lines = []
    for idx, line in enumerate(lines, 1):
      role_key, role_label = classify_line(line, selected_lang)
      role_counts[role_key] += 1
      classified_lines.append((idx, line, role_key, role_label))

    # 1. 요약 리포트
    st.subheader("📌 1. 코드 구조 및 역할 요약 리포트")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("전체 줄 수", f"{len(lines)}줄")
    c2.metric("함수/메서드 구문", f"{role_counts['FUNCTION']}줄")
    c3.metric("조건문 구문", f"{role_counts['CONDITION']}줄")
    c4.metric("반복문 구문", f"{role_counts['LOOP']}줄")
    c5.metric("출력 구문", f"{role_counts['OUTPUT']}줄")

    st.info(
        f"**[{selected_lang} 분석 결과]** 총 **{len(lines)}줄** 중 실제 실행 코드는 **{len(lines) - role_counts['BLANK']}줄**입니다.\n"
        f"• 주석 **{role_counts['COMMENT']}줄**, 조건 분기 **{role_counts['CONDITION']}회**, "
        f"반복 처리 **{role_counts['LOOP']}회**, 화면 출력 구문이 **{role_counts['OUTPUT']}회** 탐지되었습니다."
    )

    st.markdown("---")

    # 2. 구간별 역할 컬러 시각화
    st.subheader("🎨 2. 구간 및 역할별 컬러 시각화 뷰어")
    st.markdown(
        "각 코드 라인의 **역할(함수, 조건문, 반복문, 출력문, 주석 등)**에 따라 **구간 배경색**과 라벨을 다르게 입혔습니다."
    )

    # 구간별 스타일 정의 (배경색, 테두리, 라벨 색상)
    styles = {
        "FUNCTION": {
            "bg": "#FFF0F0",
            "border": "#FF4D4F",
            "tag_bg": "#FF4D4F",
            "tag_color": "#FFFFFF",
            "code_color": "#A8071A",
        },
        "CONDITION": {
            "bg": "#F9F0FF",
            "border": "#9254DE",
            "tag_bg": "#9254DE",
            "tag_color": "#FFFFFF",
            "code_color": "#391085",
        },
        "LOOP": {
            "bg": "#E6F7FF",
            "border": "#1890FF",
            "tag_bg": "#1890FF",
            "tag_color": "#FFFFFF",
            "code_color": "#003A8C",
        },
        "OUTPUT": {
            "bg": "#F6FFED",
            "border": "#52C41A",
            "tag_bg": "#52C41A",
            "tag_color": "#FFFFFF",
            "code_color": "#135200",
        },
        "COMMENT": {
            "bg": "#FFFBE6",
            "border": "#FAAD14",
            "tag_bg": "#FAAD14",
            "tag_color": "#000000",
            "code_color": "#8C6B00",
        },
        "GENERAL": {
            "bg": "#FAFAFA",
            "border": "#D9D9D9",
            "tag_bg": "#8C8C8C",
            "tag_color": "#FFFFFF",
            "code_color": "#262626",
        },
        "BLANK": {
            "bg": "#FFFFFF",
            "border": "#F0F0F0",
            "tag_bg": "#BFBFBF",
            "tag_color": "#FFFFFF",
            "code_color": "#8C8C8C",
        },
    }

    # 범례 안내
    st.markdown(
        """
        <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 15px; font-size: 13px;">
            <span style="background:#FFF0F0; border:1px solid #FF4D4F; padding:4px 8px; border-radius:4px; color:#A8071A; font-weight:bold;">■ 함수/클래스 정의</span>
            <span style="background:#F9F0FF; border:1px solid #9254DE; padding:4px 8px; border-radius:4px; color:#391085; font-weight:bold;">■ 조건문(if/else)</span>
            <span style="background:#E6F7FF; border:1px solid #1890FF; padding:4px 8px; border-radius:4px; color:#003A8C; font-weight:bold;">■ 반복문(for/while)</span>
            <span style="background:#F6FFED; border:1px solid #52C41A; padding:4px 8px; border-radius:4px; color:#135200; font-weight:bold;">■ 출력문(print/printf/cout)</span>
            <span style="background:#FFFBE6; border:1px solid #FAAD14; padding:4px 8px; border-radius:4px; color:#8C6B00; font-weight:bold;">■ 주석(//, #)</span>
            <span style="background:#FAFAFA; border:1px solid #D9D9D9; padding:4px 8px; border-radius:4px; color:#262626;">■ 일반 코드</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # HTML 화면 렌더링 생성
    html_lines = []
    for line_num, line_content, role_key, role_label in classified_lines:
      style = styles[role_key]

      # 문법 인코딩 및 공백 유지
      safe_content = html.escape(line_content).replace(" ", "&nbsp;")
      if not safe_content:
        safe_content = "&nbsp;"

      line_html = f"""
        <div style="
            display: flex;
            align-items: center;
            background-color: {style['bg']};
            border-left: 5px solid {style['border']};
            margin-bottom: 4px;
            padding: 5px 10px;
            border-radius: 4px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
        ">
            <span style="min-width: 35px; color: #8c8c8c; font-size: 12px; user-select: none;">{line_num:2d}</span>
            <span style="
                background-color: {style['tag_bg']};
                color: {style['tag_color']};
                font-size: 11px;
                padding: 1px 6px;
                border-radius: 3px;
                margin-right: 12px;
                min-width: 70px;
                text-align: center;
                font-weight: bold;
                display: inline-block;
            ">{role_label}</span>
            <span style="color: {style['code_color']}; font-weight: {'bold' if role_key in ['FUNCTION', 'CONDITION', 'LOOP', 'OUTPUT'] else 'normal'}; font-family: monospace;">{safe_content}</span>
        </div>
        """
      html_lines.append(line_html)

    # 구간별 컬러 뷰어 출력
    st.markdown(
        f"""
        <div style="background-color: #262626; padding: 12px; border-radius: 8px; border: 1px solid #434343;">
            {''.join(html_lines)}
        </div>
        """,
        unsafe_allow_html=True,
    )
