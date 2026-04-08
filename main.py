import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

def agent_planner(goal):
    prompt = f"전략 기획 전문가로서 이 목표의 실행 계획을 3단계로 작성하세요. 목표: {goal} 한국어로 답하세요."
    return model.generate_content(prompt).text

def agent_executor(plan):
    prompt = f"실행 전문가로서 이 계획의 실제 결과물을 작성하세요. 계획: {plan} 한국어로 답하세요."
    return model.generate_content(prompt).text

def agent_reviewer(result):
    prompt = f"품질 검토 전문가로서 이 결과물을 평가하고 개선점 2~3가지와 10점 만점 점수를 주세요. 결과물: {result} 한국어로 답하세요."
    return model.generate_content(prompt).text

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ AI 에이전트 팀 준비 완료!\n\n"
        "사용법: /run 목표내용\n"
        "예시: /run 오늘 코스피 주목할 섹터 알려줘"
    )

async def run_agents(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    goal = " ".join(ctx.args)
    if not goal:
        await update.message.reply_text("목표를 입력하세요.\n예: /run 유튜브 주제 찾아줘")
        return

    await update.message.reply_text(f"🚀 시작!\n목표: {goal}")
    await update.message.reply_text("🧠 [1/3] 기획 중...")
    plan = agent_planner(goal)

    await update.message.reply_text("⚙️ [2/3] 실행 중...")
    result = agent_executor(plan)

    await update.message.reply_text("✅ [3/3] 검토 중...")
    review = agent_reviewer(result)

    await update.message.reply_text(
        f"🧠 기획\n{plan[:800]}\n\n"
        f"⚙️ 실행\n{result[:800]}\n\n"
        f"✅ 검토\n{review[:800]}"
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run_agents))
    print("봇 실행 중...")
    app.run_polling()
