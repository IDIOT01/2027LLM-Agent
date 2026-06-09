"""
SQLite 岗位数据库
持久化存储所有抓取过的岗位，自动去重，记录首次发现时间和状态变化
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from core import DATA_DIR

DB_PATH = DATA_DIR / "jobs.db"


def _conn():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT NOT NULL,
        title TEXT NOT NULL,
        department TEXT DEFAULT '',
        location TEXT DEFAULT '',
        url TEXT DEFAULT '',
        source TEXT DEFAULT '',
        first_seen TEXT NOT NULL,
        last_seen TEXT NOT NULL,
        status TEXT DEFAULT '待关注',
        match_level TEXT DEFAULT '',
        llm_reason TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        UNIQUE(company, title)
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS scrape_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scraped_at TEXT NOT NULL,
        total_jobs INTEGER,
        new_jobs INTEGER,
        source TEXT DEFAULT 'lite'
    )""")
    conn.commit()
    return conn


def upsert_jobs(jobs: list) -> dict:
    """插入或更新岗位，返回新增和总数"""
    conn = _conn()
    now = datetime.now().isoformat()
    new_count = 0
    for j in jobs:
        company = j.get("company", "")
        title = j.get("title", "")
        if not company or not title:
            continue
        try:
            conn.execute(
                "INSERT INTO jobs (company, title, department, location, url, source, first_seen, last_seen) VALUES (?,?,?,?,?,?,?,?)",
                (company, title, j.get("department", ""), j.get("location", ""),
                 j.get("url", ""), j.get("source", ""), now, now)
            )
            new_count += 1
        except sqlite3.IntegrityError:
            conn.execute(
                "UPDATE jobs SET last_seen=?, url=CASE WHEN url='' THEN ? ELSE url END, location=CASE WHEN location='' THEN ? ELSE location END WHERE company=? AND title=?",
                (now, j.get("url", ""), j.get("location", ""), company, title)
            )
    conn.execute("INSERT INTO scrape_log (scraped_at, total_jobs, new_jobs) VALUES (?,?,?)",
                 (now, len(jobs), new_count))
    conn.commit()
    conn.close()
    return {"total": len(jobs), "new": new_count}


def get_all_jobs(status: str = "", company: str = "") -> list:
    conn = _conn()
    query = "SELECT * FROM jobs WHERE 1=1"
    params = []
    if status:
        query += " AND status=?"
        params.append(status)
    if company:
        query += " AND company=?"
        params.append(company)
    query += " ORDER BY first_seen DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_new_jobs(since: str = "") -> list:
    """获取自某个时间点以来新增的岗位"""
    conn = _conn()
    if not since:
        # Default: last 24 hours
        from datetime import timedelta
        since = (datetime.now() - timedelta(days=1)).isoformat()
    rows = conn.execute("SELECT * FROM jobs WHERE first_seen > ? ORDER BY first_seen DESC", (since,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_job_status(job_id: int, status: str) -> bool:
    conn = _conn()
    conn.execute("UPDATE jobs SET status=? WHERE id=?", (status, job_id))
    conn.commit()
    conn.close()
    return True


def get_stats() -> dict:
    conn = _conn()
    total = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    by_status = {}
    for row in conn.execute("SELECT status, COUNT(*) as cnt FROM jobs GROUP BY status"):
        by_status[row["status"]] = row["cnt"]
    by_company = {}
    for row in conn.execute("SELECT company, COUNT(*) as cnt FROM jobs GROUP BY company ORDER BY cnt DESC"):
        by_company[row["company"]] = row["cnt"]
    # Scrape history
    history = []
    for row in conn.execute("SELECT scraped_at, total_jobs, new_jobs FROM scrape_log ORDER BY scraped_at DESC LIMIT 30"):
        history.append(dict(row))
    conn.close()
    return {"total": total, "by_status": by_status, "by_company": by_company, "history": history}


def get_companies_list() -> list:
    conn = _conn()
    rows = conn.execute("SELECT DISTINCT company FROM jobs ORDER BY company").fetchall()
    conn.close()
    return [r["company"] for r in rows]
