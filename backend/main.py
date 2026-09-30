import os
import re
import pandas as pd
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from supabase import create_client

from analysis_engine import calculate_engagement_analysis
from report_generator import generate_pdf_report

from youtube_api import (
    get_channel_by_handle,
    get_channel_videos,
    get_video_comments
)

from instagram_api import (
    get_instagram_profile,
    get_instagram_media
)


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

# Explicitly load .env from backend directory first, then fallback
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(ENV_PATH)
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("WARNING: SUPABASE_URL or SUPABASE_KEY is missing from environment!")


# ==========================================
# SUPABASE CONNECTION
# ==========================================

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ==========================================
# FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="EngagementPodGuard API",
    description="Synthetic Engagement & LLM Comment Pod Detector",
    version="1.0.0"
)


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# HELPER: CLEAN USERNAME / URL
# ==========================================

from profile_service import fetch_live_instagram_profile, generate_profile_telemetry

def clean_username_input(raw_input: str) -> str:
    """Extract clean username from string, handle or profile URL."""
    if not raw_input:
        return ""
    text = raw_input.strip()
    # Strip URL query parameters (e.g. ?stkn=...)
    if "?" in text:
        text = text.split("?")[0]
    # Strip URL hash / fragment
    if "#" in text:
        text = text.split("#")[0]
    text = text.rstrip("/")
    if "instagram.com" in text or "youtube.com" in text or "/" in text:
        parts = [p for p in text.split("/") if p and not p.startswith("http") and not "instagram.com" in p and not "youtube.com" in p]
        if parts:
            text = parts[-1]
    text = text.lstrip("@").strip()
    return text


# ==========================================
# ROOT
# ==========================================

@app.get("/")
def root():
    return {
        "message": "EngagementPodGuard API is running",
        "version": "1.0.0",
        "status": "operational"
    }


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "EngagementPodGuard Backend",
        "timestamp": pd.Timestamp.now().isoformat()
    }


# ==========================================
# TEST SUPABASE
# ==========================================

@app.get("/api/test-supabase")
def test_supabase():
    try:
        response = (
            supabase
            .table("influencers")
            .select("*")
            .limit(5)
            .execute()
        )
        return {
            "status": "success",
            "count": len(response.data) if response.data else 0,
            "data": response.data
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Supabase query failed",
            "details": str(e)
        }


# ==========================================
# ENGAGEMENTPODGUARD ANALYSIS
# ==========================================

@app.get("/api/analyze/{username:path}")
def analyze_influencer(username: str):
    try:
        clean_user = clean_username_input(username)
        if not clean_user:
            return {
                "status": "error",
                "message": "Invalid username or profile URL provided."
            }

        # --------------------------------------
        # 1. Get influencer from Supabase
        # --------------------------------------
        influencer_response = (
            supabase
            .table("influencers")
            .select("*")
            .eq("username", clean_user)
            .limit(1)
            .execute()
        )

        if not influencer_response.data:
            # Dynamically fetch live profile and run analysis for any creator!
            influencer = fetch_live_instagram_profile(clean_user)
            posts_df, comments_df, accounts_df = generate_profile_telemetry(influencer)
            
            analysis = calculate_engagement_analysis(
                posts_df=posts_df,
                comments_df=comments_df,
                accounts_df=accounts_df,
                influencer_info=influencer,
                stored_clusters=None,
                stored_analysis=None
            )

            # Try to cache profile into Supabase
            try:
                supabase.table("influencers").upsert({
                    "username": clean_user,
                    "platform": "instagram",
                    "profile_url": influencer.get("profile_url", f"https://instagram.com/{clean_user}"),
                    "followers": influencer.get("followers", 1000),
                    "following": influencer.get("following", 500),
                    "posts_count": influencer.get("posts_count", 15)
                }).execute()
            except Exception:
                pass

            return {
                "status": "success",
                "username": clean_user,
                "influencer": influencer,
                "analysis": analysis,
                "is_live_profile": True
            }

        influencer = influencer_response.data[0]
        influencer_id = influencer["id"]

        # --------------------------------------
        # 2. Get posts for this influencer
        # --------------------------------------
        posts_response = (
            supabase
            .table("posts")
            .select("*")
            .eq("influencer_id", influencer_id)
            .order("published_at", desc=False)
            .execute()
        )
        posts_data = posts_response.data or []

        # --------------------------------------
        # 3. Get comments for posts
        # Note: comments table references post_id, NOT influencer_id
        # --------------------------------------
        comments_data = []
        post_ids = [p["id"] for p in posts_data if "id" in p]

        if post_ids:
            # Query comments in chunks if needed
            chunk_size = 50
            for i in range(0, len(post_ids), chunk_size):
                chunk = post_ids[i:i + chunk_size]
                chunk_response = (
                    supabase
                    .table("comments")
                    .select("*")
                    .in_("post_id", chunk)
                    .execute()
                )
                if chunk_response.data:
                    comments_data.extend(chunk_response.data)

        # --------------------------------------
        # 4. Get accounts
        # --------------------------------------
        accounts_response = (
            supabase
            .table("accounts")
            .select("*")
            .execute()
        )
        accounts_data = accounts_response.data or []

        # --------------------------------------
        # 5. Fetch pre-stored analysis & clusters if present
        # --------------------------------------
        stored_analysis = None
        stored_clusters = []
        try:
            analysis_res = (
                supabase
                .table("analysis_results")
                .select("*")
                .eq("influencer_id", influencer_id)
                .limit(1)
                .execute()
            )
            if analysis_res.data:
                stored_analysis = analysis_res.data[0]
                clusters_res = (
                    supabase
                    .table("clusters")
                    .select("*")
                    .eq("analysis_id", stored_analysis["id"])
                    .execute()
                )
                stored_clusters = clusters_res.data or []
        except Exception:
            pass

        # --------------------------------------
        # 6. Run analysis engine
        # --------------------------------------
        posts_df = pd.DataFrame(posts_data)
        comments_df = pd.DataFrame(comments_data)
        accounts_df = pd.DataFrame(accounts_data)

        analysis = calculate_engagement_analysis(
            posts_df=posts_df,
            comments_df=comments_df,
            accounts_df=accounts_df,
            influencer_info=influencer,
            stored_clusters=stored_clusters,
            stored_analysis=stored_analysis
        )

        # --------------------------------------
        # 7. Return structured result
        # --------------------------------------
        return {
            "status": "success",
            "username": clean_user,
            "influencer": influencer,
            "analysis": analysis
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": "Unable to complete profile analysis due to an internal server error.",
            "details": str(e)
        }


# ==========================================
# DEMO ANALYSIS ALIAS
# ==========================================

@app.get("/api/demo-analysis")
def demo_analysis():
    return analyze_influencer("demo_creator")


# ==========================================
# PDF BRAND TRUST SCORECARD GENERATOR
# ==========================================

@app.get("/api/report/{username:path}")
@app.get("/api/generate-scorecard/{username:path}")
def generate_scorecard_pdf(username: str):
    try:
        clean_user = clean_username_input(username)
        # Fetch analysis data
        analysis_payload = analyze_influencer(clean_user)
        if analysis_payload.get("status") != "success":
            raise HTTPException(status_code=404, detail="Profile data not found for report generation")

        influencer = analysis_payload["influencer"]
        analysis = analysis_payload["analysis"]

        pdf_bytes = generate_pdf_report(clean_user, influencer, analysis)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=EngagementPodGuard_Report_{clean_user}.pdf"
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


# ==========================================
# YOUTUBE CHANNEL
# ==========================================

@app.get("/api/youtube/channel/{handle}")
def youtube_channel(handle: str):
    result = get_channel_by_handle(handle)
    return result


# ==========================================
# YOUTUBE VIDEOS
# ==========================================

@app.get("/api/youtube/videos/{channel_id}")
def youtube_videos(channel_id: str):
    result = get_channel_videos(channel_id)
    return result


# ==========================================
# YOUTUBE VIDEO COMMENTS
# ==========================================

@app.get("/api/youtube/comments/{video_id}")
def youtube_comments(video_id: str):
    result = get_video_comments(video_id)
    return result


# ==========================================
# INSTAGRAM PROFILE
# ==========================================

@app.get("/api/instagram/profile")
def instagram_profile():
    result = get_instagram_profile()
    return result


# ==========================================
# INSTAGRAM MEDIA
# ==========================================

@app.get("/api/instagram/media")
def instagram_media():
    result = get_instagram_media()
    return result