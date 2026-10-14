import os
import time
import random
from datetime import datetime
from google import genai
from google.genai.errors import ServerError, APIError

KEYWORDS = [
    "헬스장 중도해지 위약금 10% 법정 계산법",
    "필라테스 이벤트가 환불 절대 불가 대처법",
    "PT 횟수 차감 정상가 요구 시 법적 해결 방법",
    "체육시설 내용증명 작성 요령과 서식 양식",
    "헬스장 양도 거부 및 양도 수수료 과다 청구 해결책",
    "헬스장 기습 폐업 먹튀 시 카드 할부항변권 신청법",
]

def generate_post(keyword):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    prompt = f"""
    당신은 체육시설 소비자 분쟁 전문 법률 정보 블로거입니다.
    오늘의 주제: '{keyword}'

    네이버/구글 검색 상위 노출(SEO)에 최적화된 마크다운(Markdown) 블로그 글을 작성해주세요.
    반드시 다음 조건을 만족해야 합니다:
    1. 제목은 매력적인 검색용 제목으로 정하고 첫 줄에 'TITLE: 제목' 형식으로 출력할 것.
    2. 본문은 마크다운 문법(##, ###, -, **강조** 등)을 적절히 사용하여 가독성 있게 작성할 것.
    3. 방문판매법 제31조(해지권), 공정위 소비자분쟁해결기준(위약금 10% 상한선) 등 명확한 법적 근거를 포함할 것.
    4. 글 마지막에 다음 안내 문구를 마크다운 인용구 형태로 깔끔하게 넣을 것:
       > 💡 체육시설 법정 환불금 자동 계산 및 무료 내용증명 생성 서비스인 **'환불지도'** 앱이 곧 정식 출시될 예정입니다.

    출력 형식:
    TITLE: [작성된 글 제목]
    CONTENT:
    [마크다운 본문]
    """

    # gemini-3.8-flash 단일 모델로 최대 3회 재시도
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"글 생성 요청 중... (시도 {attempt + 1}/{max_retries})")
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )
            text = response.text
            title = text.split("CONTENT:")[0].replace("TITLE:", "").strip().replace('"', '')
            content = text.split("CONTENT:")[1].strip()
            return title, content

        except (ServerError, APIError) as e:
            print(f"구글 서버 일시적 지연 (503): {e}")
            if attempt < max_retries - 1:
                wait_sec = 25 * (attempt + 1)
                print(f"{wait_sec}초 동안 대기 후 다시 호출합니다...")
                time.sleep(wait_sec)
            else:
                raise e

def save_markdown_file(title, content):
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '-')[:30]
    filename = f"_posts/{date_str}-{safe_title}.md"
    
    os.makedirs("_posts", exist_ok=True)
    
    front_matter = f"""---
layout: post
title: "{title}"
date: {today.strftime("%Y-%m-%d %H:%M:%S +0900")}
categories: [환불가이드, 헬스장]
---

"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(front_matter + content)
        
    print(f"[성공] 파일 생성 완료: {filename}")

if __name__ == "__main__":
    target_keyword = random.choice(KEYWORDS)
    print(f"오늘의 주제: {target_keyword}")
    title, content = generate_post(target_keyword)
    save_markdown_file(title, content)
