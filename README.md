# خدمة إدارة المهام REST API

## 1. وصف المشروع

**Task Management REST Service**
<div dir="rtl">

هي خدمة `RESTful` لإدارة المهام، تم تطويرها باستخدام إطار العمل `FastAPI` وربطها بقاعدة بيانات `PostgreSQL`، ثم تحويلها إلى بنية متعددة الحاويات باستخدام `Docker` و `Docker Compose`.

</div>

الهدف من المشروع هو تطبيق مبادئ الحاويات والعزل والشبكات والتخزين الدائم والـ Reverse Proxy والتوزيع عبر Registry.

البنية النهائية للمشروع تفصل بين:

- Nginx كـ Reverse Proxy
- Backend REST API
- PostgreSQL Database
- Docker Named Volume لتخزين بيانات قاعدة البيانات بشكل دائم

---

## 2. المعمارية النهائية

```text
                         CLIENT
                            |
                            | HTTP :8080
                            v
                   +------------------+
                   |      NGINX       |
                   |  Reverse Proxy   |
                   +--------+---------+
                            |
                            | Internal HTTP
                            v
                   +------------------+
                   |       API        |
                   |     FastAPI      |
                   |      :8000       |
                   |    Non-root      |
                   +--------+---------+
                            |
                            | PostgreSQL :5432
                            v
                   +------------------+
                   |     DATABASE     |
                   |    PostgreSQL    |
                   +--------+---------+
                            |
                            v
                   +------------------+
                   |   Named Volume   |
                   |      db-data     |
                   +------------------+
```

في البنية النهائية يكون Nginx هو نقطة الدخول الخارجية الوحيدة:

```text
Host :8080 → Nginx :80
```

أما الـ API وقاعدة البيانات فيتواصلان داخليًا عبر شبكة Docker.

---

## 3. التقنيات المستخدمة

| المكوّن | التقنية |
|---|---|
| لغة البرمجة | Python 3.13 |
| Backend Framework | FastAPI |
| Application Server | Uvicorn |
| Database | PostgreSQL 17 |
| Reverse Proxy | Nginx |
| Containerization | Docker |
| Orchestration | Docker Compose v2 |
| API Testing | cURL |
| Registry | Docker Hub |

---

## 4. بنية المشروع

```text
Task Management REST Service/
│
├── api/
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── database/
│   └── init.sql
│
├── nginx/
│   └── nginx.conf
│
├── evidence/
│   └── screenshots
│
├── .dockerignore
├── .gitignore
├── compose.yaml
├── requirements.txt
└── README.md
```

---

## 5. المتطلبات المسبقة

يحتاج المشروع إلى:

- Docker Desktop أو Docker Engine
- Docker Compose v2
- Git
- cURL
- اتصال بالإنترنت

للتحقق:

```bash
docker --version
docker compose version
git --version
```

---

## 6. تشغيل المشروع

لتشغيل النظام كاملًا باستخدام Compose:

```bash
docker compose up -d --build
```

هذا الأمر يقوم ببناء صورة الـ API عند الحاجة ثم يشغّل الخدمات:

```text
Nginx
API
PostgreSQL
```

لمشاهدة حالة الخدمات:

```bash
docker compose ps
```

---

## 7. واجهات الـ API

العنوان الخارجي:

```text
http://localhost:8080
```

جميع الطلبات الخارجية تمر عبر Nginx.

### 7.1 الحصول على جميع المهام

```http
GET /api/tasks
```

مثال:

```bash
curl http://localhost:8080/api/tasks
```

### 7.2 الحصول على مهمة واحدة

```http
GET /api/tasks/{id}
```

مثال:

```bash
curl http://localhost:8080/api/tasks/1
```

### 7.3 إنشاء مهمة

```http
POST /api/tasks
```

مثال:

```bash
curl -X POST http://localhost:8080/api/tasks \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Example Task\",\"description\":\"Task description\",\"status\":\"Pending\",\"due_date\":\"2026-09-25\"}"
```

### 7.4 تحديث مهمة

```http
PUT /api/tasks/{id}
```

مثال:

```bash
curl -X PUT http://localhost:8080/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Updated Task\",\"description\":\"Updated description\",\"status\":\"In Progress\",\"due_date\":\"2026-09-25\"}"
```

### 7.5 حذف مهمة

```http
DELETE /api/tasks/{id}
```

مثال:

```bash
curl -X DELETE http://localhost:8080/api/tasks/1
```

---

## 8. نموذج البيانات

يتكون سجل المهمة من:

```text
id
title
description
status
due_date
```

وتم تعريف الجدول في:

```text
database/init.sql
```

---

## 9. تصميم Dockerfile

تم استخدام:

```text
python:3.13-slim
```

لأنه Base Image خفيفة ومناسبة لتشغيل Python.

ويستخدم Dockerfile:

```text
WORKDIR /app
```

كما تم فصل طبقة الـ dependencies عن طبقة source code:

```dockerfile
COPY api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY api/ ./api/
```

الهدف من هذا الترتيب هو تحسين Docker Layer Caching، بحيث يمكن إعادة استخدام طبقة تثبيت المكتبات عند تغيير source code فقط.

كما يعمل التطبيق باستخدام مستخدم غير root:

```text
appuser
```

---

## 10. Nginx Reverse Proxy

يوجد ملف إعداد مخصص:

```text
nginx/nginx.conf
```

ويستخدم Nginx اسم خدمة Docker:

```text
api:8000
```

لتوجيه الطلبات إلى الـ Backend.

الملف يتم تركيبه للقراءة فقط:

```text
./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
```

المسار الخارجي:

```text
Client
  ↓
Nginx :8080
  ↓
API :8000
```

ولا يتم نشر منفذ `8000` الخاص بالـ API على الـ Host.

---

## 11. Docker Compose

يعرّف `compose.yaml` ثلاث خدمات:

```text
nginx
api
database
```

وجميعها مرتبطة بالشبكة:

```text
app-network
```

ويتم الوصول إلى PostgreSQL من الـ API باستخدام اسم الخدمة:

```text
database:5432
```

بدلًا من:

```text
localhost
```

لأن `localhost` داخل Container يشير إلى نفس الـ Container.

---

## 12. التخزين الدائم

تستخدم قاعدة البيانات Docker Named Volume باسم منطقي داخل Compose:

```text
db-data
```

ويُستخدم لتخزين بيانات PostgreSQL خارج دورة حياة الـ Container.

تم التحقق من الـ Persistence عن طريق:

```text
إدخال سجل
   ↓
docker compose down
   ↓
docker compose up -d
   ↓
الاستعلام مرة أخرى
   ↓
السجل ما زال موجودًا
```

الفرق المهم:

```bash
docker compose down
```

لا يحذف الـ Named Volume.

بينما:

```bash
docker compose down -v
```

يحذف الـ Volumes التي يديرها Compose وقد يؤدي إلى فقدان بيانات قاعدة البيانات.

---

## 13. Health Checks والاعتماديات

تمت إضافة Health Check لقاعدة البيانات باستخدام:

```text
pg_isready
```

كما تم جعل API تنتظر جاهزية قاعدة البيانات:

```text
database → healthy
       ↓
      API
```

وجعل Nginx ينتظر جاهزية API:

```text
API → healthy
  ↓
Nginx
```

وهذا يوضح الفرق بين مجرد بدء Container وبين جاهزية الخدمة فعليًا.

---

## 14. ممارسات الأمان

المشروع يطبق عدة ممارسات أمنية، منها:

- تشغيل API كمستخدم غير root.
- عدم نشر منفذ API على الـ Host.
- عدم نشر منفذ PostgreSQL على الـ Host.
- جعل Nginx نقطة الدخول الخارجية.
- تركيب ملف Nginx للقراءة فقط.
- تثبيت إصدارات المكتبات.
- استخدام Base Image خفيفة.
- عزل الاتصال الداخلي عبر Docker bridge network.
- استخدام `.gitignore` و`.dockerignore` لاستبعاد الملفات المحلية والمؤقتة.

---

## 15. سيناريوهات الفشل التي تم اختبارها

### الحالة A — توقف API

تم تنفيذ:

```bash
docker compose stop api
```

ثم تم الوصول إلى API من خلال Nginx، وكانت النتيجة:

```text
502 Bad Gateway
```

ثم تمت استعادة الخدمة بواسطة:

```bash
docker compose start api
```

### الحالة B — توقف قاعدة البيانات

تم تنفيذ:

```bash
docker compose stop database
```

وأصبح طلب API يفشل بسبب عدم توفر قاعدة البيانات، ثم تمت استعادة قاعدة البيانات بواسطة:

```bash
docker compose start database
```

### الحالة C — إعادة إنشاء API Container

تمت إعادة إنشاء خدمة API مع:

```bash
docker compose up -d --force-recreate api
```

وبعد ذلك بقيت بيانات المهمة موجودة، مما يثبت أن البيانات تعتمد على التخزين الدائم في قاعدة البيانات وليس على Container نفسه.

### الحالة D — عزل المنافذ

تم التحقق من أن:

```text
8080 → Nginx      متاح
8000 → API        غير منشور على Host
5432 → Database   غير منشور على Host
```

---

## 16. Docker Hub وVersioning

مستودع Docker Hub:

```text
docker.io/osama2sv/task-management-api
```

الإصدارات المستخدمة:

```text
v1.0.0
latest
```

أمر البناء:

```bash
docker build -f api/Dockerfile -t task-management-api:v1.0.0 .
```

الأوامر الخاصة بالـ Registry:

```bash
docker tag task-management-api:v1.0.0 osama2sv/task-management-api:v1.0.0
docker tag task-management-api:latest osama2sv/task-management-api:latest
```

ثم:

```bash
docker push osama2sv/task-management-api:v1.0.0
docker push osama2sv/task-management-api:latest
```

والسحب:

```bash
docker pull osama2sv/task-management-api:v1.0.0
docker pull osama2sv/task-management-api:latest
```

تم التحقق من الـ Pull وتشغيل الصورة المنشورة.

---

## 17. أوامر Docker المهمة

التحقق من Compose:

```bash
docker compose config
```

التشغيل:

```bash
docker compose up -d --build
```

عرض الخدمات:

```bash
docker compose ps
```

عرض Logs:

```bash
docker compose logs
docker compose logs api
docker compose logs nginx
```

إيقاف النظام:

```bash
docker compose down
```

فحص الصور:

```bash
docker image ls
docker image history task-management-api:v1.0.0
```

فحص الشبكات:

```bash
docker network ls
docker network inspect taskmanagementrestservice_app-network
```

فحص التخزين:

```bash
docker volume ls
docker volume inspect taskmanagementrestservice_db-data
```

---

## 18. مساهمات أعضاء الفريق

| العضو | المسؤولية |
|---|---|
| **أسامة الجهوري** | تطوير REST API ودمج PostgreSQL وعمليات CRUD |
| **عبدالله اليافعي** | مراجعة Dockerfile وشرح Image Layers وDependency Caching |
| **معتز ابكر** | مراجعة Nginx وReverse Proxy وNetwork Architecture |
| **عمر الاسيدي** | مراجعة Docker Compose وPersistence وRegistry وTesting Evidence |

يجب أن يكون جميع أعضاء الفريق قادرين على شرح المعمارية الكاملة وأي جزء من المشروع أثناء التقييم.

---

## 19. الإصدار الحالي

الإصدار:

```text
v1.0.0
```

الوسم المتحرك:

```text
latest
```

---

## 20. التحقق النهائي

تم اختبار النظام من خلال:

- CRUD للـ REST API.
- أكواد HTTP المناسبة.
- الطلبات غير الصحيحة والتحقق من صحة المدخلات.
- الموارد غير الموجودة.
- Docker Build.
- `docker image history`.
- التحقق من Non-root.
- Nginx Reverse Proxy.
- Docker Compose.
- Docker Network.
- Named Volume.
- Persistence.
- Failure Scenarios.
- Docker Hub Push/Pull.
- تشغيل الصورة المنشورة.

---

## 21. أدلة الاختبار

تم حفظ لقطات التحقق داخل:

```text
evidence/
```

وتشمل الأدلة الخاصة بـ:

- API Testing
- Docker Build
- Docker Image Inspection
- Nginx Routing
- Docker Compose
- Persistence
- Network
- Failure Scenarios
- Port Isolation
- Docker Hub

---

## 22. معلومات المشروع

**اسم المشروع:** Task Management REST Service

**الإصدار:** v1.0.0

**Registry:** Docker Hub

**Repository:**

```text
docker.io/osama2sv/task-management-api
```
