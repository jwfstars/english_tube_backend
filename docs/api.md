# API 接口文档

## 接口概览

| # | 接口 | 方法 | 说明 |
|---|------|------|------|
| 1 | `/videos` | GET | 获取视频列表 |
| 2 | `/videos?id=eq.{id}` | GET | 获取单个视频详情 |
| 3 | `/subtitles` | GET | 获取视频字幕（中英文对照） |
| 4 | `/phrase_cards` | GET | 获取视频短语卡片 |
| 5 | `/word_cards` | GET | 获取视频单词卡片 |
| 6 | `/video_tags` | GET | 获取视频标签和作者信息 |

## 基础信息

- **Base URL**: `https://boyyfwfjqczykgufyasp.supabase.co/rest/v1`
- **认证方式**: API Key + Bearer Token
- **数据格式**: JSON

## 通用请求头

所有请求需要包含以下请求头：

```
accept-profile: public
apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJveXlmd2ZqcWN6eWtndWZ5YXNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg1NTA0MjUsImV4cCI6MjA3NDEyNjQyNX0.q5RlpJyVSK7dqbP1BpTc4l4ruL8-e_VUs4wzcKOKoAA
authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJveXlmd2ZqcWN6eWtndWZ5YXNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg1NTA0MjUsImV4cCI6MjA3NDEyNjQyNX0.q5RlpJyVSK7dqbP1BpTc4l4ruL8-e_VUs4wzcKOKoAA
```

---

## 1. 获取视频列表

获取所有视频列表，支持排序和筛选。

### 基本信息

- **URL**: `/videos`
- **Method**: `GET`
- **描述**: 获取视频列表，按显示顺序降序排列

### 请求参数

#### Query Parameters

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| select | string | 否 | 选择返回的字段，`*` 表示所有字段 | `*` |
| order | string | 否 | 排序规则 | `display_order.desc` |

### 请求示例

```bash
curl 'https://boyyfwfjqczykgufyasp.supabase.co/rest/v1/videos?select=*&order=display_order.desc' \
  -H 'accept-profile: public' \
  -H 'apikey: {SUPABASE_API_KEY}' \
  -H 'authorization: Bearer {SUPABASE_API_KEY}'
```

### 响应

#### 成功响应 (200 OK)

返回视频对象数组。

#### 响应字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | string (UUID) | 视频唯一标识 |
| title | string | 视频标题 |
| description | string | 视频描述 |
| cloudflare_stream_id | string | Cloudflare Stream 视频 ID |
| thumbnail_url | string | 缩略图 URL |
| duration | number | 视频时长（秒） |
| difficulty | string | 难度级别：`beginner`、`intermediate`、`advanced` |
| category_tags | array | 分类标签数组 |
| created_by | string/null | 创建者 |
| created_at | string (ISO 8601) | 创建时间 |
| updated_at | string (ISO 8601) | 更新时间 |
| is_published | boolean | 是否已发布 |
| status | string | 状态：`published` 等 |
| display_order | number | 显示顺序（用于排序） |
| tencent_cloud_url | string | 腾讯云视频 URL |

#### 响应示例

```json
[
  {
    "id": "661118fe-91fb-4c19-a140-7a62279bce57",
    "title": "习语：rise and shine",
    "description": "如何叫人起床和形容"起床气"？用两个习语把"元气满满"和"有起床气"说得特别到位。\n除了意思，你还能学到：哪些场合适合用、怎么搭配称呼和语气，说不定下次就能顺手用起来来。",
    "cloudflare_stream_id": "55f62627b830f550a3793081be54ddb7",
    "thumbnail_url": "https://boyyfwfjqczykgufyasp.supabase.co/storage/v1/object/public/video-thumbnails/thumbnails/cover-1765840336913.jpg",
    "duration": 51,
    "difficulty": "beginner",
    "category_tags": [],
    "created_by": null,
    "created_at": "2025-12-15T23:13:10.771622+00:00",
    "updated_at": "2025-12-15T23:17:11.997708+00:00",
    "is_published": false,
    "status": "published",
    "display_order": 109,
    "tencent_cloud_url": "https://video-cn.dongchenyu.cn/riseandshine.mp4"
  }
]
```

---

## 2. 获取视频详情

根据视频 ID 获取单个视频的详细信息。

### 基本信息

- **URL**: `/videos`
- **Method**: `GET`
- **描述**: 获取指定 ID 的视频详情

### 请求参数

#### Query Parameters

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| select | string | 否 | 选择返回的字段，`*` 表示所有字段 | `*` |
| id | string | 是 | 视频 ID（使用 `eq.` 前缀） | `eq.661118fe-91fb-4c19-a140-7a62279bce57` |
| status | string | 否 | 状态过滤（使用 `eq.` 前缀） | `eq.published` |

#### Headers

返回单个对象而非数组时需添加：

```
accept: application/vnd.pgrst.object+json
```

### 请求示例

```bash
curl 'https://boyyfwfjqczykgufyasp.supabase.co/rest/v1/videos?select=*&id=eq.661118fe-91fb-4c19-a140-7a62279bce57&status=eq.published' \
  -H 'accept: application/vnd.pgrst.object+json' \
  -H 'accept-profile: public' \
  -H 'apikey: {SUPABASE_API_KEY}'
```

### 响应

#### 成功响应 (200 OK)

返回单个视频对象（非数组），字段结构与视频列表接口相同。

#### 响应示例

```json
{
  "id": "661118fe-91fb-4c19-a140-7a62279bce57",
  "title": "习语：rise and shine",
  "description": "如何叫人起床和形容"起床气"？...",
  "cloudflare_stream_id": "55f62627b830f550a3793081be54ddb7",
  "thumbnail_url": "https://boyyfwfjqczykgufyasp.supabase.co/storage/v1/object/public/video-thumbnails/thumbnails/cover-1765840336913.jpg",
  "duration": 51,
  "difficulty": "beginner",
  "status": "published",
  "display_order": 109
}
```

---

## 3. 获取视频字幕

获取指定视频的字幕列表，包含中英文对照。

### 基本信息

- **URL**: `/subtitles`
- **Method**: `GET`
- **描述**: 获取视频的双语字幕，按时间轴升序排列

### 请求参数

#### Query Parameters

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| select | string | 否 | 选择返回的字段，`*` 表示所有字段 | `*` |
| video_id | string | 是 | 视频 ID（使用 `eq.` 前缀） | `eq.661118fe-91fb-4c19-a140-7a62279bce57` |
| order | string | 否 | 排序规则 | `start_time.asc` |

### 请求示例

```bash
curl 'https://boyyfwfjqczykgufyasp.supabase.co/rest/v1/subtitles?select=*&video_id=eq.661118fe-91fb-4c19-a140-7a62279bce57&order=start_time.asc' \
  -H 'accept-profile: public' \
  -H 'apikey: {SUPABASE_API_KEY}'
```

### 响应

#### 成功响应 (200 OK)

返回字幕对象数组。

#### 响应字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | number | 字幕条目唯一标识 |
| video_id | string (UUID) | 所属视频 ID |
| start_time | number | 开始时间（秒） |
| end_time | number | 结束时间（秒） |
| english_text | string | 英文字幕 |
| chinese_text | string | 中文字幕 |
| sequence_number | number/null | 序列号 |
| created_at | string (ISO 8601) | 创建时间 |

#### 响应示例

```json
[
  {
    "id": 7315,
    "video_id": "661118fe-91fb-4c19-a140-7a62279bce57",
    "start_time": 0,
    "end_time": 1.533,
    "english_text": "Rise and shine.",
    "chinese_text": "该起床喽。",
    "sequence_number": null,
    "created_at": "2025-12-15T23:14:51.95401+00:00"
  },
  {
    "id": 7316,
    "video_id": "661118fe-91fb-4c19-a140-7a62279bce57",
    "start_time": 2.133,
    "end_time": 3.833,
    "english_text": "Rise and shine.",
    "chinese_text": "该起床喽。",
    "sequence_number": null,
    "created_at": "2025-12-15T23:14:51.95401+00:00"
  }
]
```

---

## 4. 获取短语卡片

获取视频中的重点短语卡片，用于英语学习。

### 基本信息

- **URL**: `/phrase_cards`
- **Method**: `GET`
- **描述**: 获取视频中的短语学习卡片，按首次出现时间排序

### 请求参数

#### Query Parameters

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| select | string | 否 | 选择返回的字段，`*` 表示所有字段 | `*` |
| video_id | string | 是 | 视频 ID（使用 `eq.` 前缀） | `eq.661118fe-91fb-4c19-a140-7a62279bce57` |
| order | string | 否 | 排序规则 | `first_appearance_time.asc` |

### 请求示例

```bash
curl 'https://boyyfwfjqczykgufyasp.supabase.co/rest/v1/phrase_cards?select=*&video_id=eq.661118fe-91fb-4c19-a140-7a62279bce57&order=first_appearance_time.asc' \
  -H 'accept-profile: public' \
  -H 'apikey: {SUPABASE_API_KEY}'
```

### 响应

#### 成功响应 (200 OK)

返回短语卡片对象数组。

#### 响应字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | string (UUID) | 短语卡片唯一标识 |
| video_id | string (UUID) | 所属视频 ID |
| phrase | string | 短语内容 |
| phonetic | string | 音标 |
| chinese_definition | string | 中文释义 |
| synonyms | string | 同义词/近义词 |
| context | string | 上下文例句（英文） |
| context_translation | string | 例句翻译（中文） |
| subtitle_id | number | 关联的字幕 ID |
| first_appearance_time | number | 首次出现时间（秒） |
| difficulty_level | number | 难度级别 |
| created_at | string (ISO 8601) | 创建时间 |
| updated_at | string (ISO 8601) | 更新时间 |

#### 响应示例

```json
[
  {
    "id": "b735e281-54ce-4bbb-a9eb-de53c8dc78b3",
    "video_id": "661118fe-91fb-4c19-a140-7a62279bce57",
    "phrase": "rise and shine",
    "phonetic": "/raɪz ənd ʃaɪn/",
    "chinese_definition": "起床啦；打起精神开始一天（常用来叫人起床）",
    "synonyms": "wake up, get up",
    "context": "Rise and shine.",
    "context_translation": "该起床喽。",
    "subtitle_id": 7315,
    "first_appearance_time": 0,
    "difficulty_level": 1,
    "created_at": "2025-12-15T23:15:10.44076+00:00",
    "updated_at": "2025-12-15T23:15:10.44076+00:00"
  }
]
```

---

## 5. 获取单词卡片

获取视频中的重点单词卡片，用于词汇学习。

### 基本信息

- **URL**: `/word_cards`
- **Method**: `GET`
- **描述**: 获取视频中的单词学习卡片，按首次出现时间排序

### 请求参数

#### Query Parameters

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| select | string | 否 | 选择返回的字段，`*` 表示所有字段 | `*` |
| video_id | string | 是 | 视频 ID（使用 `eq.` 前缀） | `eq.661118fe-91fb-4c19-a140-7a62279bce57` |
| order | string | 否 | 排序规则 | `first_appearance_time.asc` |

### 请求示例

```bash
curl 'https://boyyfwfjqczykgufyasp.supabase.co/rest/v1/word_cards?select=*&video_id=eq.661118fe-91fb-4c19-a140-7a62279bce57&order=first_appearance_time.asc' \
  -H 'accept-profile: public' \
  -H 'apikey: {SUPABASE_API_KEY}'
```

### 响应

#### 成功响应 (200 OK)

返回单词卡片对象数组。

#### 响应字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | string (UUID) | 单词卡片唯一标识 |
| video_id | string (UUID) | 所属视频 ID |
| word | string | 单词 |
| phonetic | string | 音标 |
| chinese_definition | string | 中文释义 |
| english_definition | string | 英文释义/同义词 |
| example_from_video | string | 视频中的例句（英文） |
| example_translation | string | 例句翻译（中文） |
| subtitle_id | number | 关联的字幕 ID |
| first_appearance_time | number | 首次出现时间（秒） |
| difficulty_level | number | 难度级别 |
| frequency_rank | number/null | 词频排名 |
| part_of_speech | string/null | 词性 |
| other_pos_definitions | any/null | 其他词性的释义 |
| created_at | string (ISO 8601) | 创建时间 |
| updated_at | string (ISO 8601) | 更新时间 |

#### 响应示例

```json
[
  {
    "id": "054198a2-d6a7-4045-9cad-f83361a6b555",
    "video_id": "661118fe-91fb-4c19-a140-7a62279bce57",
    "word": "rise",
    "phonetic": "/raɪz/",
    "chinese_definition": "vi. 起床；起身（尤指早起）",
    "english_definition": "get up, arise",
    "example_from_video": "Rise and shine.",
    "example_translation": "该起床喽。",
    "subtitle_id": 7315,
    "first_appearance_time": 0,
    "difficulty_level": 1,
    "frequency_rank": null,
    "part_of_speech": null,
    "other_pos_definitions": null,
    "created_at": "2025-12-15T23:23:50.811097+00:00",
    "updated_at": "2025-12-15T23:23:50.811097+00:00"
  }
]
```

---

## 6. 获取视频标签和作者

获取视频的标签信息，包括作者名称、主题分类等。

### 基本信息

- **URL**: `/video_tags`
- **Method**: `GET`
- **描述**: 获取视频关联的标签信息，支持关联查询 tags 表获取详细标签信息

### 请求参数

#### Query Parameters

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| select | string | 否 | 选择返回的字段，支持关联查询 | `video_id,tag_id,is_primary,tags(*)` |
| video_id | string | 是 | 视频 ID 过滤，支持单个或多个 | `eq.xxx` 或 `in.(xxx,yyy)` |

### 关联查询说明

使用 `tags(*)` 可以关联查询 tags 表，获取标签的详细信息：
- `tags(*)` - 获取关联标签的所有字段
- `tags(id,name,type)` - 只获取指定字段

### 请求示例

#### 单个视频

```bash
curl 'https://boyyfwfjqczykgufyasp.supabase.co/rest/v1/video_tags?select=video_id,tag_id,is_primary,tags(*)&video_id=eq.661118fe-91fb-4c19-a140-7a62279bce57' \
  -H 'accept-profile: public' \
  -H 'apikey: {SUPABASE_API_KEY}'
```

#### 多个视频（批量查询）

```bash
curl 'https://boyyfwfjqczykgufyasp.supabase.co/rest/v1/video_tags?select=video_id,tag_id,is_primary,tags(*)&video_id=in.(661118fe-91fb-4c19-a140-7a62279bce57,a6c0e934-62c2-4c03-b163-3448d3b7e5d8)' \
  -H 'accept-profile: public' \
  -H 'apikey: {SUPABASE_API_KEY}'
```

### 响应

#### 成功响应 (200 OK)

返回视频标签关联对象数组。

#### 响应字段说明

**video_tags 表字段**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| video_id | string (UUID) | 视频 ID |
| tag_id | string (UUID) | 标签 ID |
| is_primary | boolean | 是否为主标签 |
| tags | object | 关联的标签详细信息 |

**tags 表字段**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | string (UUID) | 标签唯一标识 |
| name | string | 标签名称 |
| type | string | 标签类型：`creator`（作者）、`topic`（主题） |
| color | string | 标签颜色（HEX 格式） |
| category | string/null | 标签分类（如"生活"、"旅行"） |
| icon | string/null | 标签图标 |
| usage_count | number | 使用次数 |
| display_order | number | 显示顺序 |
| created_at | string (ISO 8601) | 创建时间 |
| updated_at | string (ISO 8601) | 更新时间 |

#### 响应示例

```json
[
  {
    "video_id": "661118fe-91fb-4c19-a140-7a62279bce57",
    "tag_id": "b10232ed-0cc7-4315-8fb1-3ae529363bac",
    "is_primary": false,
    "tags": {
      "id": "b10232ed-0cc7-4315-8fb1-3ae529363bac",
      "name": "Volka English",
      "type": "creator",
      "color": "#3B82F6",
      "category": null,
      "icon": null,
      "usage_count": 3,
      "display_order": 0,
      "created_at": "2025-11-30T00:18:16.380407+00:00",
      "updated_at": "2025-12-15T23:13:11.322333+00:00"
    }
  },
  {
    "video_id": "661118fe-91fb-4c19-a140-7a62279bce57",
    "tag_id": "6bcd52d5-a63c-453f-8154-59750f4419f8",
    "is_primary": true,
    "tags": {
      "id": "6bcd52d5-a63c-453f-8154-59750f4419f8",
      "name": "日常生活",
      "type": "topic",
      "color": "#10B981",
      "category": "生活",
      "icon": null,
      "usage_count": 68,
      "display_order": 0,
      "created_at": "2025-09-30T14:51:56.773342+00:00",
      "updated_at": "2025-12-15T23:13:11.322333+00:00"
    }
  }
]
```

#### 标签类型说明

- **creator**: 视频作者/博主名称（如 "Volka English"、"Ariannita la Gringa"）
- **topic**: 视频主题分类（如 "日常生活"、"自然风光"）

#### 使用场景

1. **获取视频作者**: 筛选 `type=creator` 的标签
2. **获取视频主题**: 筛选 `type=topic` 的标签
3. **主标签识别**: `is_primary=true` 标记该标签为主要标签
4. **批量查询**: 使用 `in.()` 语法一次获取多个视频的标签

---

## 错误码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（API Key 无效或缺失） |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 数据关系说明

这是一个视频英语学习应用，数据之间的关系如下：

```
videos (视频)
  ├─ video_tags (视频标签关联) - 通过 video_id 关联
  │    └─ tags (标签详情) - 通过 tag_id 关联
  │         ├─ type: creator (视频作者)
  │         └─ type: topic (主题分类)
  │
  └─ subtitles (字幕) - 通过 video_id 关联
       ├─ phrase_cards (短语卡片) - 通过 video_id 和 subtitle_id 关联
       └─ word_cards (单词卡片) - 通过 video_id 和 subtitle_id 关联
```

### 典型的数据获取流程

1. 获取视频列表 (`/videos`) - 展示可用视频
2. 用户选择视频后，获取视频详情 (`/videos?id=eq.xxx`)
3. 获取视频标签 (`/video_tags?video_id=eq.xxx&select=*,tags(*)`) - 显示作者和主题
4. 加载视频的字幕 (`/subtitles?video_id=eq.xxx`) - 用于双语字幕显示
5. 加载短语卡片 (`/phrase_cards?video_id=eq.xxx`) - 用于学习重点短语
6. 加载单词卡片 (`/word_cards?video_id=eq.xxx`) - 用于学习重点单词

### 批量数据获取优化

对于视频列表页，可以使用批量查询减少请求次数：

```bash
# 一次性获取多个视频的标签
/video_tags?video_id=in.(id1,id2,id3)&select=*,tags(*)
```

## 视频播放地址

应用提供了两种视频播放方式：

### 1. Cloudflare Stream (推荐)

使用视频对象中的 `cloudflare_stream_id` 构造 HLS 播放地址：

**m3u8 地址格式**:
```
https://customer-pqultjblfor3dl6u.cloudflarestream.com/{cloudflare_stream_id}/manifest/video.m3u8
```

**示例**:
```bash
# 从视频接口获取 cloudflare_stream_id
{
  "cloudflare_stream_id": "55f62627b830f550a3793081be54ddb7"
}

# 构造播放地址
curl 'https://customer-pqultjblfor3dl6u.cloudflarestream.com/55f62627b830f550a3793081be54ddb7/manifest/video.m3u8'
```

**特性**:
- 自适应码率，支持多种分辨率（240p ~ 1080p）
- 标准 HLS 协议，兼容主流播放器
- Cloudflare CDN 加速，全球低延迟

### 2. 腾讯云直链

视频对象中的 `tencent_cloud_url` 提供直接的 MP4 播放地址：

```json
{
  "tencent_cloud_url": "https://video-cn.dongchenyu.cn/riseandshine.mp4"
}
```

适用于需要直接下载或简单播放的场景。

---

## 注意事项

1. **时间格式**: 所有时间字段均为 ISO 8601 格式，包含时区信息
2. **认证**: API Key 和 Authorization Token 保持一致
3. **Schema**: `accept-profile: public` 指定访问的 Supabase schema
4. **视频播放**: 优先使用 Cloudflare Stream m3u8 地址，提供更好的播放体验
5. **状态字段**: `is_published` 字段可能与 `status` 字段不一致，建议以 `status` 为准
6. **过滤语法**: Supabase PostgREST 使用 `eq.` 前缀进行等值过滤，如 `id=eq.xxx`
7. **排序语法**: 使用 `.asc` 或 `.desc` 后缀进行排序，如 `start_time.asc`
8. **字幕时间轴**: 字幕的 `start_time` 和 `end_time` 以秒为单位
9. **卡片关联**: 短语卡片和单词卡片通过 `subtitle_id` 与具体的字幕条目关联，`first_appearance_time` 记录了该短语/单词在视频中首次出现的时间点
