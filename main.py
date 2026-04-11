import os
import time
import telebot
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
GROQ_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

client = Groq(api_key=GROQ_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def ask_groq(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def agent_planner(goal):
    return ask_groq(f"전략 기획 전문가로서 이 목표의 실행 계획을 3단계로 작성하세요. 목표: {goal} 한국어로 답하세요.")

def agent_executor(plan):
    return ask_groq(f"실행 전문가로서 이 계획의 실제 결과물을 작성하세요. 계획: {plan} 한국어로 답하세요.")

def agent_reviewer(result):
    return ask_groq(f"품질 검토 전문가로서 이 결과물을 평가하고 개선점 2~3가지와 10점 만점 점수를 주세요. 결과물: {result} 한국어로 답하세요.")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,
        "✅ AI 에이전트 팀 준비 완료!\n\n"
        "사용법: /run 목표내용\n"
        "예시: /run 오늘 코스피 주목할 섹터 알려줘"
    )

@bot.message_handler(commands=['run'])
def run_agents(message):
    goal = message.text.replace('/run', '').strip()
    if not goal:
        bot.reply_to(message, "목표를 입력하세요.\n예: /run 유튜브 주제 찾아줘")
        return

    bot.reply_to(message, f"🚀 시작!\n목표: {goal}")
    bot.send_message(message.chat.id, "🧠 [1/3] 기획 중...")
    plan = agent_planner(goal)

    bot.send_message(message.chat.id, "⚙️ [2/3] 실행 중...")
    result = agent_executor(plan)

    bot.send_message(message.chat.id, "✅ [3/3] 검토 중...")
    review = agent_reviewer(result)

    bot.send_message(message.chat.id,
        f"🧠 기획\n{plan[:800]}\n\n"
        f"⚙️ 실행\n{result[:800]}\n\n"
        f"✅ 검토\n{review[:800]}"
    )

print("봇 실행 중...")
while True:
    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"에러: {e}")
        print("5초 후 재연결...")
        time.sleep(5)
