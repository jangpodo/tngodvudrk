import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="소스코드 컬러 분석기", page_icon="🎨", layout="wide"
)

st.title("🎨 소스코드 요약 및 역할별 컬러 시각화 대시보드")
st.markdown(
    "파이썬 코드를 입력하면, 전체 코드를 짧게 요약하고 **함수, 조건문,"
    " 반복문, 출력문** 등 역할별로 색상을 다르게 입혀 보기 편하게"
    " 보여줍니다."
)
st.markdown("---")

# 1. 사용자 코드 입력 장소
code_input = st.text_area(
    "📝 분석할 파이썬 소스코드를 이곳에 붙여넣으세요:",
    height=250,
    placeholder=(
        "def calculate_total(price, tax):\n    total = price + (price * tax)\n "
        "   if total > 10000:\n        print('할인 대상입니다.')\n    else:\n       "
        " print('일반 대상입니다.')\n\nfor i in range(3):\n    "
        "print(f'반복 횟수: {i}')"
    ),
)

if st.button("🚀 코드 요약 및 컬러 분석 실행", type="primary"):
  if code_input.strip() == "":
    st.warning("⚠️ 분석할 코드가 입력되지 않았습니다. 코드를 입력해주세요!")
  else:
    st.success("✨ 분석이 완료되었습니다!")
    st.markdown("---")

    # 2. 코드 짧은 요약 (통계 및 구조 파악)
    total_lines = len(code_input.split("\n"))
    func_count = code_input.count("def ")
    loop_count = code_input.count("for ") + code_input.count("while ")
    if_count = code_input.count("if ")
    print_count = code_input.count("print")

    st.subheader("📌 1. 코드 짧은 요약 리포트")
    st.info(
        f"이 코드는 총 **{total_lines}줄**로 이루어져 있으며, 주요 기능으로"
        f" 함수 정의(`def`) **{func_count}개**, 조건 분기(`if`) **{if_count}개**,"
        f" 반복 처리(`for/while`) **{loop_count}개**, 화면 출력(`print`)"
        " 구문이 포함되어 있습니다. 전체적으로 데이터를 받아 조건에 따라"
        " 처리하고 결과를 출력하는 흐름을 가집니다."
    )

    st.markdown("---")

    # 3. 역할별 색상 구분 시각화 (HTML 마크다운 활용)
    st.subheader("🎨 2. 역할별 컬러 시각화 뷰어")
    st.markdown(
        "코드가 어떤 역할을 하는지 구별하기 쉽도록 주요 키워드와 구문에"
        " 색상을 입혔습니다."
    )

    # 간단한 키워드 기반 컬러 하이라이팅 변환 로직
    formatted_code = (
        code_input.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
        .replace(" ", "&nbsp;")
    )

    # 주요 구문별 색상 입히기 (HTML 스타일)
    keywords_colors = {
        "def ":
            '<span style="color: #d73a49; font-weight: bold;">def </span>',  # 함수 정의 (빨간색 계열)
        "if ": (
            '<span style="color: #6f42c1; font-weight: bold;">if </span>'
        ),  # 조건문 (보라색 계열)
        "else:": (
            '<span style="color: #6f42c1; font-weight: bold;">else:</span>'
        ),
        "for ": (
            '<span style="color: #005cc5; font-weight: bold;">for </span>'
        ),  # 반복문 (파란색 계열)
        "while ": (
            '<span style="color: #005cc5; font-weight: bold;">while </span>'
        ),
        "return ": (
            '<span style="color: #e36209; font-weight: bold;">return </span>'
        ),  # 반환문 (주황색 계열)
        "print": (
            '<span style="color: #22863a; font-weight: bold;">print</span>'
        ),  # 출력문 (초록색 계열)
    }

    for kw, html_tag in keywords_colors.items():
      formatted_code = formatted_code.replace(kw, html_tag)

    # 컬러풀한 박스 안에 결과 출력
    st.markdown(
        f"""
        <div style="background-color: #f6f8fa; padding: 20px; border-radius: 10px; border: 1px solid #d1d5da; font-family: monospace; line-height: 1.6;">
            {formatted_code}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 색상 가이드 설명
    st.markdown("")
    st.markdown(
        "**색상 가이드:** "
        '<span style="color: #d73a49; font-weight: bold;">■ 함수정의(def)</span> | '
        '<span style="color: #6f42c1; font-weight: bold;">■ 조건문(if/else)</span> | '
        '<span style="color: #005cc5; font-weight: bold;">■ 반복문(for/while)</span> | '
        '<span style="color: #e36209; font-weight: bold;">■ 반환(return)</span> | '
        '<span style="color: #22863a; font-weight: bold;">■ 출력(print)</span>',
        unsafe_allow_html=True,
    )
