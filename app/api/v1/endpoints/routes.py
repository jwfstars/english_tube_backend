from fastapi import APIRouter, Depends

from app.auth import fastapi_users
from app.models.user import User

router = APIRouter()
current_user = fastapi_users.current_user(active=True)


@router.get("/get-async-routes")
async def get_async_routes(user: User = Depends(current_user)):
    if not user.is_superuser:
        return {"success": True, "data": []}

    admin_routes = {
        "path": "/admin",
        "name": "Admin",
        "component": "Layout",
        "meta": {
            "title": "管理后台",
            "icon": "ep/setting",
            "rank": 1,
            "roles": ["admin"],
        },
        "children": [
            {
                "path": "/admin/users",
                "name": "AdminUsers",
                "component": "admin/users/index",
                "meta": {
                    "title": "用户管理",
                    "icon": "ep/user",
                    "roles": ["admin"],
                },
            },
            {
                "path": "/admin/activation",
                "name": "AdminActivation",
                "component": "admin/activation/index",
                "meta": {
                    "title": "激活码",
                    "icon": "ep/key",
                    "roles": ["admin"],
                },
            },
            {
                "path": "/admin/content",
                "name": "AdminContent",
                "component": "Layout",
                "meta": {
                    "title": "内容管理",
                    "icon": "ep/document",
                    "roles": ["admin"],
                },
                "children": [
                    {
                        "path": "/admin/content/videos",
                        "name": "AdminVideos",
                        "component": "admin/content/videos",
                        "meta": {
                            "title": "视频管理",
                            "icon": "ep/video-camera",
                            "roles": ["admin"],
                        },
                    },
                    {
                        "path": "/admin/content/tags",
                        "name": "AdminTags",
                        "component": "admin/content/tags",
                        "meta": {
                            "title": "标签管理",
                            "icon": "ep/price-tag",
                            "roles": ["admin"],
                        },
                    },
                    {
                        "path": "/admin/content/subtitles",
                        "name": "AdminSubtitles",
                        "component": "admin/content/subtitles",
                        "meta": {
                            "title": "字幕管理",
                            "icon": "ep/comment",
                            "roles": ["admin"],
                        },
                    },
                    {
                        "path": "/admin/content/word-cards",
                        "name": "AdminWordCards",
                        "component": "admin/content/word_cards",
                        "meta": {
                            "title": "单词卡片",
                            "icon": "ep/document",
                            "roles": ["admin"],
                        },
                    },
                    {
                        "path": "/admin/content/phrase-cards",
                        "name": "AdminPhraseCards",
                        "component": "admin/content/phrase_cards",
                        "meta": {
                            "title": "短语卡片",
                            "icon": "ep/document",
                            "roles": ["admin"],
                        },
                    },
                ],
            },
        ],
    }

    return {"success": True, "data": [admin_routes]}
