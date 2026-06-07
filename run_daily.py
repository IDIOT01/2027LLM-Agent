#!/usr/bin/env python3
"""
每日一键执行：抓取 + Gmail监控 + 更新 + 播报 + 推送
用法:
  python3 run_daily.py                # 完整执行（Playwright + Gmail + 推送）
  python3 run_daily.py --lite         # 轻量模式（不需要Playwright）
  python3 run_daily.py --no-gmail     # 跳过Gmail检查
  python3 run_daily.py --no-push      # 跳过微信/QQ推送
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

USE_LITE = "--lite" in sys.argv
SKIP_GMAIL = "--no-gmail" in sys.argv
SKIP_PUSH = "--no-push" in sys.argv


async def main():
    print("=" * 60)
    print(f"  秋招Agent - 每日更新")
    print(f"  执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  模式: {'轻量' if USE_LITE else '完整'} | Gmail: {'跳过' if SKIP_GMAIL else '启用'}")
    print("=" * 60)

    total_steps = 2 if SKIP_GMAIL else 3
    step = 1

    # Step 1: 抓取招聘信息
    print(f"\n[Step {step}/{total_steps}] 开始抓取各公司招聘信息...")
    print("-" * 40)

    if USE_LITE:
        from scraper_lite import run as lite_scrape
        results = lite_scrape()
        job_count = len(results)
    else:
        try:
            from scraper import RecruitmentScraper
            scraper = RecruitmentScraper()
            results = await scraper.run()
            job_count = len(results)
        except Exception as e:
            print(f"[WARN] Playwright抓取失败({e})，回退到轻量模式...")
            from scraper_lite import run as lite_scrape
            results = lite_scrape()
            job_count = len(results)

    step += 1

    # Step 2: Gmail监控（可选）
    gmail_report = ""
    if not SKIP_GMAIL:
        print(f"\n[Step {step}/{total_steps}] 检查Gmail招聘邮件...")
        print("-" * 40)
        try:
            from gmail_monitor import run as check_gmail, generate_email_report
            emails = check_gmail(days=1)
            if emails:
                gmail_report = generate_email_report(emails)
        except Exception as e:
            print(f"[WARN] Gmail监控失败: {e}")
            print("  如未配置，请参考 gmail_monitor.py 顶部说明完成授权")
        step += 1

    # Step 3: 生成播报 + 更新Excel
    print(f"\n[Step {step}/{total_steps}] 生成每日播报 + 更新Excel...")
    print("-" * 40)
    from update_report import run as generate_report
    report = generate_report()

    # Append Gmail report to daily report if available
    if gmail_report:
        today = datetime.now().strftime("%Y-%m-%d")
        report_path = Path(__file__).parent / "每日播报" / f"{today}.md"
        if report_path.exists():
            with open(report_path, "a", encoding="utf-8") as f:
                f.write(gmail_report)
            print("[INFO] Gmail监控结果已追加到每日播报")

    # Step 4: 推送通知
    if not SKIP_PUSH:
        print(f"\n[Push] 推送每日播报到微信/QQ...")
        print("-" * 40)
        try:
            from notifier import send_daily_report
            send_daily_report()
        except Exception as e:
            print(f"[WARN] 推送失败: {e}")
            print("  请编辑 config.json 配置推送渠道")

    print("\n" + "=" * 60)
    print(f"  执行完毕！")
    print(f"  - 岗位信息: {job_count} 条")
    print(f"  - Gmail: {'已检查' if not SKIP_GMAIL and not gmail_report == '' else '跳过/无新邮件'}")
    print(f"  - 推送: {'已发送' if not SKIP_PUSH else '跳过'}")
    print(f"  - 播报路径: 每日播报/{datetime.now().strftime('%Y-%m-%d')}.md")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
