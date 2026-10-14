import os
import time
import random
import urllib.parse
from datetime import datetime
import requests
from google import genai
from google.genai.errors import ServerError, APIError

# 1. 검색 키워드 풀
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
    2. 글의 주제를 상징하는 영문 이미지 생성 프롬프트(간결한 명사 구문, 10단어 이내)를 'IMAGE_PROMPT: 영어프롬프트' 형식으로 둘째 줄에 출력할 것.
       (예: modern fitness gym interior with contracts and scales, warm lighting, professional photography)
    3. 본문은 마크다운 문법(##, ###, -, **강조** 등)을 적절히 사용하여 가독성 있게 작성할 것.
    4. 방문판매법 제31조(해지권), 공정위 소비자분쟁해결기준(위약금 10% 상한선) 등 명확한 법적 근거를 포함할 것.
    5. 글 맨 마지막에 소비자의 시선을 사로잡는 '환불지도' 서비스 홍보 카드 섹션을 HTML 박스 형태로 반드시 포함할 것:
       <div style="background-color: #f8f9fa; border: 2px solid #2563eb; border-radius: 12px; padding: 24px; margin-top: 40px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
         <h3 style="color: #1e40af; margin-top: 0; font-size: 20px;">⚖️ 헬스장·PT·필라테스 위약금 분쟁, 혼자 고민하지 마세요!</h3>
         <p style="font-size: 15px; color: #374151; line-height: 1.6;">
           복잡한 법적 계산식과 업체의 막무가내 환불 거부로 스트레스받고 계신가요?<br>
           소비자의 정당한 권리를 지켜주는 <strong>'환불지도'</strong>가 해결해 드립니다.
         </p>
         <ul style="padding-left: 20px; color: #1f2937; font-size: 14px; line-height: 1.8;">
           <li><strong>법정 환불금 원터치 자동 계산</strong> (방문판매법·공정위 기준 위약금 10% 상한 적용)</li>
           <li><strong>법적 효력 내용증명 1분 자동 생성</strong> (양식 고민 없이 즉시 출력 및 발송 가능)</li>
           <li><strong>환불 거부 피해 사례 공유 및 대처 가이드</strong></li>
         </ul>
         <div style="margin-top: 16px; padding: 12px; background-color: #e0e7ff; border-radius: 8px; text-align: center; font-weight: bold; color: #1e3a8a;">
           🚀 현재 비공개 최종 테스트 중! 곧 구글 플레이스토어에 정식 출시됩니다.
         </div>
       </div>


    출력 형식:
    TITLE: [작성된 글 제목]
    IMAGE_PROMPT: [영문 이미지 프롬프트]
    CONTENT:
    [마크다운 본문]
    """

    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"글 생성 요청 중... (시도 {attempt + 1}/{max_retries})")
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )
            text = response.text
            
            title_part = text.split("IMAGE_PROMPT:")[0]
            rest = text.split("IMAGE_PROMPT:")[1]
            img_part = rest.split("CONTENT:")[0]
            content = rest.split("CONTENT:")[1].strip()

            title = title_part.replace("TITLE:", "").strip().replace('"', '')
            image_prompt = img_part.strip()
            return title, image_prompt, content

        except (ServerError, APIError) as e:
            print(f"구글 서버 일시적 지연 (503 등): {e}")
            if attempt < max_retries - 1:
                wait_sec = 25 * (attempt + 1)
                print(f"{wait_sec}초 대기 후 재시도...")
                time.sleep(wait_sec)
            else:
                raise e

def download_image(image_prompt, file_base_name):
    """무료 Pollinations AI를 통해 이미지 생성 및 다운로드"""
    os.makedirs("assets/images", exist_ok=True)
    img_filename = f"assets/images/{file_base_name}.jpg"
    
    encoded_prompt = urllib.parse.quote(image_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=450&nologo=true"
    
    print(f"이미지 다운로드 시도 중: {image_prompt}")
    try:
        res = requests.get(image_url, timeout=30)
        if res.status_code == 200:
            with open(img_filename, "wb") as f:
                f.write(res.content)
            print(f"[성공] 이미지 다운로드 완료: {img_filename}")
            return img_filename
    except Exception as e:
        print(f"이미지 생성 실패 (건너뜀): {e}")
    return None

def save_markdown_file(title, image_path, content, file_base_name):
    today = datetime.now()
    os.makedirs("_posts", exist_ok=True)
    filename = f"_posts/{file_base_name}.md"
    
    # 썸네일 이미지 마크다운 삽입
    image_markdown = ""
    if image_path:
        # 상대 경로로 안전하게 연결
        image_markdown = f"\n![{title}](/{image_path})\n\n"

    front_matter = f"""---
layout: post
title: "{title}"
date: {today.strftime("%Y-%m-%d %H:%M:%S +0900")}
categories: [환불가이드, 헬스장]
---

"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(front_matter + image_markdown + content)
        
    print(f"[성공] 파일 생성 완료: {filename}")

if __name__ == "__main__":
    target_keyword = random.choice(KEYWORDS)
    print(f"오늘의 주제: {target_keyword}")
    
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    
    title, image_prompt, content = generate_post(target_keyword)
    
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '-')[:30]
    file_base_name = f"{date_str}-{safe_title}"
    
    image_path = download_image(image_prompt, file_base_name)
    save_markdown_file(title, image_path, content, file_base_name)
