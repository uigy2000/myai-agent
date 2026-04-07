import os
import asyncio
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

# 환경변수에서 키 불러오기
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Gemini AI 연결
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# ────────────────────────────────────────
# 에이전트 1: 기획자
# 목표를 받아서 실행 계획을 만듦
# ────────────────────────────────────────
def agent_planner(goal: str) -> str:
    prompt = f"""
당신은 전략 기획 전문가입니다.
목표: {goal}

이 목표를 달성하기 위한 구체적 실행 계획을 3단계로 작성하세요.
각 단계는 명확하고 실행 가능해야 합니다.
한국어로 답하세요.
"""
    return model.generate_content(prompt).text

# ────────────────────────────────────────
# 에이전트 2: 실행자
# 기획자의 계획을 받아서 실제 결과물 만듦
# ────────────────────────────────────────
def agent_executor(plan: str) -> str:
    prompt = f"""
당신은 실행 전문가입니다.
실행 계획: {plan}

위 계획을 바탕으로 실제 결과물을 작성하세요.
구체적이고 즉시 활용 가능한 형태로 작성하세요.
한국어로 답하세요.
"""
    return model.generate_content(prompt).text

# ────────────────────────────────────────
# 에이전트 3: 검토자
# 실행자의 결과물을 받아서 품질 검증
# ────────────────────────────────────────
def agent_reviewer(result: str) -> str:
    prompt = f"""
당신은 품질 검토 전문가입니다.
검토할 결과물: {result}

품질을 평가하고 개선점 2~3가지를 제안하세요.
최종 점수(10점 만점)도 제시하세요.
한국어로 답하세요.
"""
    return model.generate_content(prompt).text

# ────────────────────────────────────────
# 텔레그램 명령어: /start
# ────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ AI 에이전트 팀 준비 완료!\n\n"
        "사용법:\n"
        "/run 목표내용\n\n"
        "예시:\n"
        "/run 한국 증시 오늘 주목할 섹터 알려줘\n"
        "/run 유튜브 쇼츠 아이디어 5개 줘"
    )

# ────────────────────────────────────────
# 텔레그램 명령어: /run
# 에이전트 3개를 순서대로 실행
# ────────────────────────────────────────
async def run_agents(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    goal = " ".join(ctx.args)

    if not goal:
        await update.message.reply_text(
            "목표를 입력하세요.\n예: /run 유튜브 주제 찾아줘"
        )
        return

    await update.message.reply_text(f"🚀 에이전트 팀 실행 시작!\n목표: {goal}")
    await update.message.reply_text("🧠 [1/3] 기획 에이전트 작동 중...")
    plan = agent_planner(goal)

    await update.message.reply_text("⚙️ [2/3] 실행 에이전트 작동 중...")
    result = agent_executor(plan)

    await update.message.reply_text("✅ [3/3] 검토 에이전트 작동 중...")
    review = agent_reviewer(result)

    await update.message.reply_text(
        f"━━━━━━━━━━━━━━━━\n"
        f"🧠 기획 에이전트\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"{plan[:1000]}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"⚙️ 실행 에이전트\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"{result[:1000]}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"✅ 검토 에이전트\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"{review[:1000]}"
    )

# ────────────────────────────────────────
# 봇 실행
# ────────────────────────────────────────
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("run", run_agents))
    print("봇 실행 중...")
    app.run_polling()
